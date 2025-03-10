---
date: 2024-06-29
categories: 
    - Software Engineering
tags: 
    - Tools 
    - Fun
---

# Delve 5: The Quest for a Full Screen Raspberry Pi Application

![Banner](../assets/images/banners/delve5.png)

> "All life is problem solving." -Karl Popper

## Full Screen Applications on the Raspberry Pi, Why so Hard?

Hello data delvers! Apologies for the lack of updates, life has been busy! For today I have a quick delve on a frustrating problem I had to solve, longer delves are on the way!

Like I'm sure many of you, I greatly enjoy doing side projects on the [Raspberry Pi](https://www.raspberrypi.com/) mini computer. If you've read my [previous delve](2024-01-28-linux-fun.md), you'll know there are lots of fun utilities you can run on a linux machine. One such application I like to use my Raspberry Pi for is to stream music from web services such as Spotify to my television and then use an audio visualizer like those covered in my previous delve to provide a visual.

<!-- more -->

This worked great in combination with making the terminal full screen so that the only thing visible on the screen was the audio visualizer. Previously this was as simple as executing the keyboard shortcut Alt+F11. However, I noticed when I updated my Linux distribution from Debian 11 "Bullseye" to Debian 12 "Bookworm" the full screen command shortcut stopped working! Confused I thought some configuration got messed up, doing some quick internet searching was not yielding any helpful results and so I resolved myself to live with unmaximized applications for now...

## What's Going On?

A few months go by and I recently got the itch to tinker with my Raspberry Pi again. I wanted to stream some music and was confronted with the same issue of no full screen! Picking up the trail searching I saw that one of the big differences in the new distribution was the [switch to using Wayland as the display system](https://www.raspberrypi.com/news/bookworm-the-new-version-of-raspberry-pi-os/). "Ah ha!" I thought, "Maybe the shortcuts have changed in the new display!". More searching later I eventually stumbled upon [this guide](https://forums.raspberrypi.com/viewtopic.php?p=2207533) on the Raspberry Pi forums discussing how to make the new distribution more keyboard centric. Buried in the configuration options it discusses is a [modification for windows settings](https://github.com/gnmearacaun/rpios-wayfirewm-config/blob/e1399227623a211c1f80f8f700167d5b5a7b3a13/wayfire.ini#L76) in `~/.config/wayfire.ini`:

```ini
# Actions related to window management functionalities.
[wm-actions]
toggle_maximize = <super> KEY_F
toggle_fullscreen = <super> <shift> KEY_F
```
Excitedly, I modified my configuration file to add the shortcuts for the above actions and rebooted my Pi. Upon rebooting, I opened a terminal and executed the shortcut and "Tada!", my application was now full screen again!

Why this functionality was removed in the new distribution by default I can't say, it also seems to be conspicuously undocumented in the official sources, but I'm glad to have it back. It's my hope that this delve will help others stuck with the same issue overcome it faster than I did!

That's all I have for now, expect some more ML engineering delves soon!

As a side note, I have to check out some of the other shortcuts mentioned in that guide!

## Delve Data

* The Alt+F11 full screen shortcut was removed in the Debian 12 "Bookworm" distribution of the Raspberry Pi OS
* The solution is to add a new shortcut to the `wayfire.ini` file