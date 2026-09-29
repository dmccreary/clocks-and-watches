---
title: Coordinates, Trigonometry, and Clock Geometry
description: Coordinates, radians, sine and cosine, and polar geometry for placing clock hands and tick marks on a display.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:38:33
version: 1.10
---

# Coordinates, Trigonometry, and Clock Geometry

## Summary

Students work with X-Y pixel coordinates, radians, sine, cosine, and polar coordinates. They compute hand angles and tick positions. After this chapter they can calculate where to draw any point on a clock face.

## Concepts Covered

This chapter covers the following 13 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Radians vs Degrees | 29 |
| X Y Coordinate System | 40 |
| Integer Math Tricks | 2 |
| Trigonometry Basics | 28 |
| Center Point Calculation | 8 |
| Fixed Point Arithmetic | 1 |
| Sine Function | 4 |
| Cosine Function | 4 |
| Polar Coordinates | 8 |
| Clock Hand Length | 4 |
| Angle Calculation | 7 |
| Tick Mark Geometry | 3 |
| Rotation Math | 2 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)

---

!!! mascot-welcome "Math With a Purpose"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Ever wonder how a screen knows where to draw the tip of a clock hand? It's a little trigonometry, and this chapter gives you a clear, no-fear recipe for it. Get this right and every analog face in the book becomes easy. Let's make time tick!

## Why a Clock Needs Geometry

A digital clock only needs digits. An **analog** clock draws hands that point at the correct angle, and to draw a hand the Pico must turn "it is 3:30" into "draw a line from the center to the pixel at (x, y)." That conversion uses coordinates, angles, and two functions from trigonometry, sine and cosine. You will learn each piece and then combine them into one short formula that places any hand, tick mark, or digit on a round display.

## X Y Coordinate System

A display is a grid of pixels, and each pixel is located by two numbers: **x**, the column counted from the left, and **y**, the row counted from the top. Together they form a **coordinate** written as `(x, y)`.

The screen's coordinate system differs from the math class graph you may know in one important way:

| Property | Math class | Display |
|----------|-----------|---------|
| Origin (0, 0) | Bottom-left | **Top-left** |
| x increases | To the right | To the right |
| y increases | **Upward** | **Downward** |

That flipped y-axis catches almost everyone once. On a 240 by 240 display, the top-left pixel is (0, 0) and the bottom-right is (239, 239). A point that is "higher" on the screen has a *smaller* y.

**Worked example.** You want to draw a horizontal line one third of the way down a 240-pixel-tall screen, from the left edge to the right edge. One third down is \( y = 240 / 3 = 80 \). The line runs from (0, 80) to (239, 80). To move a shape **up** by 10 pixels you *subtract* 10 from y.

!!! mascot-warning "Upside-Down Y"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If your hands point down when they should point up, the y-axis is flipped. Math formulas assume y goes up, but the screen's y goes down, so the sign of the y term must be reversed. Every formula in this chapter already accounts for that.

### Center Point Calculation

Analog hands all start at the **center point** of the face. For a screen of a given width and height, the center is half of each:

\[ c_x = \frac{W}{2} \qquad c_y = \frac{H}{2} \]

Use integer division in code so the result stays a whole number:

```python
WIDTH = 240
HEIGHT = 240
cx = WIDTH // 2      # 120
cy = HEIGHT // 2     # 120
radius = min(cx, cy) # 120: distance from the center to the nearest edge
```

For the 360 by 360 round display used in the Chrono Smart Clock Kit, the center is (180, 180) and the radius is 180. Compute these from `WIDTH` and `HEIGHT` instead of typing numbers, and the same program will work on any screen.

## Radians vs Degrees

An **angle** measures a turn. Two units are common:

- **Degrees** split a full circle into 360 parts. This is the unit people use.
- **Radians** measure a turn by the length of arc along a circle of radius 1. A full circle is \( 2\pi \approx 6.283 \) radians.

MicroPython's math functions, like most programming languages, expect **radians**. Converting between them uses one relationship, that 180 degrees equals \( \pi \) radians:

\[ \text{radians} = \text{degrees} \times \frac{\pi}{180} \]

```python
import math
angle_rad = math.radians(90)     # 1.5708
angle_deg = math.degrees(1.5708) # about 90
```

| Degrees | Radians | Clock position |
|---------|---------|----------------|
| 0 | 0 | 12 o'clock |
| 90 | \( \pi/2 \approx 1.571 \) | 3 o'clock |
| 180 | \( \pi \approx 3.142 \) | 6 o'clock |
| 270 | \( 3\pi/2 \approx 4.712 \) | 9 o'clock |

