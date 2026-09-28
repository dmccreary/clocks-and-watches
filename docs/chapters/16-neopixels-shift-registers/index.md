---
title: NeoPixels and Shift Register Clocks
description: NeoPixel LEDs, HSV color, LED power budgeting, and 74HC595 shift registers for creative art clocks.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:47:54
version: 1.10
---

# NeoPixels and Shift Register Clocks

## Summary

Students control WS2812B strips, mix colors with HSV, and budget LED power. They expand outputs with shift registers. After this chapter they can build an art clock from many addressable LEDs.

## Concepts Covered

This chapter covers the following 20 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| NeoPixel LEDs | 16 |
| HSV Color Model | 3 |
| WS2812B Standard | 1 |
| NeoPixel Wiring | 2 |
| NeoPixel Color Mixing | 1 |
| Binary Clock | 1 |
| Fibonacci Clock | 1 |
| NeoPixel Seven Segment | 1 |
| Serial to Parallel | 6 |
| Color Wheel | 1 |
| NeoPixel Library | 1 |
| LED Density Per Meter | 3 |
| Shift Register | 5 |
| LED Power Calculation | 1 |
| NeoPixel Strip Types | 2 |
| 74HC595 Chip | 4 |
| NeoPixel Ring | 1 |
| NeoPixel Matrix | 1 |
| Latch Pin | 2 |
| Shift Register Chaining | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Computational Thinking and Physical Computing](../01-foundations/index.md)
- [Chapter 2: Electronics Fundamentals and Breadboard Wiring](../02-electronics-fundamentals/index.md)
- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)
- [Chapter 4: Control Flow, Functions, and Modules](../04-control-flow-functions/index.md)
- [Chapter 5: The Pico Platform: Pins, Files, and Firmware](../05-pico-platform/index.md)
- [Chapter 8: Communication Buses: I2C, SPI, and UART](../08-communication-buses/index.md)
- [Chapter 9: LED Displays and the First Digital Clock](../09-led-displays/index.md)
- [Chapter 15: Color Displays and Smartwatch Faces](../15-color-displays/index.md)

---

!!! mascot-welcome "Let's Get Colorful"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Now for the fun part: clocks made of glowing lights. You'll control hundreds of full-color LEDs with a single wire, and learn a chip that turns three pins into as many outputs as you like. Let's make time tick!

## Clocks Made of Light

Every clock so far used a display module. In this chapter the *arrangement of lights* becomes the display. A strip of addressable LEDs can be bent into a ring, folded into digits, or laid out as a binary or Fibonacci pattern, and the clock's personality comes from your design. We also meet a second tool for the same goal: the shift register, which gives you more output pins when you run out.

## NeoPixel LEDs

A **NeoPixel** is an LED that contains a tiny controller chip and a red, a green, and a blue LED in one package. The chips are chained together. The Pico sends a stream of color data down one wire; the first pixel takes its color and passes the rest along to the next, and so on down the line. Each pixel can be set to any color and brightness independently.

The name NeoPixel is Adafruit's brand. The chip inside most of them is the **WS2812B**, which you will also see in many cheap strips. The advantage over the LED displays of Chapter 9 is huge:

| | Individual LEDs | NeoPixels |
|---|-----------------|-----------|
| Wires per pixel | 2 or more (plus a resistor) | Shared; 3 wires for the whole strip |
| Pico pins for 100 LEDs | 100 or more | 1 |
| Color | One per LED | 16 million per pixel |

### WS2812B Standard

The **WS2812B** is the specification these LEDs follow. Three facts matter for us:

- It runs from **5 V** power.
- It receives data on a single wire at **800 kHz**, which is fast, and any timing error garbles the colors. MicroPython handles the timing for you.
- Each pixel takes **24 bits** of data: 8 each for green, red, and blue, so every color channel runs from 0 to 255. The pixel latches its color when the data line is quiet for about 50 microseconds.

### NeoPixel Wiring

A strip has three connections: **5V**, **GND**, and **DIN** (data in). Connect them as follows:

| Strip wire | Connect to |
|------------|-----------|
| 5V (red) | VBUS (5 V from USB) or an external 5 V supply |
| GND (black) | Pico GND, and the supply's ground |
| DIN (data, often green) | A Pico GPIO pin such as GP16 |

