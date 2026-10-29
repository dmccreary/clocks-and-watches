---
title: Resolution and Memory Calculator
description: Calculate the framebuffer size of five displays and a custom one, and judge whether each fits in the Pico's 264 KB of RAM.
image: /sims/resolution-memory-calculator/resolution-memory-calculator.png
og:image: /sims/resolution-memory-calculator/resolution-memory-calculator.png
twitter:image: /sims/resolution-memory-calculator/resolution-memory-calculator.png
social:
   cards: false
quality_score: 0
---

# Resolution and Memory Calculator

<iframe src="main.html" height="472px" width="100%" scrolling="no"></iframe>

[Run the Resolution and Memory Calculator MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

Every pixel on a screen must be stored in memory. The framebuffer size is:

\[ \text{memory (bytes)} = \frac{W \times H \times \text{bpp}}{8} \]

The chart shows that size in kilobytes (1 KB = 1,024 bytes) for the five displays in the
chapter's table, plus a **custom** display whose width and height you type.

Two lines mark the limits on a Raspberry Pi Pico:

- The **red** line at 264 KB is all of the Pico's RAM.
- The **yellow** dashed line at 200 KB is a practical limit. MicroPython itself and your program
  need the rest.

Bars are green when they fit comfortably, orange when they squeeze past 200 KB, and red when they
cannot fit at all. Hover over a bar to see the formula with the numbers filled in.

## How to Use

1. Start with **16 bits per pixel** (color). Which displays fit under the yellow line?
2. Hover over the GC9B72 bar and check the chapter's worked example: 259,200 bytes.
3. Switch to **1 bit per pixel**. How small is the OLED's buffer now?
4. Type your own width and height into **Custom display**. Find the largest square color display
   that still fits under 200 KB.
5. Try **8 bits per pixel** and see which displays move from red or orange to green.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/resolution-memory-calculator/main.html"
        height="472px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Display resolution and pixel counts (Chapter 11)
- Bits and bytes (Chapter 8)

### Learning Objectives

Students will be able to:

- Calculate framebuffer memory from width, height and bits per pixel
- Evaluate whether a display's framebuffer fits in the Pico's 264 KB of RAM
- Compare the memory cost of monochrome and color displays

### Activities

1. **Check the table** (4 min): Compute the OLED and GC9B72 buffer sizes by hand, then hover to check.
2. **Largest square screen** (6 min): Use the custom inputs to find the largest square 16-bit display that stays under the 200 KB line.
3. **Recommend a display** (5 min): A student wants a 320x240 color clock on a Pico. Write a recommendation that uses numbers from the chart.

### Assessment

- The student computes 128 x 64 x 1 / 8 = 1,024 bytes.
- The student explains why 360 x 360 at 16 bpp leaves almost no RAM for the program.
- The student proposes a way to fit a large display (lower bpp or partial buffers).

## References

1. [Display resolution](https://en.wikipedia.org/wiki/Display_resolution) - Wikipedia article on pixel counts.
2. [Color depth](https://en.wikipedia.org/wiki/Color_depth) - Wikipedia article on bits per pixel.
3. [High color (RGB565)](https://en.wikipedia.org/wiki/High_color) - Wikipedia article on 16-bit color.
4. [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) - Official datasheet listing the 264 KB of on-chip SRAM.
5. [Chart.js documentation](https://www.chartjs.org/docs/latest/) - The charting library used for this MicroSim.
