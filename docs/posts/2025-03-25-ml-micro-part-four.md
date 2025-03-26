---
date: 2025-03-25
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
---

# Delve 10: Let's Build a Modern ML Microservice Application - Part 4, Configuration

![Banner](../assets/images/banners/delve10.png)

> "The measure of intelligence is the ability to change." - Albert Einstein

## ML Microservices, The Great Env-scape

Hello data delvers! In [part three](2025-02-16-ml-micro-part-three.md) of this series we refactored our application into three separate layers, allowing us to better separate concerns within our codebase. However, if we examine certain parts of our code we can still observe some brittleness:
<!-- more -->

```python title="src/main.py" linenums="1" hl_lines="7"
from fastapi import FastAPI, HTTPException

from provider.met_provider import MetProvider
from service.search_service import SearchService

app = FastAPI()
search_service = SearchService(MetProvider('https://collectionapi.metmuseum.org'))# (1)!


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

1. Notice a problem here?

The problem occurs on line 7, right now we are hardcoding a link to `https://collectionapi.metmuseum.org`. However, what if this link changes? We would have to change our code! What's the big deal you may ask? I can just update my code when needed right? While yes you could, the problem comes if we want to deploy different versions of our code each with a different url. This can happen in a few different scenarios:

**Scenario 1:**

Imagine we want to load balance our application. In this setup we have one copy of our application deployed on servers on the east coast and another copy deployed on servers on the west. In addition, the search API has hypothetically deployed two different copies of itself, one in east and one it west each behind two different urls:

* https://collectionapi-**east**.metmuseum.org
* https://collectionapi-**west**.metmuseum.org

We want to deploy the same code to each region but change the url it is pointing to.

**Scenario 2:**

