---
title: Pico Pinout Explorer
description: "An interactive Raspberry Pi Pico pinout: hover a pin for its GP number, physical number and functions, click it for MicroPython code, filter by bus, and quiz yourself."
image: /sims/pico-pinout-explorer/pico-pinout-explorer.png
og:image: /sims/pico-pinout-explorer/pico-pinout-explorer.png
twitter:image: /sims/pico-pinout-explorer/pico-pinout-explorer.png
social:
   cards: false
quality_score: 100
---

# Pico Pinout Explorer

<iframe src="main.html" height="542px" width="100%" scrolling="no"></iframe>

[Run the Pico Pinout Explorer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

The Pico has 40 physical pins, numbered 1 to 40 around the edge of the board, but your code never uses those numbers. It uses **GP numbers**: `Pin(15)` means GP15, which is physical pin 20. Mixing the two up is one of the most common beginner mistakes.

This MicroSim draws the Pico from above with USB at the top. Every pin is labeled with its name and colored by type: blue for GPIO, green for the three ADC pins, red for power, black for ground and gray for control pins. Hover over a pin to see its GP number, physical number and special functions; click it to pin the MicroPython code that sets it up. The filter menu highlights every pin that can do I2C, SPI, UART, ADC or PWM, and the code changes to match. **Quiz mode** hides the GP labels and asks you to find a GP number.

This MicroSim supports the chapter [The Pico Platform: Pins, Files, and Firmware](../../chapters/05-pico-platform/index.md).

## How to Use

1. Hover over any pin label or gold pad to see its details in the panel.
2. Click a pin to keep its details and code in the panel.
3. Choose I2C, SPI, UART, ADC or PWM in the filter menu to highlight the pins with that function. Click a highlighted pin to see setup code for that bus.
4. Check **Quiz mode**, read the GP number in the panel and click that pin. Press **New question** for the next one.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/pico-pinout-explorer/main.html"
        height="542px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Identify the GP number and the physical pin number of any Pico pin
- Identify which pins can be used for I2C, SPI, UART, ADC and PWM
- Recall that MicroPython code uses the GP number, not the physical pin number

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- What a GPIO pin is
- The 3.3 V logic level from Chapter 2

### Activities

1. **Exploration** (4 min): Find GP14 and GP15, the mode and cycle button pins used in Chapter 7. Write down their physical pin numbers.
2. **Guided Practice** (6 min): Use the filter to find two different pin pairs that can run I2C0, and the only three pins that can read analog voltages.
3. **Assessment** (5 min): Turn on Quiz mode and answer ten questions. Aim for at least 8 correct.

### Assessment

- Students locate any GP number on the board in quiz mode.
- Students state that GP26, GP27 and GP28 are the only ADC pins.
- Students correct the line `Pin(20)` when the LED is wired to physical pin 20.

## References

1. [Raspberry Pi Pico datasheet and pinout](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) - official Pico documentation with the pinout diagram
2. [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) - section 1.4 lists the function of every GPIO
3. [MicroPython quick reference for the RP2](https://docs.micropython.org/en/latest/rp2/quickref.html) - Pin, ADC, PWM, I2C, SPI and UART examples