Three good habits protect the LEDs and the Pico:

- **Always connect the grounds together.** The data signal is measured relative to ground, so without a shared ground the strip ignores it.
- Place a **300 to 500 ohm resistor** in series with the data line, close to the first pixel, to protect it from voltage spikes.
- Add a **large capacitor**, about 1000 µF, across the strip's 5 V and GND, near its start, to absorb the surge when the LEDs switch on.

The strip wants a data signal near its supply voltage, while the Pico provides 3.3 V. For short wires this usually works in practice, though it is technically outside the specification. If the first pixels flicker or show random colors, use a **level shifter** to raise the data line to 5 V.

!!! mascot-warning "Share the Ground First"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A strip that lights up randomly, or not at all, is usually missing a shared ground or has power connected before ground. Connect ground first, add the data resistor, and then apply power. It takes a few seconds and saves both strip and Pico.

## The NeoPixel Library

MicroPython includes a built-in **`neopixel`** library. You create a strip object by telling it which pin and how many pixels, set individual pixels by index, and call `write()` to send the colors, just like `show()` on a framebuffer display.

```python
NAME = "16-neopixel-hello.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import neopixel
from machine import Pin
from time import sleep

NUM = 12
np = neopixel.NeoPixel(Pin(16), NUM)

np[0] = (255, 0, 0)         # first pixel red   (red, green, blue)
np[1] = (0, 255, 0)         # second pixel green
np[2] = (0, 0, 255)         # third pixel blue
np.write()                  # nothing lights up until this line
sleep(2)

np.fill((0, 0, 0))          # all pixels off
np.write()
```

Nothing changes until `write()`, so you can update every pixel and then show them all at the same instant. Pixels are numbered from 0, starting at the end of the strip that connects to the Pico.

### NeoPixel Color Mixing

NeoPixel color is **additive**: light from the three LEDs adds together. Full red plus full green looks yellow, and all three at full make white. Values are three numbers from 0 to 255.

| Color | (R, G, B) |
|-------|-----------|
| Red | (255, 0, 0) |
| Yellow | (255, 255, 0) |
| Cyan | (0, 255, 255) |
| Purple | (128, 0, 128) |
| Warm white | (255, 147, 41) |
| White | (255, 255, 255) |

NeoPixels are extremely bright, and a value of 255 is uncomfortable to look at from a desk. Use values from about 10 to 60 for indoor clocks. That also saves power, as the next sections show.

!!! mascot-tip "Turn Down the Brightness"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Start every NeoPixel project with color values of 30 or less. You'll get a more pleasant glow, a cooler strip, and a much smaller power bill. You can always turn it up later.

## LED Power Calculation

Each NeoPixel draws up to about **60 mA** when all three colors are at full brightness (white at 255). Lit pixels of a single color draw about 20 mA. The current adds up quickly over a whole strip:

\[ I = N \times 60\ \text{mA} \times \text{brightness fraction} \]

**Worked example.** A ring of 60 pixels, all white, at 25 percent brightness draws \( 60 \times 60 \times 0.25 = 900 \) mA, almost a full amp. A USB port provides about 500 mA, so this ring could overload it. But a clock rarely lights all its pixels at once. Three lit pixels with a moderate color draw \( 3 \times 20 = 60 \) mA, no problem.

Compare the worst case for whole strips:

| Strip density | LEDs per meter | Worst-case current per meter (all white) |
|---------------|----------------|------------------------------------------|
| Low | 30 | 1.8 A |
| Standard | 60 | 3.6 A |
| Dense | 144 | 8.6 A |

Plan for the maximum your program can light up, and if it exceeds about 400 mA, power the strip from a separate 5 V supply, with its ground tied to the Pico's ground.

### NeoPixel Strip Types

NeoPixels come in several shapes, each suited to a different clock:

| Type | Description | Good for |
|------|-------------|----------|
| Strip | A long flexible line | Seven-segment art, binary clocks |
| Ring | Pixels in a circle (12, 16, 24, or 60) | Analog-style faces |
| Matrix | A grid (8 by 8, 16 by 16) | Scrolling text, pictures |
| String | Individual pixels on a wire | Placing pixels anywhere |

