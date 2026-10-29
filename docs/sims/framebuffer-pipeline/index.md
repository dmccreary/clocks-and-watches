---
title: Framebuffer Pipeline
description: Follow the path from a drawing call to lit pixels on an OLED, and compare the state before and after show().
image: /sims/framebuffer-pipeline/framebuffer-pipeline.png
og:image: /sims/framebuffer-pipeline/framebuffer-pipeline.png
twitter:image: /sims/framebuffer-pipeline/framebuffer-pipeline.png
social:
   cards: false
quality_score: 0
---

# Framebuffer Pipeline

<iframe src="main.html" height="547px" width="100%" scrolling="no"></iframe>

[Run the Framebuffer Pipeline MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

Drawing on an OLED happens in two stages. First your program changes bytes in a **framebuffer** in
the Pico's RAM. Then `oled.show()` copies all 1,024 bytes over the bus to the display.

The diagram follows that path:

1. **Your program** decides what to show.
2. **Drawing calls** such as `oled.text()` and `oled.pixel()` change bytes in RAM only.
3. The **framebuffer** holds 1,024 bytes, one bit per pixel.
4. **`oled.show()`** sends the whole buffer.
5. The **I2C or SPI bus** carries about 1,030 bytes (the buffer plus a few commands).
6. The **SSD1306 controller** stores its own copy.
7. The **OLED panel** lights the 8,192 pixels.

Click (or hover over) any box to read what it does and how many bytes pass through it.

The **Before show()** and **After show()** buttons highlight the two states. Before `show()`, only
the boxes inside the Pico have changed: the buffer says "12:35" but the panel still shows "12:34".
After `show()`, the bytes reach the module and the panel matches the buffer.

## How to Use

1. Click each box from left to right and read its role and byte count.
2. With **Before show()** selected, compare the two mini screens in the side panel.
3. Press **After show()**. Which boxes light up now?
4. Explain in one sentence why nothing appears on the OLED if you forget to call `show()`.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/framebuffer-pipeline/main.html"
        height="547px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
12 minutes

### Prerequisites

- Bits and bytes (Chapter 8)
- OLED display basics (Chapter 11)

### Learning Objectives

Students will be able to:

- Explain the path from a drawing call to lit pixels on the OLED
- Distinguish what changes before show() from what changes after show()
- State how many bytes cross the bus on each show()

### Activities

1. **Trace the path** (4 min): Click the seven boxes in order and write one phrase per box describing its job.
2. **Before and after** (4 min): Switch between the two states. List which parts of the system change in each.
3. **Debug a blank screen** (4 min): A program calls oled.text() in a loop but the screen stays blank. Use the diagram to explain the bug and the fix.

### Assessment

- The student explains that drawing calls change only RAM.
- The student states that show() sends all 1,024 bytes every time.
- The student diagnoses a missing show() call from its symptom.

## References

1. [MicroPython framebuf module](https://docs.micropython.org/en/latest/library/framebuf.html) - Official documentation for the drawing methods the SSD1306 driver inherits.
2. [Framebuffer](https://en.wikipedia.org/wiki/Framebuffer) - Wikipedia article on screen memory.
3. [Multiple buffering](https://en.wikipedia.org/wiki/Multiple_buffering) - Wikipedia article on drawing off-screen to avoid flicker.
4. [SSD1306 datasheet](https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf) - Controller datasheet describing its display RAM.
5. [Mermaid flowchart syntax](https://mermaid.js.org/syntax/flowchart.html) - Documentation for the diagram library used here.
