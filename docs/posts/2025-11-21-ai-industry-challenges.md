---
date: 2025-11-21
categories: 
    - Data Science
tags: 
    - Opinion
---

# Delve 18: The Challenges of AI in Industry

![Banner](../assets/images/banners/delve18.png)

> "The first rule of any technology used in a business is that automation applied to an efficient operation will magnify the efficiency. The second is that automation applied to an inefficient operation will magnify the inefficiency." - Bill Gates

## A Challenge

"What are the biggest challenges you've faced when integrating AI into your work?"

Greetings data delvers! I had the opportunity to serve on a multi-disciplinary panel recently where I was asked that very question. At the time, my answer focused on immediate challenges with data quality and access to tooling. While those are legitimate concerns, the question has stuck with me for the past few weeks as requiring a deeper answer. As I've been thinking more about it, I've developed a more nuanced view which I'd like to capture here. Hopefully, it may be of use if you are looking to adopt more AI into your workflows!

<!-- more -->

When AI first emerged into the cultural zeitgeist with the release of ChatGPT a few years ago, I distinctly remember many people heralding it as the end of software engineering, that programmers would become "prompt engineers", and that we should stop learning to code because that would be obsolete, yet here we are a few years later, still writing code. Now, it would be naive to state that AI has not transformed software engineering, it absolutely has, but it has not replaced it. It is this relationship of augmentation rather than automation that I think perfectly encapsulates the limits of AI today. There is an often quoted statistic that 80% of AI projects fail, why then do we see continued investment in it? What challenges are enterprising facing that are causing them to fail? Do individuals have anything to learn from these challenges when implementing AI in their own work? What can I do to increase the odds of my project being more successful? These are the questions I'd like to wrangle with today.

## The Promise of AI

With the inherent high failure rate of AI projects, why do enterprises continue to pursue them? Would those dollars be better spent somewhere else? In many cases: yes. I think this speaks to a disconnect between the marketing and hype of AI and the problems it is actually good at solving. Marketing would have you believe that AI is a silver bullet that can solve all conceivable problems when in reality there is only a narrow set of tasks it really excels at completing. Make no mistake, AI as it exists today is just a more sophisticated form of auto-complete. Given the preceding words (tokens) in a string, it predicts the next most likely token in the sequence. That's it—it has no more *understanding* of the content it is producing than some of the first chatbots created in the 1960s. It simply is better at simulating realistic responses.

This next most likely token flow also explains why AI systems *hallucinate*. When an AI hallucinates, it has not inherently produced an "incorrect" output; it produced the next most likely token in the sequence, which is what it is designed to do. The issue is that simply predicting next most likely token in the sequence does not convey any understanding about the *world*. This is actually the focus of a different line of AI model research championed by Yann LeCun, the former Chief of AI at Meta, known as *World Models* which may prove to be more useful than the *Large Language Models* we use today. However, all of the LLMs in use today suffer from this drawback.

Given these drawbacks, enterprises often fail to realize value from AI when they task it with solving problems where hallucination poses too great a risk or when the problem could be solved with a much simpler approach. I have seen misinformed executives mandate that teams must use AI in "everything". However, this perspective is fundamentally flawed as AI cannot, in its current form, solve everything. It also doesn't invalidate decades of other approaches, it is simply another tool in the toolbox. For example, if you have a dataset where you'd like to recognize phone numbers within it you *could* prompt an LLM to solve this problem and it most likely would, though it would be:

* Expensive to operate
* Still prone to the occasional hallucination

