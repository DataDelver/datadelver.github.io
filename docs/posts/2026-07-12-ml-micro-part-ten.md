---
date: 2026-07-12
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
    - Part Nine: posts/2025-12-07-ml-micro-part-nine.md
social:
  cards_layout_options:
    title: Docker Container Optimization
---

# Delve 23: Let's Build a Modern ML Microservice Application - Part 10, Improving DevX with AI

![Banner](../assets/images/banners/delve23.png)

> "Code is read much more often than it is written." - Guido van Rossum

Greetings data delvers! It has been a while since we last delved into modern ML microservices. In [part nine](2025-12-07-ml-micro-part-nine.md) of this series we looked at optimizing our docker container setup. Since then, AI of course has become a much more prominent tool in the software engineering space. While there has been much commentary about how AI can lead to developer burnout for this delve I want to take a look at how AI can actually improve the developer experience!
<!-- more -->

## DevX

When starting a new project, the Developer Experience (or DevX) is usually not top of mind. The focus is on "ship it" without much thought into how the code will be maintained over time. This leads to many issues that negatively impact the experience of working with the code: poor documentation, cryptic build processes, technical debt, etc. In the era of AI vibe coding, this problem can become even worse with the volume of code being produced. However, just as AI can be a tool to push slop, it can also be very useful in taming the very issues that come from it. Let's dive in and see how.

## The Setup

I'm starting with the [part nine](https://github.com/DataDelver/modern-ml-microservices/tree/part-nine) state of my Modern ML Microservices repo. While I hope this repo is pretty straightforward it has a few drawbacks:

* Lack of clear instructions of how to run the project - You have to remember all of the `uv` and `pytest` commands to fix everything
* No automated linting - While we have ruff available, we need to remember to run it
* Sparse Readme - Pretty self explanatory

This mirrors what I typically find neglected in most projects, since none of these issues are critical path to getting the software functional they are deprioritized. A perfect candidate for improvement with AI.

## Enter... the AI!