Perhaps more common, we are following a [Deployment Environment](https://en.wikipedia.org/wiki/Deployment_environment) pattern in our codebase and we have 3 separate environments:

* DEV - Where we deploy changes we are actively working on
* QA - Where we test that our code is behaving as expected
* PROD - Where consumers of our application directly interact with it

We'd like to only hit the "real" search service in our PROD environment and hit dummy urls in our lower environments to make sure we don't overwhelm the real search service with our tests.

!!! note
    There are other variations of this pattern with more environments, for this example I'm choosing to use a relatively simple setup with only 3.

There are other scenarios where the url can change but I find these two to be the most frequent and for this delve I'd like to hone in on the second scenario as the deployment environment pattern is extremely common in practice. If you haven't encountered it before I encourage you to read up on it, every enterprise application I've ever worked on has used some variation of the pattern without fail, it is that ubiquitous. So how can we implement this pattern in our codebase?

## (Con)figure it Out!

One simple way to handle this is to introduce a [configuration file](https://en.wikipedia.org/wiki/Configuration_file) to our application that could hold the url per environment. We could then set a flag (such as an environment variable) the lets the application know which environment it is running in so it can choose which setting to read. To start we need to choose how we define our config file. A few options to choose from that I've seen before include:

* [.env](https://github.com/theskumar/python-dotenv) - Probably one of the simplest formats out there, simply stores key value pairs
* [JSON](https://en.wikipedia.org/wiki/JSON) - Just like with our APIs, we can use JSON to specify our app configuration, though it is a bit verbose
* [HOCON](https://github.com/lightbend/config/blob/main/HOCON.md) - A superset of JSON designed to be more human readable, though not as common in Python projects
* [YAML](https://en.wikipedia.org/wiki/YAML) - Another superset of JSON with additional capabilities, fairly common
* [TOML](https://en.wikipedia.org/wiki/TOML) - A simplified format somewhere between .env and YAML, starting to become more popular in Python projects, especially with the advent of the `pyproject.toml` standard

You could be successful using any of these formats but I'm going to go with YAML as I like that it is not as verbose as JSON but provides support for more complex structures than TOML.

To begin, let's create a new file to hold our configuration:

```yaml title="src/config/shared/config/config.yaml" linenums="1"
dev: 
  met_api_url: https://collectionapi-dummy.metmuseum.org

qa:
  met_api_url: https://collectionapi-dummy.metmuseum.org

prod:
  met_api_url: https://collectionapi.metmuseum.org
```

Take note of the filepath, that will come in handy later. We now have a file that accomplishes our objective: having a dummy url in our non-prod environments. However, there's a problem, we're copy pasting the same url multiple times! This isn't a big deal now, but you can probably imagine as our app grows and has more and more settings making sure we copy paste everything correctly could become a challenge. Fortunately, we can take advantage of one of the more advanced features of YAML here to help us: [anchors and references](https://en.wikipedia.org/wiki/YAML#Advanced_components). Essentially we can define a separate section of our file that defines the default values a field should take and only override the default when necessary. That looks something like this:

```yaml title="src/config/shared/config/config.yaml" linenums="1"
default: &default # (1)!
  met_api_url: https://collectionapi-dummy.metmuseum.org

dev: 
  <<: *default # (2)!

qa:
  <<: *default

prod:
  <<: *default
  met_api_url: https://collectionapi.metmuseum.org # (3)!
```

1. We use the `&` syntax to define an *anchor* to this section of the document, we name the anchor the same as the section for simplicity
2. We can break this syntax into two parts: `*default` which is a *reference* to the anchor named `default` and `<<:` which means this section should inherit all of the values defined in the following reference
3. We then need to explicitly override the `met_api_url` value in prod

In setting up our file in this way, we reduce the amount of duplicate lines in our configuration file we have to maintain! So now that we have a config file, how do we load it into our code?

## Loading Time

Fortunately Pydantic comes to the rescue again here with the [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) extension which makes loading config files a breeze!

To get started we can add `pydantic-settings` as a dependency of our project:

```
uv add pydantic-settings
```

Next we can create a new module in our python project under `src/shared/config` called `config_loader.py` to handle loading our configuration files. To start we can include a simple Pydantic data model to define our project's settings:

```python title="src/config/shared/config/config_loader.yaml" linenums="1"
from pydantic import BaseModel

class Settings(BaseModel):
    met_api_url: str
```

!!! note
    Don't forget to add an empty `__init__.py` file in the directory to make the module importable!

Next, we create a model to define our config file's structure, including each environment:

```python title="src/config/shared/config/config_loader.yaml" linenums="1" hl_lines="6-10"
from pydantic import BaseModel

class Settings(BaseModel):
    met_api_url: str

class Config(BaseSettings):
    default: Settings
    dev: Settings
    qa: Settings
    prod: Settings
```

So far, so good. Now we need to tell Pydantic where the config file is located on disk and specify the logic for loading it in. Admittedly this isn't very clear in the Pydantic documentation so I'll share what I found to work and then break it down (make sure to scroll over to see all the annotations!):

```python title="src/config/shared/config/config_loader.yaml" linenums="1" hl_lines="16 18-33"
import pathlib
from typing import Tuple, Type
from pydantic import BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource


class Settings(BaseModel):
    met_api_url: str


class Config(BaseSettings):
    default: Settings
    dev: Settings
    qa: Settings
    prod: Settings
    model_config = SettingsConfigDict(yaml_file=pathlib.Path(__file__).parent.resolve() / 'config.yaml') # (1)!

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]: # (2)!
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            YamlConfigSettingsSource(settings_cls),
        )
```

1. `model_config` is a magic attribute that tells Pydnatic where to look for the configuration settings, it can actually point to many sources but here we are telling it to look for a yaml file. We use a trick I like to call the file loader pattern where we have the file we want to load in the same directory as the script that loads it. This allows us to make the path to the file relative to the current Python file's path (which we can get from the `__file__` keyword). This means we don't have to worry about what context we are importing the Python file from, it will always be able to find the config file.

2. This method looks scary until you understand what it does. Pydantic Settings allows you to pull configuration values from multiple different sources each with an assigned priority. Pydantic will look for a setting value from the highest priority source first and only look in lower priority sources if it doesn't find it. This allows us to easily override settings if we want to. In this setup, I'm putting the YAML file at the **end** of the returned tuple so it has the **lowest** priority. This allows us to effectively override the value of our config setting by setting a value in one of the other sources for example if we need to.

!!! tip
    Pydantic Settings supports a [wide variety of settings sources](https://docs.pydantic.dev/latest/concepts/pydantic_settings/#other-settings-source) including some of the alternative file formats we discussed, so you are free to choose whichever format you like best!

Finally we need to provide a function for loading the config when it is needed:

```python title="src/config/shared/config/config_loader.yaml" linenums="1" hl_lines="37-40"
from functools import lru_cache
import pathlib
from typing import Tuple, Type
from pydantic import BaseModel
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource


class Settings(BaseModel):
    met_api_url: str


class Config(BaseSettings):
    default: Settings
    dev: Settings
    qa: Settings
    prod: Settings
    model_config = SettingsConfigDict(yaml_file=pathlib.Path(__file__).parent.resolve() / 'config.yaml')

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            YamlConfigSettingsSource(settings_cls),
        )


@lru_cache # (1)!
def load_config_settings(env: str) -> Settings:
    appconfig = Config()  # type: ignore (2)
    return getattr(appconfig, env) # (3)!
```

1. This is an optimization that will only execute this function once and cache the result (provided the arguments to the function do not change). This means we only have to pay the cost of loading the file from disk once and any subsequent calls will load the already cached result.
2. Our linter complains here that we are not passing in all of the model's attributes but we can safely ignore that warning since we will be loading them from our YAML config file
3. This is a trick that allows use to return only the settings for the environment we care about, you can read more about getattr [here](https://www.geeksforgeeks.org/python-getattr-method/)!

Now, we could make this more robust make making env an `enum` but this will work for now. Now that we have our config loader class we can use it to load our app settings!

## Powering our App with Settings!

To use this loader we only need to make a few edits to our `main.py` function:

```python title="src/main.py" linenums="1" hl_lines="1 6 9 10"
import os
from fastapi import FastAPI, HTTPException

from provider.met_provider import MetProvider
from service.search_service import SearchService
from shared.config.config_loader import load_config_settings

app = FastAPI()
app_settings = load_config_settings(os.getenv('ENV', 'dev')) # (1)!
search_service = SearchService(MetProvider(app_settings.met_api_url)) # (2)!


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

1. Here we look for our current environment from an environment variable called `ENV`, if it is not found we default to `dev`
2. Now we can pull our url from our settings object rather than hard coding it!

Now all that's left is to let our code know what environment it is running in and test out the app! An easy way to do this is create a new file called `.env` in the root of the project with the following contents:

```ini title=".env" linenums="1"
ENV=prod
```

When you start up a new shell uv is smart enough to load these environment variables for you. Go ahead and try it out! The app should still work as before, try changing the environment to QA and verify that the app breaks when it hits the dummy url! Congratulations, you now have a per-environment configurable app! Full code for this part is available [here](https://github.com/DataDelver/modern-ml-microservices/tree/part-four).

## Delve Data
* Applications often have a need to change variable values per Deployment Environment
* Hard coding these values makes this difficult
* Using tools like Pydantic Settings, we can create a configuration file that makes it easy to switch these values per environment