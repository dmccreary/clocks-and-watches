---
title: Hysteresis Demonstrator
description: Compare a single threshold with a two-threshold dead zone on a noisy light reading, and count how often each output switches.
image: /sims/hysteresis-demonstrator/hysteresis-demonstrator.png
og:image: /sims/hysteresis-demonstrator/hysteresis-demonstrator.png
twitter:image: /sims/hysteresis-demonstrator/hysteresis-demonstrator.png
social:
   cards: false
quality_score: 0
---

# Hysteresis Demonstrator

<iframe src="main.html" height="562px" width="100%" scrolling="no"></iframe>

[Run the Hysteresis Demonstrator MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

An auto-brightness clock reads a light sensor and decides whether the room is **bright** or
**dim**. Real sensor readings are noisy. When the room light hovers near a single threshold,
the noise pushes the reading back and forth across the line, and the display flickers
between two brightness levels. This is called **chatter**.

**Hysteresis** fixes chatter with two thresholds. The output switches to *bright* only when
the reading rises above the **upper** threshold, and switches back to *dim* only when it falls
below the **lower** threshold. Between them is a **dead zone** (shaded purple) where the output
keeps whatever state it already had.

The top chart shows 400 noisy readings with the two thresholds and the single threshold (the
dotted midpoint). The two traces below show the outputs:

- **Single threshold** (orange) is *bright* whenever the reading is above the midpoint.
- **With hysteresis** (green) uses the upper and lower thresholds, like the `update()`
  function in the chapter.

The counters show how many times each output switched in the window.

## How to Use

1. The chart opens paused with a full window of readings. Press **Start** to scroll new
   readings in, and **Pause** to freeze them.
2. Compare the switch counts. Where in the chart does the single-threshold output chatter?
3. Move the **Noise amount** slider. How does noise change each count?
4. Move the **Upper threshold** and **Lower threshold** sliders to widen or narrow the dead zone.
5. Check **Lock thresholds together** to make the gap zero. Both outputs become the same.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/hysteresis-demonstrator/main.html"
        height="562px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Reading a light sensor with the ADC (Chapter 18)
- `if` and `elif` decisions and a state variable that remembers a value

### Learning Objectives

Students will be able to:

- Analyze why a single threshold chatters when a noisy signal hovers near it
- Explain how a dead zone between two thresholds removes chatter
- Choose a gap that is wide enough for the noise but still responds to real changes

### Activities

1. **Spot the chatter** (4 min): With the default settings, find each place where the
   single-threshold trace switches many times in a row. What is the light reading doing there?
2. **Noise versus gap** (6 min): Lock the thresholds together and record the switch count. Unlock
   them and widen the gap step by step until the hysteresis count stops changing. Repeat at noise
   500 and noise 3000. How does the gap you need depend on the noise?
3. **Too much of a good thing** (5 min): Make the gap very wide (upper 38000, lower 18000). What
   goes wrong now? Write one sentence describing the trade-off.

### Assessment

- The student explains that the dead zone must be wider than the noise swings to stop chatter.
- The student predicts that a gap of zero behaves exactly like a single threshold.
- The student connects hysteresis to debouncing and to a thermostat.

## References

1. [Hysteresis](https://en.wikipedia.org/wiki/Hysteresis) - Wikipedia article on systems whose output depends on their history.
2. [Schmitt trigger](https://en.wikipedia.org/wiki/Schmitt_trigger) - Wikipedia article on the electronic circuit that uses two thresholds to clean noisy signals.
3. [Thermostat](https://en.wikipedia.org/wiki/Thermostat) - Wikipedia article explaining why heating controls use a temperature dead band.
4. [MicroPython ADC class](https://docs.micropython.org/en/latest/library/machine.ADC.html) - Official documentation for `read_u16()`, used to read the light sensor.