### LED Density Per Meter

**LED density** is how many pixels a strip packs into each meter. Common densities are 30, 60, and 144 per meter. A denser strip looks smoother and brighter, but costs more and draws more power, as the table above showed. Sixty per meter puts pixels about 17 mm apart, a good size for a clock digit. Pick the density to match your layout: sparse strips suit large art clocks, and dense strips suit small, detailed ones.

#### Diagram: NeoPixel Power Budget

<details markdown="1">
<summary>NeoPixel Power Budget</summary>
Type: MicroSim
**sim-id:** neopixel-power-budget<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *calculate* the current a LED design draws and *evaluate* whether it needs an external supply (Bloom: Applying, Evaluating).

**Visual elements:** A strip of pixels where the student clicks to light each one. A gauge shows total current in mA with a green zone below 400 mA, yellow to 500 mA, and red above 500 mA (the USB limit).

**Controls:** A dropdown for strip length (12, 30, 60, 144), a color picker for the lit color, a brightness slider (0 to 100 percent), and a "Light all" button. The readout shows the formula with the numbers substituted.

**Responsive design:** The strip wraps into rows on narrow screens.

Implementation: p5.js with a per-pixel current estimate of R+G+B channel values times 20 mA per full channel.
</details>

## HSV Color Model

Mixing red, green, and blue by hand is awkward when you want "the same color, but dimmer" or a rainbow. The **HSV color model** describes a color with three more natural numbers:

- **Hue:** the color itself, as an angle from 0 to 359 degrees around a color wheel (0 is red, 120 green, 240 blue).
- **Saturation:** how vivid it is, from gray (0) to pure color (255).
- **Value:** how bright it is, from 0 (off) to 255 (full).

To change brightness, you change only the value. To move through the rainbow, you change only the hue. MicroPython has no built-in HSV converter, so here is a compact one that uses only integers:

```python
def hsv_to_rgb(h, s, v):
    """h: 0-359, s and v: 0-255. Returns an (r, g, b) tuple."""
    if s == 0:
        return (v, v, v)
    region = h // 60
    rem = (h % 60) * 255 // 60
    p = v * (255 - s) // 255
    q = v * (255 - s * rem // 255) // 255
    t = v * (255 - s * (255 - rem) // 255) // 255
    if region == 0: return (v, t, p)
    if region == 1: return (q, v, p)
    if region == 2: return (p, v, t)
    if region == 3: return (p, q, v)
    if region == 4: return (t, p, v)
    return (v, p, q)
```

### Color Wheel

A **color wheel** arranges all the hues around a circle, so the hue of a point is just its angle, the same idea as the clock angles of Chapter 10. On a ring of `N` pixels, giving pixel `i` the hue \( 360 \times i / N \) paints a rainbow. Adding an offset that grows every frame rotates it.

```python
NAME = "16-rainbow-ring.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import neopixel
from machine import Pin
from time import sleep_ms

N = 12
np = neopixel.NeoPixel(Pin(16), N)

offset = 0
while True:
    for i in range(N):
        hue = (i * 360 // N + offset) % 360
        np[i] = hsv_to_rgb(hue, 255, 30)     # value 30: comfortable brightness
    np.write()
    offset = (offset + 5) % 360
    sleep_ms(40)
```

Because value stays at 30, the rainbow is easy on the eyes, and changing that one number changes the brightness of everything.

!!! mascot-thinking "Hue Is Just an Angle"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A color wheel is a circle, and a hue is an angle on it. You already know how to spin an angle around a clock face, so making colors move is the same skill: add a little to the angle each frame and wrap around at 360.

#### Diagram: HSV Color Wheel

<details markdown="1">
<summary>HSV Color Wheel</summary>
Type: MicroSim
**sim-id:** hsv-color-wheel<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *understand* hue, saturation, and value and *convert* between HSV and RGB (Bloom: Understanding, Applying).

**Visual elements:** A color wheel with a draggable marker, and a swatch of the selected color. A 12-pixel virtual ring below it shows the rainbow that `hsv_to_rgb` would produce.

