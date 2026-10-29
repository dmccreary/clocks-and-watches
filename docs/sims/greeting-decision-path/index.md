---
title: Greeting Decision Path
description: "Trace an if/elif/else chain that picks a greeting from the hour, one test at a time, and see how reordering the tests changes the answer."
image: /sims/greeting-decision-path/greeting-decision-path.png
og:image: /sims/greeting-decision-path/greeting-decision-path.png
twitter:image: /sims/greeting-decision-path/greeting-decision-path.png
social:
   cards: false
quality_score: 100
---

# Greeting Decision Path

<iframe src="main.html" height="522px" width="100%" scrolling="no"></iframe>

[Run the Greeting Decision Path MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

An `if`/`elif`/`else` chain checks its tests **from the top down** and runs only the first block whose test is `True`. Everything below that point is skipped, even tests that would also be true. This is why the order of the tests matters.

The flowchart shows the chapter's greeting program for any `hour` from 0 to 23. Each press of **Step** checks exactly one test: a false test turns pink and the marker moves down, and the first true test turns green and sends the marker to its greeting. Tests that are never reached turn gray. On wider screens the matching line of code is highlighted beside the flowchart. Check **Reorder tests** to put `hour < 18` first, and you will find hours where the program now gives the wrong greeting.

This MicroSim supports the chapter [Control Flow, Functions, and Modules](../../chapters/04-control-flow-functions/index.md).

## How to Use

1. Move the **hour** slider to choose a time of day. Predict the greeting before you start.
2. Press **Step** to check one test. Read the message under the flowchart to see why the marker moved.
3. Keep pressing **Step** until a greeting box turns green. Press **Reset trace** to trace the same hour again.
4. Check **Reorder tests** and trace hour 3 or hour 9. Compare the answer with the normal order.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/greeting-decision-path/main.html"
        height="522px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Trace an if/elif/else chain one test at a time to predict which block runs
- Explain that Python runs only the first block whose test is True and skips the rest
- Analyze how changing the order of elif tests can produce a wrong answer

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- Comparison operators such as < and >=
- Booleans (True and False)

### Activities

1. **Exploration** (4 min): Trace hours 3, 9, 15 and 21. Count how many tests Python checks for each hour.
2. **Guided Practice** (6 min): Turn on Reorder tests. Find every hour that now gets the wrong greeting and explain why.
3. **Assessment** (5 min): Without the MicroSim, write the greeting for hours 0, 6, 12 and 18, then check with the slider.

### Assessment

- Students predict the greeting for any hour before stepping and are right at least 4 times out of 5.
- Students explain why hour 12 gives "Afternoon" and not "Morning".
- Students state a rule for ordering `<` tests: smallest limit first.

## References

1. [Python Tutorial: if Statements](https://docs.python.org/3/tutorial/controlflow.html#if-statements) - official explanation of if, elif and else
2. [Conditional (computer programming)](https://en.wikipedia.org/wiki/Conditional_(computer_programming)) - Wikipedia article on conditionals
3. [Flowchart](https://en.wikipedia.org/wiki/Flowchart) - Wikipedia article on flowchart symbols such as the decision diamond
