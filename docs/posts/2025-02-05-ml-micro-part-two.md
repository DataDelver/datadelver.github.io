---
date: 2025-02-05
categories:
    - Software Engineering
tags: 
    - Series 
    - Tutorial
    - Modern ML Microservices
---

# Delve 7: Let's Build a Modern ML Microservice Application - Part 2, The Data Layer

![Banner](../assets/images/banners/delve7.png)

> "Data is not just the new oil, it's also the new soil." - David McCandless

## ML Microservices, the Second

Hello data delvers! In [part one](2025-01-26-ml-micro-part-one.md) of this series we left off creating a basic application that allowed us to search for a work by title in the Metropolitan Museum of Art's collection. We were able set up a basic project structure as well as the tooling we would need to get the project off the ground. In this second part, I'd like to focus on how we can reorganize our code to make it a bit easier to manage as the complexity of our application scales. However, to begin I'd like to take a slight detour and discussing debugging.

<!-- more -->

## To Debug or Not

In part one I mentioned running the main script to check its output, but I didn't discuss how to do that specifically in VSCode. You could of course open a shell and simply execute `python3 main.py` however that missed out on one of the most powerful tools an IDE provides you: the debugger. VSCode relies on something know as a [launch configuration](https://code.visualstudio.com/docs/editor/debugging#_launch-configurations) to define how code should be executed. Go ahead and follow the instruction in that link to create a launch configuration for FastAPI (VSCode should be smart enough to auto detect it). Run the configuration and:

```
ERROR:    Error loading ASGI app. Could not import module "main".
```

What's going on? Remember how in part one we moved all of our Python source code to a directory called `src`? This will have a lot of benefits as we will see but one of the downsides is that by default VSCode expects our main script to be in the root directory of the project. Not to worry though, this is easy to fix. Open up your `launch.json` file that was created in the `.vscode` directory and modify it like so:

```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python Debugger: FastAPI",
            "type": "debugpy",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "main:app",
                "--reload"
            ],
            "jinja": true,
            "cwd": "${workspaceFolder}/src",
            "env": {
                "PYTHONPATH": "${cwd}:${env:PYTHONPATH}"
            },
        }
    ]
}
```

We need to add two additional arguments:

* The `cwd` argument tells the configuration to change the current working directory to the `src` folder relative to the workspace folder.
* The `PYTHONPATH` argument appends the current working directory to the `PYTHONPATH` environment variable, this will ensure that imports within our project codebase will work correctly.