Or you could simply write a [regular expression](https://en.wikipedia.org/wiki/Regular_expression) that captures all common phone number formats. The regular expression approach has the added benefit of eliminating the risk of hallucination!

It can also go the other direction as well. I sometimes see individuals requesting "AI Magic" to essentially replace an entire high-skilled professional's job. However, there is no way to break such problems down into a series of steps that an AI could reasonably solve, as they require many years of experience to understand. For example, you probably don't want your physician to be replaced by an AI, given its propensity to hallucinate, though a human physician could see benefit consulting one, because they have the expertise to determine when an AI's outputs could be trusted.

Thus, the first challenge of leveraging AI in your work is to determine if you *should* use AI to solve it, given the inherent limitations of AI today. If you have decided to use AI, the next step is to figure out if you *can*.

## Organizational Challenge 1: Data

Often, the first barrier to an organization leveraging AI is the data quality of the organization itself. This is not a new challenge—[Garbage In, Garbage Out](https://en.wikipedia.org/wiki/Garbage_in,_garbage_out) has been in the computer science vernacular since at least the 1950s. However, AI especially depends on high quality data to be successful, and it is not in itself a substitute for poor data quality within an organization. I have observed executives essentially trying to "short-cut" to AI without putting in any of the foundational effort needed to support it. What is needed to support AI is the same good data quality as was needed for ML & statistics before it, ignoring the effort to get it right will result in projects that under deliver or ultimately fail.

To overcome this challenge, organizations should establish *Data Governance* by defining clear roles and processes for data ownership (who can modify data and when), as well as implementing strict data validation rules as far upstream as possible to ensure data consistency across the organization rather than in isolated fragments. 

The second challenge related to organizational data is the architecture surrounding it. My former colleague [Yafet Tamene](https://www.linkedin.com/posts/yafet-t_ai-engineering-technicalleadership-activity-7373326534171992064-v1mI?utm_source=share&utm_medium=member_desktop&rcm=ACoAAA9YmdgBd6NlJg9MMvIqR7iUMylWOMZd4O0), now a Principal MLE at Microsoft put it well when he stated:

> Traditional applications can be built in silos. Conventional software can function effectively within departmental boundaries, operating on isolated data sets and delivering value independently. AI applications cannot.

As an effect of [Conway's Law](https://en.wikipedia.org/wiki/Conway%27s_law), organizations often build architectures that mirror the hierarchical and siloed structure of how their people are organized. This tends to work fairly well for static, independent applications. However, in order to truly gain value from AI, it must have context of the data across the entire enterprise, not just within a single operating group. If I want to understand how a product will perform, I may need context on how it is operating, current sales metrics, and customer feedback. If each of these sources of data is stored in separate isolated systems I can't hope to build a AI that can accurately forecast demand.

To address this, organizations must invest in building a unified data ecosystem that makes data readily accessible and easily joinable across the enterprise. (More to come on this in future Delves!)

## Organizational Challenge 2: The Proof on Concept Trap

Another common challenge organizations face is building endless proof-of-concept projects. AI often performs well at small scale but fails when attempted to scale to "real-world" use cases. This can happen for many reasons: there may not be the infrastructure or MLOps practices in place to deploy the model, important edge cases may have been overlooked during the PoC, or measuring the return on investment may prove difficult.

To address this, organizations should start small with well-defined use cases where the data is clean and readily available, and the desired outcome is clear and objectively measurable.

## Organizational Challenge 3: Ethics

Perhaps one of the most important challenges an organization may face is considering the ethical implications of using AI. Answering questions such as "Was there any bias in the data that was used to build this model?" or "Do we have safeguards in place to prevent undesired outcomes in the case of hallucination?" are critical to answer before deploying an AI solution. This is further compounded by the "black box" nature of AI. Unlike prior ML approaches that could provide some level of explainability through weights and decision boundaries, AI is inherently *unexplainable*. It should only be used in applications where there is no legal or moral requirement to explain why a decision was made.

Organizations should take care when deploying AI solutions to ensure they consider the ethical and legal implications before impacting their customers.

## Individual Challenge 1: Verification Tax

In addition to the organizational challenges above, individuals can also face challenges when leveraging AI. Perhaps the largest and most time-consuming is verification. An AI might generate a full project in minutes, but verifying it works correctly could take you hours. In their article [Being "Confidently Wrong" is holding AI back](https://promptql.io/blog/being-confidently-wrong-is-holding-ai-back), PromptQL co-founder Tanmai Gopal coins this the "Verification Tax". This friction is a direct result of shifting from being a *creator* to an *editor*. Editing often requires more cognitive effort because it demands a higher level of vigilance in spotting subtle errors in AI outputs.

To combat this, individuals should break larger tasks into smaller subtasks before handing them to an AI. This makes it easier to verify the AI's output is correct before moving to the next task.

## Individual Challenge 2: Prompt Fatigue

Another challenge individuals face is endlessly adjusting prompts to get desired outputs. This is particularly challenging when prompts are vague, requiring multiple iterations to get the desired output making it feel faster to just do the work yourself. This also occurs when the AI lacks necessary context, such as knowledge of previous attempts at creating a solution.

To address this challenge, you should develop a collection of templates for your most useful prompts. Start each problem with one of these templates rather than a blank prompt and iterate from there. In addition, provide *context* and *structure* to your prompts by giving the AI a persona, goal, and constraints. For example:

> Act as a data analyst. Analyze the following spreadsheet and produce three key takeaways for an executive audience, limiting your answer to 150 words.

This provide the AI a framework to produce the type of output you are looking for rather than a free-form response.

## Individual Challenge 3: Skill Atrophy

Finally, a legitimate concern for many individuals leveraging AI is becoming over-reliant on it. The goal is to treat AI as a *collaborative partner* rather than a shortcut, ensuring you remain "in-the-loop" in the development cycle.

Some strategies you could employ include:

* Always produce the initial draft of work yourself and then ask AI to optimize or refine it. This forces you to attempt a solution yourself before relying on AI.
* Reverse engineer the output, particularly when learning new skills. Instead of using AI output verbatim, ask the AI *why* it produced a specific output and cross-reference it with other non-AI sources to gain deeper understanding.
* Delegate tasks to AI, not skills. Use AI for solving repetitive, low-value tasks (the ones it is good at!) but do the complex, high-value tasks yourself that require the skills of your career.

Ultimately, it is up to you to determine where your boundary with AI is, but remember you are responsible for how the output is utilized, so take steps to use it responsibly.

## Responsible Innovation

AI has truly accelerated our ability to explore, comprehend, and produce vast amounts of data. However, if one is not aware of the limitations and challenges that come with leveraging AI, it will continue to underdeliver on the value it promises. Organizations should focus on strong data governance above all else and shouldn't invest in the latest flashy AI tools until their data house is in order. Individuals should focus on "human-in-the-loop" workflows and treat AI as a collaborator, not a replacement.

With these challenges addressed you are ready to innovate responsibly with AI!

## Delve Data

* Leveraging AI effectively comes with several challenges both to organizations and individuals
* Organizations should focus on effective data governance before attempting to leverage AI
* Individuals should treat AI as a collaborative partner and keep themselves "in-the-loop" in the development cycle