Sending a degree value to `math.sin()` without converting is a classic mistake. It gives an answer, just the wrong one.

## Trigonometry Basics

**Trigonometry** is the mathematics of triangles and the angles inside them. For a right triangle, where one angle is exactly 90 degrees, three sides matter: the **hypotenuse** (the longest side, opposite the right angle), the **opposite** side (across from the angle you care about), and the **adjacent** side (next to that angle). The ratios of these sides depend only on the angle.

The two ratios we need are:

\[ \sin\theta = \frac{\text{opposite}}{\text{hypotenuse}} \qquad \cos\theta = \frac{\text{adjacent}}{\text{hypotenuse}} \]

Rearranged, they tell you the length of each side when you know the hypotenuse and angle. That is what we need: the hand is the hypotenuse, so the horizontal and vertical distances to its tip come from the angle.

### Sine Function

The **sine function**, `math.sin(angle)`, takes an angle in radians and returns a number between -1 and 1. It is 0 at 0 degrees, rises to 1 at 90 degrees, returns to 0 at 180, drops to -1 at 270, and repeats every 360. Sine tells you the *vertical* part of a point on a circle.

### Cosine Function

The **cosine function**, `math.cos(angle)`, has the same shape as sine but shifted a quarter turn. It equals 1 at 0 degrees, 0 at 90, -1 at 180, 0 at 270. Cosine tells you the *horizontal* part of a point on a circle.

| Angle | sin | cos |
|-------|-----|-----|
| 0° | 0 | 1 |
| 90° | 1 | 0 |
| 180° | 0 | -1 |
| 270° | -1 | 0 |

A handy way to picture this is the **unit circle**: a circle of radius 1. A point at angle \( \theta \) on it is \( (\cos\theta, \sin\theta) \). Multiplying by a radius \( r \) gives a point on a circle of any size.

#### Diagram: Unit Circle Explorer

<details markdown="1">
<summary>Unit Circle Explorer</summary>
Type: MicroSim
**sim-id:** unit-circle-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *understand* sine and cosine as the vertical and horizontal parts of a point on a circle (Bloom: Understanding).

**Visual elements:** A circle with a rotating radius and a colored point. A horizontal bar shows the cosine value and a vertical bar shows the sine value. Two small graphs to the right plot sine and cosine against angle.

**Controls:** Slider "Angle" (0 to 360 degrees) with a toggle "Degrees/Radians"; a "Play" button that rotates continuously; checkboxes to show the right triangle and the values.

**Responsive design:** Circle and graphs scale to container width; graphs move below the circle on narrow screens.

Implementation: p5.js with `sin` and `cos` drawn from a single angle variable.
</details>

## Polar Coordinates

**Polar coordinates** describe a point by *how far* it is from the center and *in which direction*, instead of by x and y. A polar coordinate is written \( (r, \theta) \): the radius \( r \) and the angle \( \theta \). A clock hand is naturally polar, since its description is "length 90, pointing at 180 degrees."

The screen needs x and y, so we convert. Clock angles are measured **clockwise from 12 o'clock**, and the y-axis points down. Working through both changes gives this pair:

\[ x = c_x + r \sin\theta \]

\[ y = c_y - r \cos\theta \]

where \( \theta \) is in radians and increases clockwise starting at 12. Check it: at \( \theta = 0 \) (12 o'clock), \( x = c_x \) and \( y = c_y - r \), a point straight above the center, which is correct. At \( \theta = 90^\circ \) (3 o'clock), \( x = c_x + r \) and \( y = c_y \), a point to the right. 

```python
import math

def polar_to_xy(cx, cy, r, degrees):
    a = math.radians(degrees)
    x = cx + int(r * math.sin(a))
    y = cy - int(r * math.cos(a))
    return x, y

print(polar_to_xy(120, 120, 100, 90))    # (220, 120): 3 o'clock
print(polar_to_xy(120, 120, 100, 180))   # (120, 220): 6 o'clock
```

!!! mascot-thinking "Sin for X, Cos for Y (With a Minus)"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    On a clock, angles start at 12 and go clockwise, which swaps the usual roles: sine goes with x, and cosine goes with y, negated because the screen's y points down. Once you memorize this pair, every hand, tick, and number on a round face uses the same two lines.

#### Diagram: Polar to Screen Converter

