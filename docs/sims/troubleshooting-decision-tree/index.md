---
title: Troubleshooting Decision Tree
description: Walk a clickable troubleshooting tree for Pico clocks: pick a symptom, answer yes or no questions, and reach a likely cause, the test to run and the chapter to review.
image: /sims/troubleshooting-decision-tree/troubleshooting-decision-tree.png
og:image: /sims/troubleshooting-decision-tree/troubleshooting-decision-tree.png
twitter:image: /sims/troubleshooting-decision-tree/troubleshooting-decision-tree.png
social:
   cards: false
quality_score: 0
---

# Troubleshooting Decision Tree

<iframe src="main.html" height="602px" width="100%" scrolling="no"></iframe>

[Run the Troubleshooting Decision Tree MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

Most clock problems fall into a few families. This decision tree turns the troubleshooting
table in Chapter 20 into a path you can follow one question at a time, always checking the
cheapest and most likely cause first.

The first view shows the five symptom families:

- Nothing on the display
- Wrong image (colors, noise, offset)
- Wrong time
- Buttons misbehave
- Random resets

Click a symptom to draw its branch. Orange six-sided boxes are **questions** with *yes* and *no*
arrows, and green boxes are **suggested fixes**. Every box is clickable. The panel on the right
explains *why* that question is asked and the exact **test to run**, and each fix names the
chapter to review. The yellow box marks where you are, the boxes on the path from the top have a
dark blue outline, and the breadcrumb at the top lists the answers you have given so far.

## How to Use

1. Click the symptom that matches your problem.
2. Read the question and the **test to run** in the right panel. Do the test on your clock.
3. Click the **yes** or **no** box under the question to follow your answer.
4. When you reach a green fix, apply it and test again.
5. Hover over any box to preview its details. Press **Start over** to return to the top.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/troubleshooting-decision-tree/main.html"
        height="602px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15-20 minutes

### Prerequisites

- The troubleshooting table and systematic debugging steps in Chapter 20
- Running an I2C scan and reading a traceback

### Learning Objectives

Students will be able to:

- Analyze a symptom and select the most likely cause
- Choose the next test that best splits the remaining possible causes
- Explain why power and wiring are checked before code

### Activities

1. **Case studies** (8 min): For each case, walk the tree and record the path and the fix:
   (a) an OLED clock shows nothing, the 3.3 V rail is fine, and `i2c.scan()` returns `[]`;
   (b) a clock shows 2021-01-01 every morning after the power strip is switched off;
   (c) the mode button skips two modes at a time.
2. **Why this order?** (4 min): In the *Nothing on the display* branch, why is the power test asked
   before the I2C scan, and the scan before checking `show()`? What would you waste if you started
   with the code?
3. **Extend the tree** (6 min): Choose one branch and design one more question and fix that is not
   in the tree (for example, for WiFi that will not connect). Write the question, the test, and the
   yes and no outcomes.

### Assessment

- The student reaches the correct fix for each case study and names the test that decided each step.
- The student explains the "cheapest, most likely first" ordering.
- The student's new question has a clear, quick test that splits the possible causes.

## References

1. [Troubleshooting](https://en.wikipedia.org/wiki/Troubleshooting) - Wikipedia article on systematic problem solving and the half-splitting method.
2. [Decision tree](https://en.wikipedia.org/wiki/Decision_tree) - Wikipedia article on decision trees as a way to organize choices.
3. [MicroPython I2C class](https://docs.micropython.org/en/latest/library/machine.I2C.html) - Official documentation for `scan()` and the other I2C calls used in the tests.
4. [Mermaid flowchart syntax](https://mermaid.js.org/syntax/flowchart.html) - The diagram library and the `click` directive that make each box clickable.
