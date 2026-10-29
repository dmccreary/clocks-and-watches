---
title: Sleep vs Ticks Timeline
description: "Two timelines compare a blocking sleep(1) loop with a non-blocking ticks_diff() loop and measure how long each takes to notice a button press."
image: /sims/sleep-vs-ticks/sleep-vs-ticks.png
og:image: /sims/sleep-vs-ticks/sleep-vs-ticks.png
twitter:image: /sims/sleep-vs-ticks/sleep-vs-ticks.png
social:
   cards: false
quality_score: 100
---

# Sleep vs Ticks Timeline

<iframe src="main.html" height="482px" width="100%" scrolling="no"></iframe>

[Run the Sleep vs Ticks Timeline MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

Both programs in this MicroSim blink an LED once a second, but they do it differently. The top program uses `sleep(1)`: it checks the button, toggles the LED and then does nothing at all for a full second. The bottom program never sleeps; its loop runs about every 10 ms, checks the button every time, and uses `ticks_diff()` to decide when a second has passed.

The timelines scroll as simulated time runs. Blue blocks are the program working, gray blocks are `sleep(1)` and gold lines mark the bottom program's LED toggles. Press the button and a dashed red line marks the moment, while a red bar on each timeline grows until that program finally notices. The sleeping program can take up to a whole second; the ticks program answers within about 10 ms. Like every MicroSim in this book it opens paused, and the speed slider lets you watch in slow motion.

This MicroSim supports the chapter [Getting the Time in MicroPython](../../chapters/06-getting-time/index.md).

## How to Use

1. Press **Start** to run the simulated clock, and **Pause** to freeze it.
2. Press **Press button** a few times. Each press draws a red latency bar on both timelines and updates the panel.
3. Move the **Speed** slider to slow time down (0.05x) or run it at real speed (1x).
4. Press **Reset** to clear the presses and return to the paused start.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/sleep-vs-ticks/main.html"
        height="482px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Compare blocking timing with sleep() and non-blocking timing with ticks_ms() and ticks_diff()
- Measure the delay (latency) before each program notices a button press
- Explain why a program that sleeps cannot respond to input

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- The sleep() and ticks_ms() functions
- Reading a button with value()

### Activities

1. **Exploration** (4 min): Press Start and press the button ten times at random moments. Read the average delay for each program.
2. **Guided Practice** (6 min): Press the button just after a gray sleep block begins, then just before it ends. Explain the two very different delays.
3. **Assessment** (5 min): Write two sentences explaining why the clocks in later chapters use ticks_diff() instead of sleep() when they read buttons.

### Assessment

- Students state the longest possible delay for each program (about 1000 ms and about 10 ms).
- Students explain the word "blocking" using the gray blocks.
- Students identify which program to use for a stopwatch with a start button, and why.

## References

1. [MicroPython time module](https://docs.micropython.org/en/latest/library/time.html) - official reference for sleep(), ticks_ms() and ticks_diff()
2. [Latency (engineering)](https://en.wikipedia.org/wiki/Latency_(engineering)) - Wikipedia article on delay between cause and effect
3. [Polling (computer science)](https://en.wikipedia.org/wiki/Polling_(computer_science)) - Wikipedia article on checking an input over and over in a loop
