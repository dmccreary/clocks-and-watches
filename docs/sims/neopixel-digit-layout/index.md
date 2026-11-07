---
title: NeoPixel Digit Layout
description: A seven-segment digit built from a 14-pixel NeoPixel strip. Click segments to see their pixels, choose a digit to see which pixels light, show the strip's path, design your own wiring order, and copy it as a Python SEG_PIXELS list.
image: /sims/neopixel-digit-layout/neopixel-digit-layout.png
og:image: /sims/neopixel-digit-layout/neopixel-digit-layout.png
twitter:image: /sims/neopixel-digit-layout/neopixel-digit-layout.png
social:
   cards: false
quality_score: 100
---

# NeoPixel Digit Layout

<iframe src="main.html" height="527px" width="100%" scrolling="no"></iframe>

[Run the NeoPixel Digit Layout MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/neopixel-digit-layout/main.html"
        height="527px"
        width="100%"
        scrolling="no"></iframe>
```

## About This MicroSim

A NeoPixel seven-segment digit is a short strip of addressable LEDs cut and placed so that each of the seven segments, `a` to `g`, holds two pixels. The strip is one long chain, so every pixel has a number from 0 to 13 in the order the data travels. Your program needs a lookup table that says which pixel numbers belong to which segment:

```python
SEG_PIXELS = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)]   # a to g
DIGITS = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F]
```

The digit bytes are the same ones used for the seven-segment display in Chapter 9: bit 0 is segment `a`, bit 1 is `b`, and so on up to bit 6 for `g`. To show a digit, the program checks each bit and lights both pixels of every segment whose bit is 1.

The wiring order is a design choice. The default runs the strip around the outside of the digit (`a` to `f`) and then jumps back for the middle segment `g`. Other orders can need shorter jumper wires between segments. The **strip path length** in the panel measures the total distance the strip travels from pixel 0 to pixel 13, so you can compare designs.

## How to Use

1. Pick a **Digit** from 0 to 9. The lit segments turn red, and the panel shows the digit's byte, its segments, and the pixel numbers that light.
2. **Click** any segment to see which two pixels it contains.
3. Check **Show strip order** to draw the strip's path from the data-in (DIN) end through all 14 pixels.
4. Press **Rewire**, then click the seven segments in the order you want the strip to pass through them. The pixel numbers and the `SEG_PIXELS` list update. Press **Reset wiring** to go back to `a` to `g` order.
5. Press **Copy SEG_PIXELS** to copy the Python line for your design to the clipboard. (If your browser blocks copying inside the page, select the line in the panel instead.)

## Lesson Plan

### Learning Objective

Students will design a pixel-to-segment mapping and apply it to display a digit (Bloom: Applying, Creating).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15-20 minutes

### Prerequisites

- Seven-segment patterns and segment bytes (Chapter 9)
- NeoPixel indexing and `np[i] = (r, g, b)` (Chapter 16)
- Bit shifts and masks (Chapter 8)

### Activities

1. **Apply** (4 min): For digits 1, 4, and 8, students predict the lit pixel numbers from the `DIGITS` byte, then check with the menu.
2. **Trace** (3 min): With **Show strip order** on, students find the longest jump in the default wiring.
3. **Design** (6 min): Students rewire the digit to make the strip path as short as possible and record the path length and their `SEG_PIXELS` list.
4. **Test in code** (5 min): Students paste their `SEG_PIXELS` into the chapter's `show_digit()` function and explain why the rest of the program does not need to change.

### Assessment

- With the default wiring, which pixels light for the digit 2 (`0x5B`)? (Segments a, b, d, e, g: pixels 0, 1, 2, 3, 6, 7, 8, 9, 12, 13.)
- How many pixels does a four-digit clock with a two-pixel colon need? (58.)
- Explain why changing the wiring order changes `SEG_PIXELS` but not `DIGITS`.

## References

1. [Seven-segment display](https://en.wikipedia.org/wiki/Seven-segment_display) - Wikipedia; segment names and digit patterns.
2. [Adafruit NeoPixel Uberguide](https://learn.adafruit.com/adafruit-neopixel-uberguide) - How addressable LED strips are wired and indexed.
3. [MicroPython neopixel module](https://docs.micropython.org/en/latest/library/neopixel.html) - The driver used on the Pico.
