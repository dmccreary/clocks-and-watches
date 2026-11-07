---
title: Resistor Color Code Decoder
description: Click the bands of a large four-band resistor to change their colors and read its value, then quiz yourself by reading random resistors or setting the bands to match a value.
image: /sims/resistor-color-decoder/resistor-color-decoder.png
og:image: /sims/resistor-color-decoder/resistor-color-decoder.png
twitter:image: /sims/resistor-color-decoder/resistor-color-decoder.png
social:
   cards: false
quality_score: 100
---

# Resistor Color Code Decoder

<iframe src="main.html" height="422px" width="100%" scrolling="no"></iframe>

[Run the Resistor Color Code Decoder Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

Resistors are too small to print numbers on, so their value is painted on as colored **bands**. On a four-band resistor:

- **Band 1** and **band 2** are digits (black 0, brown 1, red 2, orange 3, yellow 4, green 5, blue 6, violet 7, gray 8, white 9).
- **Band 3** is the **multiplier**: how many zeros to add (black ×1, brown ×10, red ×100, orange ×1k, yellow ×10k, and so on; gold ×0.1 and silver ×0.01).
- **Band 4**, set a little apart, is the **tolerance**: how close the real value is guaranteed to be (gold ±5%, silver ±10%, brown ±1%, red ±2%).

For example, orange-orange-brown-gold is 3, 3, then add one zero: **330 Ω ±5%**, the most common resistor in this book.

Click any band to step through its colors and watch the value change. The two quiz modes turn the decoder into practice: read a random resistor, or set the bands to make a value.

## How to Use

- In **Explore** mode, click a band to cycle its color. The readout shows the value, the tolerance, and the arithmetic. **Random resistor** shows a new random resistor.
- Choose **Quiz: read the bands** and press **Random resistor**. Type the value you read (for example `470`, `4.7k`, or `1M`) in **Your value** and press **Check** (or Enter).
- Choose **Quiz: set the bands** and press **Random resistor**. Click the bands until they match the value in the box, then press **Check**. You may also type your own value into the box and set the bands for it.
- The **Score** counts correct answers out of answers checked. Changing the mode resets the score.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/resistor-color-decoder/main.html"
        height="422px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Recall the digit value of each resistor band color.
- Apply the color code to read the value of a four-band resistor.
- Apply the color code in reverse to choose the bands for a given value.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Read the Resistors section of Chapter 2.
- Know that 1 kΩ = 1,000 Ω and 1 MΩ = 1,000,000 Ω.

### Activities

1. **Decode the favorites (3 min):** Students set the bands for 220 Ω, 330 Ω, 1 kΩ, and 10 kΩ, the resistors they will use most in this book.
2. **Read quiz (4 min):** Students answer ten random resistors in "Quiz: read the bands" and record their score.
3. **Set quiz (4 min):** Students answer five questions in "Quiz: set the bands." Ask: which band is the most common mistake?
4. **Real parts (4 min):** If a resistor kit is available, students read three real resistors and check each one in Explore mode.

### Assessment

- Students score at least 8 out of 10 when reading random resistors.
- Students can name the four bands for a given value such as 4.7 kΩ ±5% (yellow-violet-red-gold).
- Students explain what the tolerance band means for a real 330 Ω ±5% resistor (between about 314 Ω and 347 Ω).

## References

1. [Electronic color code (Wikipedia)](https://en.wikipedia.org/wiki/Electronic_color_code) - The full color code table for resistors.
2. [Resistor (Wikipedia)](https://en.wikipedia.org/wiki/Resistor) - What resistors do and how they are made.
3. [E series of preferred numbers (Wikipedia)](https://en.wikipedia.org/wiki/E_series_of_preferred_numbers) - Why resistors come in values like 22, 33, and 47.
4. [Resistor Color Code (SparkFun)](https://learn.sparkfun.com/tutorials/resistors/decoding-resistor-markings) - A tutorial with photos of real resistors.
