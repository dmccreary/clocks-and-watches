---
title: Unit Circle Explorer
description: See sine and cosine as the vertical and horizontal parts of a point on a circle of radius 1, with matching bars and graphs.
image: /sims/unit-circle-explorer/unit-circle-explorer.png
og:image: /sims/unit-circle-explorer/unit-circle-explorer.png
twitter:image: /sims/unit-circle-explorer/unit-circle-explorer.png
social:
   cards: false
quality_score: 0
---

# Unit Circle Explorer

<iframe src="main.html" height="492px" width="100%" scrolling="no"></iframe>

[Run the Unit Circle Explorer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A **unit circle** has a radius of 1. A point on it at angle \( \theta \) sits at
\( (\cos\theta, \sin\theta) \): cosine is how far the point is to the right (or left) of the
center, and sine is how far it is above (or below).

One angle drives everything on the screen:

- The **blue** horizontal bar under the circle is the cosine, and the **red** vertical bar to the
  left is the sine. Dashed lines connect the point to each bar.
- With **Right triangle** on, the blue and red legs plus the black radius form the triangle from
  the trigonometry section: the radius is the hypotenuse (length 1).
- The two graphs plot sine and cosine for every angle from 0 to 360 degrees, with an orange
  marker at the current angle.

This explorer uses the math convention: angle 0 points right (3 o'clock) and angles grow
counterclockwise. The next MicroSim, the Polar to Screen Converter, switches to the clock
convention used on a watch face.

The spec asked for a **Play** button that spins the radius continuously. For an "understand"
goal, stepping is clearer, so this version uses **-15 / +15 degree** step buttons and the slider.
Each step lets you stop, predict the signs of sine and cosine, and then check.

## How to Use

1. Drag the **Angle** slider and watch the two bars grow and shrink.
2. Press **+15 degrees** repeatedly. Before each press, predict whether sine and cosine will be
   positive or negative.
3. Find the angles where the cosine bar disappears. What are sine's values there?
4. Switch **Degrees** to **Radians** and find the angle that equals pi.
5. Turn off **Values** and estimate sin and cos from the bars alone, then turn it back on to check.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/unit-circle-explorer/main.html"
        height="492px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Degrees and radians (Chapter 10)
- Right triangles: hypotenuse, opposite and adjacent sides

### Learning Objectives

Students will be able to:

- Explain sine as the vertical part and cosine as the horizontal part of a point on a circle
- Predict the sign of sine and cosine in each quarter of the circle
- Convert between degrees and radians for key angles

### Activities

1. **Four quarters** (5 min): Make a table with one row for each quarter of the circle (0-90, 90-180, 180-270, 270-360). Fill in the sign of sin and cos for each, then check with the explorer.
2. **Same value twice** (5 min): Find two different angles where sin = 0.5. Explain using the circle why there are two.
3. **Back to the clock** (5 min): At what angle does the point sit at the top of the circle? Explain why a clock needs a different starting point and direction.

### Assessment

- The student states that cos 90 degrees = 0 and sin 90 degrees = 1 and shows why on the circle.
- The student predicts both signs for an angle such as 225 degrees before checking.
- The student converts 180 degrees to pi radians.

## References

1. [Unit circle](https://en.wikipedia.org/wiki/Unit_circle) - Wikipedia article on the circle of radius 1 and its link to sine and cosine.
2. [Sine and cosine](https://en.wikipedia.org/wiki/Sine_and_cosine) - Wikipedia article with definitions and graphs.
3. [Radian](https://en.wikipedia.org/wiki/Radian) - Wikipedia article on measuring angles by arc length.
4. [Python math module](https://docs.python.org/3/library/math.html#trigonometric-functions) - Official documentation for math.sin(), math.cos() and math.radians().
