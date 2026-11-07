---
title: Analog Watch Face Builder
description: Design an analog face for a 360 by 360 round display by choosing tick, numeral, and hand radii and a color palette, then use Erase mode to see which pixels an erased second hand destroys and which repairs the layout needs.
image: /sims/analog-watch-face-builder/analog-watch-face-builder.png
og:image: /sims/analog-watch-face-builder/analog-watch-face-builder.png
twitter:image: /sims/analog-watch-face-builder/analog-watch-face-builder.png
social:
   cards: false
quality_score: 100
---

# Analog Watch Face Builder

<iframe src="main.html" height="547px" width="100%" scrolling="no"></iframe>

[Run the Analog Watch Face Builder MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/analog-watch-face-builder/main.html"
        height="547px"
        width="100%"
        scrolling="no"></iframe>
```

## About This MicroSim

The GC9B72 round display in the Chrono Smart Clock Kit is a **direct write** display: there is no framebuffer and no `show()`. To move the second hand, your program **erases** the old hand by drawing it again in black, then draws the new one. Anything the old hand was lying on top of, such as a numeral or a tick mark, gets erased too and must be **repaired**.

The best fix is a good layout. If the hands never reach the numerals or ticks, an erase can never damage them. This MicroSim lets you design the layout and test it.

The display is 360 by 360 pixels with its center at (180, 180). The dashed ring is the **safe radius** of 168 pixels; anything outside it is hidden under the bezel. Every item is placed with the same polar formula used in Chapter 15:

```python
def polar(angle_deg, radius):
    a = math.radians(angle_deg)
    return (CENTER_X + int(radius * math.sin(a)),
            CENTER_Y - int(radius * math.cos(a)))
```

The readout checks the layout with **bounding circles**. Each numeral is treated as a circle 14 pixels in radius around its position, so a hand longer than the numeral radius minus 14 will cross a numeral at some point in its sweep. Hour marks are 20 pixels long and minute marks 10, measured inward from the tick outer radius. The opening layout uses the kit's hand lengths (minute 92, second 138), and one repair is needed: the second hand crosses the numerals.

## How to Use

1. Read the **Repairs needed** list. It starts with one problem.
2. Drag **Numeral radius**, **Minute hand**, and **Second hand** until the readout says **Repairs needed: none**. There is more than one good answer.
3. Turn on **Erase mode**. The old second-hand position (one second ago) is drawn in black, and any pixels of other items that the erase destroyed are marked in **yellow**, with a list of what must be redrawn.
4. Press **Step +1 s** to move one second at a time, or **Play** to let the seconds advance on their own. Press **Pause** to stop.
5. Drag **Tick outer** past the safe ring to see the bezel warning, and try a different color palette in the menu.

## Lesson Plan

### Learning Objective

Students will create an analog face by choosing radii and colors, and analyze which parts an erased hand damages (Bloom: Analyzing, Creating).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
20 minutes

### Prerequisites

- Polar coordinates and clock angles (Chapter 10)
- Round displays, the safe radius, and direct write displays (Chapter 15)

### Activities

1. **Diagnose** (4 min): With Erase mode on, students press Step until the second hand passes several numerals and record which items turn yellow. Why do only some seconds cause damage?
2. **Design** (6 min): Students find a layout with "Repairs needed: none" that keeps the second hand as long as possible. Record the four radii.
3. **Trade-offs** (5 min): Compare two layouts. A long second hand is easy to read but forces numerals inward or causes repairs. Which would you ship, and why?
4. **Create** (5 min): Choose a palette and write the layout as Python constants (`TICK_OUTER`, `NUMERAL_RADIUS`, `MINUTE_LENGTH`, `SECOND_LENGTH`) for your own watch face.

### Assessment

- With the tick outer radius at 162, what is the longest second hand that never touches an hour mark? (142.)
- A numeral sits at radius 120 with a bounding radius of 14. What hand lengths avoid it? (Up to 106.)
- Explain why repairs matter on a direct write display but not on a framebuffer display such as the OLED from Chapter 11.

## References

1. [Polar coordinate system](https://en.wikipedia.org/wiki/Polar_coordinate_system) - Wikipedia; the radius and angle placement used for every item on the face.
2. [Bounding volume](https://en.wikipedia.org/wiki/Bounding_volume) - Wikipedia; why simple circles make fast overlap tests.
3. [Clock face](https://en.wikipedia.org/wiki/Clock_face) - Wikipedia article on dial layouts, numerals, and hands.
4. [Chrono Smart Clock Kit](../../kits/sw-gc9b72/index.md) - The kit with the 360 by 360 GC9B72 round display.
