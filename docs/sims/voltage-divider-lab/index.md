---
title: Voltage Divider Lab
description: Adjust the input voltage and two resistors of a voltage divider, watch a bar-graph voltmeter show the output, and judge whether it is safe for a 3.3 V Pico pin.
image: /sims/voltage-divider-lab/voltage-divider-lab.png
og:image: /sims/voltage-divider-lab/voltage-divider-lab.png
twitter:image: /sims/voltage-divider-lab/voltage-divider-lab.png
social:
   cards: false
quality_score: 100
---

# Voltage Divider Lab

<iframe src="main.html" height="497px" width="100%" scrolling="no"></iframe>

[Run the Voltage Divider Lab Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A **voltage divider** is two resistors in series. The output is taken from the point between them, and it is always a fraction of the input:

\[ V_{out} = V_{in} \times \frac{R_2}{R_1 + R_2} \]

Here \(R_1\) connects to the input voltage and \(R_2\) connects to ground. Clock builders use dividers to shrink a 5 V signal down to something a Pico pin can read, because **the Pico's GPIO pins are not 5 V tolerant**.

The bar-graph voltmeter on the right has three zones:

- **Green (up to 3.3 V):** safe for a Pico pin.
- **Amber (3.3 to 3.6 V):** a little above the Pico's 3.3 V logic level. The pin will survive, but there is no safety margin, so pick a slightly larger \(R_1\).
- **Red (above 3.6 V):** too high. This can damage the pin.

The chapter's worked example (5 V, 1 kΩ, 2 kΩ) gives 3.33 V, which lands just inside the amber band. Try nudging \(R_1\) up one step to see how easy it is to add margin. The resistor sliders step through the standard E24 values from 100 Ω to 10 kΩ, so every setting is a resistor you could actually buy.

## How to Use

- Move **Input voltage Vin** to set the voltage at the top of the divider (0 to 5 V).
- Move **R1 (top)** and **R2 (bottom)** to choose standard resistor values from 100 Ω to 10 kΩ.
- Read **Vout** on the bar graph and the verdict under it: *Safe for Pico*, *Just over 3.3 V: no margin*, or *Too high!*
- The formula line along the bottom shows the calculation with your numbers, and the **Current** readout shows how much current flows through the two resistors.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/voltage-divider-lab/main.html"
        height="497px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Apply the voltage divider formula to calculate an output voltage.
- Evaluate whether a divider output is safe for a 3.3 V Pico input pin.
- Choose resistor values that bring a 5 V signal into the safe range with some margin.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Ohm's Law (V = I × R).
- Knowing that the Pico uses 3.3 V logic and its pins are not 5 V tolerant.

### Activities

1. **Check the worked example (3 min):** Set Vin = 5.0 V, R1 = 1.0 kΩ, R2 = 2.0 kΩ. Students calculate Vout by hand first, then compare with the MicroSim. Discuss why 3.33 V lands in the amber band.
2. **Find the ratio (4 min):** Students find three different R1 and R2 pairs that give between 3.0 and 3.3 V from 5 V. What do the pairs have in common? (The ratio R2 / (R1 + R2) is about 0.6 to 0.66.)
3. **Evaluate designs (4 min):** Give students two designs that both give 3.2 V, one with 100 Ω resistors and one with 10 kΩ resistors. Using the Current readout, which wastes less power? Which would you choose for a battery clock?
4. **Swap the resistors (2 min):** What happens if R1 and R2 are wired the wrong way round? Students predict, then swap the slider values to check.

### Assessment

- Students correctly calculate Vout for any Vin, R1, and R2 shown in the MicroSim.
- Students design a divider that turns 5 V into 3.0 to 3.3 V and justify their resistor choice.
- Students explain why larger resistor values waste less current but give the same output ratio.

## References

1. [Voltage divider (Wikipedia)](https://en.wikipedia.org/wiki/Voltage_divider) - Derivation of the divider formula with examples.
2. [E series of preferred numbers (Wikipedia)](https://en.wikipedia.org/wiki/E_series_of_preferred_numbers) - Why resistors come in standard values such as 1.0k, 2.0k, and 2.2k.
3. [RP2040 datasheet](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf) - The electrical limits for the Pico's GPIO pins.
4. [Logic level (Wikipedia)](https://en.wikipedia.org/wiki/Logic_level) - What 3.3 V and 5 V logic levels mean.
