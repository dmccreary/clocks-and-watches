---
title: Clock Architecture Explorer
description: A block diagram of the five parts every clock needs (power supply, microcontroller, time source, display, and input) that relabels each block with real parts for three different clocks.
image: /sims/clock-architecture-explorer/clock-architecture-explorer.png
og:image: /sims/clock-architecture-explorer/clock-architecture-explorer.png
twitter:image: /sims/clock-architecture-explorer/clock-architecture-explorer.png
social:
   cards: false
quality_score: 100
---

# Clock Architecture Explorer

<iframe src="main.html" height="450px" width="100%" scrolling="no"></iframe>

[Run the Clock Architecture Explorer Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

**Clock architecture** is the big-picture plan of which parts a clock needs and how they connect. Every clock in this book has the same five blocks:

- **Power supply:** provides the electricity everything else needs.
- **Microcontroller:** runs the program.
- **Time source:** tells the program what time it is.
- **Display:** an actuator that shows the time.
- **Input:** sensors such as buttons that let a person set the time.

Red dashed arrows show **power** flowing from the supply to every block. Blue arrows show **data**: the time source and the buttons send data *in* to the microcontroller, and the microcontroller sends data *out* to the display.

Choose a clock from the menu and each block is relabeled with the real part that fills it. The blocks never change; only the parts inside them do. That is what makes the five blocks a useful planning tool for any new clock you design.

## How to Use

- Pick a clock from **Choose a clock**: *4-digit LED clock*, *OLED clock with RTC*, or *Smartwatch*. Each box shows the part that clock uses.
- **Click** any box to read its job, a note about the chosen part, and a link to the chapter that covers it.
- Switch between clocks with a box selected to compare how each clock fills the same block.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/clock-architecture-explorer/main.html"
        height="450px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Describe the job of each of the five blocks of a clock.
- Compare how a 4-digit LED clock, an OLED clock with an RTC, and a smartwatch fill the same five blocks.
- Explain the direction of power and data flow between the blocks.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Read the Clock Architecture section of Chapter 2.
- Know the difference between a sensor and an actuator (Chapter 1).

### Activities

1. **Name the jobs (3 min):** With "Any clock" selected, students click each box and summarize its job in five words or fewer.
2. **Compare three clocks (5 min):** Students fill in a table with one row per block and one column per clock. Ask: which blocks change the most between clocks? Which part never changes?
3. **Follow the arrows (3 min):** Ask: which blocks only receive power? Which block both receives and sends data?
4. **Design your own (4 min):** Students invent a fourth clock (for example, a NeoPixel ring clock with WiFi) and list the part that fills each block.

### Assessment

- Students list the five blocks and the job of each.
- Students explain why the Smartwatch time source can be more accurate than the 4-digit LED clock time source.
- Students correctly fill all five blocks for a clock design they have not seen before.

## References

1. [Block diagram (Wikipedia)](https://en.wikipedia.org/wiki/Block_diagram) - How engineers use boxes and arrows to plan a system.
2. [Real-time clock (Wikipedia)](https://en.wikipedia.org/wiki/Real-time_clock) - Background on time-source chips like the DS3231.
3. [Network Time Protocol (Wikipedia)](https://en.wikipedia.org/wiki/Network_Time_Protocol) - How a WiFi clock gets the exact time from the internet.
4. [vis-network documentation](https://visjs.github.io/vis-network/docs/network/) - The library used to draw this diagram.