**Controls:** Sliders for hue (0 to 359), saturation, and value. Readouts for R, G, B and the `np[i] = (...)` code line. A "Rotate" button animates the offset as in the rainbow program.

**Responsive design:** The wheel scales to container width.

Implementation: p5.js with the same integer conversion as the MicroPython code.
</details>

## NeoPixel Ring

A **NeoPixel ring** is a circle of pixels, usually 12, 16, 24, or 60. A 12-pixel ring maps naturally to the 12 hours on a clock face. Pixel 0 sits at one point on the ring (often near the data connector), and you mount the ring so pixel 0 is at the top, at 12 o'clock.

A simple 12-pixel clock lights one pixel for the hour and one for the minute (each pixel is five minutes):

```python
h, m, s = time.localtime()[3:6]
np.fill((0, 0, 0))
np[h % 12] = (30, 0, 0)               # hour: red
np[m // 5] = (0, 30, 0)               # minute (in 5-minute steps): green
if h % 12 == m // 5:                  # both on the same pixel
    np[h % 12] = (30, 30, 0)          # additive mix: yellow
np.write()
```

The overlap rule shows the additive color mixing of NeoPixels in action: red and green together make yellow.

## NeoPixel Matrix

A **NeoPixel matrix** is a grid of pixels wired as one long strip that snakes back and forth. To draw on it by (x, y) position, you convert the coordinates to a strip index. On an 8 by 8 matrix wired in a **zigzag** (odd rows run backward):

```python
def index(x, y, width=8):
    return y * width + (x if y % 2 == 0 else width - 1 - x)
```

This is the same coordinate idea as the display coordinates in Chapter 12. A matrix can show scrolling text, small pictures, and 3 by 5 pixel digits.

## NeoPixel Seven Segment

A **NeoPixel seven-segment display** builds each digit from strip pixels, with every segment made of two or three pixels. It is the addressable-LED cousin of the seven-segment display in Chapter 9, and it uses the same `0x3F`-style segment bytes.

The idea is to note which pixels belong to each segment, then light them when the digit's segment bit is on:

```python
SEG_PIXELS = [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13)]   # a to g
DIGITS = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F]

def show_digit(np, first_pixel, digit, color):
    pattern = DIGITS[digit]
    for seg in range(7):
        on = (pattern >> seg) & 1
        for p in SEG_PIXELS[seg]:
            np[first_pixel + p] = color if on else (0, 0, 0)
```

With two pixels per segment, a digit uses 14 pixels, and a four-digit clock with two colon pixels needs about 58. A single 60-pixel strip is enough to display the entire time, in any color, even changing color with the hour.

#### Diagram: NeoPixel Digit Layout

<details markdown="1">
<summary>NeoPixel Digit Layout</summary>
Type: interactive diagram
**sim-id:** neopixel-digit-layout<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *design* a pixel-to-segment mapping and *apply* it to display a digit (Bloom: Applying, Creating).

**Visual elements:** A single digit drawn as seven segments, each showing its pixel numbers (0 to 13).

**Interactions:** The student can click a segment to see which pixels it contains, choose a digit 0 to 9 to see which segments and pixel indices light, and toggle "Show strip order" to see how the strip snakes through the digit. A "Copy `SEG_PIXELS`" button outputs the mapping as Python.

**Responsive design:** Digit scales to canvas size.

Implementation: p5.js with segment polygons and a lookup table.
</details>

## Binary Clock

A **binary clock** shows the time in binary, with each LED representing one bit (Chapter 8). The hours, minutes, and seconds each get a row. A pixel that is on is a 1, off is a 0. Minutes and seconds go up to 59, which needs 6 bits (32 + 16 + 8 + 4 + 2 + 1); hours go up to 23, which needs 5.

```python
def show_bits(np, first_pixel, value, bits, color):
    for b in range(bits):
        on = (value >> b) & 1
        np[first_pixel + b] = color if on else (0, 0, 0)

h, m, s = time.localtime()[3:6]
show_bits(np, 0, s, 6, (0, 0, 40))      # seconds on pixels 0 to 5
show_bits(np, 6, m, 6, (0, 40, 0))      # minutes on pixels 6 to 11
show_bits(np, 12, h, 5, (40, 0, 0))     # hours on pixels 12 to 16
np.write()
```

