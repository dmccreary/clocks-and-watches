---
title: Battery Life Calculator
description: Choose a clock's parts, backlight brightness, sleep time and battery, then compare the estimated runtime before and after your design changes.
image: /sims/battery-life-calculator/battery-life-calculator.png
og:image: /sims/battery-life-calculator/battery-life-calculator.png
twitter:image: /sims/battery-life-calculator/battery-life-calculator.png
social:
   cards: false
quality_score: 0
---

# Battery Life Calculator

<iframe src="main.html" height="532px" width="100%" scrolling="no"></iframe>

[Run the Battery Life Calculator MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

How long will a battery-powered clock run? Add up the current of every part to get the
**average current**, then use the runtime estimate from the chapter:

\[ \text{runtime (hours)} = \frac{\text{capacity (mAh)} \times 0.8}{\text{average current (mA)}} \]

The 0.8 allows for the fact that a battery never delivers its full labeled capacity.

This calculator starts with the chapter's worked example: a Pico (25 mA), a color display
backlight at 75% brightness (60 mA) and a DS3231 RTC (0.2 mA) on a 500 mAh LiPo, which gives
about 4.7 hours. The stacked bar shows how much each part adds to the average current, and the
line above it names the biggest draw. The lower chart compares the runtime of the saved
**Before** design with the design you have **Now**.

**Sleep model.** While the Pico is asleep it draws about 1.5 mA, the RTC keeps running, and every
other part (WiFi, display, backlight, buzzer, NeoPixel) is switched off. The *Time asleep* slider
sets what fraction of the time the clock spends asleep. Real parts vary, so measure your own clock
with a multimeter before trusting any estimate.

## How to Use

1. Check or uncheck the **parts** to include them in the clock.
2. Drag **TFT backlight brightness** (0 to 80 mA) and **Time asleep** (0 to 95%).
3. Pick a **battery** size.
4. Press **Save as "Before"** to remember the current design, make a change, and compare the
   two bars.
5. Press **Reset** to return to the worked example.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/battery-life-calculator/main.html"
        height="532px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15-20 minutes

### Prerequisites

- Current in milliamps and capacity in milliamp-hours (Chapter 18)
- The current draw table in Chapter 18

### Learning Objectives

Students will be able to:

- Calculate a clock's average current and estimated runtime from its parts
- Evaluate which single design change saves the most energy
- Justify a low-power design using numbers rather than guesses

### Activities

1. **Check the example** (4 min): With the default settings, calculate the runtime by hand and
   compare it with the calculator. Then dim the backlight to 25% (20 mA). Does the runtime roughly
   double, as the chapter says (about 8.9 hours)?
2. **One change at a time** (8 min): From the worked example, try each change below by itself,
   pressing **Reset** between them, and record the runtime: backlight at 25%; time asleep 90%;
   swap the TFT for the small OLED; use a 2500 mAh battery. Rank the changes from best to worst.
3. **Design challenge** (6 min): A smartwatch must run at least 2 days on a 500 mAh battery, must
   have a display, and must use WiFi. Find a combination of settings that meets the goal, save it as **Before**,
   and explain which change mattered most.

### Assessment

- The student calculates average current and runtime for a given set of parts.
- The student identifies the display backlight as the biggest target for savings in the example.
- The student explains why sleeping saves so much even though the Pico's own current is modest.

## References

1. [Ampere hour](https://en.wikipedia.org/wiki/Ampere_hour) - Wikipedia article on battery capacity in milliamp-hours.
2. [Lithium polymer battery](https://en.wikipedia.org/wiki/Lithium_polymer_battery) - Wikipedia article on the LiPo cells used in watches.
3. [Raspberry Pi Pico datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf) - Official power consumption figures for the Pico, including sleep modes.
4. [Chart.js documentation](https://www.chartjs.org/docs/latest/) - The charting library used for the stacked and comparison bars.
