---
title: Design Decision Matrix
description: Weight criteria and score up to four clock designs in a decision matrix, see the weighted totals and the winner, and test how sensitive the choice is to each weight.
image: /sims/design-decision-matrix/design-decision-matrix.png
og:image: /sims/design-decision-matrix/design-decision-matrix.png
twitter:image: /sims/design-decision-matrix/design-decision-matrix.png
social:
   cards: false
quality_score: 0
---

# Design Decision Matrix

<iframe src="main.html" height="547px" width="100%" scrolling="no"></iframe>

[Run the Design Decision Matrix MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A **decision matrix** compares designs fairly. Give each quality (criterion) a **weight**
from 0 to 5 for how much it matters to you, give each design a **score** from 1 to 5 on that
quality, then multiply and add:

\[ \text{weighted total} = \sum (\text{weight} \times \text{score}) \]

The bar chart shows each design's weighted total, and the winner gets a gold outline and a star.
The matrix below the chart holds the weight sliders and a score menu for each design.

The **Sensitivity** button asks a useful question: *how close was this decision?* It finds the
smallest change to a single weight that would let another design catch up, and reports the weight
at which they tie. If no weight change from 0 to 5 can flip the winner, the choice is robust.

The **Worked example** preset loads the chapter's bedside clock comparison: readability 4, cost 2,
power 1, accuracy 3 (user experience 0), which gives the LED clock 43 points and the round color
watch 37.

## How to Use

1. Choose a **Preset**: the worked example, four desk clock designs, wearable priorities, or a
   blank matrix of 3s.
2. Drag the **Weight** sliders to match your own priorities.
3. Change any **score** with its menu.
4. Press **Sensitivity** to see which weight the decision depends on most. (Any change clears the
   old sensitivity result, so press it again after editing.)

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/design-decision-matrix/main.html"
        height="547px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
20 minutes

### Prerequisites

- Design trade-offs (Chapter 20)
- Multiplying and adding weighted values

### Learning Objectives

Students will be able to:

- Evaluate competing clock designs with a weighted decision matrix
- Justify a choice by naming the weights that decide it
- Judge whether a decision is robust or would flip with a small change in priorities

### Activities

1. **Check the worked example** (4 min): Load the worked example and verify the totals of 43 and
   37 by hand. Press **Sensitivity**. Why is the LED clock a robust choice here?
2. **Change the user** (6 min): Load *Wearable priorities*. Which design wins now, and which two
   weights matter most? Press **Sensitivity** and explain the result in one sentence.
3. **Your own decision** (10 min): Load the blank matrix. Decide what Designs A to D are (for
   example, four clocks from this book you could build) and score each one. Set weights that match your priorities, find the
   winner, run **Sensitivity**, and write a short justification that names your two heaviest
   weights.

### Assessment

- The student calculates a weighted total by hand and matches the chart.
- The student explains how a change in priorities (weights) can reverse a decision.
- The student's written justification uses the sensitivity result to defend the choice.

## References

1. [Decision matrix](https://en.wikipedia.org/wiki/Decision_matrix) - Wikipedia article on weighted decision matrices.
2. [Pugh method](https://en.wikipedia.org/wiki/Decision-matrix_method) - Wikipedia article on the engineering decision-matrix method for comparing concepts.
3. [Sensitivity analysis](https://en.wikipedia.org/wiki/Sensitivity_analysis) - Wikipedia article on testing how much an answer depends on its inputs.
4. [Trade-off](https://en.wikipedia.org/wiki/Trade-off) - Wikipedia article on giving up one quality to gain another.
