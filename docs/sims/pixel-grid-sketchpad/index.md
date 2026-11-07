---
title: Pixel Grid Sketchpad
description: Draw on a 128 by 64 OLED pixel grid and see which of the 1,024 framebuffer bytes and which bit stores each pixel.
image: /sims/pixel-grid-sketchpad/pixel-grid-sketchpad.png
og:image: /sims/pixel-grid-sketchpad/pixel-grid-sketchpad.png
twitter:image: /sims/pixel-grid-sketchpad/pixel-grid-sketchpad.png
social:
   cards: false
quality_score: 0
---

# Pixel Grid Sketchpad

<iframe src="main.html" height="672px" width="100%" scrolling="no"></iframe>

[Run the Pixel Grid Sketchpad MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

The SSD1306 OLED has 128 x 64 = 8,192 pixels, and its framebuffer stores them in just 1,024 bytes.
Each byte holds a **vertical strip of 8 pixels** in one column, so the 64 rows are grouped into
**8 pages** of 8 rows. The chapter's formula finds the byte and bit for any pixel:

\[ \text{index} = x + \left\lfloor \frac{y}{8} \right\rfloor \times 128 \qquad \text{bit} = y \bmod 8 \]

The black grid is the screen, with faint lines marking the 8 pages. Below it, the **buffer map**
has one cell per byte: one row per page and one column per x, lined up under the screen columns.
A map cell turns blue when its byte holds any lit pixels, darker for more lit bits.

Hover over a pixel to outline its 8-pixel byte (orange) and to see the index and bit worked out
with the formula. Hover over a map cell to see which column and rows that byte covers.

**Generate code** lists the `oled.pixel()` calls that would recreate your drawing (the full
list goes to the browser console). **Challenge** gives you a coordinate to find and click.

## How to Use

1. Click or drag on the grid to turn pixels on and off.
2. Hover over the pixel (10, 20) and check the worked example from the chapter: byte 266, bit 4.
3. Press **Draw example** to load the border-and-diagonal drawing from the chapter. Look at the
   buffer map. Why are rows p0 and p7 filled all the way across?
4. Press **Generate code** to see the `pixel()` calls for your drawing.
5. Press **Challenge** and click the requested pixels. Press **Stop challenge** when done.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/pixel-grid-sketchpad/main.html"
        height="672px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Bits, bytes and shift operators (Chapter 8)
- Screen coordinates with (0, 0) at the top-left (Chapter 10)

### Learning Objectives

Students will be able to:

- Apply x and y coordinates to locate pixels on a 128 by 64 display
- Calculate the byte index and bit for any pixel using index = x + (y // 8) * 128 and bit = y % 8
- Analyze why one byte stores a vertical strip of 8 pixels

### Activities

1. **Worked example** (3 min): Hover over (10, 20) and confirm byte 266, bit 4. Then predict the byte and bit for (127, 63) before hovering.
2. **One byte, eight pixels** (5 min): Turn on pixels (40, 16) through (40, 23). How many map cells changed? What is the byte value?
3. **Challenge round** (7 min): Play the Challenge until you score 5 in a row. Then draw your initials and generate the code.

### Assessment

- The student calculates index and bit for a given pixel without the tool.
- The student explains why a horizontal line touches 1 byte per column while a vertical 8-pixel strip fits in one byte.
- The student reads (x, y) correctly with y growing downward.

## References

1. [MicroPython framebuf module](https://docs.micropython.org/en/latest/library/framebuf.html) - Official documentation for FrameBuffer, MONO_VLSB and pixel().
2. [Framebuffer](https://en.wikipedia.org/wiki/Framebuffer) - Wikipedia article on memory that holds a screen image.
3. [SSD1306 datasheet](https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf) - Controller datasheet describing the page-based display memory.
4. [Bit numbering](https://en.wikipedia.org/wiki/Bit_numbering) - Wikipedia article on bit positions within a byte.
