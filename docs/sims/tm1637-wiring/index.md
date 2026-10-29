---
title: TM1637 Wiring Diagram
description: Connect the four pins of a TM1637 display module to the correct Raspberry Pi Pico pins; correct wires lock in and the display lights up 12:34.
image: /sims/tm1637-wiring/tm1637-wiring.png
og:image: /sims/tm1637-wiring/tm1637-wiring.png
twitter:image: /sims/tm1637-wiring/tm1637-wiring.png
social:
   cards: false
quality_score: 0
---

# TM1637 Wiring Diagram

<iframe src="main.html" height="557px" width="100%" scrolling="no"></iframe>

[Run the TM1637 Wiring Diagram MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

Before writing any code for the TM1637 clock, the four wires have to go to the right places. This
virtual build lets you practice with the wiring table from Chapter 9:

| TM1637 pin | Pico pin | Physical pin | Wire color |
|------------|----------|--------------|------------|
| VCC | 3V3(OUT) | 36 | Red |
| GND | GND | 38 | Black |
| CLK | GP2 | 4 | Yellow |
| DIO | GP3 | 5 | Green |

The Pico on the left shows all 40 pins with their physical numbers. Power pins are labeled in
red, ground in black and GPIO pins in green. The four module pins glow until they are connected.

Drag a wire from a module pin to a Pico pin. A correct connection locks in with the color from
the table. A wrong one is rejected with a hint that explains why, such as "VCC needs 3.3 V, not
GND." When all four wires are correct, the display shows `12:34` with a flashing colon.

## How to Use

1. Drag from **CLK** on the module to the Pico pin from the table. On a tablet or phone, tap the
   module pin and then tap the Pico pin.
2. Read the message in the wiring-table box after each try.
3. Connect **DIO**, **VCC** and **GND** the same way.
4. When all four are correct, watch the display light up.
5. Press **Show answer** to see all four wires, or **Reset** to start over.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/tm1637-wiring/main.html"
        height="557px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Pico pin names and physical pin numbers (Chapter 2)
- Wire color conventions (Chapter 2)

### Learning Objectives

Students will be able to:

- Apply a wiring table by connecting each module pin to the correct Pico pin
- Distinguish power, ground and GPIO pins on the Pico pinout
- Explain why the module is powered from 3V3(OUT) instead of VBUS

### Activities

1. **Wire it from the table** (5 min): Connect all four wires using only the wiring table. Count how many tries you needed.
2. **Learn from the hints** (5 min): Deliberately try VCC on a GND pin and on VBUS, and CLK on GP3. Write down what each hint teaches.
3. **Real build** (5 min): Use the finished diagram as a guide to wire a real TM1637 module, then run the Chapter 9 test program.

### Assessment

- The student wires all four pins correctly without Show answer.
- The student explains why a signal pin must never go to power or ground.
- The student explains that any GND pin works but VCC must use 3V3(OUT).

## References

1. [Raspberry Pi Pico documentation](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) - Official Pico pages including the pinout diagram.
2. [micropython-tm1637](https://github.com/mcauser/micropython-tm1637) - The MicroPython TM1637 driver library used in Chapter 9.
3. [Seven-segment display](https://en.wikipedia.org/wiki/Seven-segment_display) - Wikipedia article on how the digits are formed.
4. [Jump wire](https://en.wikipedia.org/wiki/Jump_wire) - Wikipedia article on the jumper wires used for breadboard builds.
