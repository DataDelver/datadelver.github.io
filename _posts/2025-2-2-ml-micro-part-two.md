---
layout: post
title:  "Delve 7: Let's Build a Modern ML Microservice Application - Part 2, Organizing Code"
author: Chase
categories:
    - Software Engineering
tags: 
    - Series 
    - Tutorial
    - Modern ML Microservices
banner: 
    image: "/assets/images/banners/delve7.png"
---

> "The beginning is the most important part of the work." -Plato

## ML Microservices, the Second

Hello data delvers! In [part one](/software%20engineering/2025/01/26/ml-micro-part-one.html) of this series we left off creating a basic application that allowed us to search for a work by title in the Metropolitan Museum of Art's collection. We were able set up a basic project structure as well as the tooling we would need to get the project off the ground. In this second part, I'd like to focus on how we can reorganize our code to make it a bit easier to manage as the complexity of our application scales. However, to begin I'd like to take a slight detour and discussing debugging.

## To Debug or Not

In part one I mentioned running the main script to check its output, but I didn't discuss how to do that specifically in VSCode. You could of course open a shell and simply execute `python3 main.py` however that missed out on one of the most powerful tools an IDE provides you: the debugger. VSCode relies on something know as a [launch configuration](https://code.visualstudio.com/docs/editor/debugging#_launch-configurations) to define how code should be executed. Go ahead and follow the instruction in that link to create a launch configuration for FastAPI (VSCode should be smart enough to auto detect it). Run the configuration and:

```shell
ERROR:    Error loading ASGI app. Could not import module "main".
```

What's going on? Remember how in part one we moved all of our Python source code to a directory called `src`? This will have a lot of benefits as we will see but one of the downsides is that by default VSCode expects our main script to be in the root directory of the project. Not to worry though this is easy to fix open up your `launch.json` file that was created in the `.vscode` directory and modify it like so:

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



## Delve Data

* The use of ML does not preclude us from benefiting from software engineering best practices, on the contrary, we should embrace them
* *nix operating systems are generally preferred for Python development, though [WSL](https://learn.microsoft.com/en-us/windows/wsl/install) is a very good option for Windows machines
* In recent years, several new tools have emerged that have streamlined the Python development process
* The microservice architecture lends itself well to ML application development