This is a fun challenge to read: at 9:37, minutes is 37 = 32 + 4 + 1, so the 32, 4, and 1 pixels are lit. Try the interactive version below.

#### Diagram: Binary Clock

<iframe src="../../sims/binary-clock/binary-clock-vertical.html" width="420" height="295" scrolling="no"></iframe>

[Run the Binary Clock MicroSim fullscreen](../../sims/binary-clock/binary-clock-vertical.html){ .md-button }

<details markdown="1">
<summary>Binary Clock (existing MicroSim)</summary>
Type: MicroSim
**sim-id:** binary-clock<br/>
**Library:** p5.js<br/>
**Status:** Reused<br/>
**Source:** docs/sims/binary-clock/

This MicroSim is already part of this book. Learning objective: students will *apply* binary place values to read the time (Bloom: Applying).
</details>

## Fibonacci Clock

A **Fibonacci clock** shows the time using five squares whose sizes are the first Fibonacci numbers: 1, 1, 2, 3, and 5. Each square can be lit in one of four ways, and the sum of the sizes shows the value:

| Square color | Meaning |
|--------------|---------|
| Red | Counts toward the **hour** |
| Green | Counts toward the **minutes** in 5-minute units |
| Blue | Counts toward **both** |
| Off (white or dark) | Counts toward neither |

The hour is the sum of the red and blue squares, and the minutes divided by 5 is the sum of the green and blue squares. For 3:20, the hour is 3, and the minutes in 5-minute units are \( 20 / 5 = 4 \). Light the 3-square **blue**, since it counts toward both totals (hour = 3, and 3 of the 4 minute units), then light a 1-square **green** to add the last minute unit (3 + 1 = 4). Many times have more than one valid arrangement, which the clock can pick at random, so the same time looks different each time.

The Fibonacci clock combines the thinking skills from Chapter 1: the *pattern* (Fibonacci sums), *abstraction* (five squares hide the time), and an *algorithm* (choose which squares make the required sums).

## Serial to Parallel Conversion

Now for a different way to get more outputs. You know two ways of moving data: **serially** (bits one after another on a wire) and **in parallel** (many bits at the same instant on many wires). **Serial-to-parallel conversion** takes a stream of serial bits and presents them as parallel outputs. A special chip does this job so that your Pico needs only a few pins to control many outputs.

## Shift Register

A **shift register** is a chip that holds a row of bits and moves them along, one position at a time, each time it receives a pulse on its clock input. Think of a row of eight boxes, each holding a 0 or 1. Each clock pulse slides every bit one box to the right and drops a new bit into the first box. After eight pulses, the row holds the eight bits you sent, and those bits control eight output pins.

### The 74HC595 Chip

The **74HC595** is the standard shift register for hobby projects. It is an 8-bit serial-in, parallel-out register that costs pennies. Its important pins:

| Pin name | Also called | Job |
|----------|-------------|-----|
| SER | DS, DATA | Serial data in (one bit at a time) |
| SRCLK | SHCP, CLOCK | Shifts the data one place on each rising edge |
| RCLK | STCP, LATCH | Copies the shifted bits to the outputs |
| Q0 to Q7 | Outputs | The eight parallel outputs |
| QH' | Serial out | Passes the overflow bit on to a second chip |
| OE | Output enable | Tie to GND to keep outputs on |
| SRCLR | Clear | Tie to 3.3 V to disable clearing |
| VCC, GND | Power | 3.3 V and ground |

Each output can supply about 6 mA comfortably, so connect an LED with a current-limiting resistor (Chapter 2), or a transistor for bigger loads. Outputs are limited to a few dozen milliamps in total.

### Latch Pin

The **latch pin** solves a problem. While bits are being shifted in, the outputs would flicker as the data moves along. The 74HC595 avoids this with two stages: the **shift register** collects the bits, and a separate **storage register** drives the outputs. Pulsing the latch pin copies the shift register into the storage register in one instant, so all eight outputs change at exactly the same moment.

The complete sequence has three steps: shift in eight bits with the clock, then pulse the latch once. Here is the MicroPython function:

```python
NAME = "16-shift-register.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin
from time import sleep

data = Pin(2, Pin.OUT)      # SER
clock = Pin(3, Pin.OUT)     # SRCLK
latch = Pin(4, Pin.OUT)     # RCLK

def write_byte(value):
    latch.value(0)
    for i in range(8):
        data.value((value >> (7 - i)) & 1)   # most significant bit first
        clock.value(1)                       # shift this bit in
        clock.value(0)
    latch.value(1)                           # copy to the outputs

write_byte(0b10101010)      # lights Q7, Q5, Q3, Q1
```

Sending the most significant bit first makes bit *n* of the value appear on output *Qn*, so `0b00000001` lights Q0. This uses the bit ordering ideas of Chapter 8. You can also use the Pico's hardware SPI for the same job, and it is faster.

### Shift Register Chaining

The `QH'` output passes the bit that falls off the end to the next chip's `SER` input. If you connect the `QH'` of one chip to the `SER` of another and share the clock and latch lines, the two chips act as a single 16-bit register. Send two bytes instead of one, and all 16 outputs update. Chain four chips for 32 outputs, enough for a four-digit, seven-segment clock with eight segments (including the decimal point) per digit, still using only three Pico pins.

```python
def write_bytes(values):
    latch.value(0)
    for value in values:              # send the far chip's byte first
        for i in range(8):
            data.value((value >> (7 - i)) & 1)
            clock.value(1)
            clock.value(0)
    latch.value(1)

digits = [0x3F, 0x06, 0x5B, 0x4F]     # 0, 1, 2, 3 from Chapter 9
write_bytes(digits)
```

This design needs no multiplexing (Chapter 9), since every segment has its own output and stays lit on its own. It costs four chips and 32 resistors instead, but it is simple, rock solid, and needs no constant refreshing.

#### Diagram: Shift Register Simulator

<iframe src="../../sims/shift-register/main.html" width="100%" height="480px" scrolling="no"></iframe>

[Run the Shift Register MicroSim fullscreen](../../sims/shift-register/main.html){ .md-button }

<details markdown="1">
<summary>Shift Register (existing MicroSim)</summary>
Type: MicroSim
**sim-id:** shift-register<br/>
**Library:** p5.js<br/>
**Status:** Reused<br/>
**Source:** docs/sims/shift-register/

This MicroSim is already part of this book. Learning objective: students will *understand* how serial bits shift in and appear on parallel outputs after a latch pulse (Bloom: Understanding).
</details>

## Putting It Together

| Goal | Tool |
|------|------|
| Many full-color LEDs, one pin | NeoPixels with `neopixel.NeoPixel` |
| A rainbow or brightness control | HSV with `hsv_to_rgb()` |
| Circular clock face | NeoPixel ring, one pixel per 5 minutes |
| Watch out for power | Current = pixels × 60 mA × brightness |
| More outputs from few pins | 74HC595 (serial to parallel) |
| Even more outputs | Chain chips through `QH'` |

## Key Takeaways

- A NeoPixel (WS2812B) is an LED with a built-in controller; one data pin drives a whole chain.
- Connect grounds together, add a data resistor and a capacitor, and keep brightness values low.
- Power is about 60 mA per pixel at full white; add it up before choosing a supply.
- HSV separates color, vividness, and brightness, and a hue is an angle on a color wheel.
- Rings, matrices, digit layouts, binary, and Fibonacci designs are different ways to arrange the same pixels.
- A 74HC595 converts serial data to parallel outputs; the latch updates them all at once, and chaining multiplies them.

!!! mascot-celebration "Lights, Clock, Action"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now drive NeoPixels, paint a rainbow with HSV, budget the power, and expand your outputs with a shift register. Your art clock is only a design away. Every second counts!

## Practice Questions

1. A ring has 24 pixels, and your program lights 6 of them in white at 20 percent brightness. Estimate the current.
2. Why must the strip's ground be connected to the Pico's ground?
3. Write the hue values for 12 pixels spaced evenly around a color wheel.
4. Explain the job of the latch pin and what would happen without it.
5. Show the pixels lit in a binary clock for the minute value 45.
