---
title: Wrap-Around Dial
description: "A clock-style dial for 12, 24 or 60 positions shows (x + step) % n step by step, including how Python wraps negative numbers."
image: /sims/wrap-around-dial/wrap-around-dial.png
og:image: /sims/wrap-around-dial/wrap-around-dial.png
twitter:image: /sims/wrap-around-dial/wrap-around-dial.png
social:
   cards: false
quality_score: 100
---

# Wrap-Around Dial

<iframe src="main.html" height="512px" width="100%" scrolling="no"></iframe>

[Run the Wrap-Around Dial MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

Clock counters **wrap around**: after 59 seconds comes 0, and after hour 23 comes hour 0. The modulo operator `%` does this in one step: `(x + step) % n` is always between 0 and `n - 1`. Python's `%` also handles going backward, so `(0 - 1) % 60` is 59, which is exactly what a "minute down" button needs.

The dial has `n` positions, chosen with the **Modulus** menu (12, 24 or 60). The orange pointer sits on the current value of `x`. Each button changes `x` by its step, the pointer travels around the dial (passing 0 if it wraps), and the panel shows the arithmetic line by line, for example `(58 + 10) % 60 = 68 % 60 = 8`. In **Predict** mode you type where the pointer will land before it moves.

This MicroSim supports the chapter [Control Flow, Functions, and Modules](../../chapters/04-control-flow-functions/index.md).

## How to Use

1. Press **+1**, **-1** or **+10**. The pointer moves and the panel shows the calculation.
2. Change **Modulus n** to 12, 24 or 60. The dial is redrawn and `x` starts near the wrap point.
3. Check **Predict**, press a step button, type your answer and press **Check**. Your score appears beside the button.
4. Press **Reset** to return `x` to its starting value.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/wrap-around-dial/main.html"
        height="512px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Apply the modulo operator to predict where a counter lands after adding or subtracting
- Explain why (x + step) % n always gives a value from 0 to n - 1
- Predict the result of going backward past zero, such as (0 - 1) % 60 = 59

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- Integer division and remainders
- The % operator from the arithmetic section of Chapter 3

### Activities

1. **Exploration** (4 min): With n = 60, press +1 until the pointer passes 0. Then press -1 at 0 and note what Python gives.
2. **Guided Practice** (6 min): Turn on Predict. Do five +10 presses with n = 60 and five with n = 24, predicting each result.
3. **Assessment** (5 min): Write the expression a "minute down" button needs and test it on the dial at x = 0.

### Assessment

- Students predict at least 8 of 10 results correctly in Predict mode.
- Students explain why the result can never equal n.
- Students write `minute = (minute - 1) % 60` for a down button without help.

## References

1. [Modular arithmetic](https://en.wikipedia.org/wiki/Modular_arithmetic) - Wikipedia article, which uses the 12-hour clock as its first example
2. [Python Numeric Types: the % operator](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex) - official note that % takes the sign of the divisor
3. [Modulo](https://en.wikipedia.org/wiki/Modulo) - how different languages handle negative remainders