<details markdown="1">
<summary>Polar to Screen Converter</summary>
Type: MicroSim
**sim-id:** polar-to-screen<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* the polar conversion formulas and *predict* pixel coordinates (Bloom: Applying).

**Visual elements:** A 240 by 240 screen grid with axes showing pixel coordinates (origin at top-left). A line from the center to a movable point labeled with its (x, y) pixel position and its (r, θ) polar position.

**Controls:** Sliders for radius (0 to 120) and angle (0 to 359); a toggle to show the formula with the current numbers substituted; a "Predict" mode where the student types the x and y before they are revealed.

**Responsive design:** Grid scales to the canvas size.

Implementation: p5.js with `sin` and `cos` on the formula above.
</details>

## Angle Calculation

An analog clock has three hands that each sweep a full circle at a different rate. Converting the time to an angle in degrees comes down to counting how many degrees per unit:

| Hand | Full circle takes | Degrees per unit | Angle formula |
|------|-------------------|------------------|---------------|
| Second | 60 seconds | 6° per second | \( 6s \) |
| Minute | 60 minutes | 6° per minute | \( 6m + 0.1s \) |
| Hour | 12 hours | 30° per hour | \( 30(h \bmod 12) + 0.5m \) |

The extra terms make the hands move smoothly. The minute hand creeps forward 0.1 degrees each second (6° divided by 60 s), and the hour hand creeps 0.5 degrees each minute (30° divided by 60 min). Without them the hour hand would jump from the 3 straight to the 4 on the hour, which looks wrong at 3:59.

**Worked example.** At 3:30:00, the hour hand is at \( 30 \times 3 + 0.5 \times 30 = 105^\circ \), halfway between the 3 and the 4. The minute hand is at \( 6 \times 30 = 180^\circ \), pointing straight down at the 6. The second hand is at 0°, pointing up.

```python
def hand_angles(h, m, s):
    sec_angle = s * 6
    min_angle = m * 6 + s * 0.1
    hour_angle = (h % 12) * 30 + m * 0.5
    return hour_angle, min_angle, sec_angle

print(hand_angles(3, 30, 0))    # (105.0, 180.0, 0)
```

The interactive clock below shows the hand positions changing as the time changes.

#### Diagram: Analog Clock Simulation

<iframe src="../../sims/analog-clock/analog-clock.html" width="100%" height="550px" scrolling="no"></iframe>

[Run the Analog Clock MicroSim fullscreen](../../sims/analog-clock/analog-clock.html){ .md-button }

<details markdown="1">
<summary>Analog Clock (existing MicroSim)</summary>
Type: MicroSim
**sim-id:** analog-clock<br/>
**Library:** p5.js<br/>
**Status:** Reused<br/>
**Source:** docs/sims/analog-clock/

This MicroSim is already part of this book. Learning objective: students will *apply* angle formulas to see how time values position each hand (Bloom: Applying).
</details>

## Clock Hand Length

Each hand has a **length** measured from the center. The hands are different lengths so you can tell them apart at a glance: the hour hand is shortest and stubbiest, the minute hand is longer, and the second hand is longest and thinnest. Express each length as a fraction of the face **radius**, so the design scales with any display.

| Hand | Fraction of radius | On a 240 px face (radius 120) |
|------|-------------------|-------------------------------|
| Hour | 0.50 | 60 px |
| Minute | 0.75 | 90 px |
| Second | 0.90 | 108 px |

Now you can combine everything into one tip-position calculation per hand:

```python
NAME = "10-hand-tips.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
from time import localtime

cx, cy, radius = 120, 120, 120

def tip(angle_deg, length):
    a = math.radians(angle_deg)
    return cx + int(length * math.sin(a)), cy - int(length * math.cos(a))

h, m, s = localtime()[3:6]
hour_angle = (h % 12) * 30 + m * 0.5
min_angle = m * 6 + s * 0.1
sec_angle = s * 6

print("hour tip:", tip(hour_angle, radius * 0.50))
print("min tip: ", tip(min_angle, radius * 0.75))
print("sec tip: ", tip(sec_angle, radius * 0.90))
```

Each printed pair is where the far end of a hand should be. In Chapter 12, you will hand these pairs to a line-drawing function.

## Tick Mark Geometry

**Tick marks** are the small lines around the edge of the face that mark minutes and hours. There are 60 of them, one every 6 degrees, and every fifth one (every 30 degrees) is longer to mark an hour. Each tick is a short line from an outer radius to an inner radius along the same angle, so you compute two points with the same formula from before and connect them:

