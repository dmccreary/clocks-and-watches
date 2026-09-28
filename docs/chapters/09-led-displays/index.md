---
title: LED Displays and the First Digital Clock
description: Seven-segment LED displays and the TM1637 driver: build a digital clock with a flashing colon, plus MAX7219, LCD1602, and addressable LEDs.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:37:22
version: 1.10
---

# LED Displays and the First Digital Clock

## Summary

Students learn how seven-segment displays work and drive a TM1637 four-digit module with four wires. They also meet MAX7219 and character LCD displays. After this chapter they can build and wire a working digital LED clock.

## Concepts Covered

This chapter covers the following 11 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| LED Display | 190 |
| Seven Segment Display | 10 |
| Character LCD | 2 |
| Addressable LEDs | 17 |
| Wiring Diagrams | 2 |
| Segment Multiplexing | 1 |
| TM1637 Driver | 6 |
| MAX7219 Driver | 1 |
| LCD1602 Display | 1 |
| TM1637 Wiring | 1 |
| Colon Flashing | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Computational Thinking and Physical Computing](../01-foundations/index.md)
- [Chapter 2: Electronics Fundamentals and Breadboard Wiring](../02-electronics-fundamentals/index.md)
- [Chapter 4: Control Flow, Functions, and Modules](../04-control-flow-functions/index.md)
- [Chapter 5: The Pico Platform: Pins, Files, and Firmware](../05-pico-platform/index.md)
- [Chapter 6: Getting the Time in MicroPython](../06-getting-time/index.md)
- [Chapter 8: Communication Buses: I2C, SPI, and UART](../08-communication-buses/index.md)

---

!!! mascot-welcome "Your First Real Clock"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This is the chapter where glowing digits appear. With one small module that costs about two dollars and just four wires, you'll build a working digital clock with a flashing colon. Let's make time tick!

## From Numbers to Glowing Digits

You can now read the time and format it as text, but so far the answer only appears in the Shell. This chapter puts time in front of a person. You will learn how a seven-segment display works, how a driver chip lets four wires control it, and how to flash the colon each second. Then we tour the neighbors of the seven-segment family: the MAX7219, the character LCD, and addressable LEDs.

## LED Display

An **LED display** is any display whose picture is made of LEDs that give off their own light. Because each LED glows by itself, LED displays are bright and easy to read from across a room, even in the dark. They are also simple, which makes them the best place to start.

| Type | Looks like | Good for |
|------|-----------|----------|
| Single LEDs | Individual dots | Status lights, art clocks |
| Seven-segment | Digits like a calculator | Time and numbers |
| LED matrix | Grid of dots (8 by 8) | Letters and simple graphics |
| Addressable LEDs | Strips and rings | Colorful art clocks |

Their limits are size and detail. A seven-segment display can show only numbers and a few letters, and a matrix can show only a coarse picture. Later chapters cover OLED and color displays, which can draw anything.

## Seven-Segment Display

A **seven-segment display** shows a digit using seven bar-shaped LEDs, called **segments**, arranged in a figure 8. The segments are labeled `a` through `g`, starting at the top and going clockwise, with `g` in the middle. Many displays add an eighth dot, `dp`, for a decimal point.

Turning on the right combination of segments makes each digit:

| Digit | Segments on | Byte (`gfedcba`) |
|-------|-------------|------------------|
| 0 | a b c d e f | `0x3F` |
| 1 | b c | `0x06` |
| 2 | a b d e g | `0x5B` |
| 3 | a b c d g | `0x4F` |
| 4 | b c f g | `0x66` |
| 5 | a c d f g | `0x6D` |
| 6 | a c d e f g | `0x7D` |
| 7 | a b c | `0x07` |
| 8 | all seven | `0x7F` |
| 9 | a b c d f g | `0x6F` |

The **byte** column shows how a program stores a digit: one bit per segment, so bit 0 is segment `a`, bit 1 is `b`, and so on up to bit 6 for `g`. A `1` bit turns that segment on. This is the bit-manipulation idea from Chapter 8 in action, and the reason bytes are the natural way to talk to a display.

Seven-segment displays come in two electrical styles. In a **common cathode** display all the LED negative legs are tied together and you put a positive voltage on a segment to light it. In a **common anode** display the positive legs are joined instead and a segment lights when its pin goes low. Driver chips hide this difference, but it matters if you wire segments directly.

The interactive simulation below lets you control each segment yourself.

#### Diagram: Seven-Segment Display

<iframe src="../../sims/seven-segment-display/7-segment-display.html" width="100%" height="500px" scrolling="no"></iframe>

[Run the Seven-Segment Display MicroSim fullscreen](../../sims/seven-segment-display/7-segment-display.html){ .md-button }

<details markdown="1">
<summary>Seven-Segment Display (existing MicroSim)</summary>
Type: MicroSim
**sim-id:** seven-segment-display<br/>
**Library:** p5.js<br/>
**Status:** Reused<br/>
**Source:** docs/sims/seven-segment-display/

This MicroSim is already part of this book. Learning objective: students will *identify* which segments form each digit and *apply* the segment byte encoding (Bloom: Remembering, Applying).
</details>

