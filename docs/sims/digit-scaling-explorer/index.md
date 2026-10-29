---
title: Digit Scaling Explorer
description: Scale an 8 by 8 font up to 6 times on a 128 by 64 OLED preview and see when the text becomes too wide for the screen.
image: /sims/digit-scaling-explorer/digit-scaling-explorer.png
og:image: /sims/digit-scaling-explorer/digit-scaling-explorer.png
twitter:image: /sims/digit-scaling-explorer/digit-scaling-explorer.png
social:
   cards: false
quality_score: 0
---

# Digit Scaling Explorer

<iframe src="main.html" height="532px" width="100%" scrolling="no"></iframe>

[Run the Digit Scaling Explorer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

The built-in OLED font is 8 by 8 pixels, which is tiny across a room. **Scaled digits** draw each
font pixel as a `scale` by `scale` block, just like the `big_char()` function in Chapter 12.

The cost is width. Every character becomes 8 x scale pixels wide, so:

\[ \text{width} = 8 \times \text{scale} \times \text{characters} \]

The OLED preview shows the text centered when it fits. When it is wider than 128 pixels, the text
starts at the left edge and the part past x = 127 is drawn in red in the pink "off the screen"
zone, so you can see exactly what would be cut off. The readout turns red at the same moment.

The enlarged **source glyph** shows the 8 by 8 bitmap of the character under your mouse. Turn on
**Show scaled blocks** to see how each blue square of the glyph becomes a block of screen pixels.

## How to Use

1. Leave the time string as `12:34` and move **Scale** from 1 to 6. At which scale does the text
   stop fitting?
2. Change the string to `12:34:56`. What is the largest scale that fits now?
3. Hover over a digit on the preview to see its 8 by 8 glyph.
4. Turn on **Show scaled blocks** at scale 4 and count the screen pixels in one block.
5. Use the readout to find the maximum number of characters at each scale.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/digit-scaling-explorer/main.html"
        height="532px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
14 minutes

### Prerequisites

- The 8 by 8 built-in font and text() (Chapter 12)
- Pixel coordinates on the 128 by 64 OLED (Chapter 11)

### Learning Objectives

Students will be able to:

- Apply the scale factor to compute text width as 8 x scale x characters
- Analyze the tradeoff between digit size and how many characters fit
- Center text using x = (128 - width) // 2

### Activities

1. **Width table** (5 min): Make a table of scale (1 to 6) against the maximum characters that fit across 128 pixels. Check it with the explorer.
2. **Seconds or size** (5 min): Decide whether a clock should show HH:MM at scale 3 or HH:MM:SS at scale 2. Justify with numbers.
3. **Centering** (4 min): For 12:34 at scale 3, compute the centered x by hand and compare with the readout.

### Assessment

- The student computes 5 x 24 = 120 pixels for 12:34 at scale 3.
- The student states the largest scale for an 8-character string (scale 2).
- The student explains why scaled digits look blocky.

## References

1. [MicroPython framebuf module](https://docs.micropython.org/en/latest/library/framebuf.html) - Official documentation for text() and fill_rect().
2. [Computer font: bitmap fonts](https://en.wikipedia.org/wiki/Computer_font#Bitmap_fonts) - Wikipedia article on fonts stored as pixel grids.
3. [Nearest-neighbor interpolation](https://en.wikipedia.org/wiki/Nearest-neighbor_interpolation) - Wikipedia article on the scaling method that copies each pixel into a block.
4. [Pixel art scaling algorithms](https://en.wikipedia.org/wiki/Pixel-art_scaling_algorithms) - Wikipedia article on smarter ways to enlarge small bitmaps.
