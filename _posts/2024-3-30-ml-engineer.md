---
layout: post
title:  "Delve 4: The ML Engineer, Coming to an Enterprise Near You"
author: Chase
categories: 
    - ML Engineering
tags: Opinion
banner: 
    image: "/assets/images/banners/delve3.png"
---

> "Life is like riding a bicycle. To keep your balance, you must keep moving." -Albert Einstein

## Who am I?

Hello data delvers! I hope your year is off to a good start! For this delve I wanted to cover a question that I get asked often, especially whenever I meet someone new, the dialog usually goes something like this:

> Me: "Hi I'm Chase, nice to meet you!"
> 
> Other Person: "Hello Chase, it's nice to meet you too! I'm \<Insert Name Here\>. I'm a \<Insert Profession Here\>. What do you do for work?
>
> Me: "Oh! I'm a machine learning engineer!"
>
> Other Person: "Oh that's neat... What's a machine learning engineer?"

Ok, the conversations aren't usually that contrived and with the explosion in popularity of ChatGPT more and more people have heard the term machine learning than ever before but you understand the point. Those of you that have read the [about section](/about.html) of this blog will notice that (at the time of this writing) I call myself a *machine learning engineer*, but what does that profession actually entail? How does it differ from other professions in the data science and machine learning space such as *data engineer* or *data scientist*? Is it any different from a *software engineer*?  

In this delve, I intend to answer these questions and more by first providing a brief overview of the traditional roles in the "big data" space, introducing the emerging role of the machine learning engineer, and finally providing some commentary on how I think professions of this specialization can most effectively be utilized within an enterprise.

## Traditional Roles in Big Data

When we think of the world of data science and machine learning, often referred to as "Big Data", historically three distinct roles emerge:

* Data Analyst
* Data Scientist
* Data Engineer

These roles have been the pillars on which many enterprises have built the foundation of their success in the deriving value from their vast quantities of data. Understanding the responsibilities of these roles is crucial to leveraging them efficiently and effectively to drive business value. So what are they?

### Data Analyst

Arguably the profession that has been around the longest, *data analysts* specialize in collecting data from a wide variety of company sources and distilling it into reports, charts, and visualizations that stakeholders can use to inform business decisions.

Data analysts usually spend most of their time shifting through the enterprise's data lake and/or warehouse to answer a specific business question or provide an insight into a trend or pattern that is being observed in the business. 

The typical tools and technologies I have seen analysts rely on are data query languages like SQL or SAS, and data visualization suites such as PowerBI or Tableau.

The biggest strength of the business analyst is the ability to understand the context of a business problem and present just the right amount of data in order to solve it.

### Data Scientist

Deemed the "Sexist Job of the 21st Century" by the Harvard Business Review, *data scientists* use their advanced knowledge of statistics and machine learning to build and evaluate predictive models on data and solve complex problems.

Data scientists often spend much of their time in the same environments as data analysts, the data lake/warehouse. However, where the analysts focus on producing visualizations of the data, data scientists often focus on cleaning and organizing data to feed into their models. There's an often quoted statistic that "80% of a data scientists time is spent cleaning data". Due to the sensitivity of many modeling techniques to poor quality data, I can attest that this is indeed unfortunately often true. Once a cleaned collection of data has been produced, often called a *training set*, the data scientist will then use various machine learning techniques to attempt to build a model on that data which can be used to solve the business problem. Importantly, once a model has been trained, the data scientist will then evaluate that model with various statistical methods to ensure it is reasonably robust at solving the problem.

Tools and technologies data scientists use are programming languages such as R and Python along with the machine learning packages contained within them, big data processing frameworks such as Spark, and computation environments such as Jupyter Notebooks (although if you've read my [previous delve](/ml%20engineering/2023/12/10/production-notebooks.html), you may understand why this isn't the best idea).

The biggest strength of the data scientist is their advance knowledge of machine learning that enables them to solve complex problems.

### Data Engineer

If you noticed, the last two roles depend on having all of the data available in a centralized location, often referred to as a data lake or warehouse. (Technically a lake and warehouse are not the same things but the distinction is unimportant for this discussion.) It is the job of the *data engineer* to set up the pipelines to feed data into this centralized location.

Data engineers spend much of their time communicating with other engineering teams setting up ingestion processes for their data. Their primary function is to create ETL (Extract Transform Load) jobs to move and cleanse data between different systems. Often these jobs are run on a recurring cadence and take the form of python scripts, either within notebooks or plain files. 

Tools and technologies in this specialization include many of the same technologies data scientists use, python and spark, but the emphasis is on moving and transforming data rather than building ML models. In addition, job schedulers such as [Airflow](https://airflow.apache.org/) are leverage to manage ETL jobs. 

The data engineer's biggest strength is a deep technical understanding of how to process very large quantities of data at scale quickly and efficiently. 