For this particular project I decided to use the Gemma4 quants available from [Unsloth](https://huggingface.co/unsloth/gemma-4-12b-it-GGUF), since this isn't a purely coding focused task I wanted a more general purpose model. My full setup script is available below:

```powershell title="Start-Gemma4.ps1" linenums="1"
<#
.SYNOPSIS
    Starts a highly optimized llama-server instance for Claude Code using Gemma 4 Q4_K_M.
.DESCRIPTION
    Allocates a 64K context window completely on your RTX 4090 (24GB VRAM),
    safeguards port 11434 from Ollama collisions, and enforces proper multi-line escaping.
#>

# 1. Port Safety Check (Ensure local Ollama isn't occupying the backend)
$PortToCheck = 11434
$ActivePort = Get-NetTCPConnection -LocalPort $PortToCheck -ErrorAction SilentlyContinue

if ($ActivePort) {
    Write-Warning "⚠️ Port $PortToCheck is already in use by another application (likely native Ollama)."
    Write-Warning "Please close Ollama from your Windows system tray before running this llama-server script."
    Read-Host "Press Enter to exit..."
    exit
}

# 2. Server Parameter Definitions
$RepoID = "unsloth/gemma-4-12b-it-GGUF"
$ModelFile = "gemma-4-12b-it-Q4_K_M.gguf"
$ModelAlias = "gemma4"
$ContextSize = 65536
$GPULayers = 99
$HostAddress = "0.0.0.0"

Write-Host "🚀 Launching Local Gemma 4 Engine (64K Context) on RTX 4090..." -ForegroundColor Cyan

# 3. Execution Block
llama-server `
    -hf $RepoID `
    -m $ModelFile `
    --alias $ModelAlias `
    --ctx-size $ContextSize `
    -ngl $GPULayers `
    -fa on `
    --cache-type-k q8_0 `
    --cache-type-v q4_0 `
    --jinja `
    --temp 1.0 `
    --top-p 0.95 `
    --top-k 64 `
    --spec-type draft-mtp `
    --spec-draft-n-max 2 `
    --host $HostAddress `
    --port $PortToCheck
```

If you want a full breakdown of how to use this script and connect it to Claude Code check out [the previous delve](2026-06-22-local-claude-redux.md)!

!!! Note
    One of the benefits the unsloth quant provided was the ability to enable [Multi Token Prediction (MTP)](https://unsloth.ai/docs/models/mtp) with the `--spec-type draft-mtp` flag. This resulted in a pretty significant speed up in token generation for me.

# Just Do It!

Tackling the first problem of having to remember commands we can introduce [just](https://github.com/casey/just) as a command runner tool. Just is inspired by [make](https://www.gnu.org/software/make/) but designed specifically as a command runner, not a build tool meaning it can avoid some of the [complexities of the original make](https://github.com/casey/just#what-are-the-idiosyncrasies-of-make-that-just-avoids). I find it extremely useful to alias commands in projects so I don't have to remember all the syntax. For example, we can add a `justfile` to the root of our project with the following contents:

```justfile title="justfile" linenums="1"
# Lint code
lint:
    @echo "🔍 Linting code..."
    uv run ruff check .
```

And instead of having to remember the specific command to invoke ruff we can instead execute `just check` in our shell instead, pretty neat!

```bash
just lint
🔍 Linting code...
uv run ruff check .
All checks passed!
```

Now, we could write all of our command aliases by hand, but that would take awhile, instead let's ask AI to do it!

!!! claude
    Create a justfile for this repo with standard command such as installing or updating all packages, building workspace packages, spinning up and tearing down the docker containers, running tests (optionally with coverage or generating an html report), linting, lint fixing, formatting the code and running a format check. Include emoji echo outputs for each command.

You can iterate back and forth with Claude to configure it how you like it but I ended up with something like this:

```justfile title="justfile" linenums="1"
# Default command: List all available commands
default:
    @just --list

# Install all dependencies
install:
    @echo "📦 Installing dependencies..."
    uv sync

# Update all dependencies
update:
    @echo "🔄 Updating dependencies..."
    uv lock --upgrade

# Build workspace packages
build:
    @echo "🏗️ Building workspace packages..."
    uv sync --all-packages

# Spin up Docker containers
up:
    @echo "🚀 Spinning up Docker containers and attaching to logs..."
    docker compose up -d --build --remove-orphans && docker compose logs -f

# Tear down Docker containers
down:
    @echo "🛑 Tearing down Docker containers..."
    docker compose down

# Run tests
test:
    @echo "✅ Running tests..."
    uv run pytest

# Run tests with coverage
test-cov:
    @echo "📊 Running tests with coverage..."
    uv run pytest --cov=housing-price-orchestrator/src

# Run tests and generate HTML coverage report
test-html:
    @echo "🌐 Running tests and generating HTML coverage report..."
    uv run pytest --cov=housing-price-orchestrator/src --cov-report=html

# Lint code
lint:
    @echo "🔍 Linting code..."
    uv run ruff check .

# Lint and fix code
lint-fix:
    @echo "🔧 Linting and fixing code..."
    uv run ruff check . --fix

# Format code
format:
    @echo "✨ Formatting code..."
    uv run ruff format .

# Check formatting
format-check:
    @echo "🧐 Checking formatting..."
    uv run ruff format --check .

# Run tests, linting, and formatting check
check: lint format-check test pre-commit
    @echo "🎉 All checks passed!"

# Clean local build artifacts
clean:
    @echo "🧹 Cleaning local build artifacts..."
    find . -type d -name "__pycache__" -exec rm -rf {} +
    find . -type d -name ".pytest_cache" -exec rm -rf {} +
    find . -type d -name ".ruff_cache" -exec rm -rf {} +

# Clean Docker environment
clean-docker:
    @echo "🐳 Cleaning Docker environment..."
    docker compose down -v --remove-orphans
    docker system prune -f

# Clean everything
clean-all: clean clean-docker
    @echo "🗑️ Removing virtual environment..."
    rm -rf .venv
```

Now when I open a shell in my project and execute `just` I get a nice list of all the commands I have available to me!

```
just
Available recipes:
    build              # Build workspace packages
    check              # Run tests, linting, and formatting check
    clean              # Clean local build artifacts
    clean-all          # Clean everything
    clean-docker       # Clean Docker environment
    default            # Default command: List all available commands
    down               # Tear down Docker containers
    format             # Format code
    format-check       # Check formatting
    install            # Install all dependencies
    lint               # Lint code
    lint-fix           # Lint and fix code
    pre-commit
    pre-commit-install # Pre-commit hooks
    test               # Run tests
    test-cov           # Run tests with coverage
    test-html          # Run tests and generate HTML coverage report
    up                 # Spin up Docker containers
    update             # Update all dependencies
```

## Delve Data
* There are a number of optimizations described in the `uv` documentation for Docker image builds.
* Using multi-stage Docker builds, we can support additional build-time dependencies while ensuring they don't increase the size of the overall image.
