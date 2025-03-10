---
date: 2023-12-10
categories: 
    - ML Engineering
tags: 
    - Opinion
---

# Delve 1: The (Hidden) Danger of Notebooks in Production

![Banner](../assets/images/banners/delve1.png)

> "Coming together is a beginning. Keeping together is progress. Working together is success." - Henry Ford

## When Good Intentions go Awry 

At many points in my career I have come across the topic of deploying code related to machine learning models in the form of [Jupyter Notebooks](https://jupyter.org/). Often, the push towards this idea comes from a place of good intentions, of speeding up the the model deployment process or enabling better access to and understanding of the production environment by data scientists. However, despite the good intentions, this approach has in my experience created an environment of quite negative effect for the engineering teams asked to maintain these systems. In this delve, I will share my own personal experiences on working with notebooks in production systems, some of the ways I have observed them creating unnecessary friction between data scientists and ML engineers, and reflect how I think notebooks can be used as part of a healthy production system.

<!-- more -->

### What are Notebooks Anyway?

According to [Wikipedia](https://en.wikipedia.org/wiki/Project_Jupyter):
> Jupyter Notebook (formerly IPython Notebook) is a web-based interactive computational environment for creating notebook documents. Jupyter Notebook is built using several open-source libraries, including IPython, ZeroMQ, Tornado, jQuery, Bootstrap, and MathJax. A Jupyter Notebook application is a browser-based REPL containing an ordered list of input/output cells which can contain code, text (using Github Flavored Markdown), mathematics, plots and rich media.
>
> Jupyter Notebook is similar to the notebook interface of other programs such as Maple, Mathematica, and SageMath, a computational interface style that originated with Mathematica in the 1980s. Jupyter interest overtook the popularity of the Mathematica notebook interface in early 2018.

Essentially this makes notebooks a shell with several quality of life enhancements. They come with the ability to run blocks of code, called "cells", individually and in any order and inspect their output. They provide the ability to embed rich markdown snippets alongside code blocks to capture any documentation right with the code. And perhaps most usefully, they provide support for visualization, allowing the user to visual complex graphs or tables directly in the notebook.

All of these capabilities combine to create a one-stop-shop for data exploration, visualization, and processing. This creates several advantages, namely in simplicity and ease of use. Notebooks provide a mechanism for individuals without a software engineering background to interface with and manipulate data in an intuitive way, providing a force multiplier to the data science space in much the same way excel spreadsheets were in the business world.

However, just as when business processes grow to complex to manage within a spreadsheet and more rigorous engineering process must take over, so too can the work of a data scientist become too unwieldy to manage within a production environment in the form of a notebook.

### A "Production" Environment

Production can mean a lot of different things to different people, an analyst might say his work is in production when it is being used to influence business decisions. However, for the sake of this discussion I'd like to adopt a slightly more rigorous definition:

An ML model is said to be in *production* when it's outputs are being used to affect a business process in some way, and the output needs to be accessed programmatically. 

That's it. Note: I have seen models used for a one-time report, or even *ad-hoc* reporting on a continual basis. However, the common thread there is such reporting can be done without leaving the data scientist's personal environment, be that their own laptop or cloud environment. As soon as a model needs the support of an external engineering team to deliver value I consider it in production.

## Why Notebooks in Production are so Appealing

The initial idea of using a notebook directly in production seems very appealing at first. The data scientist has already spent a considerable about of effort getting their code working, why can't we just use that? Wouldn't that create a much faster path for our data scientists to test new ideas and iterate faster?

This argument has become so compelling that whole ecosystems of tools have sprung up around the idea of serving models directly from notebooks. Notably [Databricks](https://www.databricks.com/blog/2022/06/25/software-engineering-best-practices-with-databricks-notebooks.html) will espouse running notebooks within their platform as software engineering best practice and a preferred mechanism for deploying ML pipelines.

However, time and again throughout my career I have seen engineering organizations adopt this paradigm of productionizing notebooks only to regret it and go through expensive refactors later. Why is this the case?

The answer is that fundamentally notebooks are an *exploratory* and *prototyping* tool. This is what they were originally designed for, and no amount of tooling, or a surrounding platform, can substitute them for the principles of good software engineering.

## Dangers, Explicit and Covert

Notebooks, from their inception, were designed as a tool to enable the exploration and visualization of code in a highly collaborative way. At this objective they excel! There is a reason why notebooks are the preferred mechanism for sharing ideas on portals such as [Kaggle](https://www.kaggle.com/). They are much more readable that a verbose script, and are excellent for producing demos of a concept and visualizing results in real time. I often rely on notebooks when producing reports or giving a presentation of model outputs to stakeholders. The dangers of notebooks are manifested not when they are used in this context for which they were envisioned, arguable no other tool does it better, but when the are used in an environment for which they were never intended, production engineering.

From an engineering standpoint, notebooks present several challenges, all of which contribute to a cumbersome production environment that is difficult to maintain, namely:

* Notebooks are inherently difficult to test (especially unit test), which makes it difficult to determine if they are producing the correct outputs programmatically.
* Notebooks are difficult to debug, they don't play nice with the debugging tools built into popular IDEs like VSCode, nor with the native python debugger.
* Notebooks are difficult to check in to version control, the notebook file format does not easily incorporate into git.
* Notebooks do not promote software engineering best practices such as breaking code into modules, classes, or re-useable snippets, leading to large swaths of copy-pasta throughout the code base.
* Notebooks allow for out of order execution of cells, leading to non-deterministic execution patterns.

For each of these use cases I will present potentially workarounds I have seen employed and why they usually fall flat.

### Notebooks are Difficult to Test

Automated [Unit Testing](https://en.wikipedia.org/wiki/Unit_testing) and testing in general are some of the best tools we have as software engineers to prevent bugs from being released into production.  A software suite with a good amount of test coverage I have observed has been able to be modified more frequently and with more confidence by the developers tasked with maintaining it. Unfortunately, the notebook format is very antithetical to concept of unit testing. You can seen in the Databricks blog post above that though they claim to support unit testing with notebooks, the test themselves are written in plain python files and the notebook is only serving as a wrapper (with a funky prod toggle built into it no less) to execute the tests. This presents several challenges:

* It promotes different code behavior in different environments, how can you be confident about releasing your code to production if the are parts of the code that only run in production?
* It doesn't actually test the code in the notebook itself, all of the attempts I've seen to unit test notebooks treat the notebook itself as one "unit", however this doesn't let you break the notebook into smaller atomic pieces to test individual parts of the notebook. If you have a massive 500 line notebook with a bug in it it doesn't do you much good to know that it's somewhere in those 500 lines of code.
* It introduces much more complexity, all of the python unit testing frameworks (pytest, pyunit, nose, etc.) already provide excellent mechanisms for managing suites of unit tests, using the notebook as a wrapper to execute the tests feels like an attempt to shoehorn a software engineering best practice into an environment not designed to support it just for the sake of claiming that notebooks support unit testing.

At the end of the day, whether or not it's *possible* to support unit testing in notebooks isn't really the issue. The issue is if running unit tests within notebooks is the most straightforward or maintainable way to test your code. I can speak from experience that the answer is no, so much so that I have seen engineering teams forgo automated testing all together when working in a notebook environment. If your solution to supporting a use case is so cumbersome that teams just avoid using it, it's not much of a solution is it?

### Notebooks are Difficult to Debug

Related to the previous issue, notebooks are notoriously difficult to debug. While this is changing and extensions are being released to enable better debugging experiences when working in notebooks, they are no where close to the debug experiences proper IDEs such as VSCode support for plain old python code out of the box. Concepts like *breakpoints* or *variable inspection* are not easy to implement in notebooks, requiring the insertion of ugly debug statements within your notebook code. 
While notebooks do support running cells individually and inspecting their outputs, you are at the mercy of how long those cells are. I have seen massive 1000+ line cells be produced by data scientists that become impossible to debug when something goes wrong. Usually in such situations, engineers resort to copy pasting the code into a regular python file to to use their familiar debugging tools on it, which is not always feasible depending on how intricate the dependencies for they block of code are.

### Notebooks are Difficult to Version Control

The standard iPython notebook file format is JSON with source code, markdown, images, and cell outputs all stored in a single file. This makes it incredibly hard to handle merge conflicts or even viewing diffs of notebooks in git. For example, has this notebook file changed simply because it's been run and its cell outputs are now visible or has their been a functional change to the code? In order to solve this an engineer must dive through a pile of nested JSON to try and find out, yuck!

This is such an issue that whole suites of tools have been developed such as [Jupyterlab-Git](https://github.com/jupyterlab/jupyterlab-git) to try and solve it, but they all required stepping outside the bounds of plain old git in favor of adding additional complexity and tooling to your version control stack.

This speaks to the nature of what notebooks where intended to be used for, they were never meant to hold production code, otherwise their file format would have been designed differently to work with industry standard version control tools such as git. As is a recurring them, if we want to use notebooks in this manner for which they were not intended we must introduce additional complexity to make notebooks "fit" within best practices.

### Notebooks do not Promote Software Engineering Best Practice

Notebooks promote a linear style of scripting by their very design. You run one cell and then the next and then the next and so on. This is fine for very simple problems but breaks down when the problems to solve become more complex. One of the core tenets of software engineering is breaking a complex problem down into smaller sub-problems and solving each of those individually. This is often done but employing methods of object oriented programming: classes, functions, methods, and libraries.  Unfortunately these concepts are note available natively in notebooks, while you can import python code into notebooks and execute it (as is done in the aforementioned Databricks article) this delegates the notebook to be merely a wrapper to call well designed python code. The only way this would be maintainable is that if no business logic was within the notebook itself and the notebook just served as a "main" function, calling other non-notebook python modules. However in this scenario, what value is the notebook providing? Wouldn't it just be simpler at that point to have your main function within a plain old python script as well? The answer is none and yes.  

Notebooks do allow calling other notebooks, however this promotes a false sense of modularity, instead of having your linear script within one notebook, you have simply distributed it across multiple notebooks, increasing the complexing of determining what is going on without any of the benefits of modular python code.

In practice, notebooks promote the development of very brittle, linear scripts, spanning multiple files, they don't allow for any kind of modularity natively and their only mechanism to employ such modularity is to hold no logic at all and merely serve as a wrapper. Unfortunately I have never seen this done in industry and instead the engineers must shoulder the burden of maintaining massive linear scripts.

### Notebooks Allow Out of Order Execution of Cells

One of notebooks greatest strengths, the ability to run code cell by cell, is also one of their greatest weaknesses. There is no guarantee that cells are run in the order in which they are defined within the notebooks, what's worse is that cells can be modified and re-run mid execution, leading to all sorts of weird state behaviors. While this can certainly be useful when experimenting it can lead to a more extreme version of the "works on my machine" syndrome which is "works during my session". Imagine a scenario where a a data scientist is working in a notebook, they run the first 5 cells and encounter and issue. In order to resolve the issue the go back an modify one of the earlier cells and re-run it. They then proceed to run the rest of the notebook without issue. Unfortunately, when they modified the pervious cell they accidentally deleted a critical import statement. This wouldn't affect their current session as the module was already imported from the previous cell run. However, time passes and another data scientist takes up the task of reproducing the previous scientist's work. They go to run the cells in the notebook and are surprised to find that it is not producing the correct output, it is throwing a missing import error instead.

The above scenario in various forms is all to common when working with notebooks, the lack of guardrails to prevent entering into bad states means that reproducibility and consistency become very large challenges.  Notice how the above scenario didn't involve an engineer? This leads to another question:

### Are Notebooks Even Good Tools for Doing Data Science Work?

In the above scenario, one data scientist had trouble reproducing the work of another data scientist. As reproducibility is one of the core tenets of any kind of scientific method, it begs the question, should we be using notebooks to do "science" work at all. In my opinion, probably not. I hope to expand on this idea in a future delve, but for now I'll simply say that when it comes time to re-train models (You are retraining your models to account for [concept drift](https://en.wikipedia.org/wiki/Concept_drift) right?), for many of the same reasons notebooks present challenges for engineering teams to contend with, so to do similar challenges arise when model training code within notebooks need to be run.  Again, notebooks are excellent for exploration and experimentation, but when they are used to produce any kind of production artifact, whether that be the inference code or the model artifact themselves, they fall decidedly flat compared to plain old python code. 

### The Hidden Cost of Notebooks

While from an engineering perspective the issues described above may seem self apparent, and are often brought up in various engineering blogs. There is another hidden cost to using notebooks in production that I think is far more nefarious and severe, but is much less discussed: It creates friction and even a level of resentment between engineers and data scientists.

Fundamentally the issue is that **engineers need to better understand the day to day work of data scientists, and data scientists need to better understand the day to day work of engineers**. They must work together to productionize a model after all. So often I see an "over the wall" dynamic develop at companies between data scientists and machine learning engineers. The data scientists produce some highly experimental code and toss it "over the wall" for the engineers to deploy. The engineers look at the code and realize that in order to deploy it they must completely re-write it from scratch in order for it to be maintainable. The data scientists become frustrated and dis-trustful of engineers because it takes so long to deploy their models. The engineers become frustrated and resentful of data scientists because they feel pressure to deliver as fast as possible and feel stymied by the code they receive from the data scientists.

This dynamic can lead to a very non-functional organization with an "us vs them" mentality between scientists and engineers, which ultimately stifles innovation and affects the bottom line and causes talent attrition as individuals look for greener pastures!

As a leader within an organization you are hopefully thinking "That sounds terrible! How do I prevent that from happening? What is the path forward?". Harmonious collaboration between scientists and engineers is possible, and when it is done well, I have seen it lead to tremendous unlocking of value. However, it requires re-thinking the relationship between data scientists and machine learning engineers.

## The Path Forward

As mentioned previously, the solution to stamping out this unhealthy dynamic is more awareness of job roles between data scientists and machine learning engineers. So scientists and engineers should talk to each other more, problem solved! Right? Well to some extent yes, certainly having more discussions between scientists and engineers is a good start, but if just talking to each other more would solve the problem, why does this seems to be such a pervasive issue when you do a cursory search online. The answer, perhaps unsurprisingly after reading this delve is simple: Notebooks.

In order for scientists and engineers to truly collaborate during the model development and deployment process they must speak a common language and work with a common tool set. If they do not there will always be the metaphorical "fence". This means **data scientists should strive to work in the same codebases as engineers** and **engineers should do everything they can to empower the data scientists to operate in their engineering codebases**. While the idea of giving a data scientist access to your code may at first make an engineer's skin crawl, the benefits over the long term will be numerous. Once data scientists exit the exploratory phase of their projects (notebooks) they can work hand and hand with machine learning engineers to productionize their models. This gives the scientists a sense of empowerment and control "I'm not just waiting for the engineers to hurry up and finish" and also gives them visibility into the engineering process, which should naturally lead to them producing code that is more easily productionizable. The engineering teams feel less pressure to deliver code, because now they are receiving help from the scientist who originally wrote it, and ultimately higher quality code is produced and released faster, driving the innovation cycle.

To conclude, the goal was never about putting notebooks in production, that's a distraction, it's to empower data scientists and include them in the responsibility of delivering functional software that delivers value to the business. Shifting away from notebooks for anything but exploration and experimentation is the most efficient mechanism to achieve this in my opinion.

## Additional Reading
* [Don't put data science notebooks into production](https://martinfowler.com/articles/productize-data-sci-notebooks.html) - David Johnston provides an excellent perspective on why notebooks in production create several hurdles for engineering teams to solve
* [Why (and how) to put notebooks in production](https://ploomber.io/blog/nbs-production/) - Eduardo Blancas provides a counterpoint of an approach to use notebooks in production
* [Jupyter Notebooks in production......NO! JUST NO!](https://www.reddit.com/r/datascience/comments/ezh50g/jupyter_notebooks_in_productionno_just_no/) - Reddit thread on `r/datascience` where several individuals offer their opinions both for and against using notebooks in production

## Delve Data
* Notebooks are an excellent tool for data exploration and model experimentation
* Notebooks have several engineering drawbacks when used as a mechanism for deploying models to production
* Using notebooks in production can lead to distrust and resentment between data science and engineering teams
* Having data scientists shift away from notebooks once experimentation has concluded and into the same codebases and tooling as the engineering teams is the best way to reduce friction and increase delivery frequency of model pipelines 
