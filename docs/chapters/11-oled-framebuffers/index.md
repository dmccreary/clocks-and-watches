---
title: OLED Displays and Framebuffers
description: OLED displays, the SSD1306 driver, the framebuffer model, show and fill commands, refresh rate, and baudrate tuning.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:39:47
version: 1.10
---

# OLED Displays and Framebuffers

## Summary

Students learn how OLED pixels are stored in a framebuffer and pushed to the screen over I2C or SPI. They initialize a display and clear it. After this chapter they can set up an OLED and put pixels on it.

## Concepts Covered

This chapter covers the following 14 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Display Resolution | 78 |
| OLED Display | 67 |
| SSD1306 Driver | 3 |
| SH1106 Driver | 1 |
| Framebuffer | 58 |
| Pixel Coordinate Mapping | 1 |
| SSD1306 I2C Setup | 1 |
| SSD1306 SPI Setup | 1 |
| Display Show Command | 4 |
| Display Fill Command | 2 |
| Pixel Drawing | 15 |
| Display Refresh Rate | 9 |
| Baudrate Tuning | 2 |
| Screen Clearing | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 4: Control Flow, Functions, and Modules](../04-control-flow-functions/index.md)
- [Chapter 5: The Pico Platform: Pins, Files, and Firmware](../05-pico-platform/index.md)
- [Chapter 8: Communication Buses: I2C, SPI, and UART](../08-communication-buses/index.md)
- [Chapter 9: LED Displays and the First Digital Clock](../09-led-displays/index.md)
- [Chapter 10: Coordinates, Trigonometry, and Clock Geometry](../10-clock-math/index.md)

---

!!! mascot-welcome "Pixels You Control"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Seven-segment digits are great, but an OLED lets you light any of its 8,192 pixels. In this chapter you'll wire one up, learn the trick of drawing in memory first, and put your first pixels on screen. Let's make time tick!

## A Screen You Can Draw On

The TM1637 can show only digits. To draw a clock face, an icon, or a graph you need a display where **every pixel is individually controlled**. The small OLED display, at about three to four dollars, is the ideal first one. This chapter covers what an OLED is, how to connect and initialize it, and the core idea that makes all modern display programming work: the **framebuffer**.

## OLED Display

An **OLED** (organic light-emitting diode) display is a screen made of tiny pixels that each emit their own light. Unlike an LCD, it needs no backlight. A pixel that is off is truly black, so OLEDs have excellent contrast and remain readable from wide angles.

| Property | OLED | LCD (character or TFT) |
|----------|------|------------------------|
| Light source | Each pixel glows | Needs a separate backlight |
| Black level | Truly black (pixel off) | Dark gray from backlight bleed |
| Viewing angle | Very wide | Narrower |
| Power | Depends on how many pixels are lit | Backlight is always on |
| Weakness | Long-term burn-in of static images | Contrast and angle |

The OLED in your kit is **monochrome**, so each pixel is either on (white, blue, or yellow depending on the model) or off. It measures about 0.96 inch across, has 128 columns by 64 rows, and comes in two versions: a 4-pin I2C model and a 7-pin SPI model.

Burn-in means that showing the same bright pixels for months can leave a faint ghost. For a clock, an easy fix is to dim the display or shift the image slightly now and then.

## Display Resolution

**Display resolution** is the number of pixels on the screen, written as width by height. It tells you how much detail you can show.

| Display | Resolution | Pixels |
|---------|-----------|--------|
| Small OLED (SSD1306) | 128 × 64 | 8,192 |
| ST7735 color TFT | 160 × 128 | 20,480 |
| GC9A01 round display | 240 × 240 | 57,600 |
| ILI9341 color TFT | 320 × 240 | 76,800 |
| GC9B72 round smartwatch | 360 × 360 | 129,600 |

Resolution matters because every pixel has to be stored somewhere. The memory needed is the pixel count times the **bits per pixel** (bpp), which is how many bits describe one pixel's color. A monochrome pixel needs 1 bit. A color pixel in the RGB565 format, from Chapter 15, needs 16 bits, which is 2 bytes.

\[ \text{memory (bytes)} = \frac{W \times H \times \text{bpp}}{8} \]

**Worked example.** The OLED needs \( 128 \times 64 \times 1 / 8 = 1{,}024 \) bytes. A 360 by 360 color display needs \( 360 \times 360 \times 16 / 8 = 259{,}200 \) bytes, which is almost the entire 264 KB of RAM on the Pico. This single calculation explains why the small OLED can use a full memory copy of its screen and the large color displays sometimes cannot.

#### Diagram: Resolution and Memory Calculator

