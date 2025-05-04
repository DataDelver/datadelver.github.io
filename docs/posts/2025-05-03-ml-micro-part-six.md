---
date: 2025-05-03
categories:
    - Software Engineering
tags: 
    - Series 
    - Tutorial
    - Modern ML Microservices
links:
    - Part One: posts/2025-01-26-ml-micro-part-one.md
    - Part Two: posts/2025-02-05-ml-micro-part-two.md
    - Part Three: posts/2025-02-16-ml-micro-part-three.md
    - Part Four: posts/2025-03-25-ml-micro-part-four.md
    - Part Five: posts/2025-04-12-ml-micro-part-five.md
---

# Delve 12: Let's Build a Modern ML Microservice Application - Part 6, Containerization

![Banner](../assets/images/banners/delve12.png)

> "This containers revolution is changing the basic act of software consumption. It’s redefining this much more lightweight, portable unit, or atom, that is much easier to manage… It’s a gateway to dynamic management and dynamic systems." - Craig McLuckie

## ML Microservices, Deployment through Docker

Hello data delvers! In [part five](2025-04-13-ml-micro-part-four.md) of this series we added automated tests to our application to make it easier to catch bugs. I this part we'll cover packaging and deploying the app!  
<!-- more -->

## From Near to Afar, Or How to Leave my Local Machine

Up until this point, we have been executing our application on our local machine with the command line or the built in VSCode runner, but we aren't going to ship our whole local computer to production! We need a simple way to package our application with its dependencies in a way that makes it easy to deploy (either in an on-prem computing environment or with a cloud provider). By this point you've probably heard of [containerization](https://en.wikipedia.org/wiki/Containerization_(computing)), most likely through its most popular implementation: [Docker](https://www.docker.com/). Fortunately for us, Docker is the perfect tool to package our app. It provides a convenient way to package all the Python dependencies our application needs, provide an environment to execute our Fast API application, and deploy the application to our desired computing environment. So let's get started!

Firstly, you will need to install Docker on your machine if you have not done so already. Docker Desktop is the official tooling provided by Docker to achieve this, however [due to some drama about commercial use licensing of Docker Desktop](https://www.servethehome.com/docker-abruptly-starts-charging-many-users-for-docker-desktop/), I actually prefer to use [Rancher Desktop](https://rancherdesktop.io/) as an alternative with a more permissive license. Whichever you prefer, install it and make sure you have the WSL integration enabled if you plan to use it within your WSL environment (if you are on a Windows machine). You can verify that Docker is correctly installed by opening a shell and running the `docker --version` command. You should see something like the below output:

```
$docker --version
Docker version 27.5.1-rd, build 0c97515
```

Next, you'll want to grab the official [Container Tools Extension for VSCode](https://marketplace.visualstudio.com/items/?itemName=ms-azuretools.vscode-containers) and with that your development environment should be all set up!

## Dock and Load: Packing Microservices Like a Pro

To containerize our application using Docker we must create a `Dockerfile` which serves as a set of instructions for building your container *image*. An *image* is to a *container* what as *class* is to an *object* in OOP. The *image* is the static definition of the "object" (in this case our application) while the *container* is a running instance of that image. When creating Dockerfiles it is common to build them on top of existing Docker images, in this way you don't need to specify all of the dependencies of your underlying operating system for example, you can just build on top of an image that already has all of the OS dependencies installed. Fortunately for us uv provides a [prebuilt Docker Image](https://docs.astral.sh/uv/guides/integration/docker/) we can use for the base of our our Dockerfile as well as an [example Dockerfile](https://github.com/astral-sh/uv-docker-example/blob/main/Dockerfile), a slightly modified version of which is provided below:

```docker title="Dockerfile" linenums="1"
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Then, copy the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Run the FastAPI application by default
CMD ["fastapi", "run", "src/main.py", "--port", "80"]
```

An explanation of many of the optimizations present in the above file are provided in the uv documentation. For our purposes the only things to note are that we use `COPY` instead of `ADD` (which is the best practice [recommended by Docker](https://docs.docker.com/build/building/best-practices/#add-or-copy)) and we modify the last line from the example provided by uv to be a "prod" configuration by not running Fast API in dev mode as well as specifying a port for the application to run on rather than a host of `0.0.0.0`. We can go ahead an add the above file to the root of our project and build the container by running:

```
docker build -t modern-ml-microservices-app .
```

This builds our application image with the tag `modern-ml-microservices-app` which allows us to then reference that tag to run the application like so:

```
docker run -p 80:80 -e ENV=prod modern-ml-microservices-app
```

This command does a few things:

* Binds port 80 on the host machine to port 80 within the container, this allows us to easily access the application on the host's network.
* Sets the `ENV` environment to `prod` to tell our application to run in a production configuration
* Runs the application

With that you should be able to navigate to [http://localhost/docs](http://localhost/docs) and view your running application, now in a docker container!

## Optimize!

With our app containerized you have everything you need to deploy it on your compute platform of choice. However, before we do there are a few more optimizations we could do. Firstly, when we copy our application files to the container we are copying the *entire* project, **including files the application does not need to execute** such as the application README. Such files do nothing but increase the size of our container. We could copy the individual files we need one by one, but Docker provides a `.dockerignore` [file](https://docs.docker.com/build/concepts/context/#dockerignore-files) which works exactly like a .gitignore file and allows excluding files which match a specific pattern from the build context. For example, we could add a `.dockerignore` file with the following contents to the root of our project to exclude unneeded files:

```title=".dockerignore" linenums="1"
__pycache__
.pytest_cache
.venv
.vscode
data
deployment
tests
.env
.gitignore
.git
LICENSE
README.md
```

Finally, when building your project it's best practice to also run all of your tests. Instead of remembering to run both commands I like to create a bash script that automates this process (that we can also use as part of our CI/CD pipeline later 😉). To do that we can create a new folder called `deployment` to hold our deployment scripts, and create an `app-build.sh` script to execute that process:

```bash title="deployment/app-build.sh" linenums="1"
#! /usr/bin/env bash

# This script builds a Docker image for the app.
# Usage: ./app-build.sh

cd $(dirname "$0")/.. || exit 1

# Run tests
pytest --cov

# Build the Docker image for the app
docker build -t modern-ml-microservices-app .
```

You can then execute the script from the root of your project like so:

```
./deployment/app-build.sh 
```

## Reaching a Basecamp

Congratulations! You now have a fully containerized application! In addition, this concludes the first "leg" of our journey into the labyrinth of ML Microservices. Up until this point we have focused on developing the software engineering foundation to build good microservices whether they use ML or not. For the next leg of our journey we will finally introduce ML and start to discuss some of the ways we can apply what we've covered thus far to building ML powered services! As always full code for this part can be found [here](https://github.com/DataDelver/modern-ml-microservices/tree/part-six)!

## Delve Data
* Many challenges exist when deploying Python applications to compute environments other than a local machine
* Docker provides a convenient way to solve many of these challenges
* uv provides a pre-built Docker base image that makes deploying Python applications using uv even easier