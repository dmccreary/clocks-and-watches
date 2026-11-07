---
title: LDR Light Sensor Lab
description: Use the voltage divider formula to predict the ADC reading of a light-dependent resistor as the room brightness and the fixed resistor change.
image: /sims/ldr-light-sensor-lab/ldr-light-sensor-lab.png
og:image: /sims/ldr-light-sensor-lab/ldr-light-sensor-lab.png
twitter:image: /sims/ldr-light-sensor-lab/ldr-light-sensor-lab.png
social:
   cards: false
quality_score: 0
---

# LDR Light Sensor Lab

<iframe src="main.html" height="537px" width="100%" scrolling="no"></iframe>

[Run the LDR Light Sensor Lab MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A **light-dependent resistor (LDR)** has a resistance that falls as the light gets brighter:
about 1 MΩ in the dark and as little as 500 Ω in direct sunlight. The Pico's ADC measures
voltage, not resistance, so the LDR is wired into a **voltage divider** with a fixed resistor:

\[ V_{out} = 3.3 \times \frac{R_{fixed}}{R_{LDR} + R_{fixed}} \]

The ADC turns that voltage into a number from 0 to 65,535:

\[ \text{ADC} = \frac{V_{out}}{3.3} \times 65535 \]

The MicroSim shows four panels: the **schematic** (3.3 V, the LDR, the GP26 ADC pin, the fixed
resistor and ground), a **room** whose light follows the brightness slider, the **formula
worked out** with the current numbers, and a **gauge** of the ADC reading. On narrow screens
the gauge is hidden and the reading appears in the formula panel.

## How to Use

1. Move the **Brightness** slider from *Dark room* to *Direct sunlight*. Watch \( R_{LDR} \)
   fall and the ADC reading rise.
2. Move the **Fixed resistor** slider through standard resistor values from 1 kΩ to 100 kΩ.
   See how it changes the reading for the same light.
3. Check **Hide Vout and the ADC reading** to hide the answers. Calculate \( V_{out} \) and the
   ADC value by hand, then uncheck the box to check your work.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/ldr-light-sensor-lab/main.html"
        height="537px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15-20 minutes

### Prerequisites

- Voltage dividers and Ohm's law (Chapter 2)
- ADC readings from 0 to 65,535 (Chapter 18)

### Learning Objectives

Students will be able to:

- Apply the voltage divider formula to calculate \( V_{out} \) for a given LDR resistance
- Convert \( V_{out} \) into the 16-bit ADC reading that `read_u16()` returns
- Explain how the choice of fixed resistor changes the sensor's useful range

### Activities

1. **Check the worked example** (3 min): Set *Bright room* so that \( R_{LDR} \) is 2.0 kΩ with a
   10 kΩ fixed resistor. Confirm the chapter's answer of 2.75 V.
2. **Predict first** (7 min): Check *Hide Vout and the ADC reading*. For three brightness settings
   of your choice, write down \( R_{LDR} \), calculate \( V_{out} \) and the ADC value, then reveal
   the answers. Within how many counts were you?
3. **Choose the resistor** (7 min): For a bedroom clock that must tell *Dark room* from *Dim room*,
   which fixed resistor gives the biggest change in the ADC reading between those two settings?
   Try 1 kΩ, 10 kΩ and 100 kΩ, and explain the result.

### Assessment

- The student calculates \( V_{out} \) and the ADC reading for a given \( R_{LDR} \) and \( R_{fixed} \).
- The student explains why brighter light gives a bigger reading with this wiring.
- The student justifies a fixed resistor value for a dark-room or a sunny-room application.

## References

1. [Photoresistor](https://en.wikipedia.org/wiki/Photoresistor) - Wikipedia article on light-dependent resistors and how their resistance changes with light.
2. [Voltage divider](https://en.wikipedia.org/wiki/Voltage_divider) - Wikipedia article deriving the divider formula used here.
3. [MicroPython ADC class](https://docs.micropython.org/en/latest/library/machine.ADC.html) - Official documentation for `read_u16()` and its 0 to 65,535 range.
4. [E series of preferred numbers](https://en.wikipedia.org/wiki/E_series_of_preferred_numbers) - Why resistors come in values like 4.7 kΩ and 6.8 kΩ.
