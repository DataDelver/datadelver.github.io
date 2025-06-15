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

**Differentiate Yourself** - Think about what unique skills/capabilities you bring to the table and how you can highlight them in your resume. For myself, I view one of my differentiators as my ability to write and breakdown technical topics. In order to demonstrate this, I selected a handful of my blog posts and linked them directly on my resume with a brief description of each. I received feedback from multiple potential employers that this was something that made my resume stand out (some of them had also read my blog and we were able to talk about the posts in my interviews!).

## What is a Machine Learning Engineer Anyway?

For my job search, I was targeting a *Machine Learning Engineer* job title. However, [Machine Learning Engineer](2024-04-27-ml-engineer.md) can mean different things to different people and the role can have a different focus depending on the requirements of the job. Some roles were much closer to a pure Data Scientist position, while others were more a DevOps engineer. I would try to determine the focus of the role based on the job description but often times couldn't really tell until I was able to speak to someone at the company about the responsibilities of the role. If you find that the focus of the role is not what you are looking for, be upfront about it. You don't want to waste the time of the interviewer or yourself if there isn't alignment, they will appreciate your candor and it may open up doors with that employer in the future if they do eventually open a role that aligns more with your interests.

## Interviewing

If you made it to the stage of interviewing, congratulations! Your effort on building your profile has paid off! My main piece of advice at this stage is to be authentic and to be *fun*. Individuals at the end of the day want to hire people A: They think can do the job and B: They would enjoy working with. A lot of people when prepping for interviews really focus on the former but in doing so try to warp themselves and their personalities to fit an artificial persona they think matches the job description. I'm not saying you shouldn't try to emphasize your past experience that best aligns with the job (you should absolutely do that), just don't do it in a way that feels fake or contrived, experienced interviews can see right through that. Instead, try to let your own self shine through in ways that align with the requirements of the job, but still demonstrate what is unique and personable about you. The final high-level piece of advice I'd give is don't be afraid to admit you don't know something, many interviewers will appreciate you saying something like "I'm not very familiar with this topic, but if I were to try to reason through it on the spot I would do X." rather than you just trying to "fake" your way to an answer. It goes back to the second point, who would you rather work with? Someone who can never admit they don't know something and will hide that from you or someone who isn't afraid to admit they don't have the answer to a problem and will ask for help?

With the high level out of the way I wanted to discuss some of the different types of interviews I encountered and how I prepared for each of them. Broadly speaking, interviews could be in one of two categories: Technical and Non-Technical.

## Technical Interviews

The first style of interview you typically will encounter is some form of a technical interview. These interviews emphasize your technical "know-how" and "hard" skills. They usually involve solving some kind of technical problem during the interview. The main categories of interviews of this type I encountered included:

### Leetcode

