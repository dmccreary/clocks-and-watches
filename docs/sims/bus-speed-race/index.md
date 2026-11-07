---
title: Bus Speed Race
description: Compare how long UART, I2C and SPI take to send one full screen of pixels to three different displays, on a logarithmic time axis.
image: /sims/bus-speed-race/bus-speed-race.png
og:image: /sims/bus-speed-race/bus-speed-race.png
twitter:image: /sims/bus-speed-race/bus-speed-race.png
social:
   cards: false
quality_score: 0
---

# Bus Speed Race

<iframe src="main.html" height="422px" width="100%" scrolling="no"></iframe>

[Run the Bus Speed Race MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

Every time a clock updates its screen, the whole picture has to travel from the Pico to the
display over a bus. This chart races the three buses from Chapter 8 against each other and shows
how many **seconds one full frame** takes on each.

The time comes from one formula: bytes in the frame, times the bits each byte needs on the wire,
divided by the bus speed.

| Bus | Bits on the wire per byte | Formula |
|-----|---------------------------|---------|
| UART at 115,200 baud | 10 (start + 8 data + stop) | bytes x 10 / 115,200 |
| I2C | 9 (8 data + ACK) | bytes x 9 / I2C clock |
| SPI | 8 | bytes x 8 / SPI clock |

The frame size depends on the display: the 128x64 monochrome OLED holds 1,024 bytes, while the
240x240 and 320x240 color displays use 2 bytes per pixel (115,200 and 153,600 bytes).

The horizontal axis is **logarithmic**: each grid line is ten times the one before, so a 0.2 ms
bar and a 10 s bar fit on the same chart. A bar turns **green** when the bus can reach
20 frames per second (50 ms per frame or less), the dashed line. These are best-case times for
the data alone; real drivers add a little overhead for commands.

## How to Use

1. Pick a **Display** from the dropdown. Start with the 128x64 mono OLED.
2. Hover over any bar to see the exact time, the formula with the numbers filled in, and the
   maximum frames per second.
3. Drag the **I2C clock** slider from 100 kHz to 1 MHz. Which bars move, and which stay put?
4. Switch to the **240x240 color** display. Can any I2C speed reach the green zone now?
5. Lower the **SPI clock** until the SPI bar stops being green. Read the speed where it changes.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/bus-speed-race/main.html"
        height="422px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Bits, bytes and the I2C, SPI and UART buses (Chapter 8)
- Display resolution and pixels

### Learning Objectives

Students will be able to:

- Compare the time UART, I2C and SPI need to send one frame to a display
- Calculate frame time from bytes, bits per byte and bus speed
- Evaluate which bus a display needs to reach 20 frames per second

### Activities

1. **Predict first** (4 min): Before touching anything, predict which bus is fastest for the OLED and by roughly how much. Then hover over the three bars and check.
2. **Find the limit** (6 min): For the 240x240 color display, find the lowest SPI clock that still reaches 20 fps. Use the formula to check the slider answer on paper.
3. **Make the case** (5 min): Write two sentences explaining why the small OLED can use I2C but a round color watch display must use SPI.

### Assessment

- The student computes 1,024 x 9 / 400,000 = 23 ms for the OLED on 400 kHz I2C.
- The student explains that each tick on a log axis is ten times the previous one.
- The student justifies a bus choice using frames per second, not just "faster".

## References

1. [I2C](https://en.wikipedia.org/wiki/I%C2%B2C) - Wikipedia article on the two-wire bus, including its speed modes.
2. [Serial Peripheral Interface](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface) - Wikipedia article on SPI and why it can run so much faster than I2C.
3. [Universal asynchronous receiver-transmitter](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter) - Wikipedia article on UART framing with start and stop bits.
4. [Logarithmic scale](https://en.wikipedia.org/wiki/Logarithmic_scale) - Wikipedia article explaining how to read a log axis.
5. [MicroPython machine.SPI](https://docs.micropython.org/en/latest/library/machine.SPI.html) - Official documentation for the baudrate argument used in the chapter.