<details markdown="1">
<summary>Resolution and Memory Calculator</summary>
Type: chart
**sim-id:** resolution-memory-calculator<br/>
**Library:** Chart.js<br/>
**Status:** Specified

**Learning objective:** Students will *calculate* the memory a screen needs and *evaluate* whether it fits in the Pico's RAM (Bloom: Applying, Evaluating).

**Visual elements:** A bar chart of framebuffer size in KB for the five displays in the table, with a horizontal red line at 264 KB (total RAM) and a yellow line at 200 KB (a practical limit).

**Controls:** Dropdown to choose bits per pixel (1, 8, 16); a custom "width" and "height" input pair that adds a sixth bar. The tooltip on each bar shows the formula with numbers substituted.

**Responsive design:** The chart resizes to the container.

Implementation: Chart.js bar chart with a computed dataset.
</details>

## The SSD1306 Driver

The **SSD1306** is the controller chip inside most small OLED modules. It stores the pixel pattern and drives the panel. Your program does not talk to the panel directly. It sends bytes to the SSD1306 through a **driver**, a library that hides the chip's commands behind friendly calls. The standard library is a file named `ssd1306.py` that you copy to the Pico, as shown in Chapter 4.

The driver has two classes, one per bus: `SSD1306_I2C` and `SSD1306_SPI`. Both are built on top of MicroPython's `framebuf` module, so they share the same drawing methods. Once created, you use the same calls no matter which bus is underneath.

### SSD1306 I2C Setup

On the I2C model, wire four connections: VCC to 3.3 V, GND to ground, SDA to GP0, and SCL to GP1. Confirm the address with the scanner from Chapter 8 (usually `0x3C`), then create the display.

```python
NAME = "11-oled-i2c-hello.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin, I2C
import ssd1306

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)    # width, height, bus
oled.fill(0)                                # clear the buffer
oled.text("Hello", 0, 0)                    # draw text in the buffer
oled.show()                                 # send the buffer to the screen
```

The three drawing lines are explained in the framebuffer section below. The key points here are the three arguments to `SSD1306_I2C`: the display width, the height, and the I2C bus.

### SSD1306 SPI Setup

The SPI model has seven pins. On these boards the clock pin is labeled **D0** and the data pin is labeled **D1**, which are just SPI names in disguise (see Chapter 8).

| OLED pin | Pico pin | Signal |
|----------|----------|--------|
| GND | GND | Ground |
| VCC | 3V3(OUT) | Power |
| D0 | GP2 | SPI clock (SCK) |
| D1 | GP3 | SPI data (MOSI) |
| RES | GP5 | Reset |
| DC | GP4 | Data/command |
| CS | GP6 | Chip select |

```python
NAME = "11-oled-spi-hello.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin, SPI
import ssd1306

spi = SPI(0, baudrate=10_000_000, sck=Pin(2), mosi=Pin(3))
dc = Pin(4)
res = Pin(5)
cs = Pin(6)
oled = ssd1306.SSD1306_SPI(128, 64, spi, dc, res, cs)
oled.fill(0)
oled.text("Hello SPI", 0, 0)
oled.show()
```

The SPI version is faster than I2C, which is why the larger kits use it.

!!! mascot-warning "Blank Screen Checklist"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A blank OLED almost always means one of three things: a missing `show()` call, a wrong bus pin or address, or a power wire on the wrong pin. Run the I2C scanner first, then check that you called `oled.show()` after drawing.

### SH1106 Driver

Some 1.3-inch OLED modules use a different controller, the **SH1106**. It looks the same and even works with the same wiring, but its memory is 132 columns wide instead of 128. If you use the SSD1306 driver on an SH1106 display, the image shows up shifted two pixels to the side with garbage at the edge. The fix is to use the `sh1106.py` driver, which has the same methods as the SSD1306 one. Check the controller name in the product listing before you buy.

## Framebuffer

A **framebuffer** is a block of RAM that holds a copy of every pixel on the screen. When you draw a line or text, you are changing bytes in this buffer, not the physical display. Nothing appears on the OLED until you send the buffer to it.

This two-step design is the most important idea in this chapter. Its benefits:

- **No flicker.** You can draw a hundred things and show them all at the same instant.
- **Simple code.** Drawing is just changing memory, with no hardware delays.
- **One transfer.** The whole screen goes across the bus in one fast burst.

The cost is the RAM you calculated earlier. For the OLED, that is only 1,024 bytes.

The flow is the same every time you update the screen:

1. **Clear** the buffer.
2. **Draw** everything into it.
3. **Show** the buffer on the display.

!!! mascot-thinking "Draw in Memory, Then Reveal"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Think of a painter who finishes a canvas behind a curtain, then pulls the curtain. Your program paints into the framebuffer out of sight and then reveals the finished picture with `show()`, so viewers never see half-drawn frames.

