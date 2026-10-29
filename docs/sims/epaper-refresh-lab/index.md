---
title: E-Paper Refresh Lab
description: Compare always-full, always-partial and mixed refresh schedules on an e-paper clock, and watch the trade-off between refresh time, screen flashes and ghosting.
image: /sims/epaper-refresh-lab/epaper-refresh-lab.png
og:image: /sims/epaper-refresh-lab/epaper-refresh-lab.png
twitter:image: /sims/epaper-refresh-lab/epaper-refresh-lab.png
social:
   cards: false
quality_score: 0
---

# E-Paper Refresh Lab

<iframe src="main.html" height="537px" width="100%" scrolling="no"></iframe>

[Run the E-Paper Refresh Lab MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

An e-paper clock that shows minutes must update its screen 1,440 times a day. There are two
ways to do it:

- A **full refresh** flashes the whole screen between black and white before showing the new
  picture. It takes about 2 seconds and leaves a perfectly clean image.
- A **partial refresh** changes only the pixels that need to change. It takes about 0.3
  seconds and does not flash, but each one leaves a faint **ghost** of the old digits.

This lab uses a simple ghost model: every partial refresh adds 1.6 percent to the ghost level,
and a full refresh resets it to zero. The preview shows the ghosts as faint copies of earlier
times behind the current one, the meter shows the ghost level (above 50 percent the ghosts are
easy to notice), and the timeline shows the last 120 refreshes with the ghost level drawn above
them as a red sawtooth.

## How to Use

1. Choose a **Refresh mode**: always full, always partial, or mixed (a full refresh after
   every N partial refreshes).
2. In mixed mode, set **N** with the slider.
3. Press **Advance one minute** to step through refreshes one at a time. A full refresh shows
   a short black-and-white flash.
4. Press **Run a day** to fast-forward 24 hours (1,440 updates). Press **Pause** to stop early.
5. Read the counts, the total refresh time and the ghost level. Changing the mode or N starts
   a fresh test; **Reset** also starts over at 07:00.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/epaper-refresh-lab/main.html"
        height="537px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Full and partial e-paper refresh and ghosting (Chapter 19)
- The `if partials >= 30` scheduling code in Chapter 19

### Learning Objectives

Students will be able to:

- Analyze how full and partial refresh strategies trade speed and flashing against ghosting
- Calculate the total refresh time for a day from the counts of each refresh type
- Evaluate a value of N that keeps ghosting below the noticeable level with the fewest flashes

### Activities

1. **Three strategies** (6 min): Run a full day in each mode (mixed with N = 30). Record the
   partial count, full count, total refresh time and final ghost level in a table.
2. **Check the math** (3 min): For the mixed run, multiply the partial count by 0.3 s and the full
   count by 2.0 s. Does your total match the readout?
3. **Tune N** (6 min): Find the largest N that never lets the ghost level reach the noticeable mark.
   Why might a real clock still choose a smaller N, or add a full refresh once an hour?

### Assessment

- The student explains why "always full" is the cleanest but slowest and most distracting choice.
- The student explains why "always partial" eventually becomes unreadable.
- The student justifies a value of N using the ghost meter and the flash count.

## References

1. [Electronic paper](https://en.wikipedia.org/wiki/Electronic_paper) - Wikipedia article on how e-paper particles move and why images persist.
2. [Screen burn-in and image persistence](https://en.wikipedia.org/wiki/Screen_burn-in) - Wikipedia article on ghost images left on displays.
3. [Waveshare e-Paper Driver HAT wiki](https://www.waveshare.com/wiki/E-Paper_Driver_HAT) - Notes on full and partial refresh for Waveshare panels.
4. [MicroPython framebuf module](https://docs.micropython.org/en/latest/library/framebuf.html) - The frame buffer used to prepare each e-paper image.
