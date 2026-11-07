---
title: Schematic Symbol Matcher
description: Click the hidden symbols in an LED circuit schematic to reveal each part, match drawings of real parts to their symbols, and trace the current from pin GP15 to ground.
image: /sims/schematic-symbol-matcher/schematic-symbol-matcher.png
og:image: /sims/schematic-symbol-matcher/schematic-symbol-matcher.png
twitter:image: /sims/schematic-symbol-matcher/schematic-symbol-matcher.png
social:
   cards: false
quality_score: 100
---

# Schematic Symbol Matcher

<iframe src="main.html" height="472px" width="100%" scrolling="no"></iframe>

[Run the Schematic Symbol Matcher Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A **schematic** is a circuit map. Instead of drawing what parts look like, it uses simple symbols and lines that show how the parts are connected. Reading schematics is how you will follow every wiring diagram in this book.

This schematic shows the first LED circuit you will build:

- Pico pin **GP15** supplies 3.3 V when the program turns it on.
- A **330 Ω resistor** (the zigzag) limits the current.
- The **LED** (triangle and bar) lights up when current flows through it the right way.
- **Ground** (three stacked lines) is the 0 V return path that completes the circuit.

Each symbol starts with its name hidden. Click a symbol to reveal its name, a drawing of the real part, and a tip for recognizing the symbol. Then switch to **Match mode** to test yourself, and press **Trace the current** to follow the path the current takes.

## How to Use

- **Click** a symbol to reveal its name. The panel shows a drawing of the real part, what it does, and how to recognize its symbol.
- Press **Trace the current** to watch an orange dot travel from GP15 through the resistor and LED to ground. The panel explains each part as the dot passes it, and the LED lights up when current reaches it.
- Press **Match mode** to hide all names. The panel shows a real part; click the symbol that matches it. Click any symbol after the feedback to get the next part. Press **Explore** to leave Match mode.
- Press **Hide labels** to hide the names again and start over.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/schematic-symbol-matcher/main.html"
        height="472px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Recall the schematic symbols for a GPIO pin, a resistor, an LED, and ground.
- Interpret a simple LED circuit diagram by tracing the path of the current.
- Explain the job of each part in the circuit.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Read the Schematic Symbols and LED Basics sections of Chapter 2.

### Activities

1. **Reveal (3 min):** Students click each symbol and copy the symbol and its name into their notes.
2. **Trace (3 min):** Students press Trace the current and then explain, in order, what each part does to the current.
3. **Match (4 min):** Students switch to Match mode and answer until they get five in a row correct.
4. **Draw it (5 min):** Without the MicroSim, students draw the same circuit using GP14 and a green LED, then compare their drawing with a partner.

### Assessment

- Students correctly name all four symbols without help.
- Students can explain why the LED symbol points from the resistor toward ground.
- Students draw a correct schematic for an LED connected to a different GPIO pin.

## References

1. [Electronic symbol (Wikipedia)](https://en.wikipedia.org/wiki/Electronic_symbol) - Standard schematic symbols for common parts.
2. [Circuit diagram (Wikipedia)](https://en.wikipedia.org/wiki/Circuit_diagram) - How schematics differ from wiring pictures.
3. [Light-emitting diode (Wikipedia)](https://en.wikipedia.org/wiki/Light-emitting_diode) - How LEDs work, including anode and cathode.
4. [Ground (electricity) (Wikipedia)](https://en.wikipedia.org/wiki/Ground_(electricity)) - What ground means in a circuit.