#### Diagram: Framebuffer Pipeline

<details markdown="1">
<summary>Framebuffer Pipeline</summary>
Type: workflow diagram
**sim-id:** framebuffer-pipeline<br/>
**Library:** Mermaid<br/>
**Status:** Specified

**Learning objective:** Students will *understand* the path from a drawing call to lit pixels (Bloom: Understanding).

**Nodes:** Your program, `oled.text()` and `oled.pixel()` (drawing calls), framebuffer in RAM (1,024 bytes), `oled.show()`, I2C or SPI bus, SSD1306 controller memory, OLED panel.

**Interactions:** Every node has a Mermaid `click` directive that opens an infobox describing its role and how many bytes pass through it. A toggle highlights the "Before show()" state, where only the buffer has changed and the panel is unchanged, and the "After show()" state.

**Responsive design:** The diagram scales to container width.

Implementation: Mermaid flowchart with click callbacks.
</details>

### Pixel Coordinate Mapping

Every pixel in the framebuffer has an address in memory, and understanding it demystifies the whole system. The SSD1306 groups the 64 rows into **8 pages** of 8 rows each. A single byte holds a **vertical strip of 8 pixels** in one column. This layout is called `MONO_VLSB` (monochrome, vertical, least-significant-bit first).

For the pixel at (x, y), the byte index and bit position are:

\[ \text{index} = x + \left\lfloor \frac{y}{8} \right\rfloor \times \text{width} \qquad \text{bit} = y \bmod 8 \]

**Worked example.** For pixel (10, 20) on a 128-wide display, the page is \( \lfloor 20/8 \rfloor = 2 \), so the index is \( 10 + 2 \times 128 = 266 \), and the bit is \( 20 \bmod 8 = 4 \). Setting that pixel means setting bit 4 of byte 266. You never do this by hand, because `pixel()` does it for you, but it shows why the bit tricks from Chapter 8 matter.

The phrase "pixel coordinate mapping" also describes the more everyday job of turning a data value into a screen position. To plot a value from 0 to 100 as a height on the 64-pixel screen, where y = 63 is the bottom:

```python
def map_value(v, in_max=100, out_height=64):
    return (out_height - 1) - (v * (out_height - 1)) // in_max

y = map_value(50)      # 32: halfway up
```

## Display Show Command

The **`show()` command** copies the framebuffer to the display. Until you call it, the screen keeps showing the previous picture. Every update needs exactly one `show()` at the end.

```python
oled.fill(0)
oled.text("12:34", 40, 28)
oled.show()               # nothing changes on screen before this line
```

Calling `show()` is the slowest step in your drawing code, because it moves the whole 1,024-byte buffer over the bus. Do all your drawing first and call it **once per frame**. Calling it after every line multiplies the cost for no benefit.

### Display Fill Command

The **`fill()` command** sets every pixel in the buffer to one value: `oled.fill(0)` makes the whole buffer black, and `oled.fill(1)` makes it all white. It is the standard first step of a new frame.

### Screen Clearing

**Screen clearing** is erasing the old picture before drawing a new one. Without it, a changing value is drawn on top of the old one and the digits smear into an unreadable blob. The routine is always `fill(0)`, then draw, then `show()`.

```python
NAME = "11-oled-counter.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin, I2C
from time import sleep
import ssd1306

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

count = 0
while True:
    oled.fill(0)                      # clear the old picture
    oled.text("Count: " + str(count), 0, 0)
    oled.show()                       # reveal the new one
    count += 1
    sleep(1)
```

If you removed the `fill(0)` line, each new number would be drawn over the last, and the display would fill up with overlapping digits.

## Pixel Drawing

The most basic drawing tool is **`pixel(x, y, color)`**, which sets one pixel to color 1 (on) or 0 (off). Calling `pixel(x, y)` with no color returns the current value. Coordinates use the system from Chapter 10: (0, 0) is the top-left, and y increases downward. Pixels outside the screen are silently ignored, so you do not need to check bounds.

```python
oled.fill(0)
for x in range(128):
    oled.pixel(x, 0, 1)         # top border
    oled.pixel(x, 63, 1)        # bottom border
for i in range(64):
    oled.pixel(i * 2, i, 1)     # a diagonal line
oled.show()
```

Drawing a line pixel by pixel like this works but is slow. Chapter 12 introduces `line()`, `rect()`, and `ellipse()`, which do the same job in a single call.

!!! mascot-tip "Test With a Border"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    When you set up a new display, draw a one-pixel border around the whole screen first. If any edge is missing, you have the wrong width, height, or controller, and you find out before you build a whole clock on top of it.

