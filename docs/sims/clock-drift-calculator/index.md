---
title: Drift Calculator
description: A Chart.js line chart of accumulated drift versus days for a Pico crystal, a DS1307, a DS3231, and a custom ppm value, with the days until each clock is one minute off.
image: /sims/clock-drift-calculator/clock-drift-calculator.png
og:image: /sims/clock-drift-calculator/clock-drift-calculator.png
twitter:image: /sims/clock-drift-calculator/clock-drift-calculator.png
social:
   cards: false
quality_score: 100
---

# Drift Calculator

<iframe src="main.html" height="532px" width="100%" scrolling="no"></iframe>

[Run the Drift Calculator MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

Every clock crystal runs a tiny bit fast or slow. The error is stated in **parts per million (ppm)**, and it adds up day after day:

\[ \text{drift} = \text{ppm} \times \frac{\text{elapsed seconds}}{1{,}000{,}000} \]

This chart plots that formula for the three clock sources from Chapter 13:

| Source | Accuracy | Drift per day | Days until 1 minute off |
|--------|----------|---------------|-------------------------|
| Pico crystal | 30 ppm | 2.6 s | 23 days |
| DS1307 | 20 ppm | 1.7 s | 35 days |
| DS3231 | 2 ppm | 0.17 s | 347 days |

Each line is straight because drift grows at a steady rate. A steeper line means a worse clock. The dotted gray line marks **1 minute off**, a reasonable point at which most people would notice and reset a wall clock. The table under the chart gives the exact drift after the chosen number of days and how many days each source lasts before it reaches one minute.

## How to Use

1. Drag **Elapsed days** from 1 to 365. Watch which lines cross the dotted 1-minute line, and when.
2. Hover over any line to read the exact drift on a given day.
3. Click a legend entry to hide or show that line. Hiding the Pico crystal makes the DS3231 line easier to read.
4. Type a value in **Custom ppm** (for example 10, or the drift you measured for your own clock) to add a fourth, dashed line. Clear the box to remove it.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/clock-drift-calculator/main.html"
        height="532px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objective

Students will calculate and compare the accumulated drift of different clock sources (Bloom: Applying, Evaluating).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Parts per million and the drift formula (Chapter 13)
- Reading a line graph

### Activities

1. **Calculate first** (4 min): Students use the formula to compute the drift of a DS1307 after 30 days by hand (about 52 seconds), then set the slider to 30 and check.
2. **Compare** (4 min): Set the slider to 365. How many times more drift does the Pico crystal have than the DS3231? Why is the ratio the same on every day?
3. **Custom clock** (4 min): Students enter 3.5 ppm, the drift of the clock in the Chapter 14 worked example, and read how many days it lasts before being one minute off.
4. **Evaluate** (3 min): Students decide which source they would use for a clock with no WiFi that should be reset only twice a year, and justify the choice with numbers from the table.

### Assessment

- Compute the drift in one year for a 20 ppm crystal (31,536,000 seconds). (About 631 seconds, or 10.5 minutes.)
- A clock is 60 seconds off after 100 days. Estimate its ppm. (About 6.9 ppm.)
- Explain why the lines are straight and why they all start at zero.

## References

1. [Crystal oscillator](https://en.wikipedia.org/wiki/Crystal_oscillator) - Wikipedia article on why crystal frequencies vary slightly.
2. [Parts-per notation](https://en.wikipedia.org/wiki/Parts-per_notation) - Wikipedia; explains ppm.
3. [DS3231 Datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/DS3231.pdf) - Analog Devices; the ±2 ppm accuracy specification.
4. [DS1307 Datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/DS1307.pdf) - Analog Devices; an RTC that uses an external, uncompensated crystal.
5. [Chart.js documentation](https://www.chartjs.org/docs/latest/) - The charting library used by this MicroSim.
