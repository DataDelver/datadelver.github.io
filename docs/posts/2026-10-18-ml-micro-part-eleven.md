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

Finally, wrapping up the provider a bug that existing in the sync version that we should fix:

```python title="housing-price-orchestrator/src/provider/mlflow_model_provider.py" linenums="53"
async def close(self) -> None:
    """Closes the underlying async HTTP client."""
    await self.client.aclose()
```

In order to gracefully handle application shutdown, we should have a way to close the underlying client. We can expose a method on the provider itself to do this.

## Async Service

Our pricing service must now be updated to call our async provider, fortunately it's a pretty easy conversion:

```python title="housing-price-orchestrator/src/service/pricing_service.py" linenums="11"
async def predict_price(
    self, price_prediction_request: PricePredictionRequest
) -> PricePrediction:
    """Predicts the price using the MLFlow model provider.

    Args:
        price_prediction_request: The input data for the prediction.

    Returns:
        A PricePrediction containing the predicted price.
    """

    input_data = price_prediction_request.model_dump(by_alias=True)

    input_df = pd.DataFrame([input_data])
    predictions = await self.pricing_model_provider.predict(input_df)
    predicted_price = predictions.predictions[0] if predictions.predictions else None

    if predicted_price is None:
        raise ValueError("No predictions returned from the model.")
```

The batch endpoint follows a similar conversion.

## Async Main