```python
for i in range(60):
    angle = i * 6
    inner = radius - (12 if i % 5 == 0 else 6)     # hour ticks are longer
    x1, y1 = tip(angle, radius - 2)                # outer end
    x2, y2 = tip(angle, inner)                     # inner end
```

## Rotation Math

Sometimes a hand is a shape, such as a triangle, rather than a line. To point it in any direction, **rotate** each of its corner points around the center. For a point \( (x, y) \) measured from the center, rotating by angle \( \theta \) gives

\[ x' = x\cos\theta - y\sin\theta \qquad y' = x\sin\theta + y\cos\theta \]

You compute the sine and cosine once, then apply those two lines to each corner. Because the screen's y-axis points down, a positive angle turns the shape clockwise on the display. This is the same idea as the polar conversion, applied to several points instead of one.

## Integer Math Tricks

The RP2040 has no floating-point hardware, so every `sin()` and `cos()` is done in software, which is relatively slow. Calling them for 60 tick marks each frame wastes time. A few **integer math tricks** avoid floats:

- Use `//` instead of `/` for whole-number division.
- Use `>> n` to divide by \( 2^n \) and `<< n` to multiply by \( 2^n \), for instance `x >> 1` is `x // 2`.
- Do arithmetic in whole numbers first and convert to floats only at the end, if at all.
- Precompute values that never change, such as the tick-mark positions, once at startup.

## Fixed Point Arithmetic

**Fixed-point arithmetic** stores fractions as integers by multiplying by a fixed **scale factor**, typically a power of two such as 256. To represent 0.5 you store 128. To get the real value back you divide (or shift right) by the scale.

Here is the payoff for clock faces. Sine and cosine only need to be computed for the 60 angles that occur, and their results can be stored once as scaled integers in a **lookup table**:

```python
import math
SCALE = 256
SIN = [int(math.sin(math.radians(i * 6)) * SCALE) for i in range(60)]
COS = [int(math.cos(math.radians(i * 6)) * SCALE) for i in range(60)]

def tip_fast(i, length):           # i is 0..59 for seconds or minutes
    x = cx + ((length * SIN[i]) >> 8)     # >> 8 divides by 256
    y = cy - ((length * COS[i]) >> 8)
    return x, y
```

The tables cost a moment at startup, and every frame afterward uses only integer multiplication and shifts. The rounding error is at most \( 1/256 \) of the length, less than half a pixel for a 120-pixel hand.

!!! mascot-tip "Precompute Once, Draw Forever"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    If a calculation gives the same answer every time, such as where the minute ticks go, do it once when the program starts and reuse the results. It makes redraws faster and frees the Pico to do other work.

## Putting It Together

| To place... | Use |
|-------------|-----|
| The center | \( c_x = W//2,\ c_y = H//2 \) |
| Any point at distance \( r \), clock angle \( \theta \) | \( x = c_x + r\sin\theta,\ y = c_y - r\cos\theta \) |
| Second hand angle | \( 6s \) |
| Minute hand angle | \( 6m + 0.1s \) |
| Hour hand angle | \( 30(h \bmod 12) + 0.5m \) |
| A fast version | Lookup tables with fixed-point scale 256 |

## Key Takeaways

- Screen coordinates start at the top-left, and y increases downward.
- Angles for `math.sin()` and `math.cos()` must be in radians; use `math.radians()`.
- For clock angles measured clockwise from 12: \( x = c_x + r\sin\theta \) and \( y = c_y - r\cos\theta \).
- Hands turn 6° per second, 6° per minute, and 30° per hour, plus small extra terms for smooth motion.
- Express hand lengths as fractions of the radius so the face scales.
- Lookup tables and fixed-point arithmetic keep drawing fast on a Pico with no floating-point hardware.

!!! mascot-celebration "Geometry Unlocked"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now convert any time into hand angles, turn angles into pixel positions, and speed it all up with lookup tables. You have every equation needed for an analog watch face. Every second counts!

## Practice Questions

1. On a 320 by 240 screen, what is the center point? Which direction is y increasing?
2. Convert 45 degrees to radians. Leave your answer in terms of \( \pi \) and as a decimal.
3. Compute the three hand angles at 9:15:00 and the pixel position of the minute hand tip on a 240 by 240 display with length 90.
4. Why do we add \( 0.5m \) to the hour hand angle?
5. A lookup table uses SCALE = 256. What integer represents the sine of 30 degrees, and what is the maximum error in a hand of length 120?
