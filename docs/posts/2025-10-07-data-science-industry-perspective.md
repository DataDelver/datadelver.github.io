---
date: 2025-10-07
categories: 
    - Data Science
tags: 
    - Opinion
---

# Delve 17: Data Science, An Industry Perspective

![Banner](../assets/images/banners/delve17.png)

> "Academia is about discovering truth. Industry is about delivering value." - Cassie Kozyrkov

## Oops

Hello data delvers! I recently had the opportunity to give a guest lecture at my Alma Mater to students about the differences between practicing data science in academia vs industry. It was a lively discussion and I wanted to capture some of my thoughts as I think they could be particularly useful to individuals transitioning from an academic setting to an industrial one. The objectives, methods of working, and ultimately what determines your success are vastly different in academia compared to industry. To illustrate this here is an example of a conversation I had early in my career:

<!-- more -->

🧑‍🎓New Grad Chase: "Look at this cool model I built! I was able to improve my F1 score by 0.1!"

🙍‍♂️Business Stakeholder: "Sounds interesting! What's the impact to our OKRs by making this improvement??"

🧑‍🎓New Grad Chase: "Um, I don't know if there is one..."

🤦‍♂️Business Stakeholder: "..."

## A Shift

The above conversation encapsulates the biggest shift I found when transitioning from academia to industry: *Business Value*. When I was a grad student doing research, my focus was on advancing science, discovering new knowledge, and working on novel problems. However, when working in industry, the ultimate goal is unlocking business value, whether that requires machine learning *or not*. There's an adage that often comes up when talking to other ML engineers that goes something like "The best model in academia is the most accurate. The best model in industry is the one that ships." which I have found to be very true. I have seen new hire data scientists trying to maximize the predictive performance of their models, adding more and more features, without considering that for each new data source they leverage, they are adding months to the delivery time of their models. I have also seen scientists fall into the trap of maximizing a *theoretical* performance metric without correlating it to a real-world outcome.

These types of mistakes often go unnoticed when times are good, however, if your enterprise is honed-in on discovering value, it will quickly become apparent that you are delivering none: don't be in that position.

## Or Not

You may have noticed that I mentioned that being a data scientist in industry means delivering business value whether the solution requires machine learning or not. Non-technical stakeholders are often quick to jump to whatever the latest trends be, whether that be neural networks, automl, or generative AI. It is your responsibility as a practitioner to determine what is the *simplest* solution that achieves the desired *business outcome*. Another example:

Early in my career I was asked to develop a method for detecting anomolous data points. "I know how to do that!" I thought to myself as I broke out my isolation forrest models and autoencoders. However, after spending some time tinkering with modeling I decided to plot the distribution of the data points I was working with (something I should have done to begin with), to my surprise the key feature in the dataset had a normal distribution, detecting anomalies was a simple as determining if the key feature was more than two standard deviations away from the mean. 

This also had the added benefit of being much easier to explain to my stakeholders that had never even heard of isolation forrest before, let alone understood how it worked. Ironically, this same time of situation has popped up multiple times in my career. The takeaway here is simple, explainable approaches, that meet the business objective are always better than more complex ones, **even if they perform worse**.  If you need to slice a stick of butter, you could use a chainsaw, but why would you when a butter knife will work just as well?

With all the latest hype around GenAI and LLMs I have observed a trend of business leaders mandating that AI should be used in "everything", even in situations where it doesn't make sense. GenAI is definitely a valuable tool, but it is not a panacea that invalidates all other approaches, don't jump to using it to solve problems when a simple logistic regression is good enough.

This is a hard lesson to accept at times, there's an inherent draw to using the newest flashy technique, however your future self with thank you when something breaks and you need to understand why, or you need to get a key stake holder to trust your approach.

## Fast over Flashy

Industry often follows tight delivery times, with quick iterations and a focus on delivering minimum viable products. This is in sharp contrast to the academic process, taking months or even years to validate with rigor. Once more, in academia you are often working with the most cutting-edge algorithms and techniques, whereas in industry you often fall back to tried-and-true methods. That isn't to say you can't try something new and flashy but my recommendation is to always try a simple technique first before jumping to the latest and greatest approach, this has two main benefits:

1. The simple approach is usually faster meaning you can get to an MVP sooner and start realizing value on a shorter timeline
2. The simple approach now becomes your *baseline* to compare any further developments against

It is that second benefit that I find can be particularly beneficial for your own career. If you can go to your stakeholders and say "I solved *X* and increased our metrics by *Y%* over the baseline", it is a much more compelling reference point when your annual review comes up than just "I solved *X*". Do your future self a favor and create a baseline!

## The Trouble with Data

The other big difference I've experienced between academia and industry is the dramatic difference in the type of data that is leveraged. In academia you often find yourself leveraging *benchmark* datasets that are pristine and clean so the focus can be on the modeling techniques themselves. However, the world of industry is *messy*, data is missing, misleading, or flat out wrong. Much more time and effort must be spent to validate that the data you have is even suitable to build a model with (hint: often it is not).

In a similar vein, the data in industry is *dynamic*, customer preferences change over time, new products are released, the market ebbs and flows. Due to this fluid nature, the techniques you employ must be much more tolerant to change that if you were simply optimizing on a static reference dataset.

## The End Result

Finally, the work output is very different between these two worlds. As an academic I was expected to produce papers, present research, and develop prototypes. However, as a practitioner in industry, I produce products, APIs, and systems. These systems are not frozen artifacts either, they must change and evolve with new requirements, shifting customer trends, and the emergence of new technologies. I find this constant change exhilarating, but by its very nature, it forces a different prioritization of time. Ultimately I academia I was successful when I prioritized rigorous validation and research, but in industry I am successful when I can move fast, deliver positive impacts to the business, and do it in a way that is sustainable over time. 

## Closing Thoughts

Academia and industry are both areas where Data Science thrives. However, the focus, and end result, are vastly different. Hopefully if you are considering making the switch to industry, these thoughts are helpful! If you want to see more of *how* to build and launch data science products in an enterprise setting, stick around, we have a lot more delves to do. 🙂

## Delve Data

* The focus of academia and industry in Data Science is very different
* Academia emphasizes exploration and rigor; industry prioritizes speed and impact
* Prefer *simple*, *explainable* approaches in industry
* Real-world data is often very messy
* The goal is to build sustainable products that deliver **business value**