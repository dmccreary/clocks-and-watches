---
title: Tilt and Step Explorer
description: Drag a 3D watch to see gravity move between the accelerometer's x, y and z axes, then tune a step counter's threshold and minimum time between steps on a simulated walk.
image: /sims/tilt-step-explorer/tilt-step-explorer.png
og:image: /sims/tilt-step-explorer/tilt-step-explorer.png
twitter:image: /sims/tilt-step-explorer/tilt-step-explorer.png
social:
   cards: false
quality_score: 0
---

# Tilt and Step Explorer

<iframe src="main.html" height="547px" width="100%" scrolling="no"></iframe>

[Run the Tilt and Step Explorer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

An accelerometer at rest does not read zero. It reads **1 g** pointing up, away from the
ground, and it splits that 1 g among its three axes depending on how it is tilted. This
MicroSim has two panels.

**Tilt (left).** Drag the watch to tilt it. The red, green and blue arrows are the sensor's
x, y and z axes, and the bars show how many g each axis reads. The label uses the rules from
the chapter: *Face up* when \( a_z > 0.8 \) and *Wrist raised* when \( a_y < -0.5 \) and
\( |a_z| < 0.6 \). (In this watch the sensor is mounted so that its y axis points toward 6
o'clock, which is why raising your wrist makes \( a_y \) negative.)

**Steps (right).** A step counter combines the three axes into one magnitude,
\( |a| = \sqrt{a_x^2 + a_y^2 + a_z^2} \), which stays near 1 g at rest no matter how the watch
is tilted. Each footstep makes a bump. The counter adds a step every time \( |a| \) crosses
**upward** through the threshold (dashed red line), but ignores any crossing that comes
sooner than the **minimum time between steps** after the last counted one. Orange markers show
the counted steps, and the readout compares them with the real number of steps in the
5-second window.

## How to Use

1. Drag the watch up and down and side to side. Find a tilt that shows *Wrist raised*.
2. Notice that the magnitude stays 1.00 g whatever the tilt.
3. The step plot opens paused with 5 seconds of walking already recorded. Press **Walk** to
   keep walking and **Stop** to freeze the plot.
4. Move the **Step threshold** slider up and down and watch the counted steps change.
5. Set **Min time between steps** to 0 ms and see what happens to the count.
6. Press **Reset** to return the watch to flat and reload the original recording.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/tilt-step-explorer/main.html"
        height="547px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15-20 minutes

### Prerequisites

- Accelerometer basics and units of g (Chapter 18)
- Debouncing a button with a minimum time between presses (Chapter 7)

### Learning Objectives

Students will be able to:

- Apply the x, y and z readings of an accelerometer to decide whether a watch is face up or on a raised wrist
- Analyze how the step threshold changes missed steps and extra steps
- Explain why a minimum time between steps prevents one footstep from counting twice

### Activities

1. **Tilt rules** (5 min): Find a tilt where the label reads *Wrist raised*. Record \( a_x \),
   \( a_y \) and \( a_z \), then check them against the `wrist_raised()` rule in the chapter.
   Why is \( |a| \) still 1.00 g?
2. **Threshold sweep** (5 min): With the walk paused, move the threshold from 1.00 g to 2.00 g.
   Record the counted steps at 1.05, 1.20, 1.40 and 1.60 g. Where is the count correct, and why
   does it fail at each end?
3. **Double counting** (5 min): Set the threshold to 1.15 g and the minimum time to 0 ms. Count
   the extra steps. Raise the minimum time until the count matches. What is the smallest time
   that works, and why should it be less than half a second for walking?

### Assessment

- The student explains why a very low threshold counts noise and a very high threshold misses light steps.
- The student identifies the second bump of each footstep as the cause of double counting.
- The student connects the minimum-time rule to button debouncing in Chapter 7.

## References

1. [Accelerometer](https://en.wikipedia.org/wiki/Accelerometer) - Wikipedia article on how accelerometers measure acceleration and gravity.
2. [Pedometer](https://en.wikipedia.org/wiki/Pedometer) - Wikipedia article on step counting devices and their accuracy.
3. [MPU-6050 product page (TDK InvenSense)](https://invensense.tdk.com/products/motion-tracking/6-axis/mpu-6050/) - The accelerometer and gyroscope chip used in Chapter 18.
4. [Switch debouncing](https://en.wikipedia.org/wiki/Switch#Contact_bounce) - Wikipedia section on contact bounce, the same idea as the minimum time between steps.
