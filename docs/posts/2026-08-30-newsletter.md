---
date: 2026-08-30
categories:
  - Meta
tags:
  - Tools
repo: https://github.com/DataDelver/datadelver.github.io
---

# Delve 24: Adding a Newsletter & Other Site Enhancements with AI

![Banner](../assets/images/banners/delve24.webp)

> "asdf" - Unknown

## Acquire Front End

Greetings data delvers! You may have noticed some changes to the site recently. No, I did not suddenly develop front-end skills, however with a local LLM available to me now I have the ability to improve several aspects of the site's UX. This all started with a simple prompt:

!!! claude

    How would you improve this blog: https://www.datadelver.com/ source code is here @Documents/Blog/datadelver.github.io/

!!! Note

    For this task I decided to give [Qwen3.6-27B](https://huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF) a try since it was a more coding oriented question.

<!-- more -->

You can find my complete model launch script below:

??? "Start-Qwen3.6.ps1"

    ```powershell linenums="1"
    <#
    .SYNOPSIS
        Starts a highly optimized llama-server instance for Claude Code using Qwen3.6-27B-MTP.
    .DESCRIPTION
        Optimized for RTX 4090 (24GB VRAM). Utilizes MTP (Multi-Token Prediction) 
        for faster inference.
    #>

    # 1. Port Safety Check
    $PortToCheck = 11434
    $ActivePort = Get-NetTCPConnection -LocalPort $PortToCheck -ErrorAction SilentlyContinue

    if ($ActivePort) {
        Write-Warning "⚠️ Port $PortToCheck is already in use."
        Read-Host "Press Enter to exit..."
        exit
    }

    # 2. Server Parameter Definitions
    $RepoID = "unsloth/Qwen3.6-27B-MTP-GGUF"
    $ModelFile = "Qwen3.6-27B-Q4_K_M.gguf"
    $ModelAlias = "qwen3.6-27b"
    $ContextSize = 65536
    $GPULayers = 99
    $HostAddress = "0.0.0.0"

    # Set the JSON environment variable
    $env:LLAMA_ARG_CHAT_TEMPLATE_KWARGS = '{"preserve_thinking": true}'

    Write-Host "🚀 Launching Local Qwen3.6-27B-MTP Engine..." -ForegroundColor Cyan

    # 3. Execution Block
    llama-server `
        -hf $RepoID `
        -m $ModelFile `
        --alias $ModelAlias `
        --ctx-size $ContextSize `
        -ngl $GPULayers `
        -fa on `
        --cache-type-k q8_0 `
        --cache-type-v q8_0 `
        --jinja `
        --temp 0.2 `
        --top-p 0.95 `
        --spec-type draft-mtp `
        --spec-draft-n-max 3 `
        --host $HostAddress `
        --port $PortToCheck
    ```

This produced the following analysis:

> **Priority Summary**
>
> | Priority  | Item                                   | Effort | Impact                      |
> | --------- | -------------------------------------- | ------ | --------------------------- |
> | 🔴 High   | Optimize banner images (70 MB → ~5 MB) | 30 min | Very High — page load speed |
> | 🔴 High   | Fix typo in about.md                   | 1 min  | Medium                      |
> | 🔴 High   | Fix pyproject.toml description         | 1 min  | Low                         |
> | 🟡 Medium | ML Micro series index + cross-links    | 30 min | High                        |
> | 🟡 Medium | Add reading time                       | 5 min  | Medium                      |
> | 🟡 Medium | CI cache key improvement               | 5 min  | Medium                      |
> | 🟡 Medium | Post template                          | 15 min | Medium                      |
> | 🟢 Low    | Analytics integration                  | 1 hr   | High                        |
> | 🟢 Low    | Newsletter signup                      | 30 min | High                        |
> | 🟢 Low    | JSON-LD structured data                | 1 hr   | Medium                      |
>
> The #1 thing to fix is the banner images. At 70 MB of uncompressed PNGs, every blog post forces readers to download
> 2-4 MB just for the hero banner. Converting to WebP would reduce that to ~300-500 KB per image — a 10x improvement
> with zero visual quality loss. This single change would dramatically improve page load times, especially for mobile
> users.

From there I entered a loop, asking Claude to tackle each issue one by one starting with the highest priority tasks and working down the list. Once all the tasks were completed I asked it to re-evaluate the site and generate more suggestions. This led to several enhancements to the site, many in the form of custom [MkDocs Plugins](https://www.mkdocs.org/dev-guide/plugins/). Here were a few enhancements that stood out to me.

## Anonymous Analytics with Umami

One of the more interesting, but very low-effort enhancements, that Claude suggested was adding site analytics. Prompting for suggestions, it provided several options though I ultimately settled on [Umami](https://umami.is/) for its privacy-first stance, and free tier for hobbyists. Integrating it into the site was a simple [one-line change](https://github.com/DataDelver/datadelver.github.io/pull/38/changes) as MkDocs already has built-in support for an analytics provider.

![Umami](../assets/images/figures/delve24/umami.png)

!!! Note

    This was probably one of my first very clear experiences of LLM-driven search. Instead of relying on a Google search to suggest analytics providers, Claude suggested providers directly in its response, bypassing the Google search altogether.

Having this data will be great to see how people are discovering this site! Importantly, however, all of this data is *anonymous*, unlike some of the other analytics providers out there.

## UX Enhancements

Several UX enhancements were added to the site. Some of the highlights in rapid fire order were:

- Custom Callout Button on the Homepage and dedicated landing page for the [Modern ML Microservices Series](https://www.datadelver.com/series/ml-microservices.html)
- A [Reading Progress Bar](https://github.com/DataDelver/datadelver.github.io/pull/48/changes#diff-e367d91bc273f41e7df5de1babaed6b2878046bdd06fbc4a385674f695bb7a25) at the top of posts
- A [View the Code on GitHub](https://github.com/DataDelver/datadelver.github.io/pull/65) custom call to action plugin
- A [Custom 404 page](https://github.com/DataDelver/datadelver.github.io/pull/46), view it [here](https://www.datadelver.com/notfound)!
- Social button share links, previous/next delve navigation, and related delves at the bottom of all posts!

Many more behind-the-scenes optimizations for page loading time and SEO performance were made as well.

## RSS Plugin

I wanted to add the [MkDocs RSS Plugin](https://guts.github.io/mkdocs-rss-plugin/) to the site to provide an easy way to get notified of a new delve going live. However, when validating the feed generated by the plugin it actually produced several validation errors. Working with Claude I initially developed a [monkey patch](https://github.com/DataDelver/datadelver.github.io/pull/60) script to fix the issue locally, but figured it would be useful to others as well so I had Claude fork the repo and [contribute a fix](https://github.com/Guts/mkdocs-rss-plugin/pull/451) to the upstream plugin!

There were some interesting takeaways from this experience of using an LLM to contribute to open source.

- The maintainer of the plugin wanted me to disclose the [level of AI involvement](https://www.visidata.org/blog/2026/ai/) used to make the contribution (I settled on Level 8). I think using a classification like this will be a good practice for me to carry forward toward future contributions.
- As with all contributions, splitting into smaller PRs with one change each makes them easier to review and merge. LLMs tend to prefer making one massive PR with all the changes bundled, so you need to be especially diligent with AI to make sure it breaks things down into smaller pieces.

Check out the RSS Feed [here](https://www.datadelver.com/feed_rss_created.xml) (and subscribe to it with your RSS reader of choice)!

## Newsletter

Finally, the enhancement I was most excited about is the launch of a newsletter, which sends out an email whenever a new delve is published. In another example of LLM-driven search, I settled on [Buttondown](https://buttondown.com/) as my email distribution platform.

This was a [fairly large PR](https://github.com/DataDelver/datadelver.github.io/pull/67/changes) that consolidated several of the text utilities used in other plugins into a shared module, however Claude did a pretty good job handling it with some prompting.

If you scroll to the bottom of the homepage (or the bottom of any delve page) you'll now see a signup!

![Buttondown](../assets/images/figures/delve24/buttondown.png)

I encourage you to subscribe so you never miss a delve going forward!

## Final Evaluation

After making all of the suggested changes I prompted Claude to re-evaluate the site with the exact same prompt:

!!! claude

    How would you improve this blog: https://www.datadelver.com/ source code is here @Documents/Blog/datadelver.github.io/

> I dug through your repo, the build config, and the live site. Short version: the infrastructure is genuinely solid — per-post social cards, JSON-LD, RSS, Umami, reading progress bar, related posts, series nav, a "Start Here" page, custom 404, and newsletter automation are all things most blogs never get to...

Nice!

## Delve Data

- A local LLM can audit an entire site's codebase and produce a prioritized improvement list with effort and impact estimates
- An iterative loop of prompting the LLM to fix one issue at a time and re-evaluating the site is a good way to make incremental improvements
- LLM-driven search can replace conventional web search, with models suggesting tools like Umami and Buttondown directly from their training data
