---
title: Polar to Screen Converter
description: Convert a radius and a clockwise clock angle into pixel coordinates on a 240 by 240 screen, and practice predicting x and y.
image: /sims/polar-to-screen/polar-to-screen.png
og:image: /sims/polar-to-screen/polar-to-screen.png
twitter:image: /sims/polar-to-screen/polar-to-screen.png
social:
   cards: false
quality_score: 0
---

# Polar to Screen Converter

<iframe src="main.html" height="632px" width="100%" scrolling="no"></iframe>

[Run the Polar to Screen Converter MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A clock hand is easiest to describe in **polar** form: how long it is (\( r \)) and which way it points
(\( \theta \)). The screen needs **pixel** coordinates instead. This MicroSim shows the conversion
on a 240 by 240 round-display grid whose origin (0, 0) is the **top-left** corner and whose
center is (120, 120).

Clock angles start at 12 o'clock and grow **clockwise**, and screen y grows **downward**. That
gives the pair of formulas from the chapter:

\[ x = c_x + r \sin\theta \qquad y = c_y - r \cos\theta \]

The green line runs from the center to the orange point. Dashed lines carry the point's x and y
out to the axes, and the label shows (x, y). With **Show formula** on, the panel substitutes the
current numbers into each formula, step by step. Results are truncated toward zero, like
`int()` in the chapter's `polar_to_xy()` function.

**Predict mode** hides the point and its coordinates. Type your x and y and press **Check**.
Answers within 1 pixel count as correct.

## How to Use

1. Set **Radius r** to 100 and move **Angle** to 0, 90, 180 and 270. Compare the points with the
   chapter's examples.
2. Read the substituted formulas in the panel. Which part of each formula changes sign?
3. Turn on **Predict mode** (or press **New point**). Work out x and y on paper or with a
   calculator.
4. Type your answers in the **x =** and **y =** boxes and press **Check**.
5. Press **New point** for another problem.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/polar-to-screen/main.html"
        height="632px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Sine and cosine (Chapter 10)
- Screen coordinates with the origin at the top-left (Chapter 10)

### Learning Objectives

Students will be able to:

- Apply x = cx + r sin(theta) and y = cy - r cos(theta) to find pixel coordinates
- Predict the pixel position of a clock-hand tip before it is revealed
- Explain why screen y uses a minus sign

### Activities

1. **Check the chapter** (4 min): Reproduce both printed examples from polar_to_xy(): (100, 90 degrees) and (100, 180 degrees).
2. **Five predictions** (8 min): In Predict mode, solve five New point problems. Record each guess, the answer and any mistake.
3. **Minute hand** (3 min): Find where the tip of a 90-pixel minute hand points at 20 minutes past the hour (120 degrees).

### Assessment

- The student computes (220, 120) for r = 100 at 90 degrees.
- The student explains that the minus sign makes points above the center have smaller y.
- The student gets at least four of five Predict mode problems within 1 pixel.

## References

1. [Polar coordinate system](https://en.wikipedia.org/wiki/Polar_coordinate_system) - Wikipedia article on describing points by radius and angle.
2. [Sine and cosine](https://en.wikipedia.org/wiki/Sine_and_cosine) - Wikipedia article on the two functions used in the conversion.
3. [Python math module](https://docs.python.org/3/library/math.html#trigonometric-functions) - Official documentation for math.radians(), math.sin() and math.cos().
4. [Clock face](https://en.wikipedia.org/wiki/Clock_face) - Wikipedia article on the layout of an analog dial.
