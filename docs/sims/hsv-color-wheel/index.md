---
title: HSV Color Wheel
description: Explore hue, saturation, and value on a color wheel with a draggable marker, see the RGB values from the same integer hsv_to_rgb function used on the Pico, and watch a 12-pixel virtual NeoPixel ring show and rotate the rainbow.
image: /sims/hsv-color-wheel/hsv-color-wheel.png
og:image: /sims/hsv-color-wheel/hsv-color-wheel.png
twitter:image: /sims/hsv-color-wheel/hsv-color-wheel.png
social:
   cards: false
quality_score: 100
---

# HSV Color Wheel

<iframe src="main.html" height="602px" width="100%" scrolling="no"></iframe>

[Run the HSV Color Wheel MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

NeoPixels want red, green, and blue numbers, but people think about color differently: "the same color, only dimmer," or "move around the rainbow." The **HSV** model matches that way of thinking:

- **Hue** is the color itself, an angle from 0 to 359 degrees around the wheel. Here 0 (red) is at the top and the angle grows clockwise, just like the clock angles of Chapter 10. 120 is green and 240 is blue.
- **Saturation** is how vivid the color is, from gray at the center of the wheel (0) to pure color at the rim (255).
- **Value** is the brightness, from 0 (off) to 255 (full). Lowering it dims the whole wheel.

Every color in this MicroSim is computed with the same integer `hsv_to_rgb(h, s, v)` function as the MicroPython code in Chapter 16, so the R, G, and B readouts are exactly what your Pico would send with `np[i] = (r, g, b)`. The gray lines show the first steps inside the function: which 60-degree **region** of the wheel the hue falls in, the remainder **rem**, and **p**, the lowest channel.

The 12-pixel ring is a virtual NeoPixel ring running the chapter's rainbow program. Pixel `i` gets the hue `(i * 360 // 12 + offset) % 360` with your saturation and value.

## How to Use

1. Drag the marker on the wheel, or use the **Hue** and **Saturation** sliders. The swatch, the RGB readout, and the `np[i]` line update together.
2. Lower **Value** to about 30, the comfortable brightness the chapter recommends. Notice that the hue stays the same while all three RGB numbers shrink.
3. Lower **Saturation** and watch the ring fade toward white or gray.
4. Press **Rotate** to add 5 degrees to the offset every 40 ms, like the rainbow program's loop. Press **Stop** to freeze it.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/hsv-color-wheel/main.html"
        height="602px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objective

Students will understand hue, saturation, and value and convert between HSV and RGB (Bloom: Understanding, Applying).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- RGB color mixing on NeoPixels (Chapter 16)
- Angles on a clock face (Chapter 10)
- Integer division `//` and remainder `%` (Chapter 3)

### Activities

1. **Name the angles** (3 min): Students find the hue for red, yellow, green, cyan, blue, and magenta and record the RGB values at full saturation and value.
2. **Convert by hand** (5 min): Students compute `hsv_to_rgb(200, 255, 255)` step by step using region, rem, p, q, and t, then check their answer with the sliders.
3. **Dim without changing color** (3 min): Students set hue 30 and lower value from 255 to 30. Which RGB numbers change? What happens to the ratio between them?
4. **Rainbow program** (4 min): With Rotate running, students explain what the offset does and predict the hue of pixel 3 when the offset is 90.

### Assessment

- What hue is halfway between green and blue? (180, cyan.)
- What does `hsv_to_rgb(h, 0, 120)` return for any hue? Why? (`(120, 120, 120)`, a gray, because zero saturation means no color.)
- With offset 0, what hue does pixel 4 of the 12-pixel ring get? (120, green.)
- Explain why HSV makes a rainbow easier to program than RGB.

## References

1. [HSL and HSV](https://en.wikipedia.org/wiki/HSL_and_HSV) - Wikipedia article on the HSV color model and its conversion to RGB.
2. [Color wheel](https://en.wikipedia.org/wiki/Color_wheel) - Wikipedia; arranging hues around a circle.
3. [Adafruit NeoPixel Uberguide](https://learn.adafruit.com/adafruit-neopixel-uberguide) - Practical advice on NeoPixel colors and brightness.
4. [MicroPython neopixel module](https://docs.micropython.org/en/latest/library/neopixel.html) - The driver used on the Pico.
