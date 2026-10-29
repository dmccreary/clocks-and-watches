---
title: Button Bounce Oscilloscope
description: "A single-shot oscilloscope captures contact bounce on every press; adjust the debounce window and a 0.1 uF hardware filter until one press counts once."
image: /sims/button-bounce-scope/button-bounce-scope.png
og:image: /sims/button-bounce-scope/button-bounce-scope.png
twitter:image: /sims/button-bounce-scope/button-bounce-scope.png
social:
   cards: false
quality_score: 100
---

# Button Bounce Oscilloscope

<iframe src="main.html" height="547px" width="100%" scrolling="no"></iframe>

[Run the Button Bounce Oscilloscope MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

When a button's metal contacts close, they bounce apart and together several times in a few milliseconds. A program fast enough to notice sees each bounce as a separate press. **Debouncing** ignores those extra edges, either in software with a time window or in hardware with a capacitor.

This MicroSim works like an oscilloscope set to single-shot: each **Press button** captures the pin voltage starting 5 ms before the first falling edge. Every press makes a new random bounce of 3 to 13 contact changes over 1 to 15 ms. Triangles under the trace mark each falling edge the Pico sees: green if the software counts it, red if the debounce window rejects it. The shaded blue band is the window after each accepted edge. Move the **Debounce window** slider until each press counts once, and try the **Hardware filter**, which smooths the bounce so only one clean edge reaches the pin.

This MicroSim supports the chapter [Buttons, Interrupts, and State Machines](../../chapters/07-buttons-state-machines/index.md).

## How to Use

1. Press **Press button** several times. Compare "Physical presses" with "Presses counted".
2. Move the **Debounce window** slider. The markers and the verdict update for the current capture, and new presses are counted with the new window.
3. Check **Hardware filter (0.1 uF capacitor)** to see the smoothed trace and the input thresholds.
4. Use the **Span** menu to zoom in (20 ms) or out (150 ms). Press **Reset count** to start counting again.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/button-bounce-scope/main.html"
        height="547px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Analyze how contact bounce turns one press into several falling edges
- Evaluate how long a software debounce window must be to count each press once
- Compare software debouncing with a hardware RC filter

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- Pull-up resistors and active-low buttons from Chapter 5
- ticks_ms() and ticks_diff() from Chapter 6

### Activities

1. **Exploration** (4 min): With the window at 0 ms, press the button ten times. Record how many presses are counted.
2. **Guided Practice** (6 min): Find the smallest window that counts every press once over ten presses. Compare it with the longest bounce you saw.
3. **Evaluate** (5 min): Argue for a window between 20 and 50 ms. Explain what goes wrong with 0 ms and with a very long window such as 300 ms.

### Assessment

- Students choose a window longer than the longest bounce and justify it with data from the scope.
- Students explain why the hardware filter produces one falling edge.
- Students relate the slider to `DEBOUNCE_MS` in the chapter's code.

## References

1. [Switch: contact bounce](https://en.wikipedia.org/wiki/Switch#Contact_bounce) - Wikipedia section on why contacts bounce
2. [A Guide to Debouncing (Jack Ganssle)](http://www.ganssle.com/debouncing.htm) - measured bounce times from real switches and debounce methods
3. [RC time constant](https://en.wikipedia.org/wiki/RC_time_constant) - Wikipedia article on tau = R x C used by the hardware filter
