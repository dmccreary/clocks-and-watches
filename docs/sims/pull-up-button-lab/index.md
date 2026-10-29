---
title: Pull-Up Button Lab
description: "A GP14 button circuit with the internal pull-up resistor: toggle the button and the pull-up to see the pin voltage, value() and a floating input."
image: /sims/pull-up-button-lab/pull-up-button-lab.png
og:image: /sims/pull-up-button-lab/pull-up-button-lab.png
twitter:image: /sims/pull-up-button-lab/pull-up-button-lab.png
social:
   cards: false
quality_score: 100
---

# Pull-Up Button Lab

<iframe src="main.html" height="472px" width="100%" scrolling="no"></iframe>

[Run the Pull-Up Button Lab MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A digital input reads 1 when its voltage is high and 0 when it is low, but an input connected to nothing has no defined voltage. It **floats**, picking up electrical noise, and `value()` flips between 0 and 1 by itself. A **pull-up resistor** fixes this by joining the pin to 3.3 V through a large resistance. The RP2040 has one built in that you switch on with `Pin.PULL_UP`.

The schematic shows GP14, the internal pull-up of about 50 kOhm to 3.3 V, and a push button to ground. The voltage bar shows the pin voltage against the input thresholds (about 2.0 V for a sure 1 and 0.8 V for a sure 0), and the readout shows what `button.value()` returns. On wider screens a strip chart shows the last four seconds of readings, taken ten times a second like the chapter's example program. Turn the pull-up off and release the button to watch a floating input misbehave.

This MicroSim supports the chapter [The Pico Platform: Pins, Files, and Firmware](../../chapters/05-pico-platform/index.md).

## How to Use

1. Press **Press button** to close the switch, and press it again (now **Release button**) to open it.
2. Uncheck **Internal pull-up (Pin.PULL_UP)** to remove the resistor. The code line at the top changes to match.
3. Watch the voltage bar, the `value()` readout and the strip chart for each of the four combinations.
4. Read the explanation under the schematic after each change.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/pull-up-button-lab/main.html"
        height="472px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Analyze how a pull-up resistor sets the resting voltage of an input pin
- Explain why a pressed button reads 0 (active low) with a pull-up
- Describe what a floating input is and why it gives random readings

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- Voltage and current basics from Chapter 2
- Pin configuration with Pin.IN

### Activities

1. **Exploration** (4 min): Try all four combinations of button (open or pressed) and pull-up (on or off). Record the voltage and value() for each in a table.
2. **Guided Practice** (6 min): Explain in writing why the pressed button reads 0, and why only one combination gives random readings.
3. **Assessment** (5 min): Predict what happens if the button were wired to 3.3 V with Pin.PULL_DOWN instead, then check your idea against the chapter text.

### Assessment

- Students complete the four-row table correctly.
- Students use the words "floating" and "active low" correctly in an explanation.
- Students explain why no current flows through the pull-up while the button is open.

## References

1. [Pull-up resistor](https://en.wikipedia.org/wiki/Pull-up_resistor) - Wikipedia article on pull-up and pull-down resistors
2. [Floating input (high impedance)](https://en.wikipedia.org/wiki/High_impedance) - Wikipedia article explaining why an unconnected input floats
3. [MicroPython machine.Pin](https://docs.micropython.org/en/latest/library/machine.Pin.html) - official reference for Pin.IN, Pin.PULL_UP and value()