#### Diagram: Pixel Grid Sketchpad

<details markdown="1">
<summary>Pixel Grid Sketchpad</summary>
Type: MicroSim
**sim-id:** pixel-grid-sketchpad<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* coordinates and the buffer layout by turning pixels on and off (Bloom: Applying, Analyzing).

**Visual elements:** A 128 by 64 grid drawn at 6x scale. Beside it, a table of the 1,024 buffer bytes that highlights the byte containing the hovered pixel, with its index and bit.

**Interactions:** Click a pixel to toggle it. Hovering shows `(x, y)`, the byte index using the formula in the text, and the bit. A "Generate code" button outputs the `pixel()` calls for the current drawing. A "Challenge" mode asks the student to click a given (x, y).

**Responsive design:** The grid scales to the container width.

Implementation: p5.js with an array of 1,024 bytes and bit operations.
</details>

## Display Refresh Rate

The **refresh rate** is how many times per second your program redraws the screen, measured in frames per second (fps). The time for one frame is dominated by how long `show()` takes to send the buffer across the bus:

\[ t_{frame} = \frac{\text{bytes} \times \text{bits per byte on the wire}}{\text{bus speed}} \]

For an I2C bus, each byte takes 9 clock cycles. At 400 kHz, the 1,024-byte OLED buffer takes \( 1024 \times 9 / 400{,}000 \approx 23 \) ms, or up to about 43 frames per second. On SPI at 10 MHz, the same buffer takes \( 1024 \times 8 / 10{,}000{,}000 \approx 0.8 \) ms, and other overhead usually dominates.

You can measure the real time with `ticks_us()`, which counts microseconds:

```python
from time import ticks_us, ticks_diff

t0 = ticks_us()
oled.show()
t1 = ticks_us()
print("show() took", ticks_diff(t1, t0) / 1000, "ms")
```

Your eyes need about 24 to 30 frames per second to see smooth motion. A clock display only needs to change once per second, so an OLED has more than enough speed. Speed matters for animation and for the larger color screens in later chapters.

### Baudrate Tuning

**Baudrate tuning** is finding the fastest bus speed at which your particular display works reliably. The SPI baudrate from Chapter 8 controls how fast bits move. Faster means a quicker `show()`, but if it is too fast, the display shows garbled or missing pixels because wires and chips cannot keep up.

Follow this test procedure:

1. Start at a safe speed, such as 1,000,000.
2. Draw a full-screen test pattern, such as the border and diagonal above.
3. Measure `show()` time and inspect the picture.
4. Increase the baudrate (4 MHz, 8 MHz, 10 MHz, 20 MHz) and repeat.
5. Find the first speed that shows errors, then use a value about 20 to 30 percent below it.

The safe choice matters because a setup that works on your desk can fail with longer wires or a warmer chip. For I2C, the equivalent is the `freq` argument: try 100 kHz, then 400 kHz. Many small modules do not work above 400 kHz.

## Putting It Together

| Step | Call |
|------|------|
| Create the bus | `I2C(...)` or `SPI(...)` |
| Create the display | `SSD1306_I2C(128, 64, i2c)` or `SSD1306_SPI(...)` |
| Start a frame | `oled.fill(0)` |
| Draw | `oled.text(...)`, `oled.pixel(...)` |
| Reveal | `oled.show()` |

## Key Takeaways

- An OLED makes its own light, giving high contrast, and the common one is 128 × 64 monochrome.
- Resolution times bits per pixel gives the memory needed; 128 × 64 mono is 1,024 bytes.
- The SSD1306 driver builds on `framebuf`; choose `SSD1306_I2C` or `SSD1306_SPI`.
- Draw in the framebuffer, and call `show()` once to update the screen.
- Start each frame with `fill(0)` so old drawings do not smear.
- Measure `show()` time, and tune the baudrate by testing upward until errors appear.

!!! mascot-celebration "Pixels On!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now initialize an OLED over I2C or SPI, clear a framebuffer, draw pixels, and reveal them with `show()`. Every display in the rest of this book builds on that same pattern. Every second counts!

## Practice Questions

1. How many bytes does a 128 × 64 monochrome framebuffer need? What about a 240 × 240 display at 16 bits per pixel?
2. Your program draws text but the OLED stays blank. List the first three things you check.
3. Why does a changing number look smudged if you forget `fill(0)`?
4. Find the byte index and bit for pixel (30, 45) on a 128-wide `MONO_VLSB` buffer.
5. An I2C OLED at 400 kHz needs 23 ms per `show()`. What is the maximum frame rate, and is that enough for a once-per-second clock?
