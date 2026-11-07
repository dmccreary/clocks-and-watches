---
title: Logic Analyzer Trace Reader
description: Read captured I2C and button waveforms on a logic analyzer, click each part to decode it, and diagnose a missing acknowledgment, weak pull-ups or contact bounce.
image: /sims/logic-analyzer-trace-reader/logic-analyzer-trace-reader.png
og:image: /sims/logic-analyzer-trace-reader/logic-analyzer-trace-reader.png
twitter:image: /sims/logic-analyzer-trace-reader/logic-analyzer-trace-reader.png
social:
   cards: false
quality_score: 0
---

# Logic Analyzer Trace Reader

<iframe src="main.html" height="527px" width="100%" scrolling="no"></iframe>

[Run the Logic Analyzer Trace Reader MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A **logic analyzer** records digital signals over time so you can see what is really
happening on the wires. This MicroSim shows four captures:

- Three captures of a Pico writing three bytes to an SSD1306 OLED over **I2C**, with the
  clock line **SCL** (yellow) and the data line **SDA** (cyan).
- One capture of a push button on **GP14**, with a second channel that marks every press the
  program counted.

The colored **decode** band above the traces names each part of an I2C message: the **START**
condition (S), the 7-bit **address**, the **W** (write) bit, the **ACK** (A) or **NACK** (N) on
the ninth clock, the **data** bytes, and the **STOP** condition (P). The 0 and 1 under SDA are
the bit values, read while SCL is high. The dotted lines show the logic-high threshold.

One capture is healthy and the others each hide a common fault. The capture names are hidden so
you have to diagnose each one from the waveform; a correct diagnosis reveals the name. On narrow
screens, use the **Scroll** slider to pan along the trace.

## How to Use

1. Choose a **Capture** from the menu.
2. Click any part of the waveform (or the decode band) to read what that part is.
3. Choose a **Diagnosis** and press **Check**. A wrong answer gives a hint about where to look.
4. Repeat for all four captures.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/logic-analyzer-trace-reader/main.html"
        height="527px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15-20 minutes

### Prerequisites

- The I2C bus: SDA, SCL, addresses and the I2C scan (Chapter 8)
- Binary and hexadecimal numbers
- Button bounce and debouncing (Chapter 7)

### Learning Objectives

Students will be able to:

- Interpret an I2C waveform, identifying the start, address, R/W bit, ACK, data and stop
- Diagnose a missing acknowledgment from the ninth clock pulse
- Distinguish a wiring fault (weak pull-ups) and contact bounce from a healthy signal

### Activities

1. **Decode by hand** (6 min): In Capture 1, read the eight bits under SDA during the address and
   W boxes. Convert the first seven to hexadecimal. Do you get 0x3C? Then read the two data bytes.
2. **Diagnose** (8 min): For each of the four captures, write down the one feature you used to make
   your diagnosis, then check it. In the capture with no ACK, what address did the code send, and how would
   `i2c.scan()` help you find the right one?
3. **Connect to the fix** (4 min): For each faulty capture, name the fix from Chapter 20's
   troubleshooting table.

### Assessment

- The student labels the parts of an I2C message on a printed trace.
- The student explains that a NACK means no device answered the address on the ninth clock.
- The student explains why missing pull-ups make rising edges slow, and why bounce makes one press count many times.

## References

1. [I2C](https://en.wikipedia.org/wiki/I%C2%B2C) - Wikipedia article on the I2C bus, start and stop conditions, and acknowledgments.
2. [Logic analyzer](https://en.wikipedia.org/wiki/Logic_analyzer) - Wikipedia article on capturing and decoding digital signals.
3. [SSD1306 datasheet (Adafruit)](https://cdn-shop.adafruit.com/datasheets/SSD1306.pdf) - The OLED controller whose address and display-on command appear in the captures.
4. [Sigrok PulseView](https://sigrok.org/wiki/PulseView) - Free logic analyzer software that decodes I2C traffic from low-cost USB analyzers.
