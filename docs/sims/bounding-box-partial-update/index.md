---
title: Bounding Box and Partial Update
description: Compare a full redraw with a partial update on an OLED clock by counting the pixels each one redraws when the seconds change.
image: /sims/bounding-box-partial-update/bounding-box-partial-update.png
og:image: /sims/bounding-box-partial-update/bounding-box-partial-update.png
twitter:image: /sims/bounding-box-partial-update/bounding-box-partial-update.png
social:
   cards: false
quality_score: 0
---

# Bounding Box and Partial Update

<iframe src="main.html" height="542px" width="100%" scrolling="no"></iframe>

[Run the Bounding Box and Partial Update MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

Each item on this OLED clock lives inside a **bounding box** `(x, y, w, h)`: the hours, the
minutes, the seconds and the date. The colored outlines show the four boxes.

When one second passes, only the seconds change. There are two ways to update the screen:

- **Full redraw**: `fill(0)`, draw everything, `show()`. All 8,192 pixels are redrawn, and the
  whole screen flashes red.
- **Partial update**: `fill_rect(*box, 0)` to erase only the changed item's box, then draw the
  new value. Only that box flashes red: 16 x 8 = 128 pixels for the seconds.

Press **Advance one second** in each mode and compare the counters. Use **Jump to :59** to see a
minute rollover, where the minutes box changes too.

The panel also reminds you of the catch from the chapter: with the OLED's framebuffer driver,
`show()` still sends all 1,024 bytes either way. A partial update saves **drawing** work here; on
larger color displays that can send just a window, it also saves bus time.

## How to Use

1. With **Update mode** set to **Partial update**, press **Advance one second**. Note the pixel count.
2. Switch to **Full redraw** and press **Advance one second** again. Compare the two bars.
3. Press **Jump to :59**, then **Advance one second** in Partial mode. Which boxes changed?
4. Turn **Bounding boxes** off and on to match each outline with its `(x, y, w, h)` entry.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/bounding-box-partial-update/main.html"
        height="542px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
14 minutes

### Prerequisites

- Drawing shapes and text with framebuf (Chapter 12)
- The fill, draw, show routine (Chapter 11)

### Learning Objectives

Students will be able to:

- Analyze how erasing one bounding box updates part of the screen without disturbing the rest
- Compare the pixels redrawn by a full redraw and a partial update
- Explain why show() still sends the whole buffer on the OLED

### Activities

1. **Count the savings** (4 min): Record pixels redrawn for one second in each mode. Compute the percentage saved by the partial update.
2. **Rollover** (4 min): Use Jump to :59 and advance. Which boxes changed and how many pixels were redrawn?
3. **Design a box** (6 min): Add a temperature reading at (88, 56) with 4 characters. Write its bounding box and the two lines of code to update it.

### Assessment

- The student computes the seconds box area as 16 x 8 = 128 pixels.
- The student explains that items whose boxes do not overlap the changed one are untouched.
- The student states that the bus still carries 1,024 bytes per show().

## References

1. [Minimum bounding box](https://en.wikipedia.org/wiki/Minimum_bounding_box) - Wikipedia article on the smallest box around an object.
2. [MicroPython framebuf module](https://docs.micropython.org/en/latest/library/framebuf.html) - Official documentation for fill_rect(), text() and blit().
3. [Clipping (computer graphics)](https://en.wikipedia.org/wiki/Clipping_(computer_graphics)) - Wikipedia article on limiting drawing to a region.
4. [Framebuffer](https://en.wikipedia.org/wiki/Framebuffer) - Wikipedia article on screen memory.
