---
date: 2025-12-07
categories:
    - ML Engineering
tags: 
    - Series 
    - Tutorial
    - Modern ML Microservices
links:
    - Part One: posts/2025-01-26-ml-micro-part-one.md
    - Part Two: posts/2025-02-05-ml-micro-part-two.md
    - Part Three: posts/2025-02-16-ml-micro-part-three.md
    - Part Four: posts/2025-03-25-ml-micro-part-four.md
    - Part Five: posts/2025-04-13-ml-micro-part-five.md
    - Part Six: posts/2025-05-04-ml-micro-part-six.md
    - Part Seven: posts/2025-06-01-ml-micro-part-seven.md
    - Part Eight: posts/2025-08-17-ml-micro-part-eight.md
---

# Delve 19: Let's Build a Modern ML Microservice Application - Part 9, Docker Container Optimization

![Banner](../assets/images/banners/delve19.png)

> "Containerization is the new virtualization." - James Turnbull

Greetings data delvers! In [part eight](2025-08-17-ml-micro-part-eight.md) of this series we deployed our first multi-service system. In this part, we examine more deeply how we are deploying our services with Docker and look for opportunities to make our deployment more optimized and secure.
<!-- more -->

## Where we Left Off

In our last part we briefly touched on [dockerizing our application](2025-08-17-ml-micro-part-eight.md#building-the-orchestrator-dockerizing) using the below Dockerfile:

```docker title="housing-price-orchestrator/Dockerfile" linenums="1"
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, copy the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
```

We can quickly check the size of the image built from this file with the `docker image ls` command:

```bash
docker image ls modern-ml-microservices-housing-price-orchestrator
REPOSITORY                                           TAG       IMAGE ID       CREATED        SIZE
modern-ml-microservices-housing-price-orchestrator   latest    c02bbc40ca76   2 months ago   375MB
```

`375MB` — not bad! This file does what we need it to do but has a few shortcomings; let's break them down.

## Standard Base Image

We are currently using the `ghcr.io/astral-sh/uv:python3.13-bookworm-slim` base image provided by Astral. This works great; however, enterprises often have a set of standard base images approved by the organization. What if we want to use a standard base image but install `uv` into it? Fortunately, Astral provides [guidance](https://docs.astral.sh/uv/guides/integration/docker/#installing-uv) on how to do that. We can instead copy the `uv` binary from one of their official images into ours:

```docker title="housing-price-orchestrator/Dockerfile" linenums="1" hl_lines="1-4"
FROM python:3.13-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.16 /uv /uvx /bin/

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, copy the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
```

!!! note
    The offical Astral docs show installing `uv` from the `latest` tag however I recommend pinning to a specific version instead. This ensures that no breaking changes in `uv` inadvertently break your build.

## Build Dependencies

Many Python popular packages with C extensions (such as Numpy) will often require compilers such as `gcc` or `g++` to be available on the machine in which they are installed. We can preemptively install these into our image to ensure that we won't run into any issues, we can also use this as an opportunity to make sure all system packages are up to date in the image as well:

```docker title="housing-price-orchestrator/Dockerfile" linenums="1" hl_lines="9-15"
FROM python:3.13-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.16 /uv /uvx /bin/

# Install the project into `/app`
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, copy the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
```

!!! note
    Notice how we are adding `rm -rf /var/lib/apt/lists/*` to the end of the install command, this saves us space in the final image. When `apt-get update` is executed inside the Docker container, the package manager downloads package lists and metadata into /var/lib/apt/lists/. These files are crucial for the installation process but are not needed for running the final application. Removing them frees up significant space. 

This will have the effect of increasing the size of the image but we'll see how to deal with that soon.

## Environment Variables

Version `0.8.7` of `uv` added the [UV_NO_DEV](https://docs.astral.sh/uv/reference/environment/#uv_no_dev) environment variable. Since we don't want dev dependencies in this image we can set it globally to ensure that no dev dependencies are installed:

```docker title="housing-price-orchestrator/Dockerfile" linenums="1" hl_lines="17-24"
FROM python:3.13-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.16 /uv /uvx /bin/

# Install the project into `/app`
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Don't install dev dependencies
ENV UV_NO_DEV=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, copy the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
```

It's also worth explaining the other environment variables we are leveraging:

* [UV_COMPILE_BYTECODE](https://docs.astral.sh/uv/reference/environment/#uv_compile_bytecode) - Setting this ensures that `uv` will compile the bytecode of all Python source files ahead of time, leading to longer container build times but shorter execution times, typically a desired tradeoff in deployed images.

* [UV_LINK_MODE](https://docs.astral.sh/uv/reference/environment/#uv_link_mode) — We can pair setting this variable along with a [caching strategy] described in the `uv` documentation to speed up local builds by reusing the system `uv` cache instead of forcing `uv` to create its own inside the container.

## Installing Dependencies

We can clean up and optimize the dependency installation steps as well:

```docker title="housing-price-orchestrator/Dockerfile" linenums="1" hl_lines="26-37"
FROM python:3.13-slim-bookworm

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.16 /uv /uvx /bin/

# Install the project into `/app`
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Don't install dev dependencies
ENV UV_NO_DEV=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Then, copy the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    uv sync --frozen

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
```

We are taking advantage of our caching strategy when installing our dependencies, we also no longer need the `--no-dev` flag since we've set the environment variable.

We also want to install dependencies exactly as they exist in the `uv.lock` file without modification so we are using the `--frozen` flag.

Notice we are installing project dependencies separately from the source code. This is due to the [Docker build cache](https://docs.docker.com/build/cache/). Each command in the Dockerfile creates a new layer in the final image. These layers are cached by Docker. Whenever a layer changes, it will need to be rebuilt. When this happens, all layers that come *after* that layer will also have to be rebuilt. This means you should always put layers that are more likely to change *after* layers that are less likely to change. In our case, it's more likely we'll change our project's source code while developing it rather than its dependencies. Breaking the install step into two separate layers allows us to reuse the dependency installation layer when rebuilding our Docker image if only the source code has changed, leading to faster local build times.

!!! warning
    The official `uv` docs recommend using the `--locked` flag instead of `--frozen` to prevent building with an outdated lockfile; however, this does not work when using `uv` [workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) as we are. This is because `uv` would need access to all `pyproject.toml` files to verify that the lockfile is up to date, not just the individual workspace lockfile. As such, **ensure that your lockfile is up to date by running `uv sync`** before building the image!

## Everything and the Kitchen Sink

The rest of the commands in the file are pretty self-explanatory and do not change. Let's go ahead and check the size of our built image now:

```bash
docker image ls modern-ml-microservices-housing-price-orchestrator
REPOSITORY                                           TAG       IMAGE ID       CREATED         SIZE
modern-ml-microservices-housing-price-orchestrator   latest    2fea0c60cd2b   8 seconds ago   667MB
```

Yikes! `667MB`! Our image has more than doubled in size, likely due to the additional build dependencies. However, we shouldn't be compiling any code when our container is running. Moreover, if a bad actor gained access to our container, they could now compile malicious code, presenting a larger attack surface. Additionally, if any of these build dependencies had unknown vulnerabilities, we would be susceptible to them even though we don't need them at runtime! We can reduce the size of our container and make it more secure by leveraging [multi-stage builds](https://docs.docker.com/build/building/multi-stage/).

Keeping with Docker's nautical theme, I liken building an image to launching a ship. To build a ship, you need substantial scaffolding around it so shipyard workers can do their jobs. However, when it comes time to launch, the scaffolding is removed before the ship leaves the dry dock. If I told you we were launching a ship with scaffolding still attached, you'd say I was crazy! Right now, we are **launching our image with the scaffolding attached**. In our case, the scaffolding is all the build-time dependencies.

To fix this, let's first designate our current image as our `builder` shipyard:

```docker title="housing-price-orchestrator/Dockerfile" linenums="1" hl_lines="1"
FROM python:3.13-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.16 /uv /uvx /bin/

# Install the project into `/app`
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Don't install dev dependencies
ENV UV_NO_DEV=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Then, copy the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    uv sync --frozen

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
```

Next, once our code is built, we can copy only what we need to execute the final application from our `builder` stage into the final image, thus removing the scaffolding:

```docker title="housing-price-orchestrator/Dockerfile" linenums="1" hl_lines="39-50"
FROM python:3.13-slim-bookworm AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.9.16 /uv /uvx /bin/

# Install the project into `/app`
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Don't install dev dependencies
ENV UV_NO_DEV=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

# Then, copy the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock,from=project_root \
    uv sync --frozen

FROM python:3.13-slim-bookworm

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Install the project into `/app`
WORKDIR /app

# Copy project from the builder stage
COPY --from=builder /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
CMD ["fastapi", "run", "src/main.py", "--port", "8000"]
```

Since this is a new base image, we can take the opportunity to update its system packages. This is also where we could install any runtime system dependencies.

With our scaffolding removed let's check the size of the final image:

```bash
 docker image ls modern-ml-microservices-housing-price-orchestrator
REPOSITORY                                           TAG       IMAGE ID       CREATED         SIZE
modern-ml-microservices-housing-price-orchestrator   latest    a28fc433e42d   7 seconds ago   324MB
```

`324MB` — smaller than where we started (likely because `uv` is no longer installed in the final image). Congratulations! You now have an image that is both smaller and more secure than our original, while capable of supporting projects with more complex system-dependency requirements. Code for this part can be found [here](https://github.com/DataDelver/modern-ml-microservices/tree/part-nine)!

## Delve Data
* There are a number of optimizations described in the `uv` documentation for Docker image builds.
* Using multi-stage Docker builds, we can support additional build-time dependencies while ensuring they don't increase the size of the overall image.
