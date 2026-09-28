---
title: Drawing Shapes, Text, and Animation
description: Drawing lines, shapes, and text on framebuffer displays, plus custom fonts, scaled digits, animation, and partial updates.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:41:09
version: 1.10
---

# Drawing Shapes, Text, and Animation

## Summary

Students draw lines, rectangles, circles, and polygons and render text with built-in and custom fonts. They learn animation and partial screen updates. After this chapter they can draw a complete clock face on an OLED.

## Concepts Covered

This chapter covers the following 19 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Text Rendering | 20 |
| Display Coordinates | 3 |
| Line Drawing | 14 |
| Font Loading | 5 |
| Scaled Digits | 5 |
| Partial Screen Update | 2 |
| Rectangle Drawing | 3 |
| Circle Drawing | 3 |
| Polygon Drawing | 2 |
| Custom Fonts | 4 |
| Animation Technique | 3 |
| Triangle Drawing | 1 |
| Font to Py Converter | 2 |
| Arc Drawing | 1 |
| Double Buffering | 1 |
| Scroll Marquee | 1 |
| Bounding Box | 2 |
| Multiple Font Support | 1 |
| Clipping Region | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)
- [Chapter 4: Control Flow, Functions, and Modules](../04-control-flow-functions/index.md)
- [Chapter 6: Getting the Time in MicroPython](../06-getting-time/index.md)
- [Chapter 10: Coordinates, Trigonometry, and Clock Geometry](../10-clock-math/index.md)
- [Chapter 11: OLED Displays and Framebuffers](../11-oled-framebuffers/index.md)

---

!!! mascot-welcome "From Pixels to Pictures"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Setting one pixel at a time is like painting with a single grain of sand. In this chapter you'll get real brushes: lines, circles, big digits, and smooth motion. By the end you'll draw a complete analog clock face. Let's make time tick!

## Drawing With Real Tools

You now know how the framebuffer works and how to set a single pixel. Drawing whole pictures pixel by pixel would be slow and tedious, so MicroPython's `framebuf` module provides ready-made shapes. This chapter covers the shape tools, text and fonts, and the techniques that make screens update smoothly and efficiently. All the examples use the `oled` object from Chapter 11.

## Display Coordinates

Every drawing call needs positions, and each call interprets its numbers a little differently. The coordinate system is the one from Chapter 10: the origin (0, 0) is at the **top-left**, x grows to the right, and y grows downward. What changes from call to call is what the numbers *mean*.

| Call | Arguments | What (x, y) means |
|------|-----------|-------------------|
| `pixel(x, y, c)` | position, color | The pixel itself |
| `line(x1, y1, x2, y2, c)` | two end points | Start and end of the line |
| `rect(x, y, w, h, c)` | corner, size | **Top-left corner**, then width and height |
| `ellipse(x, y, xr, yr, c)` | center, radii | **Center** of the shape |
| `text(s, x, y, c)` | string, corner | **Top-left** of the first character |
| `poly(x, y, coords, c)` | offset, points | Offset added to every point |

Two of these trip people up. A rectangle takes a width and height, not a second corner, and an ellipse takes its **center**, not its corner. On the 128 by 64 OLED, valid x values run from 0 to 127 and y values from 0 to 63.

!!! mascot-warning "Size, Not Corner"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    `rect(10, 10, 50, 30, 1)` draws a box 50 wide and 30 tall, ending at (59, 39), not at (50, 30). Mixing up "width and height" with "second corner" is the most common shape bug, and the giveaway is a rectangle that is too big or too small by exactly the starting offset.

## Text Rendering

**Text rendering** is drawing characters on the screen. The built-in `text()` method uses a fixed **8 by 8 pixel** font, so every character occupies an 8-pixel cell:

```python
oled.text("12:34", 0, 0, 1)      # string, x, y, color (1 = on)
```

