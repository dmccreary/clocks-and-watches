---
title: Four-Digit Digital Clock
description: An interactive p5.js simulation displaying current time using four seven-segment digits with AM/PM indicator
quality_score: 72
---

# Four-Digit Digital Clock

<iframe src="main.html" width="100%" height="280px" scrolling="no"></iframe>

**Copy this iframe to your website:**

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/4-digits/main.html" width="100%" height="280px" scrolling="no"></iframe>
```

[Run the Four-Digit Digital Clock MicroSim in fullscreen](main.html){ .md-button .md-button--primary }

## Description

This MicroSim displays the current time using a classic four-digit seven-segment display format commonly seen in digital clocks and alarm clocks. The simulation automatically updates to show hours and minutes with a blinking colon separator and an AM/PM indicator.

Key features:

- Real-time clock display synced to your device's local time
- Seven-segment digit rendering using p5.js line drawing
- 12-hour format with AM/PM indicator
- Navy blue digits on an alice blue background
- Leading zero suppression for single-digit hours

### How to Use

1. Open the simulation to see the current time displayed
2. The clock automatically updates every minute
3. The colon between hours and minutes provides visual separation
4. AM or PM is displayed to the right of the minutes

## Lesson Plan

### Learning Objectives

After completing this lesson, students will be able to:

- Understand how seven-segment displays work to show digits 0-9
- Explain the binary mapping used to control individual segments
- Apply trigonometry concepts to understand digit positioning

### Target Audience

- Grade level: Middle school to high school (grades 6-12)
- Prerequisites: Basic understanding of binary numbers and coordinate systems

### Activities

1. **Exploration Activity**: Observe which segments light up for each digit and create a mapping table
2. **Guided Investigation**: Modify the code to change colors or add seconds display
3. **Extension Activity**: Design a countdown timer or stopwatch using the same display logic

### Assessment

- Can students identify which segments are active for any given digit?
- Can students explain how the time values are split into individual digits?
- Can students modify the display colors or add new features?

## References

- [p5.js Reference](https://p5js.org/reference/) - Documentation for the p5.js library
- [Seven-Segment Display](https://en.wikipedia.org/wiki/Seven-segment_display) - Wikipedia article on seven-segment displays
