---
layout: post
title:  "Delve 3: Fun Linux Utilities"
author: Chase
categories: 
    - Software Engineering
tags: Tools Fun
banner: 
    image: "/assets/images/banners/delve3.png"
---

> "People rarely succeed unless they have fun in what they are doing" -Dale Carnegie

## *nix the Workhorse of MLOps

Welcome to 2024 data delvers! I hope you had a wonderful holiday season! As we enter into the new year I'd like wanted to take some time to talk about things that make my day to day as a developer fun! As I hope to get into in future delves, for many reasons I prefer a *nix (Unix or Linux) based environment for doing development. My preferred method of achieving this in recent years has been the [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/about). It is super easy to set up on any modern windows machine, integrates very nicely with my IDE of choice, [Visual Studio Code](https://code.visualstudio.com/docs/remote/wsl), and avoids many of the dangers associated with partitioning your hard drive to dual-boot your machine with multiple operating systems. As a bonus, when working with cloud providers you are almost always deploying your model on a Linux server, so mirroring that same environment on your dev machine makes everything that much smoother.

Importantly for our delve today, WSL provides a full bash shell to interact with the OS. Over the years many a Linux developer has created fun and useful utilities to use within a shell, some of which I'd like to share with you today!

# Text-Based Utilities

The following utilities work by printing text out to your terminal.

* [cmatrix](https://github.com/abishekvashok/cmatrix) - This has long been a staple of my dev machines, if you ever wanted to feel like a hacker in "The Matrix", this utility will simulate the iconic terminal screens from the film.

    ![cmatrix screencast](https://github.com/abishekvashok/cmatrix/raw/master/data/img/capture_orig.gif)

* [cbonsai](https://gitlab.com/jallbrit/cbonsai) - In a similar vein to cmatrix, cbonsai procedurally generates a bonsai tree within your terminal.

    ![cbonsai](https://user-content.gitlab-static.net/516ebf93882a9132c52dfbd25843c529d6f7ce95/68747470733a2f2f692e696d6775722e636f6d2f726e714a7833502e676966)

* [fortune](https://en.wikipedia.org/wiki/Fortune_(Unix)) - A very old, but still fun utility. Fortune prints a random fortune every time it is executed.

    ```
    $ fortune
    Q:      Why was Stonehenge abandoned?
    A:      It wasn't IBM compatible.  
    ```

* [cowsay](https://en.wikipedia.org/wiki/Cowsay) - Another old, but very fun utility. Cowsay allows you to make an ascii art cow (or other animal) say a phrase of your choice.
 
    ```
    $ cowsay Hello world!
     ______________
    < Hello world! >
     --------------
            \   ^__^
             \  (oo)\_______
                (__)\       )\/\
                    ||----w |
                    ||     ||
    ```

    For more fun you can pipe fortune into cowsay to get your animal to give you a random fortune.

    ```
    $ fortune | cowsay -f tux
     _____________________
    / Big book, big bore. \
    |                     |
    \ -- Callimachus      /
     ---------------------
       \
        \
            .--.
           |o_o |
           |:_/ |
          //   \ \
         (|     | )
        /'\_   _/`\
        \___)=(___/
    ```

    * [wttr.in](https://github.com/chubin/wttr.in) - Allows you to get a weather report directly in your terminal.

    ```
    $ curl wttr.in
    Weather for City: Paris, France
    
         \   /     Clear
          .-.      10 – 11 °C
       ― (   ) ―   ↑ 11 km/h
          `-’      10 km
         /   \     0.0 mm
    ```

For each of these utilities (except cmatrix!), you can add them to the Message of the Day (motd) shown when you first log in to your shell by following these steps:

**Note:** This assumes you are using the *Ubuntu* distribution in WSL.

1. Navigate to `/etc/update-motd.d`
2. Create a file called `01-custom-message`
3. Paste any commands you like to be run in this file and save it.
    ```
    #!/usr/bin/env bash

    fortune | cowsay -f tux
    ```
4. Make the file executable `$ sudo chmod +x 01-custom-message`

Now when you log into your machine you'll get your own custom message!

```
Welcome to Ubuntu 22.04.3 LTS (GNU/Linux 5.15.133.1-microsoft-standard-WSL2 x86_64)
 ______________________________________
< Today is what happened to yesterday. >
 --------------------------------------
   \
    \
        .--.
       |o_o |
       |:_/ |
      //   \ \
     (|     | )
    /'\_   _/`\
    \___)=(___/


 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage
```

## Audio Visualizers
