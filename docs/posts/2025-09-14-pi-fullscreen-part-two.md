---
date: 2025-09-14
categories: 
    - Software Engineering
tags: 
    - Tools 
    - Fun
links:
    - Part One: posts/2024-06-29-pi-fullscreen.md
---

# Delve 16: The Quest for a Full Screen Raspberry Pi Application - Part 2

![Banner](../assets/images/banners/delve16.png)

> "The only constant in life is change." - Heraclitus

## Full Screen Applications on the Raspberry Pi, Why so Hard AGAIN?

Hello data delvers! I recently revisited my [Raspberry Pi](https://www.raspberrypi.com/) after a long hiatus. As part of this I made sure to update all the packages and OS to the latest version. If you've read my [previous Raspberry Pi delve](2024-06-29-pi-fullscreen.md), you'll know that being able to make applications full screen isn't as straightforward as it should be. Much to my surprise, after updating everything my fullscreen keyboard shortcut broke! 
After spending some time sleuthing around support forms I'd like to share what the fix is with you all!

<!-- more -->

## What's Going On?

The culprit is that in late 2024 (I know I haven't touched my Pi in that long!), Raspberry Pi switched it's default compositor (the software component for rendering windows) from [Wayfire](https://wayfire.org/) to [labwc](https://labwc.github.io/) as it was better optimized for the Raspberry Pi's limited hardware resources (when updating I was presented with a screen asking if I wanted switch to Labwc). In doing so though the keyboard configuration for Wayfire located at `~/.config/wayfire.ini` would no longer work!

## A New Config

labwc uses its own config file located at `~/.config/lawbwc/rc.xml`, by default it will look something like this:

```xml title="~/.config/lawbwc/rc.xml" linenums="1"
<?xml version="1.0"?>
<openbox_config
	xmlns="http://openbox.org/3.4/rc">
	<theme>
		<font place="ActiveWindow">
			<name>PibotoLt</name>
			<size>16</size>
			<weight>Normal</weight>
			<slant>Normal</slant>
		</font>
		<font place="InactiveWindow">
			<name>PibotoLt</name>
			<size>16</size>
			<weight>Normal</weight>
			<slant>Normal</slant>
		</font>
		<name>PiXnoir_l</name>
	</theme>
</openbox_config>
```

With some prompting of with CoPilot, I discovered the trick is to add a new `<keyboard>` section to this file with your desired shortcuts. For example, to have my previous shortcut of ++super+shift+f++ to toggle fullscreen you could add the following section:

```xml title="~/.config/lawbwc/rc.xml" linenums="1" hl_lines="19-23"
<?xml version="1.0"?>
<openbox_config
	xmlns="http://openbox.org/3.4/rc">
	<theme>
		<font place="ActiveWindow">
			<name>PibotoLt</name>
			<size>16</size>
			<weight>Normal</weight>
			<slant>Normal</slant>
		</font>
		<font place="InactiveWindow">
			<name>PibotoLt</name>
			<size>16</size>
			<weight>Normal</weight>
			<slant>Normal</slant>
		</font>
		<name>PiXnoir_l</name>
	</theme>
	<keyboard>
		<keybind key="W-S-f">
  			<action name="ToggleFullscreen"/>
		</keybind>
	</keyboard>
</openbox_config>
```

!!!tip
    A more complete list of configuration options can be found [here](https://github.com/labwc/labwc/blob/master/docs/rc.xml.all).


After making the above modifications and rebooting my Pi I can make applications fullscreen again!

## Delve Data

* In late 2024 the Raspberry Pi switched its default compositor from [Wayfire](https://wayfire.org/) to [labwc](https://labwc.github.io/)
* This requires a new config file located at `~/.config/lawbwc/rc.xml` to define keyboard shortcuts