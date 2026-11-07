---
title: Seconds-to-Clock Flowchart
description: Step a number of seconds since midnight through a six-box flowchart that uses whole-number division and remainders to produce an hours:minutes:seconds clock reading.
image: /sims/seconds-to-clock-flowchart/seconds-to-clock-flowchart.png
og:image: /sims/seconds-to-clock-flowchart/seconds-to-clock-flowchart.png
twitter:image: /sims/seconds-to-clock-flowchart/seconds-to-clock-flowchart.png
social:
   cards: false
quality_score: 100
---

# Seconds-to-Clock Flowchart

<iframe src="main.html" height="542px" width="100%" scrolling="no"></iframe>

[Run the Seconds-to-Clock Flowchart Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

A clock program often knows only one number: how many seconds have passed since midnight. This flowchart shows the **algorithm** that turns that single number into the hours, minutes, and seconds you see on a clock face.

The algorithm uses two operators you will meet again in Chapter 3:

- `//` divides and keeps only the whole number (45296 // 3600 is 12).
- `%` gives the remainder that is left over (45296 % 3600 is 2096).

Each press of **Next step** runs one box. The box turns gold and shows the value it produced, and the boxes already finished turn green. A panel on the right shows the arithmetic with the real numbers, so you can check every step by hand.

## How to Use

- Type a number from 0 to 86,399 into **Seconds since midnight** (the default is 45,296), then press Enter or click outside the box.
- Before each step, **predict** the value the next box will produce.
- Press **Next step** to run one box and check your prediction against the gold box and the panel.
- Click any box in the flowchart to read a one-sentence explanation of what that step does.
- Press **Reset** to clear the values and start the trace again.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/seconds-to-clock-flowchart/main.html"
        height="542px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Apply the seconds-to-clock algorithm by tracing a number of seconds through each step.
- Use whole-number division (//) and remainder (%) to split a total into larger and smaller units.
- Predict the output of each step before running it, and check the prediction.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Long division with a remainder.
- Knowing that an hour has 3,600 seconds and a minute has 60 seconds.

### Activities

1. **Trace the example (4 min):** With the default 45,296 seconds, students predict each value on paper before pressing Next step. The final reading should be 12:34:56.
2. **Edge cases (4 min):** Students try 0, 59, 60, 3599, 3600, and 86399. Ask: which inputs make a box produce 0? What is the largest hour the algorithm can produce?
3. **Reverse it (4 min):** Give students a clock reading such as 07:05:09 and ask them to find the seconds since midnight. They enter their answer and step through to check it.
4. **Connect to code (3 min):** Students write the four assignment statements from the boxes as MicroPython lines and compare them with the flowchart.

### Assessment

- Students can trace any input from 0 to 86,399 to the correct hh:mm:ss reading without the MicroSim.
- Students can explain why the remainder step is needed before computing minutes.
- Students can convert a clock reading back into seconds since midnight.

## References

1. [Algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Algorithm) - What makes a list of steps an algorithm: precise, ordered, and finite.
2. [Modulo operation (Wikipedia)](https://en.wikipedia.org/wiki/Modulo) - How the remainder operator works, with examples.
3. [Flowchart (Wikipedia)](https://en.wikipedia.org/wiki/Flowchart) - The standard shapes used to draw algorithms.
4. [Mermaid flowchart syntax](https://mermaid.js.org/syntax/flowchart.html) - The library used to draw this diagram.
