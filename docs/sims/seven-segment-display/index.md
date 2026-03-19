---
title: Seven-Segment Display
description: Interactive p5.js simulation demonstrating how seven-segment displays work with individual segment control
image: /sims/seven-segment-display/7-segment-display.png
og:image: /sims/seven-segment-display/7-segment-display.png
quality_score: 72
---

# Seven-Segment Display

<iframe src="7-segment-display.html" width="100%" height="500px" scrolling="no"></iframe>

**Copy this iframe to your website:**

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/seven-segment-display/7-segment-display.html" width="100%" height="500px" scrolling="no"></iframe>
```

[Run the Seven-Segment Display MicroSim in fullscreen](7-segment-display.html){ .md-button .md-button--primary }

## Description

This MicroSim demonstrates how seven-segment displays work by allowing users to control individual segments. Seven-segment displays are the most common way to display digits on digital clocks, calculators, and many electronic devices.

Key features:

- Interactive control of all 7 segments (A-G)
- Visual representation of segment layout
- Learn the standard segment naming convention
- See how different combinations create digits 0-9

### How to Use

1. Toggle individual segments using the controls
2. Observe how each segment contributes to the display
3. Try to create each digit from 0 to 9
4. Note the segment pattern for each number

## Segment Layout

```
   AAA
  F   B
  F   B
   GGG
  E   C
  E   C
   DDD
```

| Digit | A | B | C | D | E | F | G |
|-------|---|---|---|---|---|---|---|
| 0 | 1 | 1 | 1 | 1 | 1 | 1 | 0 |
| 1 | 0 | 1 | 1 | 0 | 0 | 0 | 0 |
| 2 | 1 | 1 | 0 | 1 | 1 | 0 | 1 |
| 3 | 1 | 1 | 1 | 1 | 0 | 0 | 1 |
| 4 | 0 | 1 | 1 | 0 | 0 | 1 | 1 |
| 5 | 1 | 0 | 1 | 1 | 0 | 1 | 1 |
| 6 | 1 | 0 | 1 | 1 | 1 | 1 | 1 |
| 7 | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
| 8 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| 9 | 1 | 1 | 1 | 1 | 0 | 1 | 1 |

## Lesson Plan

### Learning Objectives

After completing this lesson, students will be able to:

- Identify all seven segments by their standard names (A-G)
- Determine which segments must be lit to display any digit
- Explain how binary values control segment states

### Target Audience

- Grade level: Middle school to high school (grades 6-12)
- Prerequisites: Basic understanding of binary on/off states

### Activities

1. **Exploration Activity**: Manually create each digit 0-9 using the segment controls
2. **Guided Investigation**: Record the binary pattern for each digit in a table
3. **Extension Activity**: Design letters using the seven segments (e.g., A, b, C, d, E, F for hexadecimal)

### Assessment

- Can students recreate any digit from 0-9 without reference?
- Can students explain why certain letters cannot be displayed clearly?
- Can students identify which segment is faulty given a broken display?

## References

- [Seven-Segment Display](https://en.wikipedia.org/wiki/Seven-segment_display) - Wikipedia article with history and applications
- [p5.js Reference](https://p5js.org/reference/) - Documentation for the p5.js library
- [LED Display Technology](https://www.electronics-tutorials.ws/blog/7-segment-display-tutorial.html) - Electronics tutorial on seven-segment displays