Because each character is 8 pixels wide, you can predict text width exactly: `width = 8 * len(string)`. On the 128-pixel-wide OLED, 16 characters fit on a line, and with 8-pixel rows, 8 lines fit in 64 pixels. To center a string horizontally:

```python
msg = "12:34"
x = (128 - 8 * len(msg)) // 2       # 44
oled.text(msg, x, 28, 1)
```

The built-in font supports basic ASCII letters, digits, and symbols, but it cannot be resized and has no accented characters. The next sections show how to overcome that.

## Scaled Digits

A clock should be readable across a room, and 8-pixel digits are tiny. **Scaled digits** enlarge the built-in font by drawing each font pixel as a block of several screen pixels. The idea is to render the character into a small scratch buffer, then copy each lit pixel as a `scale` by `scale` square.

```python
import framebuf

scratch = framebuf.FrameBuffer(bytearray(8), 8, 8, framebuf.MONO_HLSB)

def big_char(oled, ch, x, y, scale):
    scratch.fill(0)
    scratch.text(ch, 0, 0, 1)                 # draw the character at 8x8
    for py in range(8):
        for px in range(8):
            if scratch.pixel(px, py):
                oled.fill_rect(x + px * scale, y + py * scale, scale, scale, 1)
```

With `scale = 3`, each digit is 24 by 24 pixels, so `12:34` needs \( 5 \times 24 = 120 \) pixels and fits across the 128-pixel screen. The `MONO_HLSB` format is a horizontal layout that suits a scratch buffer, and it does not need to match the display's own layout because you copy pixel by pixel.

#### Diagram: Digit Scaling Explorer

<details markdown="1">
<summary>Digit Scaling Explorer</summary>
Type: MicroSim
**sim-id:** digit-scaling-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* scaling to make digits fit the screen and *analyze* the width tradeoff (Bloom: Applying, Analyzing).

**Visual elements:** A 128 by 64 OLED preview showing a time string, with the 8 by 8 source glyph shown enlarged beside it.

**Controls:** Text input for the time string, a scale slider (1 to 6), and a readout "Width = 8 × scale × characters" that turns red when it exceeds 128. A checkbox shows the grid of scaled blocks.

**Responsive design:** The preview scales to the container width.

Implementation: p5.js with a stored 8 by 8 bitmap font for digits and colon.
</details>

## Font Loading

A **font** is a set of bitmap pictures, one for each character. To use a font other than the built-in one, you **load** it from a Python file and use a helper called a writer to draw text with it. The commonly used tool is Peter Hinch's `writer.py`, together with font modules generated by his converter.

```python
import writer
import freesans32             # a font module copied to the Pico

wri = writer.Writer(oled, freesans32)
writer.Writer.set_textpos(oled, 10, 4)     # row, column
wri.printstring("12:34")
oled.show()
```

A loaded font is stored as Python data, so it takes up flash space and RAM when imported. Big fonts with many characters can use tens of kilobytes. That matters on a Pico with 264 KB of RAM, so import only the fonts you need.

### Custom Fonts

A **custom font** is one you make yourself in exactly the size and style you want, from any TrueType (`.ttf`) or OpenType (`.otf`) font file. This is how you get large, clean clock digits that the 8 by 8 font cannot give you.

### Font to Py Converter

The **font-to-py converter** is a program that runs on your computer, not on the Pico, and turns a font file into a Python module at a chosen pixel height. The basic pattern is:

```bash
python font_to_py.py FreeSans.ttf 32 freesans32.py -c 0123456789:
```

The number 32 is the font height in pixels. The `-c` option lists the characters to include. Here we include only the digits and the colon, so the output file stays small. Copy the resulting `freesans32.py` to the Pico and import it, as shown above. The [Font to Py lesson](../../lessons/50-multiple-fonts/font-to-py.md) walks through the whole process.

### Multiple Font Support

Some layouts need more than one font, such as big digits for the time and a small font for the date. Create one `Writer` for each font module and use whichever suits the text:

```python
big = writer.Writer(oled, freesans32)
small = writer.Writer(oled, freesans14)
```

Each font takes memory, so limit yourself to what the screen actually needs. Two or three fonts is a practical ceiling on the Pico.

#### Diagram: Font Pipeline

<details markdown="1">
<summary>Font Pipeline</summary>
Type: workflow diagram
**sim-id:** font-pipeline<br/>
**Library:** Mermaid<br/>
**Status:** Specified

**Learning objective:** Students will *understand* the steps from a font file to text on the OLED (Bloom: Understanding).

**Nodes:** TrueType font file on your computer, `font_to_py.py` (with height and character list), generated `.py` module, copy to Pico, `import` on the Pico, `Writer`, text on screen.

**Interactions:** Every node has a Mermaid `click` directive that opens an infobox with the command or a description. A second view estimates the module's memory size from height and number of characters.

**Responsive design:** The diagram scales to container width.

Implementation: Mermaid flowchart with click callbacks.
</details>

## Line Drawing

The **`line(x1, y1, x2, y2, c)`** method draws a straight line of one-pixel thickness between two points. It also has two faster special cases for horizontal and vertical lines: `hline(x, y, w, c)` and `vline(x, y, h, c)`.

```python
oled.line(0, 0, 127, 63, 1)     # diagonal across the screen
oled.hline(0, 32, 128, 1)       # horizontal line across the middle
```

Lines are the natural tool for clock hands. Using the hand-tip calculation from Chapter 10, a hand is a line from the center to the tip:

```python
cx, cy = 64, 32                  # center of the 128 x 64 screen
x, y = tip(angle, length)        # from Chapter 10
oled.line(cx, cy, x, y, 1)
```

## Rectangle Drawing

The **`rect(x, y, w, h, c)`** method draws a rectangle outline. Add a fifth argument `True` (or use `fill_rect()`) to fill it. Rectangles make borders, progress bars, and thick lines:

```python
oled.rect(0, 0, 128, 64, 1)              # border around the whole screen
oled.fill_rect(10, 50, 60, 6, 1)         # filled bar
```

## Circle Drawing

The `framebuf` module has no `circle()`, but it has **`ellipse(x, y, xr, yr, c)`**, and an ellipse with equal radii is a circle. The position is the center:

```python
oled.ellipse(64, 32, 31, 31, 1)          # circle, radius 31, fits the 64 px height
oled.ellipse(64, 32, 4, 4, 1, True)      # small filled dot at the center
```

The `ellipse` method was added in MicroPython 1.19, so on older firmware you must draw circles by plotting points with the polar formula from Chapter 10.

## Polygon Drawing

A **polygon** is a closed shape with straight sides. The **`poly(x, y, coords, c)`** method takes an array of x, y pairs. The coordinates are relative to the offset `(x, y)`, so you can draw the same shape at different places. The array must be a 16-bit array from the `array` module:

```python
import array
diamond = array.array('h', [0, -10,  4, 0,  0, 10,  -4, 0])   # 4 points
oled.poly(64, 32, diamond, 1, True)      # filled diamond at the center
```

This is a good shape for an hour hand, because it is wide near the center and pointed at the end. Rotating its points with the rotation formula from Chapter 10 aims it at the right hour.

### Triangle Drawing

A **triangle** is the simplest polygon: three points. Triangles make arrows, play buttons, and alarm icons.

```python
tri = array.array('h', [0, 0,  10, 5,  0, 10])   # points right
oled.poly(20, 20, tri, 1, True)
```

### Arc Drawing

An **arc** is part of a circle. There is no built-in arc call, so you draw one by plotting points along the circle using the polar formula. This is perfect for a progress ring that grows as the seconds pass:

```python
def arc(cx, cy, r, start_deg, end_deg, step=3):
    for a in range(start_deg, end_deg, step):
        x, y = tip(a, r)                 # from Chapter 10
        oled.pixel(x, y, 1)

arc(64, 32, 30, 0, seconds * 6)         # ring grows with the second
```

A smaller `step` gives a smoother line but takes longer to draw.

## Animation Technique

**Animation** is the illusion of motion made by showing a series of slightly different pictures quickly. Each picture is called a **frame**. Every animation loop follows the same recipe: clear, draw the objects at their current positions, show, then change the positions for the next frame.

```python
NAME = "12-bounce.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin, I2C
from time import sleep_ms
import ssd1306

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

x, dx = 10, 3                       # position and speed (pixels per frame)
while True:
    oled.fill(0)
    oled.ellipse(x, 32, 5, 5, 1, True)
    oled.show()
    x += dx
    if x > 122 or x < 5:            # bounce off the edges
        dx = -dx
    sleep_ms(20)
```

The speed of the animation is set by how far the object moves each frame and how long the frame takes. For smooth motion aim for 20 or more frames per second, meaning the drawing plus `show()` should take under about 50 ms. Chapter 11 showed how to measure that.

### Double Buffering

**Double buffering** uses two buffers: one that is visible and one you draw into. The framebuffer you already use is a simple form, because you build the picture in RAM before revealing it. A more useful version keeps a **second buffer** that holds the parts that never change, such as the tick marks of a clock face. Each frame, you copy the face into the main buffer with `blit()` and add only the moving hands.

```python
import framebuf
face_buf = bytearray(128 * 64 // 8)
face = framebuf.FrameBuffer(face_buf, 128, 64, framebuf.MONO_VLSB)
# ... draw the tick marks into face once ...

# every frame:
oled.blit(face, 0, 0)        # copy the ready-made face
# ... draw hands on top ...
oled.show()
```

This saves the time of redrawing 60 ticks every second.

!!! mascot-tip "Draw the Static Stuff Once"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Anything that never changes, like the clock face outline and tick marks, only needs to be drawn one time into a second buffer. Copy it in each frame with `blit()` and spend your drawing time only on the hands.

### Scroll Marquee

A **scroll marquee** slides text across the screen, like a news ticker. The simplest reliable method redraws the text at a changing x position each frame, starting off the right edge and moving left until it leaves:

```python
msg = "Let's make time tick!   "
for x in range(128, -8 * len(msg), -2):
    oled.fill(0)
    oled.text(msg, x, 28, 1)
    oled.show()
```

## Partial Screen Update

A **partial screen update** redraws only the region that changed instead of the entire screen. When only the seconds digits change each second, the hours, minutes, and date need not be touched. Clear just that rectangle, then draw the new value:

```python
oled.fill_rect(80, 40, 40, 8, 0)      # erase only the old seconds
oled.text(f"{s:02d}", 88, 40, 1)      # draw the new seconds
oled.show()
```

Be clear about what this saves. With the OLED's framebuffer, `show()` still sends the *entire* 1,024 bytes over the bus, so the bus time does not shrink, but you save drawing time. On larger color displays whose drivers can send just a window of pixels, a partial update also cuts the bus time dramatically, which becomes essential in later chapters.

### Bounding Box

A **bounding box** is the smallest rectangle that completely encloses an object. It is written as `(x, y, w, h)`. For 8 by 8 text the bounding box is easy to compute:

```python
def text_box(msg, x, y):
    return (x, y, 8 * len(msg), 8)
```

The bounding box gives you two useful powers. You can **erase** an old object exactly, with `fill_rect(*box, 0)`, and you can test whether two objects **overlap** by comparing their boxes. Erasing the old bounding box before drawing the new one is the core of a partial update.

!!! mascot-thinking "Every Object Lives in a Box"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Whatever you draw, picture the smallest rectangle around it. That one idea gives you a way to erase, move, and protect any item on the screen without touching its neighbors.