### Segment Multiplexing

A four-digit display has \( 4 \times 8 = 32 \) LEDs to control. Giving each its own pin would need 32 pins, more than the Pico has spare. **Segment multiplexing** solves this by sharing. All four digits connect their `a` to `dp` wires to the *same* 8 lines, and each digit also has its own **digit select** wire. That is 8 + 4 = 12 pins.

The trick is that only **one digit is lit at a time**. The controller turns on digit 1 with its pattern, then digit 2 with its pattern, and so on, cycling faster than the eye can follow, more than 100 times per second. **Persistence of vision** makes all four appear lit at once.

Multiplexing has a cost: each digit is only on one quarter of the time, so each segment needs about four times the current to look equally bright. It also demands that something keeps cycling constantly. If your program stops to do other work, the display flickers or freezes on one digit.

!!! mascot-thinking "Fast Enough to Fool the Eye"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Multiplexing is a trick of timing: show one digit at a time, but so fast that your eyes blend them together. The good news is that a driver chip does the cycling for you, so your program never has to.

## TM1637 Driver

The **TM1637** is a small driver chip that runs a four-digit seven-segment display and does all the multiplexing by itself. You send it the digits to show, and it keeps them lit. It is found on ready-made modules that cost about one to two dollars, and it needs only four wires: power, ground, and two signal wires. That is why it is the first clock display in this course.

Despite the wires being called CLK and DIO, the TM1637 uses its own protocol. It is similar to I2C, but it has no device address. That means you can connect it to **any two GPIO pins**, and an I2C scanner will not find it.

You control it with a MicroPython driver library, `tm1637.py`, that you copy to the Pico (Chapter 4 shows how). The library provides the calls listed here:

| Call | What it does |
|------|-------------|
| `tm = tm1637.TM1637(clk=Pin(2), dio=Pin(3))` | Create the display object |
| `tm.numbers(12, 34)` | Show `12:34` with the colon on |
| `tm.number(1234)` | Show a single four-digit number |
| `tm.show("abcd")` | Show text (letters that fit seven segments) |
| `tm.brightness(0..7)` | Set brightness from 0 (dim) to 7 (bright) |

### TM1637 Wiring

Four wires connect the module to the Pico. Use the color scheme from Chapter 2: red for power, black for ground, and two other colors for the signals.

| TM1637 pin | Pico pin | Physical pin | Wire color |
|------------|----------|--------------|------------|
| VCC | 3V3(OUT) | 36 | Red |
| GND | GND | 38 | Black |
| CLK | GP2 | 4 | Yellow |
| DIO | GP3 | 5 | Green |

The module works from 3.3 V or 5 V. Powering it from 3.3 V keeps the signal levels safe for the Pico.

#### Diagram: TM1637 Wiring Diagram

<details markdown="1">
<summary>TM1637 Wiring Diagram</summary>
Type: interactive diagram
**sim-id:** tm1637-wiring<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* a wiring table by connecting the correct pins in a virtual build (Bloom: Applying).

**Visual elements:** A Pico pinout on the left and a TM1637 module on the right, with the four module pins (VCC, GND, CLK, DIO) highlighted.

**Interactions:**

- The student drags a wire from each module pin to a Pico pin. Correct connections lock in the wire color from the table; wrong ones show a hint such as "VCC needs 3.3 V, not GND."
- When all four are correct, the module display lights up `12:34` and the colon flashes.
- A "Show answer" button draws the correct wires.

**Responsive design:** Board and module scale to the canvas; touch drag is supported.

Implementation: p5.js with pin hit-testing.
</details>

The driver library must exist on the Pico before this program runs. The program builds the display object, then in a loop reads hours and minutes from the time tuple and shows them. The `numbers()` call takes hours and minutes as separate values, which keeps the leading zero, for example `09:05`.

```python
NAME = "09-tm1637-clock.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import tm1637
from machine import Pin
from time import localtime, sleep

tm = tm1637.TM1637(clk=Pin(2), dio=Pin(3))
tm.brightness(3)

while True:
    h, m = localtime()[3:5]
    tm.numbers(h, m)        # shows HH:MM with the colon on
    sleep(1)
```

### Colon Flashing

A clock with a steady colon looks static. A colon that blinks once per second shows that the clock is alive. The **colon** is an extra pair of dots between the second and third digits, and the `numbers()` call takes a `colon` argument to turn it on or off.

The simplest way to blink it is to base it on the current second: on for even seconds, off for odd ones.

```python
NAME = "09-tm1637-colon.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import tm1637
from machine import Pin
from time import localtime, sleep

tm = tm1637.TM1637(clk=Pin(2), dio=Pin(3))

while True:
    h, m, s = localtime()[3:6]
    tm.numbers(h, m, colon=(s % 2 == 0))   # colon on when the second is even
    sleep(0.2)
```

Because the colon state comes from the actual seconds value rather than a counter, it can never drift out of step with the time. Checking five times a second (`sleep(0.2)`) means the display changes within a fifth of a second of each new second.

!!! mascot-tip "Derive, Don't Count"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Base the colon on `s % 2` from the real time instead of toggling a variable each loop. A toggled variable can get out of step with the seconds, but a value calculated from the time is always right.