Go ahead and save that configuration and run again, your FastAPI application should run now! I also encourage you to play around with starting a debugging session, setting a few breakpoints and following the execution of the code. Reading the full [debugging guide](https://code.visualstudio.com/docs/editor/debugging) for VSCode will give you an idea of the options you have available to you.

With debugging all set up we are now ready to discuss refactoring our code!

## Refactor, Really?

When we left off in part one we had created a single file application with a `main.py` that looked something like this:

```python
from typing import Optional
from fastapi import FastAPI
import httpx

app = FastAPI()


@app.get('/api/search')
def search(title: str) -> str:
    """Executes a search against the Metropolitan Museum of Art API and returns the url of the primary image of the first search result.

    Args:
        title: The title of the work you wish to search for.

    Returns:
        The url of the primary image of the first search result or 'No results found.' if no search results are found.
    """
    search_request: httpx.Response = httpx.get(
        'https://collectionapi.metmuseum.org/public/collection/v1/search',
        params={'q': title, 'title': True, 'hasImages': True},
    )

    object_ids: Optional[list[int]] = search_request.json().get('objectIDs')

    if object_ids:
        object_request = httpx.get(f'https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_ids[0]}')
        primary_image_url = object_request.json().get('primaryImage')
        return primary_image_url
    else:
        return 'No results found.'
```

Now, while there isn't a lot going on in this file right now, I'd argue from an application scalability perspective it's already too complicated. It may seem outlandish to argue that functionally 8 lines of code is too complicated but I'm not arguing from a number of *lines* perspective but from a *scope* perspective. Right now this single file contains all of our business logic, that's fine while our business logic is simple, but what happens as we want to add more complexity and processing steps to our application? The way our application is structured right now we just keep adding more complexity to this single file. This is analogous to the workflow I've seen many times with data scientists creating ever larger *uber* Jupyter notebooks that contain all of their logic. In the same way maintaining a notebook with hundreds of lines of code is unmaintainable, so too is maintaining a single file application. In this delve I intend to refactor this application into something that is more maintainable and scalable without increasing the complexity of the application so we can focus purely on the refactor. To that end we can break our application into 3 main pieces of functionality:

1. We make API requests to external systems to provide *data* to our application
2. We encapsulate some *business logic* (In this case call the search API to retrieve an Object, then call the Objects API to retrieve an image) within our service
3. We provide an *interface* (API) to allow external customers to interact with our application

Intuitively as you may suspect, these are the three layers we will break our application into. If any of you are familiar with the concept of [Multitier Architecture](https://en.wikipedia.org/wiki/Multitier_architecture), this is very similar to the three tier architecture often discussed in works of that nature, but zoomed into the scope of our service itself. For this delve we are going to focus on the first of these three layers, the Data Layer.

## The Data Layer

The Data Layer, as the name implies, is all about *data*. Functionally, that means we have two objectives we must complete at this layer:

* Be able to request data from other components (both internal to the application like a database or external to the application like other services)
* Be able to represent the requested data within the application

Starting with the first objective, looking at the [Metropolitan Museum of Art API](https://metmuseum.github.io/) that we are leveraging we can see there are four different operations we can perform:

* **Objects** - A listing of all valid Object IDs available for access.
* **Object** - A record for an object, containing all open access data about that object, including its image (if the image is available under Open Access)
* **Departments** - A listing of all valid departments, with their department ID and the department display name
* **Search** - A listing of all Object IDs for objects that contain the search query within the object's data

Though currently we are only using the **Object** and **Search** operations. In order to represent these operations without our code, we can lean into our OOP principles and create a client *class* with four *methods*, one for each operation.

Before we do though I'd like to talk about naming. Generally, I like to split my client classes into two categories. Those that simply *provide* data from other systems, and those that let me *modify* data in other systems. I like to call a client in the first case a **Provider**, as it simply provides data to the application. In the second case I like to call the client a **Repository**, as it allows us to modify a repository of data (typically a database).

In our case our API does not allow modifying the collection of artwork (I hope), and so it falls firmly into the provider use case.

### The Provider Component

To that end we are now ready to refactor our code, we can create a new directory under our `src` folder called `provider`. This folder will hold all the provider clients for our application. Within that folder we need to create two files, first a empty file called `__init__.py`, this will mark this directory as a Python module and thus allow Python files within it to be imported to other parts of the application, and a file called `met_provider.py` this file as you can guess will hold our client object.

We should now have a directory structure under `src` that looks like this:

```
src
├── main.py
└── provider
    ├── __init__.py
    └── met_provider.py
```

Inside `met_provider.py` we can create a simple class to hold our API operations:

```python
class MetProvider:
    """A client for the Metropolitan Museum of Art API.

    Args:
        base_url: The base URL of the API.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
```

Now you might be asking, why not just hard code the URL to the API? We know what it is. The reason I prefer to make the url to the API a constructor parameter is to allow us to easily point to different deployments of the API with the same client. This often comes up if you follow a Dev/QA/Prod style of deployment. You might have your production API at `https://www.my-api.com` and a QA version of the API hosted at `https://www.my-api-qa.com` and a dev version at `https://www.my-api-dev.com`. Having the API url be a parameter allows us to switch between all three urls without needing to change the code of the client.

Next we can add a method for the **Objects** operation to our API like so:

```python
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
    ) -> dict:
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

        return r.json()
```

We we can already see the benefits of creating a separate class to handle calling the API. The Met API requires that department IDs be joined by a `|` character, we can hide that implementation detail at this layer and instead allow the user to pass in a much more natural and pythonic list of integers. Similarly, we can pass in a `datetime` object and allow this layer to put it in the proper format for this API. In this way we can hide the *specific* details of the API and allow the user to work with much more natural and easy to use Python objects. 

We can similarly flesh out the rest of the operations in our provider class:

```python
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
    ) -> dict:
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

        return r.json()

    def get_object(self, object_id: int) -> ObjectResponse:
        """Retrieves an object from the Metropolitan Museum of Art API.

        Args:
            object_id: The ID of the object to retrieve.

        Returns:
            The object.
        """

        r = httpx.get(f'{self.base_url}/public/collection/v1/objects/{object_id}')
        return r.json()

    def get_departments(self) -> dict:
        """Retrieves departments from the Metropolitan Museum of Art API.

        Returns:
            A list of departments.
        """

        r = httpx.get(f'{self.base_url}/public/collection/v1/departments')
        return r.json()

    def search(self, q: str, title: Optional[bool] = None, has_images: Optional[bool] = None) -> dict:
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

        return r.json()

```

One other benefit of using a provider class is we only have to implement what we need. The **Search** operation has many more parameters (and you are welcome to map them out as an exercise) but for our logic we only need the `title` and `hasImages` functionality.

You should now have a fully working client for the Met API, start up a shell and try it out!

```
>>> from provider.met_provider import MetProvider
>>> p = MetProvider('https://collectionapi.metmuseum.org')
>>> p.get_departments()
'{"departments":[{"departmentId":1,"displayName":"American Decorative Arts"},{"departmentId":3,"displayName":"Ancient Near Eastern Art"},{"departmentId":4,"displayName":"Arms and Armor"},{"departmentId":5,"displayName":"Arts of Africa, Oceania, and the Americas"},{"departmentId":6,"displayName":"Asian Art"},{"departmentId":7,"displayName":"The Cloisters"},{"departmentId":8,"displayName":"The Costume Institute"},{"departmentId":9,"displayName":"Drawings and Prints"},{"departmentId":10,"displayName":"Egyptian Art"},{"departmentId":11,"displayName":"European Paintings"},{"departmentId":12,"displayName":"European Sculpture and Decorative Arts"},{"departmentId":13,"displayName":"Greek and Roman Art"},{"departmentId":14,"displayName":"Islamic Art"},{"departmentId":15,"displayName":"The Robert Lehman Collection"},{"departmentId":16,"displayName":"The Libraries"},{"departmentId":17,"displayName":"Medieval Art"},{"departmentId":18,"displayName":"Musical Instruments"},{"departmentId":19,"displayName":"Photographs"},{"departmentId":21,"displayName":"Modern Art"}]}'
```

This works but it's a bit tricky to work with the output of our client. Notice how all the methods of our client have a return type of `dict`. This means when using the client we have no guarantees of the structure of the data we are getting back from our client, and once more, when we do get it back it's difficult to deal with. For example, to get the display name of the first department we'd need some code that looks something like this:

```python
r = p.get_departments()
r['departments'][0]['displayName']
```

Yuck! While you can type hint more complex return types, `dict[str, list[dict[str, Union[str, int]]]]` would be the type hint for that return value for example, this gets pretty ugly and does not help us with the second issue of accessing our data once it's returned. We still have to worry about handling cases where data is missing, or perhaps was a different data type than expected. We also have to type out long Python statements to access nested data structures. Luckily, there is another component of the Data Layer that can help us here: Data Models.

### The Data Model Component

When discussing how to represent data within an application, you will often hear the concept of [Data Models](https://en.wikipedia.org/wiki/Data_model) brought up. These are not models in the machine learning sense, but simply a representation or model of data within the system (hence the name). You can think of these models as simple classes with no methods, only attributes representing the data of the system. These data models are then passed between the layers of the application to facilitate the flow of data.

For example, in the above departments example I could have a `Department` class to represent a single department, every department has a `department_id` and a `display_name` so we can model that like so:

```python
class Department:
    department_id: int
    display_name: str
```

We could then have another class that models the response from the API `DepartmentResponse` which in this case is a list of `Department` objects.

```python
class DepartmentResponse:
    departments: list[Department]
```

This helps us better organize the data we are getting back but does not help us at all when it comes to validating that the data is following the schema that we expect. Fortunately, FastAPI ships with another library that can help us here: [Pydantic](https://docs.pydantic.dev/latest/) which will bring our data models to the next level.

Pydantic allows use to create data models like above but will also **validate** that the data provided matches the schema of the type hints of our models. I can't understate how big of a deal this is. This brings what is one of the core strengths of statically typed languages like Java or C# over to Python. Let's try it out!

Before we jump into code I also want to talk about naming again. Just like with clients, I like to group my data models based on what they are for. If the data model represents something *external* to the system, like the schema of an API or database I like to call an instance of those models a **View**, as it represents a view into an external component. If that data model is instead used to pass data *between* components of the application I like to call an instance of those models a **Data Transfer Object** or DTO, as it is transferring data between components. If that seems a little fuzzy right now don't worry, in this series we will see examples of both!

To start lets create a new directory under `src` called `shared` and make it a module by adding an empty `__init__.py` file. This is where I like to keep things like data models that are potentially shared between layers of the application. Within this folder create another one called `view` and similarly make it a module. This is where we will store our view models. Inside here create a Python file called `met_view.py`, you can probably guess what will go here: our view models for the Met API!

You should now have a `src` directory structure that looks like this:

```
src
├── main.py
├── provider
│   ├── __init__.py
│   └── met_provider.py
└── shared
    ├── __init__.py
    └── view
        ├── __init__.py
        └── met_view.py
```

Inside of our `met_view.py` we can create our data models as above, however they will inherit from a special parent class, `BaseModel` from pydantic.

```python
from pydantic import BaseModel

class Department(BaseModel):
    department_id: int
    display_name: str


class DepartmentResponse(BaseModel):
    departments: list[Department]
```

Once nice thing to point out here is we can use data models inside of other data models, as we do to create an attribute of type `list[Department]` in the `DepartmentResponse` model. Go ahead and start up a shell to see the data validation in action! Let's try create a valid `Department`:

```
>>> from shared.view.met_view import Department
>>> d = Department(department_id=1, display_name="My Met Department")
>>> d
Department(department_id=1, display_name='My Met Department')
```

It works! But what happens when we try to create a department with a string id instead of an int?

```
>>> d = Department(department_id="one", display_name="My Met Department")
Traceback (most recent call last):
  File "<python-input-6>", line 1, in <module>
    d = Department(department_id="one", display_name="My Met Department")
  File "/home/overlord/Documents/PythonProjects/DataDelver/modern-ml-microservices/.venv/lib/python3.13/site-packages/pydantic/main.py", line 214, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
pydantic_core._pydantic_core.ValidationError: 1 validation error for Department
department_id
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='one', input_type=str]
    For further information visit https://errors.pydantic.dev/2.10/v/int_parsin
```

Here we see that we get a `ValidationError` with a helpful message that we need to supply an int rather than a string.

**Note:** Pydantic does try to type cast fields for you if it makes sense so `Department(department_id="1", display_name="My Met Department")` works!

We can now modify our `get_deparments()` function to return an instance of `DepartmentResponse` rather than a `dict`:

```python
def get_departments(self) -> DepartmentResponse:
    """Retrieves departments from the Metropolitan Museum of Art API.

    Returns:
        A list of departments.
    """

    r = httpx.get(f'{self.base_url}/public/collection/v1/departments')
    return DepartmentResponse.model_validate(r.json())
```

`model_validate` is the key step here. This tells Pydantic we want to validate that data contained in another object (in this case the json response from the API) and return a Pydantic data model if the validation passes.

Let's try it out!

```
>>> from provider.met_provider import MetProvider
>>> p = MetProvider('https://collectionapi.metmuseum.org')
>>> p.get_departments()
Traceback (most recent call last):
  File "<python-input-2>", line 1, in <module>
    p.get_departments()
    ~~~~~~~~~~~~~~~~~^^
  File "/home/overlord/Documents/PythonProjects/DataDelver/modern-ml-microservices/src/provider/met_provider.py", line 67, in get_departments
    return DepartmentResponse.model_validate(r.json())
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^
  File "/home/overlord/Documents/PythonProjects/DataDelver/modern-ml-microservices/.venv/lib/python3.13/site-packages/pydantic/main.py", line 627, in model_validate
    return cls.__pydantic_validator__.validate_python(
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        obj, strict=strict, from_attributes=from_attributes, context=context
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
pydantic_core._pydantic_core.ValidationError: 38 validation errors for DepartmentResponse
departments.0.department_id
  Field required [type=missing, input_value={'departmentId': 1, 'disp...erican Decorative Arts'}, input_type=dict]
    For further information visit https://errors.pydantic.dev/2.10/v/missing
...
```

What's going on? The shaper-eyed among you may have noticed a different in casing when we created our data model. Typically, JSON utilizes [camelCase](https://en.wikipedia.org/wiki/Camel_case) when naming attributes, for example: `departmentId`. However, our data models follow the python convention of using [snake_case](https://en.wikipedia.org/wiki/Snake_case) for our attributes, so for example `department_id`. As a result of this mis-match in casing, the data is not being correctly parsed. How can we fix this?

One way we can do this is to take advantage of the [Field Alias](https://docs.pydantic.dev/latest/concepts/fields/#field-aliases) feature of Pydantic. This allows us, as the name implies, to create aliases other fields can go by. For our `Department` model that would look something like this:

```python
from pydantic import BaseModel, Field

class Department(BaseModel):
    department_id: int = Field(alias='departmentId')
    display_name: str = Field(alias='displayName')
```

This works but is a bit tedious to type out. Fortunately, for common casing changes, Pydantic provides another option. We can specify a [model_config](https://docs.pydantic.dev/latest/concepts/config/) for our models that changes its default behavior. One of the options is an [alias_generator](https://docs.pydantic.dev/latest/api/config/#pydantic.config.ConfigDict.alias_generator) which allows us to programmatically generate aliases for our models. Pydantic also comes with a number of [pre-made alias generators](https://docs.pydantic.dev/latest/api/config/#pydantic.alias_generators) for common use cases, including one for converting to camelCase!

Utilizing this we can change our class to:

```python
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

class Department(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
    department_id: int
    display_name: str
```

Let's try it out!

```
>>> from provider.met_provider import MetProvider
>>> p = MetProvider('https://collectionapi.metmuseum.org')
>>> p.get_departments()
DepartmentResponse(departments=[Department(department_id=1, display_name='American Decorative Arts'), Department(department_id=3, display_name='Ancient Near Eastern Art'), Department(department_id=4, display_name='Arms and Armor'), Department(department_id=5, display_name='Arts of Africa, Oceania, and the Americas'), Department(department_id=6, display_name='Asian Art'), Department(department_id=7, display_name='The Cloisters'), Department(department_id=8, display_name='The Costume Institute'), Department(department_id=9, display_name='Drawings and Prints'), Department(department_id=10, display_name='Egyptian Art'), Department(department_id=11, display_name='European Paintings'), Department(department_id=12, display_name='European Sculpture and Decorative Arts'), Department(department_id=13, display_name='Greek and Roman Art'), Department(department_id=14, display_name='Islamic Art'), Department(department_id=15, display_name='The Robert Lehman Collection'), Department(department_id=16, display_name='The Libraries'), Department(department_id=17, display_name='Medieval Art'), Department(department_id=18, display_name='Musical Instruments'), Department(department_id=19, display_name='Photographs'), Department(department_id=21, display_name='Modern Art')])
```

It works! We now have our departments correctly modeled. Let's take a look at what getting the display name of the first department looks like now:

```python
r = p.get_departments()
r.departments[0].display_name
```

Much more readable! Before we go ahead and create the rest of our views though we should consider that we want all of them to have the same config behavior of allowing camelCase payloads to be validated. We *could* go and add the `model_config` property to all of them however a more elegant way to solve this is to just have a base class that all our views inherit from that specifies this configuration, that way we only have to specify it once!

Go ahead under `src/shared` and create a new Python file called `data_model_base.py` this will (unsurprisingly) hold the base class for our data models.

You should now have a directory structure that looks like this:

```
src
├── main.py
├── provider
│   ├── __init__.py
│   └── met_provider.py
└── shared
    ├── __init__.py
    ├── data_model_base.py
    └── view
        ├── __init__.py
        └── met_view.py
```

Inside we can create a new class `ViewBase` which will be the Pydantic base class for all of our views:

```python
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ViewBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel)
```

We can now let all of our views inherit from this base class:

```python
from typing import Optional

from pydantic import Field
from shared.data_model_base import ViewBase


class SearchResponse(ViewBase):
    total: int
    object_ids: Optional[list[int]] = Field(alias='objectIDs')


class Department(ViewBase):
    department_id: int
    display_name: str


class DepartmentResponse(ViewBase):
    departments: list[Department]


class ObjectResponse(ViewBase):
    object_id: int = Field(alias='objectID')
    title: str
    primary_image: str
    additional_images: list[str]


class ObjectsResponse(ViewBase):
    total: int
    object_ids: list[int] = Field(alias='objectIDs')
```

Notice we still had to use aliases in cases where the attribute followed non-standard casing. `ID` not `Id` really? Also note, there are many more attributes available in the schema of the response to the Object operation in the Met API, however we only need to model the attributes we need. By default Pydantic will just ignore any extra fields, though you can change this in the model configuration.

Finally we can update our `MetProvider` class to utilize these views:

```python
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

## Wrangling our Data (Layer)

That wraps up our build of the data layer of our application! It may seem like a lot of code to do a small amount, but hopefully it's clear that the benefits of abstracting out the data modeling and validation to its own layer of the application will make it much easier to manage the data needs of our application as it increases in scale and the scope of the data required expands (something that often happens in ML applications). Full code for this part is available [here](https://github.com/DataDelver/modern-ml-microservices/tree/part-two). In the next part we'll see how to leverage this layer in the other parts of the application: the *Business Logic Layer* and the *Interface* layer. See you next time!

## Delve Data

* As the complexity of our application increases, a single `main.py` file application will become messy
* Adopting a three layer architecture for our application's code can help us to manage this complexity
* The first of these layers, the *Data Layer* is responsible for requesting data from other components and representing the requested data within the application