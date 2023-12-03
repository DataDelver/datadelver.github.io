---
layout: post
title:  "Delve 1: The (Hidden) Danger of Notebooks in Production"
author: Chase
categories: [ML Engineering]
tags: Opinion
banner: 
    image: "/assets/images/banners/delve0.png"
---

> ""

## When Good Intentions go Awry 

At many points in my career I have come across the topic of deploying code related to machine learning models in the form of [Jupyter Notebooks](https://jupyter.org/). Often, the push towards this idea comes from a place of good intentions, of speeding up the the model deployment process or enabling better access to and understanding of the production environment by data scientists. However, despite the good intentions, this approach has in my experience created an environment of quite negative effect for the engineering teams asked to maintain these systems. In this delve, I will share my own personal experiences on working with notebooks in production systems, some of the ways I have observed them creating unnecessary friction between data scientists and ML engineers, and reflect how I think notebooks can be used as part of a healthy production system.

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

## The Path Forward

## Additional Reading
* [Don't put data science notebooks into production](https://martinfowler.com/articles/productize-data-sci-notebooks.html) - David Johnston provides an excellent perspective on why notebooks in production create several hurdles for engineering teams to solve
* [Why (and how) to put notebooks in production](https://ploomber.io/blog/nbs-production/) - Eduardo Blancas provides a counterpoint of an approach to use notebooks in production
* [Jupyter Notebooks in production......NO! JUST NO!](https://www.reddit.com/r/datascience/comments/ezh50g/jupyter_notebooks_in_productionno_just_no/) - Reddit thread on `r/datascience` where several individuals offer their opinions both for and against using notebooks in production

## Delve Data
* Welcome to my blog!
* Stay tuned for more posts on data science, machine learning, and MLOps!
