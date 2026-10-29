---
title: Pico Startup Sequence
description: "A clickable flowchart of what the Pico does from power-on to a running clock, with a toggle that shows how the path changes when main.py is missing."
image: /sims/pico-startup-sequence/pico-startup-sequence.png
og:image: /sims/pico-startup-sequence/pico-startup-sequence.png
twitter:image: /sims/pico-startup-sequence/pico-startup-sequence.png
social:
   cards: false
quality_score: 100
---

# Pico Startup Sequence

<iframe src="main.html" height="550px" width="100%" scrolling="no"></iframe>

[Run the Pico Startup Sequence MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

When the Pico gets power, it does not wait for you to press Run. The MicroPython firmware starts, runs `boot.py` if it exists, and then looks for a file named exactly `main.py`. If it finds one, your clock starts by itself; if not, the Pico waits at the `>>>` REPL prompt. Knowing this sequence explains why a finished clock must be saved as `main.py`, and why a `main.py` with a tight loop can make the Pico hard to reach from Thonny.

Every step in the flowchart is clickable and fills the panel with an explanation. The toggle at the top switches between **Has main.py** and **No main.py**. Steps with an orange border are the part of the path that changes, and steps drawn in gray never run in that case.

This MicroSim supports the chapter [The Pico Platform: Pins, Files, and Firmware](../../chapters/05-pico-platform/index.md).

## How to Use

1. Click any step in the flowchart. The explanation appears in the panel beside it.
2. Switch between **Has main.py** and **No main.py** at the top. Compare which steps are blue, orange and gray.
3. Follow the "No" arrow from "USB connected to Thonny?" to see why the main loop keeps running on battery power.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/pico-startup-sequence/main.html"
        height="550px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Describe the steps from power-on to a running clock program
- Explain the roles of boot.py and main.py
- Explain what changes when there is no main.py, and how Thonny can interrupt a running main.py

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- Saving files to the Pico with Thonny
- The REPL prompt from Chapter 3

### Activities

1. **Exploration** (4 min): Click every step in order from Power on to the REPL prompt and read each explanation.
2. **Guided Practice** (5 min): Switch to No main.py. List the steps that are skipped, then rename a test program on your Pico to main.py and unplug and replug it.
3. **Assessment** (5 min): Explain to a partner how to regain control of a Pico whose main.py never sleeps.

### Assessment

- Students put the startup steps in order without the diagram.
- Students explain why a program named clock.py does not start at power-up.
- Students describe two ways to interrupt a running main.py.

## References

1. [MicroPython: The MicroPython boot sequence](https://docs.micropython.org/en/latest/reference/reset_boot.html) - official description of boot.py, main.py and soft reset
2. [Raspberry Pi Pico: MicroPython](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) - installing firmware and saving programs to the Pico
3. [Booting](https://en.wikipedia.org/wiki/Booting) - Wikipedia article on what happens when a computer starts
