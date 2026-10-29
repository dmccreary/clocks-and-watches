---
title: LED Resistor Calculator
description: Choose an LED color, a 3.3 V or 5 V supply, and a standard resistor to see the LED current, its brightness, a warning above 20 mA, and the resistor you would need for 10 mA.
image: /sims/led-resistor-calculator/led-resistor-calculator.png
og:image: /sims/led-resistor-calculator/led-resistor-calculator.png
twitter:image: /sims/led-resistor-calculator/led-resistor-calculator.png
social:
   cards: false
quality_score: 100
---

# LED Resistor Calculator

<iframe src="main.html" height="452px" width="100%" scrolling="no"></iframe>

[Run the LED Resistor Calculator Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

An LED drops a nearly fixed **forward voltage** that depends on its color. Whatever voltage is left over lands on the resistor, and the resistor sets the current with Ohm's Law. That gives the current-limiting formula from the chapter:

\[ I = \frac{V_{supply} - V_{LED}}{R} \qquad R = \frac{V_{supply} - V_{LED}}{I} \]

This MicroSim draws a supply, a resistor, and an LED in one loop. Change the LED color, the supply, or the resistor, and the readout recalculates the current right away. The LED glows brighter as the current rises, and a yellow warning sign appears when the current goes above **20 mA**, the safe maximum for a typical 5 mm LED. The panel also works the problem backward: it shows the resistance needed for a 10 mA design target and the nearest standard value at or above it.

The resistor slider only offers standard values you can buy (10 Ω to 2.2 kΩ). The model treats the forward voltage as fixed, which is close to how a real LED behaves once it is on; a real LED near its forward voltage glows a little more faintly than this simple model predicts.

## How to Use

- Choose an **LED color**. The menu shows each color's forward voltage (red 2.0 V up to white 3.2 V).
- Choose a **supply**: 3.3 V from a Pico pin or 5 V from USB.
- Move the **Resistor** slider to pick a standard resistor value.
- Read the **Current**, the status line, and the brightness bar. A warning sign appears above 20 mA.
- Use the bottom of the panel to check your own hand calculation of the resistor needed for 10 mA.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/led-resistor-calculator/main.html"
        height="452px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Apply the current-limiting formula to calculate LED current and the resistor needed for a target current.
- Analyze how resistor value, supply voltage, and LED color change the current and brightness.
- Choose a safe standard resistor value for an LED on a 3.3 V Pico pin.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Ohm's Law (V = I × R).
- Read the Current Limiting and LED Basics sections of Chapter 2.

### Activities

1. **Check the worked example (3 min):** Red LED, 3.3 V, 150 Ω. Students predict about 8.7 mA, then check it in the MicroSim.
2. **Find the danger zone (4 min):** For each supply, students find the smallest resistor that keeps a red LED at or below 20 mA. Why is the answer different for 5 V?
3. **Blue on 3.3 V (3 min):** Switch to a blue LED on 3.3 V. Why is it so dim even with a small resistor? What changes on 5 V?
4. **Design (5 min):** Using the chapter exercise, students pick a resistor for a green LED at 8 mA from 3.3 V, then confirm the current in the MicroSim.

### Assessment

- Students correctly calculate the resistor needed for a given LED color, supply, and target current.
- Students explain why a smaller resistor makes the LED brighter and when that becomes unsafe.
- Students explain why blue and white LEDs need smaller resistors on a 3.3 V pin.

## References

1. [LED circuit (Wikipedia)](https://en.wikipedia.org/wiki/LED_circuit) - How a series resistor limits LED current.
2. [Light-emitting diode (Wikipedia)](https://en.wikipedia.org/wiki/Light-emitting_diode) - Forward voltage and how it depends on color.
3. [Ohm's law (Wikipedia)](https://en.wikipedia.org/wiki/Ohm%27s_law) - The relationship behind the formula.
4. [E series of preferred numbers (Wikipedia)](https://en.wikipedia.org/wiki/E_series_of_preferred_numbers) - Why resistors come in standard values.
