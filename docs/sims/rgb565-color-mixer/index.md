---
title: RGB565 Color Mixer
description: Mix a color with red, green, and blue sliders and see it packed into the 16-bit RGB565 format, with the 5-6-5 bit groups, the hex value, the color565() call, the detail lost, and the banding in a gradient.
image: /sims/rgb565-color-mixer/rgb565-color-mixer.png
og:image: /sims/rgb565-color-mixer/rgb565-color-mixer.png
twitter:image: /sims/rgb565-color-mixer/rgb565-color-mixer.png
social:
   cards: false
quality_score: 100
---

# RGB565 Color Mixer

<iframe src="main.html" height="592px" width="100%" scrolling="no"></iframe>

[Run the RGB565 Color Mixer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

Your computer stores each color with 8 bits for red, 8 for green, and 8 for blue: 24 bits in all. Small color displays such as the GC9B72 and ST7735 use **RGB565** instead, which squeezes a color into 16 bits: **5 bits of red, 6 of green, and 5 of blue**. Green gets the extra bit because human eyes are most sensitive to green.

The `color565()` function from Chapter 15 keeps the top bits of each channel and shifts them into place:

\[ \text{color} = (r \,\&\, \texttt{0xF8}) \ll 8 \;|\; (g \,\&\, \texttt{0xFC}) \ll 3 \;|\; (b \gg 3) \]

The left swatch is your 24-bit color. The right swatch is the same color after packing into RGB565 and expanding back for your screen, which is what the display will actually show. Under the swatches, the 16 bits are drawn in their red, green, and blue groups. The readout gives the binary and hex values, the matching `color565()` call, and how much each channel lost: red and blue drop their lowest 3 bits (up to 7 levels) and green drops its lowest 2 (up to 3 levels).

## How to Use

1. Drag the **Red**, **Green**, and **Blue** sliders. The opening color is the chapter's orange, `color565(255, 128, 0)`, which is `0xFC00`.
2. Watch the bit groups: moving red changes only bits 15 to 11, green only bits 10 to 5, and blue only bits 4 to 0.
3. Try red values 248 to 255. They all pack to the same five bits, so the right swatch does not change. That is the lost detail.
4. Check **Gradient** to compare a smooth ramp from black to your color with the RGB565 ramp. Look for the visible steps (banding), and read how many shades each ramp has.
5. Press **Predict** to get a random color with the answer hidden. Type the RGB565 hex value (for example `FC00`) and press **Check**. Press **Exit Predict** to leave the mode.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/rgb565-color-mixer/main.html"
        height="592px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objective

Students will apply the RGB565 packing formula and analyze how many bits of color detail are lost (Bloom: Applying, Analyzing).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Binary, hex, shifts, and masks (Chapter 8)
- RGB color mixing (Chapter 15)

### Activities

1. **Check the table** (3 min): Set the sliders to make each color in the chapter's RGB565 table (black, white, red, green, blue, yellow) and confirm the hex values.
2. **Pack by hand** (5 min): Students compute `color565(110, 110, 110)` on paper, the gray from `colors.py`, then check with the sliders. (`0x6B6D`.)
3. **Find the loss** (4 min): Which slider value changes do not change the RGB565 value? Students explain in terms of the masks `0xF8` and `0xFC`.
4. **Banding** (3 min): With Gradient on, students find a color whose RGB565 ramp shows obvious steps and explain why dark, slowly changing gradients show banding most.

### Assessment

- Pack `color565(0, 255, 0)` by hand. (`0x07E0`.)
- How many different colors can RGB565 represent? (65,536.)
- Why does green get 6 bits while red and blue get 5?
- A designer picks red 250 and red 253 for two buttons. Why will they look identical on the display?

## References

1. [High color (16-bit RGB565)](https://en.wikipedia.org/wiki/High_color) - Wikipedia article on 16-bit color formats.
2. [RGB color model](https://en.wikipedia.org/wiki/RGB_color_model) - Wikipedia; additive color mixing.
3. [Colour banding](https://en.wikipedia.org/wiki/Colour_banding) - Wikipedia; why gradients show steps at low bit depth.
4. [Bitwise operation](https://en.wikipedia.org/wiki/Bitwise_operation) - Wikipedia; the masks and shifts in `color565()`.
