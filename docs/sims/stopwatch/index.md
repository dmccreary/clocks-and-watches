---
title: Stopwatch
description: Interactive p5.js stopwatch simulation with start/stop and reset controls, displaying time in MM:SS.mmm format
quality_score: 72
---

# Stopwatch MicroSim

<iframe src="main.html" width="370" height="300" scrolling="no"></iframe>

**Copy this iframe to your website:**

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/stopwatch/main.html" width="370" height="300" scrolling="no"></iframe>
```

[Run the Stopwatch MicroSim in fullscreen](main.html){ .md-button .md-button--primary }

[Edit in the p5.js Editor](https://editor.p5js.org/dmccreary/sketches/8kQCSNdA6){ .md-button }

## Description

This MicroSim simulates a digital stopwatch with start/stop and reset functionality. It displays elapsed time in minutes, seconds, and milliseconds format (MM:SS.mmm), similar to what you would see on a real OLED display.

Key features:

- OLED-style black display with white text
- Start/Stop toggle button
- Reset button to clear elapsed time
- High-precision millisecond timing
- Debounce protection on button presses

### How to Use

1. Click "Start/Stop" to begin timing
2. Click "Start/Stop" again to pause
3. Click "Reset" to clear the elapsed time
4. The timer continues from where it left off when resumed

## Related Lab

The Stopwatch MicroSim allows you to simulate the actual stopwatch hardware lab: [Stopwatch Lab](../../kits/stopwatch/index.md)

## Lesson Plan

### Learning Objectives

After completing this lesson, students will be able to:

- Understand state management in user interfaces (running vs. stopped)
- Calculate elapsed time using system timestamps
- Format time values into human-readable strings

### Target Audience

- Grade level: Middle school to high school (grades 6-12)
- Prerequisites: Basic understanding of time measurement

### Activities

1. **Exploration Activity**: Use the stopwatch to time various activities and record results
2. **Guided Investigation**: Compare the accuracy of this digital stopwatch to a physical one
3. **Extension Activity**: Modify the code to add lap time functionality

### Assessment

- Can students explain how elapsed time is calculated?
- Can students describe the difference between running and stopped states?
- Can students suggest improvements to the stopwatch functionality?

## References

- [p5.js Reference](https://p5js.org/reference/) - Documentation for the p5.js library
- [JavaScript Date Object](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date) - MDN documentation on JavaScript timing
- [State Machine Design](https://en.wikipedia.org/wiki/Finite-state_machine) - Wikipedia article on finite state machines
