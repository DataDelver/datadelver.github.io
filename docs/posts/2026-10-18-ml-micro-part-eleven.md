---
date: 2026-10-18
categories:
  - ML Engineering
tags:
  - Series
  - Tutorial
  - Modern ML Microservices
repo: https://github.com/DataDelver/modern-ml-microservices/tree/part-eleven
social:
  cards_layout_options:
    title: Improving DevX with AI
---

# Delve 24: Let's Build a Modern ML Microservice Application - Part 11, Async

![Banner](../assets/images/banners/delve24.webp)

> "Squint and pretend the async and await keywords are not there. If you do that, you'll realize that the code reads exactly like synchronous code" - Guido van Rossum

Hello data delvers! After a bit of a hiatus I wanted to return to our modern ML microservices series. [Part ten](2026-07-11-ml-micro-part-ten.md) of the series focused on leveraging AI to improve the developer experience. In this part, I'd like to leverage it to improve the application itself!

<!-- more -->

## Async

Up until this point, we have been building our microservices using a *synchronous* programming paradigm. What these means is that when a request comes in to our service, the main thread is fully blocked responding to that request. If any other requests come into the service while the original request is still being processed they have to wait. If they have to wait too long they will get a `503 (Service Unavailable)` response back!

For services that are purely doing all of their compute locally this can be perfectly acceptable. However, if your service calls any other services (or reads from a database, or writes to a disk) there will be a period of time where it is "waiting" for that operation to finish. If you find that the majority of the service execution time is consumed by this waiting, it's the perfect use case for *asynchronous* programming!