Our main script needs an async overhaul as well. This one is a bit more involved. Remember how I mentioned it was important to close the http client? We are going to do that here by taking advantage of the [FastAPI Lifespan](https://fastapi.tiangolo.com/advanced/events/#lifespan-events). Instead of initializing our clients, providers, and services globally we can instead create them within a lifespan:

```python title="housing-price-orchestrator/src/main.py" linenums="14"
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create the async HTTP client and inject services onto app.state
    client = httpx.AsyncClient()
    app.state.model_provider = MLFlowModelProvider(
        app_settings.pricing_model_url, client
    )
    app.state.pricing_service = PricingService(app.state.model_provider)
    yield
    # Shutdown: close the async HTTP client
    await client.aclose()
```

Let's break this down, the lifespan is an async context manager, FastAPI will invoke this function **once at application startup** and will execute everything **up until** the `yield` keyword. Afterwards the application will start receiving requests. Upon shutdown, once the application stops receiving requests everything **after** yield is executed. In practice this means we set everything up before `yield` and tear it down after, which is the pattern we see above.

In addition, we'd like to access the `PricingService` in other parts of our application, in oder to do this we can store it on a special object called `app.state` which is global and re-used between invocations.

In order to retrieve the pricing service from the app state we can create a helper function:

```python title="housing-price-orchestrator/src/main.py" linenums="28"
def get_pricing_service(request: Request) -> PricingService:
    """Dependency that provides the PricingService from the application state."""
    return request.app.state.pricing_service
```

Finally, we use the [Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/) pattern available in FastAPI to allow us to access the service in the context of an individual request:

```python title="housing-price-orchestrator/src/main.py" linenums="33"
@app.post("/api/v1/price/predict")
async def predict(
    price_prediction_request: PricePredictionRequest,
    pricing_service: PricingService = Depends(get_pricing_service),
) -> PricePredictionResponseView:
    """Endpoint to predict the price of a housing unit.

    Args:
        price_prediction_request: The request containing the input data for the prediction.
        pricing_service: The injected PricingService instance.

    Returns:
        A PricePredictionResponseView containing the predicted price.
    """

    try:
        price_prediction = await pricing_service.predict_price(price_prediction_request)
        return PricePredictionResponseView(
            id=price_prediction.id, predicted_price=price_prediction.predicted_price
        )
    except ValueError:
        raise HTTPException(status_code=404, detail="No results found.")
```

## Async Tests

All that's left now is to update our tests, in general, not much changes other than marking tests with `@pytest.mark.asyncio`. However, now that we are using the dependency injection we can easily mock out the pricing service for a unit test. First we create a mock:

```python title="housing-price-orchestrator/tests/unit/test_main.py" linenums="9"
@pytest.fixture
def mock_pricing_service() -> MagicMock:
    """Mock the PricingService class with async methods."""
    mock = MagicMock(spec=PricingService)
    mock.predict_price = AsyncMock(
        return_value=MagicMock(id=1, predicted_price=123456.78)
    )
    mock.predict_price_batch = AsyncMock(
        return_value=[
            MagicMock(id=1, predicted_price=123456.78),
            MagicMock(id=2, predicted_price=234567.89),
        ]
    )
    return mock
```

Then we use it in the test via `app.dependency_overrides`:

```python title="housing-price-orchestrator/tests/unit/test_main.py" linenums="226"
@pytest.mark.asyncio
async def test_predict_price_success(
    mock_pricing_service: MagicMock, payload_single: dict
) -> None:
    """Test the /api/v1/price/predict endpoint for a successful prediction."""
    # GIVEN
    app.dependency_overrides[get_pricing_service] = lambda: mock_pricing_service
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://test"
    ) as client:
        # WHEN
        response = await client.post("/api/v1/price/predict", json=payload_single)

        # THEN
        assert response.status_code == 200
        assert response.json() == {"id": 1, "predictedPrice": 123456.78}
        mock_pricing_service.predict_price.assert_awaited_once()

    app.dependency_overrides.clear()
```

All of the other tests that require async follow a similar conversion.

## Was it worth it?

Finally, whenever doing any kind of optimization it's always worth it to run a benchmark to see if it's worth it. Fortunately, this is something our LLM can whip up pretty quick for us:

!!! claude

    I'd like to compare the performance of the app pre and post async conversion, can you create a benmark script and execute it against both versions of the codebase and report back performance metrics?

This created a benchmark suite where we mock out the MLFlow server with a simulated delay of 50ms for model inference time (to isolate any performance differences to the refactor itself), then checkout both the pre and post refactor commits and run the following scenarios against them:

| Scenario   | Description                                                  |
| ---------- | :----------------------------------------------------------- |
| sequential | 50 single predictions, 1 at a time (raw latency)             |
| concurrent | 300 single predictions at concurrency 10 / 50 / 100          |
| batch      | 150 batch predictions (batch size 20) at concurrency 10 / 50 |

Here are the results:

**Throughput (RPS — higher is better)**

| Scenario       |  sync | async |      Δ |
| -------------- | ----: | ----: | -----: |
| sequential     |  18.4 |  18.5 |  +0.5% |
| concurrent-10  | 175.9 | 173.6 |  −1.3% |
| concurrent-50  | 394.9 | 470.5 | +19.1% |
| concurrent-100 | 282.4 | 425.4 | +50.6% |
| batch-10       | 128.8 | 157.9 | +22.6% |
| batch-50       | 210.3 | 298.5 | +41.9% |

**Latency (ms — lower is better, Δ = % reduction)**

| Scenario       | p95 sync | p95 async |  p95 Δ | p99 sync | p99 async |  p99 Δ |
| -------------- | -------: | --------: | -----: | -------: | --------: | -----: |
| sequential     |     54.9 |      54.6 |  +0.5% |     55.4 |      54.7 |  +1.3% |
| concurrent-10  |     63.1 |      63.7 |  −1.0% |     73.1 |      74.6 |  −2.0% |
| concurrent-50  |    164.0 |     126.3 | +23.0% |    176.4 |     144.9 | +17.9% |
| concurrent-100 |    459.0 |     412.1 | +10.2% |    469.9 |     435.2 |  +7.4% |
| batch-10       |     93.5 |      76.6 | +18.1% |     99.7 |      80.0 | +19.8% |
| batch-50       |    364.9 |     239.3 | +34.4% |    392.2 |     243.8 | +37.8% |

A few takeaways:

- *Low concurrency is a wash.* There's a negligible difference in performance with 10 concurrent requests.
- *Async has a clear advantage a high concurrency.* At 100 concurrent requests we have a massive 50% increase in requests per second through the service. Interestingly, we see the difference in latency is less dramatic than at 50 concurrent requests, but this is most likely due to the bottleneck moving off of the service and to the benchmark client itself struggling to serialize and deserialize all of the requests, as well as the single threaded mock server for the model.
- *Batch requests benefit from async the most.* Since it takes longer to process a batch request, this leads to the exact "waiting" blocked thread scenario async is meant to avoid in the synchronous implementation.

As we can see, as with most optimizations, the answer to whether it is worth doing or not is "It depends". However, in cases that are suited to async, the performance gains can be dramatic!

Go forth and async!

## Delve Data

- Async programming shines when a service's execution time is dominated by waiting on I/O, not by local computation
- Only mark a function `async` if it is actually I/O bound — making fast or CPU-bound functions async adds overhead without any benefit
- `httpx.AsyncClient` is a major win over `requests` since async HTTP support is built in rather than requiring a separate library
- FastAPI's lifespan events are the ideal place to create and cleanly tear down shared resources like HTTP clients
- FastAPI's dependency injection pattern makes services trivial to mock, keeping unit tests fast and isolated from real providers
- Heavy synchronous work like serializing large DataFrames can be offloaded with `run_in_threadpool` to avoid blocking the event loop — but only once benchmarks prove it's a bottleneck
- Always benchmark before and after an optimization like an async refactor to confirm the gains are real and where they occur
