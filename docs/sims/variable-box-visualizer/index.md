---
title: Variable Box Visualizer
description: "Step through short Python programs one assignment at a time and predict each variable's new value before the line runs."
image: /sims/variable-box-visualizer/variable-box-visualizer.png
og:image: /sims/variable-box-visualizer/variable-box-visualizer.png
twitter:image: /sims/variable-box-visualizer/variable-box-visualizer.png
social:
   cards: false
quality_score: 100
---

# Variable Box Visualizer

<iframe src="main.html" height="492px" width="100%" scrolling="no"></iframe>

[Run the Variable Box Visualizer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A **variable** is a name that refers to a value, and an assignment statement such as `x = y` or `seconds += 1` changes which value a name refers to. Most early bugs come from losing track of what each name holds after several lines have run.

This MicroSim shows a short program on one side and a box for every variable on the other. Each press of **Step** runs exactly one line. The box that changes flashes orange, and its old values stay visible, crossed out, so you can see the history. Four presets cover basic assignments, a seconds counter that uses `+=` and `%=`, a swap with a temporary variable, and Python's one-line swap `a, b = b, a`. Turn on **Predict first** to type your answer before each line runs.

This MicroSim supports the chapter [MicroPython Basics: Variables and Data Types](../../chapters/03-micropython-basics/index.md).

## How to Use

1. Pick a program from the menu. The line that will run next is highlighted in yellow.
2. Press **Step** to run that line. The changed box flashes, and the message explains the arithmetic.
3. Turn on **Predict first**, type the new value of the variable named in the message, then press **Step** to check.
4. Press **Reset** to start the same program again, or choose another preset.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/variable-box-visualizer/main.html"
        height="492px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Predict the value of each variable after a sequence of assignment statements
- Explain that x = y copies the current value, so changing y later does not change x
- Apply the shortcut operators +=, -= and %= by rewriting them as x = x + ...

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- Variables and the = assignment operator
- Integer arithmetic, including % for remainders

### Activities

1. **Exploration** (4 min): Step through "Basic assignments" with Predict first turned off. Notice that `x` keeps the value 3 when `y` changes to 10.
2. **Guided Practice** (6 min): Turn on Predict first and work through "Counter with +=" and both swap presets. Explain why the swap needs `temp`.
3. **Assessment** (5 min): Reset each preset and predict every line. Record how many of your predictions were right.

### Assessment

- Students predict every value in the "Counter with +=" preset correctly, including 60 % 60 = 0.
- Students explain why `a = b` followed by `b = a` does not swap two values.
- Students rewrite `seconds %= 60` as an ordinary assignment.

## References

1. [Python Tutorial: An Informal Introduction](https://docs.python.org/3/tutorial/introduction.html) - variables and assignment in the official tutorial
2. [Assignment (computer science)](https://en.wikipedia.org/wiki/Assignment_(computer_science)) - Wikipedia article on assignment statements
3. [Python Tutor](https://pythontutor.com/) - a free tool for stepping through any Python program line by line
