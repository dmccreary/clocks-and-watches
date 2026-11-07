---
title: Sync Interval Calculator
description: A Chart.js sawtooth chart of clock error over three days that grows between NTP syncs and drops to zero at each sync, with sliders for drift and sync interval.
image: /sims/sync-interval-calculator/sync-interval-calculator.png
og:image: /sims/sync-interval-calculator/sync-interval-calculator.png
twitter:image: /sims/sync-interval-calculator/sync-interval-calculator.png
social:
   cards: false
quality_score: 100
---

# Sync Interval Calculator

<iframe src="main.html" height="502px" width="100%" scrolling="no"></iframe>

[Run the Sync Interval Calculator MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

A WiFi clock does not need a perfect crystal. It only needs to resynchronize with an NTP server often enough that the error never grows too large. Between syncs, the error grows at the drift rate; at each sync it drops back to zero. Plotted over time, that makes a **sawtooth**.

The two formulas from Chapter 14 drive the chart:

\[ \text{worst-case error} = \text{drift (ppm)} \times \frac{\text{sync interval (s)}}{1{,}000{,}000} \]

\[ \text{sync interval} = \frac{\text{tolerated error}}{\text{drift rate}} \]

The tallest point of each tooth is the worst-case error, which happens just before a sync. The dashed green line is the 1-second accuracy goal, and the blue triangles mark each NTP sync.

## How to Use

1. Pick a **Clock source**. The presets set the drift to 30 ppm (Pico crystal), 20 ppm (DS1307), or 2 ppm (DS3231).
2. Drag **Sync interval** from 1 to 48 hours. Watch how the teeth get taller and fewer as you sync less often.
3. Drag **Drift** to any value from 1 to 100 ppm to model a better or worse crystal. The source menu switches to "Custom."
4. Read the two results above the controls: the **worst-case error** for your settings, and the **sync interval needed for 1 s accuracy** at that drift.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/sync-interval-calculator/main.html"
        height="502px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objective

Students will calculate how often a clock must resynchronize for a given accuracy goal (Bloom: Applying, Evaluating).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Clock drift in ppm (Chapter 13)
- NTP time sync with `ntptime.settime()` (Chapter 14)

### Activities

1. **Worked example** (4 min): With the Pico crystal preset, compute by hand the worst-case error for a daily sync (about 2.6 s). Confirm it on the chart, then find the interval that keeps the error under 1 second (about 9 hours).
2. **Find the limit** (4 min): Students lower the sync interval until the readout turns green and record the largest interval that meets the goal for each preset.
3. **Be a polite client** (4 min): NTP servers are shared. Students decide on a sync interval for each preset that meets the 1-second goal without syncing more often than necessary.
4. **Reflect** (3 min): Why does the DS3231 meet the goal even with a 48-hour interval? What would happen if the WiFi were down for three days?

### Assessment

- A 50 ppm clock syncs every 12 hours. What is its worst-case error? (2.16 s.)
- What sync interval keeps a 20 ppm clock within 0.5 seconds? (About 6.9 hours.)
- Explain why each tooth starts at zero and why its height depends on both drift and interval.

## References

1. [Network Time Protocol](https://en.wikipedia.org/wiki/Network_Time_Protocol) - Wikipedia overview of NTP and clock synchronization.
2. [Sawtooth wave](https://en.wikipedia.org/wiki/Sawtooth_wave) - Wikipedia; the shape of the error curve.
3. [NTP Pool Project: use the pool](https://www.ntppool.org/en/use.html) - Guidance on polite polling of shared NTP servers.
4. [Connecting to the Internet with Raspberry Pi Pico W](https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf) - Raspberry Pi guide to WiFi on the Pico W.
5. [Chart.js documentation](https://www.chartjs.org/docs/latest/) - The charting library used by this MicroSim.
