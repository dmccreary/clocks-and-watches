---
title: Ohm's Law Explorer
description: Change the voltage and resistance of a simple loop circuit to see Ohm's Law at work: live current and power readouts, moving dots that speed up with current, and a quiz that asks you to calculate the current.
image: /sims/ohms-law-explorer/ohms-law-explorer.png
og:image: /sims/ohms-law-explorer/ohms-law-explorer.png
twitter:image: /sims/ohms-law-explorer/ohms-law-explorer.png
social:
   cards: false
quality_score: 100
---

# Ohm's Law Explorer

<iframe src="main.html" height="497px" width="100%" scrolling="no"></iframe>

[Run the Ohm's Law Explorer Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

**Ohm's Law** connects the three quantities in every circuit: voltage (V), current (I), and resistance (R).

\[ V = I \times R \qquad \text{so} \qquad I = \frac{V}{R} \]

Electric **power** is how fast energy is used: \( P = V \times I \).

This MicroSim is a single loop with a battery and a resistor. Set the voltage and the resistance with the sliders and the readouts show the current in milliamps and the power in milliwatts, along with the arithmetic. The resistor box grows longer as the resistance goes up.

Press **Start** to set the blue dots moving. They show conventional current flowing out of the + terminal and back into the − terminal, and they move faster when the current is larger. The speed uses a square-root scale so that a 1 mA current still visibly moves; it is not to scale. The number of dots stays the same, because a wire does not gain or lose charge carriers when the current changes; the charges just move faster.

## How to Use

- The MicroSim opens paused. Press **Start** to set the dots moving, and **Pause** to freeze them.
- Move **Voltage** (0 to 5 V) and **Resistance** (10 to 1000 Ω). Watch the current, the power, and the dot speed change.
- Press **Quiz me**. The sliders jump to a new voltage and resistance and the current and power readouts change to **?**. Calculate the current, type it in milliamps in the box, and press **Check** (or Enter). Moving a slider before you check cancels the question.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/ohms-law-explorer/main.html"
        height="497px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Apply Ohm's Law (I = V / R) to calculate the current from a voltage and a resistance.
- Predict how the current changes when the voltage or the resistance is doubled or halved.
- Calculate electric power with P = V × I.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Read the Voltage, Current, and Resistance section of Chapter 2.
- Convert amps to milliamps (1 A = 1,000 mA).

### Activities

1. **Check the worked example (2 min):** Set 3.3 V and 330 Ω. Students confirm the chapter result of 10 mA and 33 mW.
2. **Double and halve (4 min):** Students predict, then test, what happens to the current when they double the resistance to 660 Ω, and when they halve the voltage. Record each result in a table.
3. **Find the danger (3 min):** Ask students to find the setting with the most current. Why would this be dangerous for a Pico pin?
4. **Quiz (5 min):** Students answer five Quiz me questions without a calculator, then five with one. Compare scores.

### Assessment

- Students correctly calculate the current for any voltage and resistance shown.
- Students explain that doubling the resistance halves the current and doubling the voltage doubles it.
- Students calculate power in milliwatts from voltage and current.

## References

1. [Ohm's law (Wikipedia)](https://en.wikipedia.org/wiki/Ohm%27s_law) - The law, its history, and worked examples.
2. [Electric power (Wikipedia)](https://en.wikipedia.org/wiki/Electric_power) - Power as voltage times current.
3. [Electric current (Wikipedia)](https://en.wikipedia.org/wiki/Electric_current) - Conventional current and electron flow.
4. [Voltage, Current, Resistance, and Ohm's Law (SparkFun)](https://learn.sparkfun.com/tutorials/voltage-current-resistance-and-ohms-law/all) - A beginner tutorial with the water analogy.