While there [has recently been controversy related to AI-cheating](https://techstartups.com/2025/03/27/this-21-year-old-built-an-ai-to-cheat-leetcode-tech-interviews-landed-faang-offers-then-got-kicked-out-of-columbia/) on this style of interview, it is still prevalent and something you should expect to encounter. In order to prep for this style of interview you can go through problem sets like [NeetCode 150](https://neetcode.io/practice?tab=neetcode150) to get familiar with types of problems asked. I would particularly focus on the topics of "Arrays & Hashing", "Two Pointers", and "Sliding Window" as these were the most common types of questions I was asked.

### SQL Leetcode

A slight variation of the Leetcode style interview is a SQL coding interview, the premise is the same but instead of using a programming language like Python you instead use SQL. This style of interview wasn't as common but to prep for it you can use resources such as [DataLemur](https://datalemur.com/).

### NumPy Optimization

A more common variant of the Leetcode interview I encountered was a NumPy optimization task. This was usually presented as here's a task (usually involving computing some aggregate statistics on a dataset), write the code to compute the output first using plain old Python for loops (sometimes this code was already provided), then optimize the computation using NumPy. For this I referenced [Chapter 4](https://wesmckinney.com/book/numpy-basics) of the excellent free book "Python for Data Analysis" by Wes McKinney (the whole book is a good read if you want to brush up on Pandas as well).

### Notebook Critique

This was actually one of my favorite styles of technical interview. The premise was given as "Here's a notebook one of our data scientists wrote, how would you improve and productionize the code within it?". I really liked this type of interview because I think it well represented an actual task one would do on the job (Interviewers take note!). In order to prep for this style of interview I found [Kaggle](https://www.kaggle.com/) to be an excellent resource. Enter a competition, take a look at the other submissions, and try to improve their code. 

### Data Science Fundamentals

This type of technical was more prevalent for roles that emphasized the Data Science aspect of the role. They typically involved a more academic survey of Data Science fundamentals. In order to prep the book [Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow, 3rd Edition](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/) by Aurélien Géron remains my go-to. Also, the Transformer Architecture is very much in vouge right now, be prepared to answer questions about what it is and how it works, [this course](https://huggingface.co/learn/llm-course/chapter1/4) from Hugging Face is a good reference.

### System Design

Rounding out the technical interviews is system design. Typically you are presented with a vague series of requirements which you must work to refine and then design a system around. [This guide](https://github.com/alirezadir/Machine-Learning-Interviews/blob/main/src/MLSD/ml-system-design.md) is a good reference for these types of interviews (the repo it is in also has useful materials for other types of interviews as well!).

## Non-Technical Interviews

If you make it through the initial round of technical interviews you will also typically be asked to do non-technical interviews as well. In contrast to technical interviews, these interviews emphasize how you collaborate with others and your "soft" skills. The subject matter can be diverse but usually focuses on either past experiences "Tell me a time when..." or how to collaborate with others solving a business problem. The main categories of interviews of this type I encountered included:

### Behavioral/Hiring Manager 

Typically conducted by the Hiring Manger, usually focused on your past experiences. It's good to have a set of stories prepared for different types of situations such as learning something new, navigating a conflict with a co-worker, collaborating with business partners, etc. The stories don't always have to be completely positive either, having examples of "Looking back I would have done this differently because of X" can be useful to demonstrate your own self-introspection and growth. The [STAR Method](https://interviewkickstart.com/blogs/career-advice/situational-scenario-based-interview-questions-answers) can be particularly useful here.

### Product/Past Project

This type of interview can be presented in a few different ways, it sometimes takes the form of being asked to give an overview of a past project that you've worked on, other times you are being asked to develop a new product from scratch. What ties these together is the emphasis on *measurable* business value. For your past project be prepared to discuss what some of the Key Performance Indicators (KPIs) are, how you measured the impact of your project against these KPIs, and what the outcome was (hopefully positive!). For designing a new product the ask is the same but instead of having real results you are theorizing what hypothetical results could be. In this scenario be prepared to discuss how you would adjust if a certain KPI shifted, and what some of the tradeoffs in your approach could be.

### Stakeholder

The final type of interview I encountered in this category was a Stakeholder interview. This was typically with a senior leader at the company and could be thought of as combination of the previous two types of interviews with typically more time left for you to ask questions at the end. Ask questions! This is your opportunity to get a sense of the strategic direction of the business and what the thought leadership at the top is like.

## Ask Questions

Did I mention ask questions? An important aspect of interviewing is that you are interviewing your potential employer just as much as they are interviewing you. Most interviews leave time at the end for questions, use it! I usually like to ask similar questions to all the people I was interviewing with to get different perspectives on the same topic within the company such as "What is the biggest challenge you see someone in this role tackling?" or "What are you most excited about?". You'll (hopefully) be spending a decent amount of time with these people, you want to make sure they are people you want to spend time with! 

## The Offer

If your interviewing is successful you will have one, or possibly multiple, offers to consider. When considering an offer there are many things to consider such as:

* Compensation
* Work/Life Balance
* Company Culture
* Nature of the Work

How these stack rank is up to you, the one piece of advice I'd give at this stage is to be respectful and honest. Both you and your potential employer have probably put in a considerable amount of time to get to this stage, they are invested in you by this point, you don't want to give them a bad impression and ruin the opportunity. For example, do not try to counter on one of the above points if it will not make a difference in you accepting the offer or not. If you decide not to accept an offer, do not lead the potential employer on. If you do decline, be very gracious that you were given the opportunity, even though you are declining now, you may find that you may cross paths with them again in the future.

## Closing Thoughts

The journey to find a new job can be both exciting and stressful. My final words of advice are do not rush. Allocate 3-6 months for your search, you don't want to necessarily accept the first opportunity that comes your way if it doesn't check all of your boxes but also don't go searching for the "perfect" role either, there are always tradeoffs. Finally, don't get discouraged! If you are finding you are not getting responses to your applications take a step back, work on your profile and try again. If you find that you aren't passing a particular type of interview, identify your weaknesses and work on them. The right opportunity will eventually come. 🙂

## Delve Data
* Searching for a Machine Learning Engineer Role can be both exciting and stressful
* Define what type of role you are looking for, write down a list of the attributes you'd like it to have
* Work on developing a profile that will get you past the resume screens
* Identify and close your gaps on both Technical and Non-Technical Interviews
* Be respectful when negotiating and declining offers
* Don't get discouraged!