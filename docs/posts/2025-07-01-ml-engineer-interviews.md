---
date: 2025-07-01
categories:
    - ML Engineering
tags: 
    - Opinion
    - Resource 
---

# Delve 14: Reflections on a Job Quest

![Banner](../assets/images/banners/delve14.png)

> "Your work is going to fill a large part of your life, and the only way to be truly satisfied is to do what you believe is great work." - Steve Jobs

## A New Chapter

Hello data delvers! I recently successfully wrapped up a journey to find a new job! Along the way, I had the opportunity to interview at several different companies, experience many different styles of interviews, and explore different types of roles. For this delve, I intend to distill some thoughts about this process and share some lessons learned in the hopes they may be useful to others either looking to break into this field or find their next opportunity within it. If that sounds of interest stick around!
<!-- more -->

## Beginning the Quest

To kick off my job hunt I first had to decide the criteria I was looking for in my next role. This set of criteria will be unique to you but it's a good idea to have a list of must haves and nice to haves in the role you are searching for. Write this list down and revisit it throughout your search to see if it still holds true or if things have shifted as a result of your journey. For example, your list might look something like this:

Must Have:

* Fully Remote
* Staff+ Title
* Engineering-Focused Position

Nice to Have:

* "Founding" Role
* Large scope
* Flexible PTO

With your set of criteria in hand, begin applying to jobs that meet them! I primarily relied on [LinkedIn](https://www.linkedin.com) for my job search, though there are other job boards available, particularly if you are interested in startup roles. It's also not a bad idea to set up [job alerts on LinkedIn](https://www.linkedin.com/help/linkedin/answer/a511279/job-alerts-on-linkedin?lang=en) so you can be notified of new roles as they are posted.

## Crafting your Profile

If after applying to roles you start getting contacted by potential employers, great! If not, then you may want to work on crafting your resume/profile. It's hard to say exactly why some resumes climb to the top while other do not but based on the feedback I received here are a few tips:

**Be Specific** - If you optimized a process and made it faster don't just say that, say *how* much faster, bonus points if you can tie it to business value. "I optimized a critical business process and reduced computation speeds by a factor of 10x, resulting in $10,000 a month in savings to the enterprise." sounds a lot more impressive than "I made processes faster".

**Use Keywords Strategically** - For better or worse, resumes are often screened by an automated system before they are put in front of a recruiter and these systems often look for keywords. You don't want your resume to be a buzzword salad, but pick a handful of key technologies/frameworks you are familiar with and be sure list them on your resume.

**Differentiate Yourself** - Think about what unique skills/capabilities you bring to the table and how you can highlight them in your resume. For myself, I view one of my differentiators as my ability to write and breakdown technical topics. In order to demonstrate this, I selected a handful of my blog posts and linked them directly on my resume with a brief description of each. I received feedback from multiple employers that this was something that made my resume stand out (some of them had also read my blog and we were able to talk about the posts in my interviews!).

## What is a Machine Learning Engineer Anyway?

For my job search, I was targeting a *Machine Learning Engineer* job title. However, [Machine Learning Engineer](2024-04-27-ml-engineer.md) can mean different things to different people and the role can have a different focus depending on the requirements of the job. Some roles were much closer to a pure Data Scientist position, while others were more a DevOps engineer. I would try to determine the focus of the role based on the job description but often times couldn't really tell until I was able to speak to someone at the company about the responsibilities of the role. If you find that the focus of the role is not what you are looking for, be upfront about it. You don't want to waste the time of the interviewer or yourself if there isn't alignment, they will appreciate your candor and it may open up doors with that employer in the future if they do eventually open a role that aligns more with your interests.

## Interviewing

If you made it to the stage of interviewing, congratulations! Your effort on building your profile has paid off! My main piece of advice at this stage is to be authentic and to be *fun*. Individuals at the end of the day want to hire people A: They think can do the job and B: They would enjoy working with. A lot of people when prepping for interviews really focus on the former but in doing so try to warp themselves and their personalities to fit an artificial persona they think matches the job description. I'm not saying you shouldn't try to emphasize your past experience that best aligns with the job (you should absolutely do that), don't do it in a way that feels fake or contrived, experienced interviews can see right through that. Instead, try to let your own self shine through in ways that align with the requirements of the job, but still demonstrate what is unique and personable about you. The final high-level piece of advice I'd give is don't be afraid to admit you don't know something, many interviewers will appreciate you saying something like "I'm not very familiar with this topic, but if I were to try to reason through it on the spot I would do X." rather than you just trying to "fake" your way to an answer. It goes back to the second point, who would you rather work with? Someone who can never admit they don't know and will hide that from you or someone who isn't afraid to admit they don't have the answer to a problem and will ask for help?

With the high level out of the way I wanted to discuss some of the different types of interviews I encountered and how I prepared for each of them. Broadly speaking, interviews could be in one of two categories: Technical and Non-Technical.

## Technical Interviews

The first style of interview you typically will encounter is some form of a technical interview. These interviews emphasize your technical "know-how" and "hard" skills. They usually involve solving some kind of technical problem during the interview. The main types of interviews of this type I encountered included:

### Leetcode

While there [has recently been controversy related to AI-cheating](https://techstartups.com/2025/03/27/this-21-year-old-built-an-ai-to-cheat-leetcode-tech-interviews-landed-faang-offers-then-got-kicked-out-of-columbia/) on this style of interview, it is still prevalent and something you should expect to encounter. In order to prep for this style of interview you can go through problem sets like [NeetCode 150](https://neetcode.io/practice?tab=neetcode150) to get familiar with types of problems asked. I would particularly focus on the topics of "Arrays & Hashing", "Two Pointers", and "Sliding Window" as these were the most common types of questions I was asked.

### SQL Leetcode

A slight variation of the Leetcode style interview is a SQL coding interview, the premise is the same but instead of using a programming language like Python you instead use SQL. This style of interview wasn't as common but to prep for it you can use resources such as [DataLemur](https://datalemur.com/).

### Numpy Optimization

A more common variant of the Leetcode interview I encountered was a Numpy optimization task. This was usually presented as here's a task (usually involving computing some aggregate statistics on a dataset), write the code to compute the output first using plain old Python for loops (sometimes this code was already provided), then optimize the computation using Numpy. For this I referenced [Chapter 4](https://wesmckinney.com/book/numpy-basics) of the excellent free book "Python for Data Analysis" by Wes McKinney (the whole book is a good read if you want to brush up on Pandas as well).

### Notebook Critique

This was actually one of my favorite styles of technical interview. The premise was given as "Here's a notebook one of our data scientists wrote, how would you improve it and productionize the code within it?". I really liked this type of interview because I think it well represented an actual task one would do on the job (Interviewers take note!). In order to prep for this style of interview I found [Kaggle](https://www.kaggle.com/) to be an excellent resource. Enter a competition, take a look at the other submissions, and try to improve their code. 

### Data Science Fundamentals

This type of technical was more prevalent for roles that emphasized the Data Science aspect of the role. They typically involved a more academic survey of Data Science fundamentals. In order to prep the book [Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow, 3rd Edition](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/) by Aurélien Géron remains my go-to. Also the Transformer Architecture is very much in vouge right now, be prepared to answer questions about what it is and how it works, [this course](https://huggingface.co/learn/llm-course/chapter1/4) from Hugging Face is a good reference.



## Delve Data
* Many challenges exist when training and deploying ML models
* By leveraging scikit-learn column transformers and pipelines we can greatly reduce the amount of feature engineering translation logic that needs to be done
* MLFlow provides a convient framework for both tracking model experimentation and deploying model artifacts as APIs