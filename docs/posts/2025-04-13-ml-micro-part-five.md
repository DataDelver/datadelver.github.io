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

As the complexity of the application grows, so too does the difficulty in verifying that it is behaving as expected. Right now, it is fairly straightforward to test our application. We can bring up the swagger docs, and try a few sample requests to make sure all is behaving as expected. However, we can imagine as we add more and more functionality to our app, it will become more tedious to do this type of *manual* testing every time we make a change to verify nothing has broken. Once more, if something does break, this testing may make it difficult to determine where in our application the break actually occurred (unless we have very, very helpful error messages). A better approach would be to have a set of *automated* tests, that run whenever we make a change to verify nothing has broken. It is this type of testing that I would like to focus on for the subject of this delve.

!!! info
    There are [many types of software testing](https://www.geeksforgeeks.org/types-software-testing/). For this delve we will be focusing on small subset of testing strategies. Other forms of testing may be covered in future delves.

## Let's Get Testy

To begin let's talk about how we might go about writing tests for our application. We could start at the highest level, trying to test the whole application in one go, sending it requests and validating responses. This solves the first problem of having to not run our tests manually anymore, but doesn't solve the second of trying to isolate where the breakage occurred. A different strategy would be to break the application into the smallest pieces possible and test each piece independently of the others and then once the pieces are verified to be working in isolation, test how they work together. In this way, if something breaks we should be able to tell were the breakage occurred because the test for the broken piece should fail. In this type of testing approach we call these pieces of the application *Units* and this testing strategy [Unit Testing](https://en.wikipedia.org/wiki/Unit_testing).

The next question you may be asking is "Where to begin writing your unit tests?". This is more personal preference but I like to start at the lowest layers of my application and work my way up. For us that means starting at the *Data Layer* and working our way up, though it can be valid to start in the reverse order as well.

!!! note
    Another valid question to ask is "When should I write my tests?". In this series we are following what I'd call the "conventional" or "typical" route of testing in which we already have working code and we are writing tests to ensure that is it behaving as expected. However, there is an alternative software development philosophy known as [Test Driven Development](https://en.wikipedia.org/wiki/Test-driven_development) that advocates for the opposite flow: That of writing the tests for a new piece of functionality first, then writing the code that passes the test. Test Driven Development has a lot of advantages, namely forcing the discussion around the desired functionality before any code to implement that functionality has been written. It is worth exploring this approach more and seeing if it aligns with your own development style more than the typical route. It's also worth mentioning that these two approaches are not mutually exclusive and can be mixed and matched as needed.

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

When writing tests I like to follow a structure make popular by the [Behavior Driven Development](https://dannorth.net/introducing-bdd/) testing philosophy. Each test case has three sections:

* **Given** - Initial set of conditions
* **When** - The test action occurs
* **Then** - Validate that the desired behavior has happened

In this way you can write a test case as a simple sentence. For example the above test could be written as "Given a Met Provider connected to the Met API, when I call the get objects method, then I should get 495439 results back." Now, in writing the test case in this way you might already see the problem with this test. As of right now, when I call this route on the Met API I get 495439 results, but what happens if the Met adds another work to their collection? I would then get 495440 results back and this test would *fail* even though nothing is wrong with the code. This demonstrates an important principle of unit testing, that tests should be written in such a way that they test the unit in *isolation* and should not be dependent on the state of any external system to the unit in order for the test to succeed. So how can we address this?

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

Now every test that needs the provider mocked out can simply take in the `provider_with_mock_api` argument. With this pattern in had we can go ahead and write the rest of our test cases:

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

With our provider methods all tested we can move on to the *Service Layer* and test our `SearchService` class.

## Mock all the Things!
Our search service just has one method to test `search_by_title` as a reminder, this is what the source code looks like:

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



## Delve Data
* Applications often have a need to change variable values per Deployment Environment
* Hard coding these values makes this difficult
* Using tools like Pydantic Settings, we can create a configuration file that makes it easy to switch these values per environment