### Clipping Region

A **clipping region** is a rectangle outside of which drawing is ignored. It keeps a scrolling message from spilling onto other parts of the screen. `framebuf` clips only at the edges of the whole buffer, so to clip to a smaller area, draw into a small buffer the size of the region and then `blit()` it into place. Anything that falls outside the small buffer is discarded automatically.

#### Diagram: Bounding Box and Partial Update

<details markdown="1">
<summary>Bounding Box and Partial Update</summary>
Type: MicroSim
**sim-id:** bounding-box-partial-update<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *analyze* how erasing a bounding box lets part of the screen update without disturbing the rest (Bloom: Analyzing).

**Visual elements:** A 128 by 64 OLED preview with a clock display: hours, minutes, seconds, and a date line. Each item's bounding box can be shown as a colored outline.

**Controls:** Toggle "Show bounding boxes"; button "Advance one second." A "Update mode" selector switches between *Full redraw* (all pixels flash red as they are redrawn) and *Partial update* (only the seconds box flashes). A counter shows pixels redrawn per frame in each mode.

**Responsive design:** The preview and counter stack below 600 px.

Implementation: p5.js with per-item rectangles and a redraw counter.
</details>

## Putting It Together: An Analog OLED Clock

This program uses lines, an ellipse, ticks, and the angle math from Chapter 10 to draw a complete analog clock face on the 128 by 64 OLED. The face has radius 31 so it fits the 64-pixel height.

```python
NAME = "12-analog-oled.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
from machine import Pin, I2C
from time import localtime, sleep
import ssd1306

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

cx, cy, R = 64, 32, 31

def tip(deg, length):
    a = math.radians(deg)
    return cx + int(length * math.sin(a)), cy - int(length * math.cos(a))

def draw_face():
    oled.ellipse(cx, cy, R, R, 1)
    for i in range(12):                       # 12 hour ticks
        x1, y1 = tip(i * 30, R - 4)
        x2, y2 = tip(i * 30, R - 1)
        oled.line(x1, y1, x2, y2, 1)

while True:
    h, m, s = localtime()[3:6]
    oled.fill(0)
    draw_face()
    hx, hy = tip((h % 12) * 30 + m * 0.5, R * 0.5)
    mx, my = tip(m * 6 + s * 0.1, R * 0.75)
    sx, sy = tip(s * 6, R * 0.9)
    oled.line(cx, cy, hx, hy, 1)              # hour hand
    oled.line(cx, cy, mx, my, 1)              # minute hand
    oled.line(cx, cy, sx, sy, 1)              # second hand
    oled.show()
    sleep(1)
```

## Key Takeaways

- Every drawing call interprets (x, y) differently; `rect` takes width and height, and `ellipse` takes a center.
- The built-in font is 8 × 8, so text width is `8 * len(text)`; scale it or load a custom font for large digits.
- `font_to_py.py` converts a TrueType file to a Python font module; include only the characters you need.
- `line`, `rect`, `ellipse`, and `poly` cover almost every clock shape; arcs are made by plotting points.
- Animation is clear, draw, show, and move, repeated; a second buffer holds the static parts.
- Bounding boxes let you erase and update just part of the screen.

!!! mascot-celebration "A Face Worth Drawing"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now draw lines, circles, and polygons, scale digits, load fonts, and animate hands on an OLED. You built a full analog clock face from math and pixels. Every second counts!

## Practice Questions

1. Write the call that draws a filled rectangle 40 wide and 10 tall with its top-left corner at (20, 30).
2. How wide in pixels is the string `"09:45"` at scale 1, and at scale 3? Does it fit on a 128-pixel screen?
3. Explain why `ellipse(64, 32, 31, 31, 1)` draws a circle centered on the screen.
4. What is the benefit of drawing the clock face into a second buffer and using `blit()`?
5. Describe how you would update only the seconds on a display without redrawing the hours and minutes.
