---
date: 2025-03-30
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

> "For every minute spent organizing, an hour is earned." - Benjamin Franklin

## ML Microservices, The Great Env-scape

Hello data delvers! In [part three](2025-02-16-ml-micro-part-three.md) of this series we refactored our application into three separate layers, allowing use to better separate concerns within our codebase. However, if we examine certain parts of our codebase we can still observe some brittleness:
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

The problem occurs on line 7, right now we are hardcoding a link to `https://collectionapi.metmuseum.org`. However, what if this link changes? We would have to change our code! What's the big deal you may ask? I can just update my code when needed right? While yes you could, the problem comes if we want do deploy different versions of our code each with a different url. This can happen in a few different scenarios:

**Scenario 1:**

Imagine we want to load balance our application. In this setup we have one copy of our application deployed on servers on the east coast and another copy deployed on servers on the west. In addition, the search API has hypothetically deployed two different copies of itself, one in east and one it west each behind two different urls:

* https://collectionapi-**east**.metmuseum.org
* https://collectionapi-**west**.metmuseum.org

We want to deploy the same code to each region but change the url it is pointing to.

**Scenario 2:**

Perhaps more common, we are following a [Deployment Environment](https://en.wikipedia.org/wiki/Deployment_environment) pattern in our codebase we we have 3 separate environments:

* DEV - Where we deploy changes we are actively working on
* QA - Where we test that our code is behaving as expected
* PROD - Where consumers of our application directly interact with it

We'd like to only hit the "real" search service in our PROD environment and hit dummy urls in our lower environments to make sure we don't overwhelm the real search service with our tests.

!!! note
    There are other various of this pattern with more environments, for this example I'm choosing to use a relatively simple setup with only 3 environments.

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

Take note of the filepath, that will come in handy later. We now have a file that accomplishes our objective: having a dummy url in our non-prod environments. However, there's a problem, we're copy pasting the same url multiple times! This isn't a big deal now, but you can probably imagine as our app grows and has more and more settings making sure we copy paste everything correctly could become a challenge. Fortunately, we can take advantage of one of the more advanced features of YAML here to help us [anchors and references](https://en.wikipedia.org/wiki/YAML#Advanced_components). Essentially we can define a separate section of our file that defines the default values a field should take and only override the default when necessary. That looks something like this:

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

In setting up our file in this way, we reduce the amount of duplicate lines in our configuration file we have to maintain!