## MAX7219 Driver

The **MAX7219** is another LED driver chip. It can drive up to eight seven-segment digits, or a whole 8 by 8 LED matrix, and it uses the SPI bus from Chapter 8 instead of a custom protocol. Modules such as the popular 8 by 8 matrix boards can be **chained**: the output of one connects to the input of the next, so four modules make a wide scrolling display.

| MAX7219 pin | Job |
|-------------|-----|
| VCC, GND | Power (the chip is rated for 5 V) |
| DIN | Data in (SPI MOSI) |
| CLK | SPI clock |
| CS (LOAD) | Chip select |

The MAX7219 is designed for 5 V. Many modules work fine with the Pico's 3.3 V signals, but if you see flicker or missing segments, power the module from the 5 V VBUS pin and check the datasheet's logic levels. The driver is a small library (`max7219.py`) that treats the matrix as a framebuffer, an idea covered in Chapter 11.

## Character LCD and the LCD1602

A **character LCD** is a display built for text. Instead of liquid crystal segments in the shape of digits, it holds a grid of small cells that each show one character from a built-in font. Unlike LEDs, an LCD does not make its own light. It blocks or passes light, so it needs a **backlight** to be readable in the dark.

The most common model is the **LCD1602**, which has **16 columns and 2 rows**. It uses the HD44780 controller chip. Wiring it directly takes about 10 pins, so most people buy a version with an **I2C backpack**, a small board on the back that reduces the wiring to four wires. The backpack usually appears at address `0x27` or `0x3F` on the I2C scanner from Chapter 8.

```python
lcd.putstr("12:34:56")      # print text (library-dependent)
```

!!! mascot-warning "5 V Backpack Alert"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    LCD1602 modules normally run on 5 V, and many backpacks pull SDA and SCL up to 5 V. Connecting those lines straight to the Pico can send 5 V into pins that only tolerate 3.3 V. Use a level shifter or a module with 3.3 V pull-ups, as you learned in Chapter 2.

## Addressable LEDs

An **addressable LED** contains a tiny controller chip inside the LED package. The controllers are wired one after another, so a single data wire from the Pico can set the color of every LED on the strip. Each LED "addresses" itself by position: the first takes the first color from the stream and passes the rest along.

The best-known type is the **WS2812B**, sold as **NeoPixels**. It has only three connections (5 V, ground, and data), and a strip can hold hundreds of full-color LEDs. Chapter 16 covers them in depth. For now, here is how they compare with the displays in this chapter:

| Feature | TM1637 module | LCD1602 | Addressable LEDs |
|---------|---------------|---------|------------------|
| Shows | Four digits | 32 characters | Anything you arrange |
| Color | One color | One color plus backlight | Millions of colors |
| Wires | 4 | 4 with backpack | 3 |
| Cost | About \$1 to \$2 | About \$3 to \$5 | About \$5 to \$15 per strip |

## Wiring Diagrams

A **wiring diagram** is a drawing that shows *which pin connects to which pin*, with the wires labeled and colored. It differs from the schematic in Chapter 2, which shows electrical symbols. A wiring diagram is drawn to look like the real parts, so a builder can copy it wire by wire.

A good wiring diagram follows a few habits:

- Label every pin with both its function (`CLK`) and its Pico pin (`GP2`).
- Color the wires using the convention: red power, black ground, other colors for signals.
- Keep wires from crossing when possible.
- Include a small table with the same information so you can read the connections without following lines.

The table you saw for the TM1637 is that companion table. When a project does not work, comparing your build to the wiring diagram pin by pin, and then checking each wire with a multimeter, finds most mistakes.

## Putting It Together

| Need | Choose |
|------|--------|
| Four-digit clock, cheapest and simplest | TM1637 (4 wires) |
| Eight digits or an LED matrix | MAX7219 over SPI |
| Text on two lines | LCD1602 with I2C backpack |
| Color and creative shapes | Addressable LEDs |

## Key Takeaways

- A seven-segment digit lights bar segments `a` to `g`; each digit is one byte with one bit per segment.
- Multiplexing shares wires and lights one digit at a time, faster than the eye can see.
- The TM1637 handles the multiplexing and needs only four wires and any two GPIO pins.
- Blink the colon using `s % 2 == 0` from the real time.
- The MAX7219 uses SPI; an LCD1602 needs a backlight; addressable LEDs use one data wire.
- A wiring diagram with a pin table lets someone else build your circuit correctly.

!!! mascot-celebration "Digits Are Glowing"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now wire a TM1637, show real time as `HH:MM`, flash the colon, and explain how multiplexing fools the eye. That's a complete working clock. Every second counts!

## Practice Questions

1. Which segments must be lit to display the digit 4? What is the segment byte?
2. Why does multiplexing four digits need about four times the current per segment?
3. A TM1637 is wired to GP2 and GP3, but an I2C scan finds nothing. Is the module broken? Explain.
4. Write the line that turns the colon on only during even seconds.
5. Draw a wiring diagram and pin table for a TM1637 using GP10 for CLK and GP11 for DIO.
