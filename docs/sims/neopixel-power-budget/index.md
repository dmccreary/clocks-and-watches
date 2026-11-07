---
title: NeoPixel Power Budget
description: Light pixels on a virtual NeoPixel strip, choose the color, length, and brightness, and watch a gauge compare the total current with the 500 mA USB limit, with the power formula shown with the numbers filled in.
image: /sims/neopixel-power-budget/neopixel-power-budget.png
og:image: /sims/neopixel-power-budget/neopixel-power-budget.png
twitter:image: /sims/neopixel-power-budget/neopixel-power-budget.png
social:
   cards: false
quality_score: 100
---

# NeoPixel Power Budget

<iframe src="main.html" height="517px" width="100%" scrolling="no"></iframe>

[Run the NeoPixel Power Budget MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

Every NeoPixel contains three tiny LEDs: red, green, and blue. Each one draws up to about **20 mA** at full value (255), so a pixel showing full white draws about **60 mA**. A USB port supplies only about **500 mA**, and that has to power the Pico too. A design that looks harmless on paper can overload the port once enough pixels light up.

This MicroSim estimates the current of a design with the same rule of thumb the chapter uses:

\[ I = \text{lit pixels} \times \frac{R + G + B}{255} \times 20\ \text{mA} \times \text{brightness} \]

The gauge has three zones:

- **Green** (below 400 mA): fine to run from USB.
- **Yellow** (400 to 500 mA): close to the USB limit, so the Pico may reset or the port may shut off.
- **Red** (above 500 mA): use a separate 5 V supply for the strip, with its ground tied to the Pico's ground.

The opening design is the chapter's example: three pixels lit in full red on a 30-pixel strip, which draws \( 3 \times 20 = 60 \) mA. Real pixels also draw about 1 mA each even when they are off, which this estimate leaves out.

## How to Use

1. **Click** pixels on the strip to light them or turn them off. The readout shows the formula with your numbers.
2. Pick a strip length from the **Pixels** menu: 12, 30, 60, or 144.
3. Click the **Color** box to choose the lit color. Compare red (20 mA per pixel), yellow (40 mA), and white (60 mA).
4. Drag **Brightness** to scale every pixel. Most indoor clocks look best around 10 to 25 percent.
5. Press **Light all** to light every pixel, the worst case your program might ever produce. Press **Clear all** to turn them all off.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/neopixel-power-budget/main.html"
        height="517px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objective

Students will calculate the current a LED design draws and evaluate whether it needs an external supply (Bloom: Applying, Evaluating).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Current, voltage, and the USB power limit (Chapter 2)
- NeoPixel color values (Chapter 16)

### Activities

1. **Worked example** (3 min): Choose 60 pixels, white, 25 percent brightness, and Light all. Confirm the chapter's result of 900 mA and explain why the gauge is in the red zone.
2. **Find the limit** (4 min): For a 60-pixel ring in white, find the highest brightness that stays green. Repeat in pure blue.
3. **Design a clock** (5 min): A 12-pixel ring clock lights one red hour pixel, one green minute pixel, and one blue second pixel at full brightness. Calculate the current by hand, then build it on the strip and check.
4. **Evaluate** (3 min): Students decide which of their designs need an external 5 V supply and justify each decision with the numbers.

### Assessment

- How much current do 30 pixels of full white draw at 50 percent brightness? (900 mA.)
- Why does yellow `(255, 255, 0)` draw twice the current of red `(255, 0, 0)`?
- A design draws 450 mA. Is it safe on USB? What two changes could make it safer?
- Explain why you should plan for the worst case your program can display, not the typical case.

## References

1. [Adafruit NeoPixel Uberguide: Powering NeoPixels](https://learn.adafruit.com/adafruit-neopixel-uberguide/powering-neopixels) - Current estimates and supply advice for NeoPixel strips.
2. [USB hardware: power](https://en.wikipedia.org/wiki/USB_hardware#Power) - Wikipedia; the 500 mA limit of a standard USB 2.0 port.
3. [Ohm's law](https://en.wikipedia.org/wiki/Ohm%27s_law) - Wikipedia; the basics behind current and power.
4. [MicroPython neopixel module](https://docs.micropython.org/en/latest/library/neopixel.html) - The driver used on the Pico.
