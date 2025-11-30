---
date: 2025-11-21
categories: 
    - Data Science
tags: 
    - Opinion
---

# Delve 18: Challenges of AI in Industry

![Banner](../assets/images/banners/delve18.png)

> "The first rule of any technology used in a business is that automation applied to an efficient operation will magnify the efficiency. The second is that automation applied to an inefficient operation will magnify the inefficiency." - Bill Gates

## A Challenge

"What are the biggest challenges you've faced when integrating AI into your work?"

Greetings data delvers! I had the opportunity to serve on a multi-disciplinary panel recently where I was asked that very question. At the time, my answer focused on immediate challenges with the data and access to tooling and while those are legitimate concerns, the question has stuck with me for the past few weeks as requiring a deeper answer. As I've been thinking more about it, I've developed a more nuanced view which I'd like to capture here. Hopefully, it may be of use if you are looking to adopt more AI into your workflows!

<!-- more -->

When AI first emerged into the cultural zeitgeist with the release of ChatGPT a few years ago, I distinctly remember many people heralding it as end of software engineering, that programmers would become "prompt engineers", and that we should stop learning to code because that would be obsolete, yet here we are a few years later, still writing code. Now, it would be naive to state that AI has not transformed software engineering, it absolutely has, but it has not replaced it. It is this relationship of augmentation rather than automation that I think perfectly encapsulates the limits of AI today. There is an often quoted statistic that 80% of AI projects fail, why then do we see continued investment in it? What challenges are enterprising facing that are causing them to fail? Do individuals have anything to learn from these challenges when implementing AI in their own work? What can I do to increase the odds of my project being more successful? These are the questions I'd like to wrangle with today.

## The Promise of AI

With the inherent high failure rate of AI projects, why do enterprises continue to pursue them? Would those dollars be better spent somewhere else? In many cases: yes. I think this speaks to a disconnect between the marketing and hype of AI and the problems it is actually good at solving. Marketing would have you believe that AI is a silver bullet that can solve all conceivable problems when in reality there is only a narrow set of tasks it really excels at completing. Make no mistake, AI as it exists today is just a more sophisticated form of auto-complete. Given the preceding words (tokens) in a string, it predicts the next most likely token in the sequence. That's it, it has no more *understanding* of the content it is producing than the some of the first chat bots created in the 1960's. It simply is better at simulating realistic responses.

This next most likely token flow also explains why AI systems *hallucinate*. When an AI hallucinates it has not inherently produced an "incorrect" output, it produced the next most likely token in the sequence, which is what it is designed to do. The issue is that simply predicting next most likely token in the sequence does not convey any understanding about the *world*. This is actually the focus of a different line of AI model research championed by the former Cheif of AI at Meta, Yann LeCun known as *World Models* which may prove to be more useful than the *Large Language Models* we use today. However, all of the LLMs in use today suffer from this drawback.

Given these drawbacks, where enterprises often fail to realize value from AI is they task it with solving problems where the potential for hallucination is too great a risk or the problem could by solved with a much simpler approach. I have seen misinformed executives mandate that teams must us AI in "everything" however this perspective is fundamentally flawed as AI cannot, and will not be able to solve everything. It also doesn't invalidate decades of other approaches, it is simply another tool in the toolbox. For example, if you have a dataset where you'd like to recognize phone numbers within it you *could* prompt an LLM to solve this problem and it most likely would, though it would be:

* Expensive to operate
* Still prone to the occasional hallucination

Or you could simply write a [regular expression](https://en.wikipedia.org/wiki/Regular_expression) which captures all common phone number formats. The regular expression approach has the benefit of there is no risk of hallucination either!

It can also go the other direction as well. I sometime see individuals requesting "AI Magic" essentially replacing an entire high-skilled professional's job. However, there is no way to break the problem down into a series of steps that an AI could reasonably solve, as they require many years of experience to understand. For example, you probably don't want your physician to be replaced by an AI, given it's propensity to hallucinate, though a human physician could see benefit consulting one, because they have the expertise to determine when an AI's outputs could be trusted.

Thus, the first challenge then of leveraging AI in your work is to determine if you *should* use AI to solve it, given the inherent limitations of AI today, and if you have decided to use AI the next step is to figure out if you *can*.

## Organizational Challenge 1: Data

Often, the first barrier to an organization leveraging AI is the data quality of the organization itself. This is not a new challenge, [Garbage In, Garbage Out](https://en.wikipedia.org/wiki/Garbage_in,_garbage_out) has been in the computer science vernacular since at least the 1950s, but AI especially depends on high quality data to be successful and it not in it of itself a substitute for poor data quality within an organization. I have observed executives essentially trying to "short-cut" to AI without putting in any of the foundational effort needed to support it. What is needed to support AI is the same good data quality as was needed for ML & statistics before it, ignoring the effort to get it right will result in projects the under deliver or ultimately fail.

In order to overcome this challenge organizations should establish *Data Governance* by defining clear roles and processes for data ownership (who can modifying this data and when) as well as implementing strict data validation rules as far upstream as possible to ensure data consistency within the organization as a whole rather than within fragments. 

The second related challenge when it comes to organizational data is the architecture around it. My former colleague [Yafet Tamene](https://www.linkedin.com/posts/yafet-t_ai-engineering-technicalleadership-activity-7373326534171992064-v1mI?utm_source=share&utm_medium=member_desktop&rcm=ACoAAA9YmdgBd6NlJg9MMvIqR7iUMylWOMZd4O0), Principal MLE at Microsoft put it well when he stated:

> Traditional applications can be built in silos. Conventional software can function effectively within departmental boundaries, operating on isolated data sets and delivering value independently. AI applications cannot.

An effect of [Conway's Law](https://en.wikipedia.org/wiki/Conway%27s_law), organizations often build architectures that mirror the hierarchical and siloed structure of how the people within them are organized. This tends to work fairly well for static, independent applications. However, in order to truly gain value from AI, it must have context of the data across the entire enterprise, not just within a single operating group. If I want to understand how a product will perform, I may need context of how it is operating, our current sales, and customer feedback. If each of these sources of data is stored in separate isolated systems I can't hope to build a AI that can accurately forecast demand.

To address this organizations must invest in building a unified data ecosystem that makes data readily accessible and easily joinable across the enterprise. (More to come on this in future delves!)

## Organizational Challenge 2: The Proof on Concept Trap

Another common challenge organizations face is building endless proof of concepts. AI often performs well when utilized in a small scale but fails when it is attempted to be scaled to "real-world" use cases. This can happen for a multitude of reasons, there may not be the infrastructure or MLOps practices in place to actually deploy the model, certain important real-world edge cases may have been overlooked during the PoC, or even if the solution is successfully deployed, it may be difficult to measure the return on investment of the approach.

To address this organizations should start small with well defined use cases where the data is clean and readily available and the desired outcome is clear and objectively measurable.

## Organizational Challenge 3: Ethics

Perhaps one of the most important challenges an organization may face when it comes to the use of AI is considering the ethical implications of utilizing its output. Answering questions such as "Was there any bias in the data that was used to build this model?" or "Do we have safeguards in place to prevent undesired outcomes in the case of hallucination?" are critical to answer before deploying an AI solution. This is further compounded by the "black box" nature of AI. Unlike the ML approaches that came before, which could provide some level of explainability in the forms of weights and decision boundaries, AI by its very nature is *unexplainable*, it should only be used in applications where there is not a legal or moral requirement for providing an explanation for why a decision was made.

Organizations should take care when deploying AI solutions to make sure the consider the ethical and legal considerations of doing so before impacting their customers.

