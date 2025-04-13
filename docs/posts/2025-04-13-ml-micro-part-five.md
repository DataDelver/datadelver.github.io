---
date: 2025-04-13
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
---

# Delve 11: Let's Build a Modern ML Microservice Application - Part 5, Testing

![Banner](../assets/images/banners/delve11.png)

> "More than the act of testing, the act of designing tests is one of the best bug preventers known." - Boris Beizer

## ML Microservices, Keep Calm and Run Your Tests

Hello data delvers! In [part four](2025-03-125-ml-micro-part-four.md) of this series we refactored our application to include a configuration file to make it easy to switch configuration values per development environment. In this part we'll cover a critical element to building scalable systems: Testing.  
<!-- more -->

As the complexity of the application grows, so too does the difficulty in verifying that it is behaving as expected. Right now, it is fairly straightforward to test our application. We can bring up the swagger docs, and try a few sample requests to make sure everything is working. However, we can imagine as we add more and more functionality to our app, it will become more tedious to do this type of *manual* testing every time we make a change to verify nothing has broken. Once more, if something does break, this testing may make it difficult to determine where in our application the break actually occurred (unless we have very, very helpful error messages). A better approach would be to have a set of *automated* tests that run whenever we make a change to verify nothing has broken. It is this type of testing that I would like to focus on for the subject of this delve.

