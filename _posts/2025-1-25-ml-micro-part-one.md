---
layout: post
title:  "Delve 6: Let's Build a Modern ML Microservice Application - Part 1"
author: Chase
categories:
    - ML Engineering
    - Software Engineering
tags: Series Tutorial
banner: 
    image: "/assets/images/banners/delve5.png"
---

> "All life is problem solving." -Karl Popper

## A New Year, A New Start

Hello data delvers! Happy New Year! I hope you all have been well! It's been some time since our last delve (sorry!) but I want to kick off 2025 with a new series of posts I've been wanting to do for some time, building out an ML application using modern microservices principles.

In this multi-part series we'll focus on the tools, techniques, and strategies I use to bring ML applications to life in a maintainable, scalable, and extendable way. If that sounds of interest to you, put on your delving gear and join me as we go deep into the depths of the labyrinth!

## ML, Redefining Application Development?

To begin this delve I'm going to start by stating that for part one I am not going to be discussing machine learning at all, only core software engineering principles. "What? How can you talk about building ML applications and not ML at all!" I could hear you say. Firstly, I will talk about ML *eventually*. However the main point I want to raise here is **there is nothing special about ML that invalidates good software engineering practices.** I think this is such an important point that I will state it again, repeat with me:

> There is nothing special about ML that invalidates good software engineering practices.

This is something I have seen even experienced practitioners get tripped up on. Particularly those that have come from a software engineering background but have never worked with ML before. They join a team, see all the data scientists working in notebooks and see everyone else nodding their heads and working to productionize those notebooks and think "Gee, this doesn't seem to make sense to me but this is what everyone else is doing so it must be right." and go along with the herd. I'm here to say that you are right to feel like something is off.

Historically the data science community has not come from a software engineering background, but one of statistics and analytics. As a result, a whole crop of tools and companies have sprung up to make productionizing their work "easy". Sometimes even advocating for running notebooks in production as "best practice". If you've read my [previous delve](/ml%20engineering/2023/12/10/production-notebooks.html) on the subject you know that this approach is full of pitfalls.

In addition to the above drawbacks, the mentality of "ML is special, it requires a different paradigm to productionize" forces us to ignore all of the wonderful best practices that have developed over the past several decades of software engineering to improve reliability, testability, and extendability ([Object Oriented Programming](https://en.wikipedia.org/wiki/Object-oriented_programming) is over 50 years old at this point, I don't think it's going anywhere). As such, instead of asking "How do we modify our software development best practices to accommodate ML?" I prefer to ask opposite question: "How can we develop ML capabilities in a way that can benefit from all the best practices of software engineering?". It is this approach that I intend to unravel in this delve.

## Preparing the Excavation Site

Hopefully by now I have piqued your interest in this approach, which means we now need to prepare a workspace to begin developing it. The first choice we must make is what operating system to develop on, which is influenced somewhat by our choice of programming language.

As you are probably already aware [Python](https://www.python.org/) has become the lingua franca of the Data Science and Machine Learning world. According to the [2024 Stack Overflow Developer Survey](https://survey.stackoverflow.co/2024/technology#most-popular-technologies), a whopping 51% of respondents stated they work with Python. Compare this to [R](https://www.r-project.org/) the other main language used for modeling at only 4.3% and it should be clear Python is currently enjoying a resounding popularity.

While it is possible to develop Python natively on a Windows operating system, it has not been in my experience very pleasant, with most developers preferring either a macOS or Linux environment to develop in. However, if you are on a Windows machine before you go dual-booting your hard drive to install Linux you should definitely consider the [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install), which allows to run a full Linux kernel on your Windows machine. This is actually my preferred development setup and the one I will be using for this series.

With the operating system out of the way, the next major choice to make is which Integrated Development Environment (IDE) to choose. For a long time my answer here would have been [PyCharm](https://www.jetbrains.com/pycharm/) as it was the most feature rich and complete. However, in recent years [Visual Studio Code](https://code.visualstudio.com/) (VSCode) has taken the development world by storm, rising to 73.6% of respondents using it in the same [2024 Stack Overflow Developer Survey](https://survey.stackoverflow.co/2024/technology#1-integrated-development-environment). It also has the added benefit of being completely free to use. Given this, I will be using VSCode as my IDE, though most of what we cover should be IDE agnostic.

With that all out of the way, let's boot up VSCode and get to coding!

Except, when you first boot up VSCode it won't be equipped to develop Python. Head over to the extensions tab and grab the official [Python Extension](https://marketplace.visualstudio.com/items?itemName=ms-python.python) from Microsoft and if you are on Windows and want to use WSL, grab the [WSL](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-wsl) extension too (make sure to check out the extension instructions as to how to open a VSCode instance connected to WSL).

Open up a new Terminal in VSCode a do a quick Python Hello World to verify everything is working as expected:

![Python Hello World](/assets/images/figures/delve6/PythonHelloWorld.png)

One thing to note here, there are plenty of good resources out there to learn Python, https://www.learnpython.org/ is unironically a good one, so for this series I'm going to assume you have some basic Python knowledge already but I'll point out specifics that I find valuable. 

## Moving in the Digging Equipment

If you've ever worked with Python one thing you probably know already is that managing dependencies is hard! Trying to make sure you have all the right versions of your dependencies installed and they don't conflict with each other has been a recurring challenge in the Python ecosystem. Up until recently, there hasn't be a good tool that manages all of this well. Previously I used a amalgamation of [pyenv](https://github.com/pyenv/pyenv), [pipenv](https://pipenv.pypa.io/en/latest/), and some custom setup scripts to manage it all. While this worked it was finicky and brittle. Some other tools like [poetry](https://python-poetry.org/) came along but I never really found it compelling enough to switch. That all changed with [uv](https://docs.astral.sh/uv/). Simply put, this is the best tool out there, and it does it all: managing different versions of Python on your machine, blazing fast dependency resolution, and distribution packaging to boot. It has easily replaced 5-6 tools in my workflow. Needless to say, I will be using uv for all my projects going forward.

While we are on the same topic of Python tools, the same company that maintains uv also has another tool [Ruff](https://docs.astral.sh/ruff/) which is great for auto-formatting your python code so that it meets your stylistic standards. This again replaced several tools in my existing workflow and available as a [VSCode Extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff). Not a hard requirement but I highly encourage using it as well. Not having to argue with other engineers on the correct way to style code and just having a tool do it for you has saved me countless hours.

Finally, you should hopefully already have [git](https://git-scm.com/) installed on your machine. You are version controlling your code aren't you?

## Start Digging

Ok! That should be enough setup for now, let's get coding! Open up a shell and type `uv init modern-ml-microservices` this will create a new starter project directory for us to work with. You can then open up this directory in VSCode by typing `code modern-ml-microservices` and we're up and running!

![Python Hello World](/assets/images/figures/delve6/InitialProjectSetup.png)

## Delve Data

* The Alt+F11 full screen shortcut was removed in the Debian 12 "Bookworm" distribution of the Raspberry Pi OS
* The solution is to add a new shortcut to the `wayfire.ini` file