Asynchronous (Async) programming in Python allows us to perform another operation (in the case of our services respond to another request) while we are "waiting" for another operation to complete. This allows us to potentially handle many more requests from clients without having to scale up our compute. I highly recommend reading the [FastAPI Async Primer](https://fastapi.tiangolo.com/async/) to get a great intro to this paradigm as a whole.

## The AI Setup

Since this is a more programming heavy task, I decided to use the Qwen family of models to complete it, at the time only Qwen3.6 was available but I have since switched to Qwen3.8, you can find my most up to date setup script below:

```powershell title="Start-Qwen3.8.ps1" linenums="1"
<#
.SYNOPSIS
    Starts a highly optimized llama-server instance for Claude Code using Qwen3.8-27B-GGUF.
.DESCRIPTION
    Allocates an optimized context window on your RTX 4090 (24GB VRAM),
    utilizes Q4 KV caching, and allows fine-tuning the model's thinking/reasoning budget.
#>

# 1. Port Safety Check
$PortToCheck = 11434
$ActivePort = Get-NetTCPConnection -LocalPort $PortToCheck -ErrorAction SilentlyContinue

if ($ActivePort) {
    Write-Warning "⚠️ Port $PortToCheck is already in use by another application (likely native Ollama)."
    Write-Warning "Please close Ollama from your Windows system tray before running this llama-server script."
    Read-Host "Press Enter to exit..."
    exit
}

# 2. Server Parameter Definitions (Qwen3.8-27B)
$RepoID = "unsloth/Qwen3.8-27B-GGUF"
$ModelFile = "Qwen3.8-27B-Q4_K_M.gguf"
$ModelAlias = "qwen3.8-27b"
$ContextSize = 65536
$GPULayers = 99
$HostAddress = "0.0.0.0"

# Thinking/Reasoning Control 
# -1 = Unrestricted thinking (default)
#  0 = Disable thinking completely
#  Positive integer (e.g., 1024, 2048) = Max tokens allowed for reasoning block
$ReasoningBudget = -1                 # -1 = Unrestricted thinking
$TemplateFile = "chat_template.jinja" # Make sure your fixed template file is in this directory

# Set the JSON environment variable for reasoning preservation
$env:LLAMA_ARG_CHAT_TEMPLATE_KWARGS = '{"preserve_thinking": true}'

Write-Host "🚀 Launching Local Qwen3.8-27B Engine (Reasoning Budget: $ReasoningBudget) on RTX 4090..." -ForegroundColor Cyan

# 3. Execution Block
llama-server `
    -hf $RepoID `
    -m $ModelFile `
    --alias $ModelAlias `
    --ctx-size $ContextSize `
    -ngl $GPULayers `
    -fit off `
    -fa on `
    --cache-type-k q8_0 `
    --cache-type-v q8_0 `
    --jinja `
    --chat-template-file $TemplateFile `
    --reasoning-format deepseek `
    --reasoning-budget $ReasoningBudget `
    --temp 1.0 `
    --top-p 0.95 `
    --top-k 20 `
    --spec-type draft-mtp `
    --spec-draft-n-max 3 `
    --host $HostAddress `
    --port $PortToCheck
```

If you want a full breakdown of how to use this script and connect it to Claude Code check out my full setup guide [here](2026-06-22-local-claude-redux.md)!

## Clauding Away!

To start off I prompted Claude to convert the application to async.

!!! claude

    This application is currently fully synchronous, convert it to use the async functionality of FastAPI.

And that was it! It made a few changes for us, let's break them down:

## Async Providers

The main "waiting for something else" that our orchestrator does is calling our ML model. As such we need to make sure that the provider is async to not block the main thread. Fortunately this is a pretty simple conversion. To start, `httpx` already supports an Async http client (this was one of the major benefits compared to `requests`, you don't need a separate library), we just need it in the constructor:

```python title="housing-price-orchestrator/src/provider/mlflow_model_provider.py" linenums="8"
class MLFlowModelProvider:
    """Provider for interacting with MLFlow models.

    Args:
        base_url: The URI of the MLFlow model.
        client: An optional httpx.AsyncClient for making requests. If not provided, a new client will be created.
    """

    def __init__(self, base_url: str, client: Optional[httpx.AsyncClient] = None):
        self.base_url = base_url
        self.client = client or httpx.AsyncClient()
```

So far just a simple swap from `Client` -> `AsyncClient` is all we need to get started. Next lets convert the health check to be async:

```python title="housing-price-orchestrator/src/provider/mlflow_model_provider.py" linenums="20"
async def health(self) -> bool:
    """Checks the health of the MLFlow model provider.

    Returns:
        True if the model provider is healthy, False otherwise.
    """
    try:
        response = await self.client.get(f"{self.base_url}/ping")
        return response.status_code == 200
    except httpx.RequestError:
        return False
```

Is is the combination of the `async` and `await` keywords that enable the magic to happen. Let's break it down.

- `async` - This is how we denote that a function is going to support asynchronous execution
- `await` - This is how we mark the "thing that we are waiting on", this is where the main thread can be freed up to do something else while we wait for this function to return

For the health check we are offloading the call to the model endpoint's `/ping`. We can perform a similar conversion for the predict function as well:

```python title="housing-price-orchestrator/src/provider/mlflow_model_provider.py" linenums="32"
async def predict(self, data: pd.DataFrame) -> MLFlowPredictionsView:
    """Makes a prediction using the MLFlow model.

    Args:
        data: The input data for the prediction.

    Returns:
        A ModelPredictionsView containing the predictions.

    Raises:
        HTTPStatusError: If the prediction request fails.
    """

    payload = {"dataframe_split": json.loads(data.to_json(orient="split"))}

    response = await self.client.post(f"{self.base_url}/invocations", json=payload)
    response.raise_for_status()

    predictions = response.json()
    return MLFlowPredictionsView.model_validate(predictions)
```

Hold on, we are awaiting the `post` call but why not `json.loads` or `MLFlowPredictionsView.model_validate`? The simple answer, they are fast. This is a common issue I've often observed when people first start writing async Python code. They think *every function* must be async and awaited but this is not true! If a function is not I/O bound and it isn't performing complex operations that would eat up a lot of CPU time it should **not be async!** It will actually add overhead making the function async.

As with many things in async programming in Python though, it depends. If for example I was anticipating processing massive data frames with thousands of rows, that could become a heavy CPU task. In that case I should wrap parsing the payload into it's own thread doing something like this:

```python
payload = await run_in_threadpool(
    _build_payload, data
)  # pandas serialization off the loop
```

Where `_build_payload` is:

```python
def _build_payload(data: pd.DataFrame) -> dict:
    return {"dataframe_split": json.loads(data.to_json(orient="split"))}
```

This allows us to run a synchronous, heavy workload, function outside the main event loop to prevent it from blocking. However, don't preemptively optimize, run benchmarks, observe bottlenecks, and only wrap functions if they become bottlenecks.

## Delve Data

- Developer Experience (DevX) is just as important as application functionality and should be considered from the start of a project
- Command runner tools like `just` help standardize and simplify project workflows by aliasing complex commands
- Pre-commit hooks automate code quality checks, ensuring consistent formatting and linting before every commit
- Text-based diagramming tools like Mermaid integrate naturally with AI workflows and version control
- AI-assisted refactoring benefits from clear project documentation and established tooling conventions
- A `CLAUDE.md` file helps enforce project standards and improves AI-assisted development over time