!!! info
    There are [many types of software testing](https://www.geeksforgeeks.org/types-software-testing/). For this delve we will be focusing on small subset of testing strategies. Other forms of testing may be covered in future delves.

## Let's Get Testy

To begin let's talk about how we might go about writing tests for our application. We could start at the highest level, trying to test the whole application in one go, sending it requests and validating responses. This solves the first problem of having to not run our tests manually anymore, but doesn't solve the second of trying to isolate where the breakage occurred. A different strategy would be to break the application into the smallest pieces possible and test each piece independently of the others and then once the pieces are verified to be working in isolation, test how they work together. In this way, if something breaks we should be able to tell were the breakage occurred because the test for the broken piece should fail. In this type of testing approach we call these pieces of the application *Units* and this testing strategy [Unit Testing](https://en.wikipedia.org/wiki/Unit_testing).

The next question you may be asking is "Where to begin writing your unit tests?". This is more personal preference but I like to start at the lowest layers of my application and work my way up. For us that means starting at the *Data Layer*, though it can be valid to start in the reverse order as well.

!!! note
    Another valid question to ask is "When should I write my tests?". In this series we are following what I'd call the "conventional" or "typical" route of testing in which we already have working code and we are writing tests to ensure that is it behaving as expected. However, there is an alternative software development philosophy known as [Test Driven Development](https://en.wikipedia.org/wiki/Test-driven_development) that advocates for the opposite flow: That of writing the tests for a new piece of functionality first, then writing the code that passes the test. Test Driven Development has a lot of advantages, namely forcing the discussion around the desired functionality before any code to implement that functionality has been written. It is worth exploring this approach more and seeing if it aligns better with your own development style than the typical route. It's also worth mentioning that these two approaches are not mutually exclusive and can be mixed and matched as needed.

So if we follow this bottom up approach to testing we should begin at the *Data Layer* of our application with the `MetProvider` class. In order to do this we will need to install a few more dependencies. Namely [pytest](https://docs.pytest.org/en/stable/), [pytest-mock](https://pytest-mock.readthedocs.io/en/latest/index.html), and [pytest-httpx](https://github.com/Colin-b/pytest_httpx).

pytest is the most popular Python unit testing framework, the other two packages are extensions that will make it a bit easier to work with our codebase.

!!! tip
    When installing these dependencies notice that we only need them for running our tests or more generally *development* activities. We don't need them for actually executing the functionality of our application itself. In this case we can take advantage of a feature of `uv` know as [development dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/#development-dependencies) to mark these libraries as development only dependencies. This is done by adding the `--dev` flag when installing them. For example `uv add --dev pytest`. It is recommended to install these dependencies in this way.

With our development dependencies installed we then need to add a bit of configuration to our `pyproject.toml` file to tell pytest where our tests will be located.

```toml title="pyproject.toml" linenums="1" hl_lines="22-30"
[project]
name = "modern-ml-microservices"
version = "0.1.0"
description = "Example repository of how to build a modern microservice architecture to support machine learning applications."
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "fastapi[standard]>=0.115.6",
    "httpx>=0.28.1",
    "pydantic-settings>=2.7.1",
]

[tool.ruff]
line-length = 120

[tool.ruff.format]
quote-style = "single"

[tool.ruff.lint.pydocstyle]
convention = "google"

[tool.pytest.ini_options]
minversion = "6.0"
pythonpath = "src"
testpaths = [
    "tests",
]
python_files = [
    "test_*.py",
]

[dependency-groups]
dev = [
    "pytest>=8.3.5",
    "pytest-mock>=3.14.0",
    "pytest-httpx>=0.35.0",
]
```

Here we are telling pytest that our source code is located in a file called `src` that will need to be added to the python path when executing tests (this makes sure our imports will work). We are also specifying that all our tests will we located in a folder called `tests` and that the test scripts themselves will start with the prefix `test_`. We are also specifying a minimum version of pytest to use of 6.0 (the earliest version that supported using the pyproject.toml to specify these settings). With all the setup out of the way, let's start writing tests!

## Mocking and Rolling: The Art of Unit Testing

To start, let's review the code of the provider class:

```python title="src/provider/met_provider.py" linenums="1"
from datetime import datetime
from typing import Optional
import httpx


from shared.view.met_view import DepartmentResponse, ObjectResponse, ObjectsResponse, SearchResponse


class MetProvider:
    """A client for the Metropolitan Museum of Art API.

    Args:
        base_url: The base URL of the API.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_objects(
        self, metadata_date: Optional[datetime] = None, department_ids: Optional[list[int]] = None
    ) -> ObjectsResponse:
        """Retrieves objects from the Metropolitan Museum of Art API.

        Args:
            metadata_date: Returns any objects with updated data after this date.
            department_ids: Returns any objects in a specific department.

        Returns:
            A list of objects.
        """

        query_params = {}

        if metadata_date:
            query_params['metadataDate'] = metadata_date.strftime('%Y-%m-%d')
        if department_ids:
            query_params['departmentIds'] = '|'.join(map(str, department_ids))

        r = httpx.get(
            f'{self.base_url}/public/collection/v1/objects',
            params=query_params,
        )

        return ObjectsResponse.model_validate(r.json())

    def get_object(self, object_id: int) -> ObjectResponse:
        """Retrieves an object from the Metropolitan Museum of Art API.

        Args:
            object_id: The ID of the object to retrieve.

        Returns:
            The object.
        """

        r = httpx.get(f'{self.base_url}/public/collection/v1/objects/{object_id}')
        return ObjectResponse.model_validate(r.json())

    def get_departments(self) -> DepartmentResponse:
        """Retrieves departments from the Metropolitan Museum of Art API.

        Returns:
            A list of departments.
        """

        r = httpx.get(f'{self.base_url}/public/collection/v1/departments')
        return DepartmentResponse.model_validate(r.json())

    def search(self, q: str, title: Optional[bool] = None, has_images: Optional[bool] = None) -> SearchResponse:
        """Executes a search against the Metropolitan Museum of Art API.

        Args:
            q: The query string.
            title: Whether to search the title field.
            has_images: Whether to search for objects with images.

        Returns:
            The search results.
        """

        query_params = {'q': q}

        if title is not None:
            query_params['title'] = str(title).lower()

        if has_images is not None:
            query_params['hasImages'] = str(has_images).lower()

        r = httpx.get(
            f'{self.base_url}/public/collection/v1/search',
            params=query_params,
        )

        return SearchResponse.model_validate(r.json())
```

We have four methods to test:

* `get_objects()`
* `get_object()`
* `get_departments()`
* `search()`

Each should get a corresponding unit test.  We can go ahead a create a file to hold our tests located at `tests/unit/provider/test_met_provider.py`. Take note of the directory structure. We locate the tests in the `tests` folder as we configured in the `pyproject.toml`, then under a folder called `unit` (since this is a unit test), then finally we mirror the directory structure of the `src` folder so that the corresponding test will be located in a folder hierarchy structure identical as the script it is testing. This is not required but I find it makes it easier to understand were to look in the source code if a test fails.

!!! note
    Unlike the `src` folder where every directory needed an empty `__init__.py` file within it to mark it as a Python module, there is no need to do this for `tests` directories.

Let's write a test!

```python title="tests/unit/provider/test_met_provider.py" linenums="1"
from provider.met_provider import MetProvider

def test_get_objects() -> None:
    """Test the get_objects method of the MetProvider class."""

    # GIVEN
    provider = MetProvider('https://collectionapi.metmuseum.org')

    # WHEN
    response = provider.get_objects()

    # THEN
    assert response.total == 495439
```

When writing tests I like to follow a structure made popular by the [Behavior Driven Development](https://dannorth.net/introducing-bdd/) testing philosophy. Each test case has three sections:

* **Given** - Initial set of conditions
* **When** - The test action occurs
* **Then** - Validate that the desired behavior has happened

In this way you can write a test case as a simple sentence. For example the above test could be written as "Given a Met Provider connected to the Met API, when I call the get objects method, then I should get 495,439 results back." Now, in writing the test case in this way you might already see the problem with this test. As of right now, when I call this route on the Met API I get 495,439 results, but what happens if the Met adds another work to their collection? I would then get 495,440 results back and this test would *fail* even though nothing is wrong with the code. This demonstrates an important principle of unit testing, that tests should be written in such a way that they test the unit in *isolation* and should not be dependent on the state of any external system to the unit in order for the test to succeed. So how can we address this?

!!! note
    This quality of independence from external systems is not always prohibited and is even desired for types of testing other than unit testing.

Well, what if instead of calling the real Met API we could have a dummy API instead, and even better, we could control the output of this dummy API to make it deterministic so we could write test cases against it? In that way we could ensure that the Met API for this use case will *always* return the same number of results, which means if the test fails there is something wrong with the logic of the provider itself, which is exactly what we want to test! As you may guess, this is entirely possible, this process of creating dummy objects for the purposes of testing is called *mocking* and we can use the pytest extensions we previously installed to create our mock Met API. To do this we use `httpx-mock`. We can create a Mocked provider to use in our tests like so:

```python title="tests/unit/provider/test_met_provider.py" linenums="1"
from provider.met_provider import MetProvider

def test_get_objects(httpx_mock) -> None:
    """Test the get_objects method of the MetProvider class."""

    # GIVEN
    dummy_url = 'https://collectionapi-dummy.metmuseum.org'
    # Mock the response for the get_objects method
    httpx_mock.add_response(
        url=f'{dummy_url}/public/collection/v1/objects',
        json={
            'total': 1,
            'objectIDs': [1],
        }
    )
    provider = MetProvider(dummy_url)

    # WHEN
    response = provider.get_objects()

    # THEN
    assert response.total == 1
    assert response.object_ids == [1]
```

Here we take advantage of the special `httpx_mock` *fixture* to create a dummy response whenever a request is made to the url `https://collectionapi-dummy.metmuseum.org/public/collection/v1/objects`. We then use this dummy response to make assertions in our tests. Now we don't have to worry about the Met API changing their collection size and breaking our tests!

We can go ahead and run this test by simply executing the `pytest` command in the root of the project or by using the [testing panel](https://code.visualstudio.com/docs/debugtest/testing) of VSCode.

Now we could go ahead an repeat this logic for every test we want to write but it will become tedious to mock out the provider every time. Another way we could do this is create the mocked provider in a test *fixture* and re-use it in all of our tests. That would look something like this:

```python title="tests/unit/provider/test_met_provider.py" linenums="1"
from provider.met_provider import MetProvider

@pytest.fixture
def provider_with_mock_api(httpx_mock) -> MetProvider:
    """Mock responses for the Metropolitan Museum of Art API."""

    dummy_url = 'https://collectionapi-dummy.metmuseum.org'

    # Mock the response for the get_objects method
    httpx_mock.add_response(
        url=f'{dummy_url}/public/collection/v1/objects',
        json={
            'total': 1,
            'objectIDs': [1],
        },
        is_optional=True,
    )

    return MetProvider(dummy_url)

def test_get_objects(provider_with_mock_api: MetProvider) -> None:
    """Test the get_objects method of the MetProvider class."""

    # GIVEN
    provider = provider_with_mock_api

    # WHEN
    response = provider.get_objects()

    # THEN
    assert response.total == 1
    assert response.object_ids == [1]
```

Now every test that needs the provider mocked out can simply take in the `provider_with_mock_api` argument. With this pattern in hand we can go ahead and write the rest of our test cases:

```python title="tests/unit/provider/test_met_provider.py" linenums="1"
from provider.met_provider import MetProvider

@pytest.fixture
def provider_with_mock_api(httpx_mock) -> MetProvider:
    """Mock responses for the Metropolitan Museum of Art API."""

    dummy_url = 'https://collectionapi-dummy.metmuseum.org'

    # Mock the response for the get_objects method
    httpx_mock.add_response(
        url=f'{dummy_url}/public/collection/v1/objects',
        json={
            'total': 1,
            'objectIDs': [1],
        },
        is_optional=True,
    )

    # Mock the response for the get_object method
    httpx_mock.add_response(
        url=f'{dummy_url}/public/collection/v1/objects/1',
        json={
            'objectID': 1,
            'title': 'Test Object',
            'primaryImage': 'https://example.com/image.jpg',
            'additionalImages': [
                'https://example.com/image1.jpg',
                'https://example.com/image2.jpg',
            ],
        },
        is_optional=True,
    )

    # Mock the response for the get_departments method
    httpx_mock.add_response(
        url=f'{dummy_url}/public/collection/v1/departments',
        json={
            'departments': [
                {
                    'departmentId': 1,
                    'displayName': 'Test Department',
                },
            ],
        },
        is_optional=True,
    )

    # Mock the response for the search method
    httpx_mock.add_response(
        url=f'{dummy_url}/public/collection/v1/search?q=Test Title',
        json={
            'total': 1,
            'objectIDs': [1],
        },
        is_optional=True,
    )

    return MetProvider(dummy_url)

def test_get_objects(provider_with_mock_api: MetProvider) -> None:
    """Test the get_objects method of the MetProvider class."""

    # GIVEN
    provider = provider_with_mock_api

    # WHEN
    response = provider.get_objects()

    # THEN
    assert response.total == 1
    assert response.object_ids == [1]

def test_get_object(provider_with_mock_api: MetProvider) -> None:
    """Test the get_object method of the MetProvider class."""

    # GIVEN
    provider = provider_with_mock_api

    # WHEN
    response = provider.get_object(1)

    # THEN
    assert response.object_id == 1
    assert response.title == 'Test Object'

def test_get_departments(provider_with_mock_api: MetProvider) -> None:
    """Test the get_departments method of the MetProvider class."""

    # GIVEN
    provider = provider_with_mock_api

    # WHEN
    response = provider.get_departments()

    # THEN
    assert len(response.departments) == 1
    assert response.departments[0].department_id == 1

def test_search(provider_with_mock_api: MetProvider) -> None:
    """Test the search method of the MetProvider class."""

    # GIVEN
    provider = provider_with_mock_api

    # WHEN
    response = provider.search('Test Title')

    # THEN
    assert response.total == 1
    assert response.object_ids == [1]
```

Note that we set `is_optional` to `True` for our mocked responses in the fixture, this is because not every mock response will be used for every test.

!!! tip
    I find code generation tools like [GitHub Copilot](https://github.com/features/copilot) particularly good at generating test cases. I encourage you to try them out, they have saved me a lot of time!

With our provider methods all tested we can move on to the *Business Logic Layer* and test our `SearchService` class.

## Mock all the Things!
Our search service just has one method to test `search_by_title`. As a reminder, this is what the source code looks like:

```python title="src/service/search_service.py" linenums="1"
from provider.met_provider import MetProvider
from shared.dto.search_result import SearchResult


class SearchService:
    """A service for searching the Metropolitan Museum of Art API.

    Args:
        met_provider: A client for the Metropolitan Museum of Art API.
    """

    def __init__(self, met_provider: MetProvider):
        self.met_provider = met_provider

    def search_by_title(self, title: str) -> SearchResult:
        """Searches the Metropolitan Museum of Art API by title.

        Args:
            title: The title of the work to search for.

        Returns:
            The search results.

        Raises:
            ValueError: If no results are found.
        """

        # Search for a work in the Met collection by title
        search_response = self.met_provider.search(q=title)
        object_ids = search_response.object_ids

        # If the work exists
        if object_ids:
            # Fetch the details of the work
            object_request = self.met_provider.get_object(object_id=object_ids[0])

            return SearchResult(
                object_id=object_request.object_id,
                title=object_request.title,
                primary_image=object_request.primary_image,
                additional_images=object_request.additional_images,
                total_results=search_response.total,
            )
        else:
            raise ValueError('No results found.')
```

For our `SearchService` test we can go ahead and create a new file located at `tests/unit/service/test_search_service.py` to hold our tests. Now, we could re-use our same `provider_with_mock_api` fixture here as well. That would look something like this:

```python title="tests/unit/service/test_search_service.py" linenums="1"
from provider.met_provider import MetProvider
from service.search_service import SearchService

# Copy-Pasted provider_with_mock_api

def test_search_by_title(provider_with_mock_api: MetProvider) -> None:
    """Test the search_by_title method of the SearchService class."""

    # GIVEN
    service = SearchService(provider_with_mock_api)
    title = 'Test Title'

    # WHEN
    result = service.search_by_title(title)

    # THEN
    assert result.object_id == 1
    assert result.title == 'Test Object'
    assert result.primary_image == 'https://example.com/image.jpg'
    assert result.additional_images == ['https://example.com/image1.jpg', 'https://example.com/image2.jpg']
    assert result.total_results == 1
```

However, we now created a similar problem as we had before. What if we have a bug in the `MetProvider` class? Now this test could fail even if there is nothing wrong with the `SearchService`! We can solve this dilemma in a similar manner as before, by creating a mock! Though this time since we are not mocking http requests and responses but a class instead we can use the `pytest-mock` extension. That looks something like this:

```python title="tests/unit/service/test_search_service.py" linenums="1"
from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture

from provider.met_provider import MetProvider
from service.search_service import SearchService
from shared.view.met_view import DepartmentResponse, ObjectResponse, ObjectsResponse, SearchResponse


@pytest.fixture
def mock_provider(mocker: MockerFixture) -> MagicMock:
    mock = mocker.MagicMock(MetProvider)
    mock.get_objects.return_value = ObjectsResponse.model_validate(
        {
            'total': 1,
            'objectIDs': [1],
        }
    )
    mock.get_object.return_value = ObjectResponse.model_validate(
        {
            'objectID': 1,
            'title': 'Test Object',
            'primaryImage': 'https://example.com/image.jpg',
            'additionalImages': ['https://example.com/image1.jpg', 'https://example.com/image2.jpg'],
        }
    )
    mock.get_departments.return_value = DepartmentResponse.model_validate(
        {
            'departments': [
                {
                    'departmentId': 1,
                    'displayName': 'Test Department',
                },
            ],
        }
    )
    mock.search.return_value = SearchResponse.model_validate(
        {
            'total': 1,
            'objectIDs': [1],
        }
    )
    return mock 
```

We create this mock as a *fixture* as we did before so we can re-use it in multiple tests. We also take advantage of the `MagicMock` functionality of pytest-mock to easily create a dummy version of the `MetProvider` and stub out mock responses for each of its methods. We can then use this mock in our test like so:

```python title="tests/unit/service/test_search_service.py" linenums="45"
def test_search_by_title(mock_provider: MagicMock) -> None:
    """Test the search_by_title method of the SearchService class."""

    # GIVEN
    service = SearchService(mock_provider)
    title = 'Test Title'

    # WHEN
    result = service.search_by_title(title)

    # THEN
    assert result.object_id == 1
    assert result.title == 'Test Object'
    assert result.primary_image == 'https://example.com/image.jpg'
    assert result.additional_images == ['https://example.com/image1.jpg', 'https://example.com/image2.jpg']
    assert result.total_results == 1
    mock_provider.search.assert_called_once_with(q=title)
```

One other benefit of this type of mock is we can also make assertions if methods on the mock were called and what arguments were passed into them as we are doing with the `assert_called_once_with` method. Neat!

This test covers the case where we have results to return but noticed that the `SearchService` should raise as `ValueError` in the case that no results are found. How can we test this behavior as well?

!!! note
    You will sometimes hear the terms "Happy Path" and "Sad Path" used in the context of these types of tests.  In this example the happy path is the case where things go "right" and we have results to return and the sad path is where things go "wrong" and we raise an exception. Ideally you should cover both happy and sad paths in your test cases with each path being it's own test case.

It turns out pytest has a `raises` function that can be used in a context manager to implement this exact type of test:

```python title="tests/unit/service/test_search_service.py" linenums="63"
def test_search_by_title_no_results(mock_provider: MagicMock) -> None:
    """Test the search_by_title method of the SearchService class when no results are found."""

    # GIVEN
    service = SearchService(mock_provider)
    title = 'Nonexistent Title'
    mock_provider.search.return_value = SearchResponse.model_validate(
        {
            'total': 0,
            'objectIDs': [],
        }
    )

    # WHEN / THEN
    with pytest.raises(ValueError, match='No results found.'):
        service.search_by_title(title)
    mock_provider.search.assert_called_once_with(q=title)
```

A few things to note here is we have to override the return value of the search function of our mock to simulate no results. We can also verify we get back the expected error message by passing it into the `match` argument of the `raises` function. Finally given the structure of the code I often combine the *When* and *Then* sections of the test into one.

That wraps up the tests of our business logic layer! We only have one more layer to go: The *Interface Layer*.

## Bringing Unit Tests to the Interface

By this point you should know the drill, we don't want to use the `SearchService` directly in our tests, instead we want to create a mock instead. We can take a look at the code of our main script:

```python title="src/main.py" linenums="1"
import os
from fastapi import FastAPI, HTTPException

from provider.met_provider import MetProvider
from service.search_service import SearchService
from shared.config.config_loader import load_config_settings

app = FastAPI()
app_settings = load_config_settings(os.getenv('ENV', 'dev'))
search_service = SearchService(MetProvider(app_settings.met_api_url))


@app.get('/api/search')
def search(title: str) -> str:
    """Executes a search against the Metropolitan Museum of Art API and returns the url of the primary image of the first search result.

    Args:
        title: The title of the work you wish to search for.

    Returns:
        The url of the primary image of the first search result or 'No results found.' if no search results are found.
    """

    try:
        search_result = search_service.search_by_title(title)
        return search_result.primary_image
    except ValueError:
        raise HTTPException(status_code=404, detail='No results found.')
```

Looks pretty simple. We have both a happy path of returning the primary image url and a sad path where we return a 404 status code. We'll want to test both. FastAPI fortunately provides a convenient [Test Client](https://fastapi.tiangolo.com/reference/testclient/) we can use to invoke the functions in our main script without needing to rig up making HTTP requests ourselves. Putting this together we can create a simple test script as follows:

```python title="tests/test_main.py" linenums="1"
from main import app
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
import pytest
from pytest_mock import MockerFixture

from service.search_service import SearchService


@pytest.fixture
def mock_search_service(mocker: MockerFixture) -> MagicMock:
    """Mock the SearchService class."""

    mock = MagicMock(SearchService)
    mock.search_by_title.return_value.primary_image = 'https://example.com/image.jpg'
    return mock


def test_search(mock_search_service: MagicMock, mocker: MockerFixture) -> None:
    """Test the search endpoint."""

    # GIVEN
    client = TestClient(app)
    mocker.patch('main.search_service', mock_search_service)
    title = 'Test Title'

    # WHEN
    response = client.get(f'/api/search?title={title}')

    # THEN
    assert response.status_code == 200
    assert response.json() == 'https://example.com/image.jpg'
    mock_search_service.search_by_title.assert_called_once_with(title)


def test_search_no_results(mock_search_service: MagicMock, mocker: MockerFixture) -> None:
    """Test the search endpoint when no results are found."""

    # GIVEN
    client = TestClient(app)
    mocker.patch('main.search_service', mock_search_service)
    mock_search_service.search_by_title.side_effect = ValueError('No results found.')
    title = 'Test Title'

    # WHEN
    response = client.get(f'/api/search?title={title}')

    # THEN
    assert response.status_code == 404
    assert response.json() == {'detail': 'No results found.'}
```

Notice how we can use the `TestClient` to make requests against our API and make assertions on the responses. We also use `mocker.patch` to replace the search service of the app after it has been created. Finally in the case where we want the search to raise an exception we can use the `side_effect` attribute of the mock. With that we have a decent suite of unit tests for our code! But how can we know how much of the code we are testing?

## No Code Left Behind: Test Coverage

The question above relates to the concept of [Code Coverage](https://en.wikipedia.org/wiki/Code_coverage). There are many different ways to compute code coverage but perhaps one of the simplest is measuring the percentage of lines of code executed as a result of running all of your tests. Fortunately, the [pytest-cov](https://pytest-cov.readthedocs.io/en/latest/readme.html) extension does exactly that. Go ahead an install it as a development dependency of the project.

We can then add another section to our `pyproject.toml` to configure it like so:

```toml title="pyproject.toml" linenums="33"
[tool.coverage.run]
omit = [
    "tests",
]
source = [
    "src",
]

[tool.coverage.report]
fail_under = 60 
show_missing = true
skip_empty = true
```

You can read more about these config options [here](https://coverage.readthedocs.io/en/latest/config.html). An important one to call out is the `fail_under` setting. This represents a coverage threshold under which the test suite will be marked as a failure. This can be useful to make sure un-tested code doesn't accidentally get released! I generally like to set this to 60% with a goal of getting to at least 80%. Let's go ahead and run our tests and see were we are now:

```
$pytest --cov
==================================================================================== test session starts =====================================================================================
platform linux -- Python 3.13.1, pytest-8.3.5, pluggy-1.5.0
rootdir: /home/datadelver/Documents/PythonProjects/DataDelver/modern-ml-microservices
configfile: pyproject.toml
testpaths: tests
plugins: httpx-0.35.0, anyio-4.7.0, mock-3.14.0, cov-6.0.0
collected 9 items                                                                                                                                                                           
                                                                                                                                                 [ 20%]
tests/unit/provider/test_met_provider.py ....                                                                                                                                          [ 60%]
tests/unit/service/test_search_service.py ..                                                                                                                                           [ 80%]
tests/unit/test_main.py ..                                                                                                                                                             [100%]

---------- coverage: platform linux, python 3.13.1-final-0 -----------
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
src/main.py                             15      0   100%
src/provider/met_provider.py            29      4    86%   35, 37, 84, 87
src/service/search_service.py           12      0   100%
src/shared/config/config_loader.py      20      0   100%
src/shared/data_model_base.py            6      0   100%
src/shared/dto/search_result.py          7      0   100%
src/shared/view/met_view.py             19      0   100%
------------------------------------------------------------------
TOTAL                                  108      4    96%

6 empty files skipped.

Required test coverage of 60.0% reached. Total coverage: 96.30%
```

!!! tip
    You can also use the [Run with Test Coverage](https://code.visualstudio.com/docs/debugtest/testing#_test-coverage) option in the VSCode testing panel to get a nice visual display of coverage!

We are doing pretty good, but it looks like we are missing a few lines in the met provider. Taking a look we can see those lines are related to optional parameters that can get passed in. Let's add some tests to our `test_met_provider.py` script to fix this.

```python title="tests/unit/provider/test_met_provider.py" linenums="112"
def test_get_objects_with_metadata_date_and_department_ids(provider_with_mock_api: MetProvider, httpx_mock) -> None:
    """Test the get_objects method of the MetProvider class with metadata date."""

    # GIVEN
    provider = provider_with_mock_api
    metadata_date = datetime(day=1, month=1, year=2023)
    department_ids = [1]
    # Mock the response for the get_objects method with metadata date
    httpx_mock.add_response(
        url=f'{provider.base_url}/public/collection/v1/objects?metadataDate=2023-01-01&departmentIds=1',
        json={
            'total': 1,
            'objectIDs': [1],
        },
    )

    # WHEN
    response = provider.get_objects(metadata_date=metadata_date, department_ids=department_ids)

    # THEN
    assert response.total == 1
    assert response.object_ids == [1]

def test_search_with_title_and_has_images(provider_with_mock_api: MetProvider, httpx_mock) -> None:
    """Test the search method of the MetProvider class with title and has_images."""

    # GIVEN
    provider = provider_with_mock_api

    # Mock the response for the search method with title and has_images
    httpx_mock.add_response(
        url=f'{provider.base_url}/public/collection/v1/search?q=Test+Title&title=true&hasImages=true',
        json={
            'total': 1,
            'objectIDs': [1],
        },
    )

    # WHEN
    response = provider.search(q='Test Title', title=True, has_images=True)

    # THEN
    assert response.total == 1
    assert response.object_ids == [1]
```

Let's re-run our tests and see what we get:

```
$pytest --cov
==================================================================================== test session starts =====================================================================================
platform linux -- Python 3.13.1, pytest-8.3.5, pluggy-1.5.0
rootdir: /home/datadelver/Documents/PythonProjects/DataDelver/modern-ml-microservices
configfile: pyproject.toml
testpaths: tests
plugins: httpx-0.35.0, anyio-4.7.0, mock-3.14.0, cov-6.0.0
collected 11 items                                                                                                                                                                           
                                                                                                                                                  [ 16%]
tests/unit/provider/test_met_provider.py ......                                                                                                                                        [ 66%]
tests/unit/service/test_search_service.py ..                                                                                                                                           [ 83%]
tests/unit/test_main.py ..                                                                                                                                                             [100%]

---------- coverage: platform linux, python 3.13.1-final-0 -----------
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
src/main.py                             15      0   100%
src/provider/met_provider.py            29      0   100%
src/service/search_service.py           12      0   100%
src/shared/config/config_loader.py      20      0   100%
src/shared/data_model_base.py            6      0   100%
src/shared/dto/search_result.py          7      0   100%
src/shared/view/met_view.py             19      0   100%
------------------------------------------------------------------
TOTAL                                  108      0   100%

6 empty files skipped.

Required test coverage of 60.0% reached. Total coverage: 100.00%
```

Nice 100%! Don't let this lull you into a false sense of security though, 100% coverage does not necessarily mean you have good tests or that there are no bugs. As with all metrics they are simply a tool for you to use, not a target. In practice I rarely get to 100% coverage on more complex codebases (though generally above 80% is a good place to shoot for). 

With that we have successfully unit tested our code, but we aren't done yet!

## Testing Together: Because No Unit Is an Island

So far we have tested how each component of our application has worked in *isolation*, but we haven't tested how they work *together*. This type of testing falls under the category of *Integration Testing* and is similar to the premise we first started with. Of making test calls to our application and verifying the responses. In this way, we can ensure all the layers are operating together correctly.

To start off we need to tell pytest we are going to have a different type of test now. I like to prefix my integration tests with `inttest_` instead of `test_` so we need to update our config appropriately:

```toml title="pyproject.toml" linenums="22" hl_lines="9"
[tool.pytest.ini_options]
minversion = "6.0"
pythonpath = "src"
testpaths = [
    "tests",
]
python_files = [
    "test_*.py",
    "inttest_*.py",
]
```

Next, we'll create a test that looks very similar to our unit test for the main script but without the mock search service.

```python title="tests/unit/provider/test_met_provider.py" linenums="112"
from main import app
from fastapi.testclient import TestClient
import pytest
from pytest_mock import MockerFixture

from provider.met_provider import MetProvider
from service.search_service import SearchService


@pytest.fixture
def search_service(provider_with_mock_api: MetProvider) -> SearchService:
    """Fixture to provide a mocked SearchService instance."""
    return SearchService(provider_with_mock_api)


def test_search(search_service: SearchService, mocker: MockerFixture) -> None:
    """Test the search endpoint."""

    # GIVEN
    client = TestClient(app)
    mocker.patch('main.search_service', search_service)
    title = 'Test Title'

    # WHEN
    response = client.get(f'/api/search?title={title}')

    # THEN
    assert response.status_code == 200
    assert response.json() == 'https://example.com/image.jpg'


def test_search_no_results(search_service: SearchService, mocker: MockerFixture, httpx_mock) -> None:
    """Test the search endpoint when no results are found."""

    # GIVEN
    client = TestClient(app)
    mocker.patch('main.search_service', search_service)
    httpx_mock.add_response(
        url=f'{search_service.met_provider.base_url}/public/collection/v1/search?q=Test No Results Title',
        json={
            'total': 0,
            'objectIDs': [],
        },
    )
    title = 'Test No Results Title'

    # WHEN
    response = client.get(f'/api/search?title={title}')

    # THEN
    assert response.status_code == 404
    assert response.json() == {'detail': 'No results found.'}
```

Let's break this down. We still don't want to hit the real Met API so we still need our `provider_with_mock_api` fixture, but now we want to create a `SearchService` instance that uses it, which we do in the `search_service` fixture. In this way we will execute all the layers of the app up until the API call and be able to validate that they are working as expected. For the sad path we also have to provide a slightly different response that returns no results to trigger the error condition. 

Now, you may have noticed that I didn't copy paste the `provider_with_mock_api` fixture here, how can this be? Well, pytest provides a special file called `conftest.py` that gets run before the test suite is executed (not before every test). It's the perfect place to put shared fixtures we want to use in different test scripts. Go ahead and move the `provider_with_mock_api` fixture to a file called `tests/conftest.py` like so:

```python title="tests/conftest.py" linenums="1"
import pytest

from provider.met_provider import MetProvider


@pytest.fixture
def provider_with_mock_api(httpx_mock) -> MetProvider:
    """Mock responses for the Metropolitan Museum of Art API."""

    dummy_url = 'https://collectionapi-dummy.metmuseum.org'

    # Mock the response for the get_objects method
    httpx_mock.add_response(
        url=f'{dummy_url}/public/collection/v1/objects',
        json={
            'total': 1,
            'objectIDs': [1],
        },
        is_optional=True,
    )

    # Mock the response for the get_object method
    httpx_mock.add_response(
        url=f'{dummy_url}/public/collection/v1/objects/1',
        json={
            'objectID': 1,
            'title': 'Test Object',
            'primaryImage': 'https://example.com/image.jpg',
            'additionalImages': [
                'https://example.com/image1.jpg',
                'https://example.com/image2.jpg',
            ],
        },
        is_optional=True,
    )

    # Mock the response for the get_departments method
    httpx_mock.add_response(
        url=f'{dummy_url}/public/collection/v1/departments',
        json={
            'departments': [
                {
                    'departmentId': 1,
                    'displayName': 'Test Department',
                },
            ],
        },
        is_optional=True,
    )

    # Mock the response for the search method
    httpx_mock.add_response(
        url=f'{dummy_url}/public/collection/v1/search?q=Test Title',
        json={
            'total': 1,
            'objectIDs': [1],
        },
        is_optional=True,
    )

    return MetProvider(dummy_url)
```

Now we can use this fixture in all of our tests!

## Just the Beginning

This wraps up our brief delve into the world of automated software testing! We just scratched the surface of what is possible here but hopefully it gives you enough to get started! In the future we may cover other types of testing, let me know in the comments below if that's something you'd like to see! Full code for this part is available [here](https://github.com/DataDelver/modern-ml-microservices/tree/part-five)!

## Delve Data
* There are many types of software testing strategies available to validate that sofware is behaving as expected
* Unit testing seeks to test each piece of the application in isolation
* Integration testing seeks to test how each piece of the application works together
* Tools like pytest and its extensions help automate this testing process