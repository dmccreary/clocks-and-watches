---
title: Binary Clock
description: Interactive p5.js simulation displaying current time in binary format using vertical LED columns
quality_score: 72
---

# Binary Clock

<iframe src="binary-clock-vertical.html" width="420" height="295" scrolling="no"></iframe>

**Copy this iframe to your website:**

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/binary-clock/binary-clock-vertical.html" width="420" height="295" scrolling="no"></iframe>
```

[Run the Binary Clock MicroSim in fullscreen](binary-clock-vertical.html){ .md-button .md-button--primary }

[Edit the Vertical Column Binary Clock MicroSim](https://editor.p5js.org/dmccreary/sketches/cv9UW1TPK){ .md-button }

## Description

This MicroSim displays the current time using binary representation with vertical LED columns. Each column represents a digit of the time (hours, minutes, seconds), with illuminated LEDs indicating binary 1s.

Key features:

- Real-time clock synchronized to local system time
- Vertical column layout for each digit
- Visual LED representation (lit = 1, unlit = 0)
- Hours, minutes, and seconds display

### How to Use

1. Read each column from bottom to top as binary digits
2. The bottom LED represents 2^0 (1), next is 2^1 (2), then 2^2 (4), and 2^3 (8)
3. Add the values of lit LEDs to get the decimal digit
4. Time is displayed as HH:MM:SS in binary

## Alternative Versions

- [Vertical Column Binary Clock](binary-clock-vertical.html) - Main version with vertical columns
- [Horizontal Binary Clock](binary-clock.html) - Alternative horizontal layout

## Lesson Plan

### Learning Objectives

After completing this lesson, students will be able to:

- Convert binary numbers to decimal values
- Read time from a binary clock display
- Explain the place value system in binary (powers of 2)

### Target Audience

- Grade level: Middle school to high school (grades 6-12)
- Prerequisites: Basic understanding of binary numbers

### Activities

1. **Exploration Activity**: Practice reading the current time from the binary display
2. **Guided Investigation**: Calculate what binary pattern will show at specific times (e.g., 12:34:56)
3. **Extension Activity**: Design your own binary clock layout or add color coding

### Assessment

- Can students correctly read the time from the binary display?
- Can students predict the binary pattern for a given time?
- Can students explain why 4 LEDs are sufficient for each digit?

## References

- [Binary Clock](https://en.wikipedia.org/wiki/Binary_clock) - Wikipedia article on binary clocks
- [Binary Number System](https://www.mathsisfun.com/binary-number-system.html) - Math is Fun binary tutorial
- [p5.js Reference](https://p5js.org/reference/) - Documentation for the p5.js library
