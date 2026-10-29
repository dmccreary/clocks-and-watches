---
title: Quadrature Encoder Simulator
description: "Turn a rotary encoder knob one step at a time and watch the A and B signals, with each falling edge of A marked by the value of B that sets the direction."
image: /sims/quadrature-encoder-sim/quadrature-encoder-sim.png
og:image: /sims/quadrature-encoder-sim/quadrature-encoder-sim.png
twitter:image: /sims/quadrature-encoder-sim/quadrature-encoder-sim.png
social:
   cards: false
quality_score: 100
---

# Quadrature Encoder Simulator

<iframe src="main.html" height="467px" width="100%" scrolling="no"></iframe>

[Run the Quadrature Encoder Simulator MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A **rotary encoder** has two switches, A and B, that open and close a quarter of a cycle apart as the knob turns. Turning clockwise, the pair goes 00, 10, 11, 01; turning counterclockwise the same states come in reverse order. The chapter's program watches for the moment A **falls** from 1 to 0 and reads B at that instant: B is 1 when turning clockwise and 0 when turning counterclockwise.

Drag the knob, or use **Step CW** and **Step CCW**, which turn it one click (four state changes). Every new state is added to the right of the A and B traces, so the picture is a record of what happened rather than a moving animation. A dashed purple line marks each falling edge of A, labeled with the value of B and the +1 or -1 it adds to the counter. **Show table** lays out both sequences with the current state highlighted.

This MicroSim supports the chapter [Buttons, Interrupts, and State Machines](../../chapters/07-buttons-state-machines/index.md).

## How to Use

1. The MicroSim opens with one example clockwise click already on the traces, so the value starts at 1.
2. Press **Step CW** to turn the knob one click clockwise. Four new states appear on the traces and the value goes up by 1.
3. Press **Step CCW** to turn back. Look at the value of B at the new falling edge.
4. Drag the knob slowly with the mouse to add one state at a time and watch each change of A and B.
5. Check **Show table** to see both sequences. Press **Reset** to clear the traces and the counter.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/quadrature-encoder-sim/main.html"
        height="467px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Explain how the order of the A and B signals encodes the direction of rotation
- Describe the clockwise (00, 10, 11, 01) and counterclockwise (00, 01, 11, 10) sequences
- Explain why reading B at the falling edge of A is enough to decode direction

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- Interrupts on a falling edge (Pin.IRQ_FALLING)
- Binary signals that are either 0 or 1

### Activities

1. **Exploration** (4 min): Press Step CW three times, then Step CCW twice. Predict the value before each press.
2. **Guided Practice** (6 min): Drag the knob slowly and write down A and B after every state change for one clockwise click. Compare with the table.
3. **Assessment** (5 min): Explain to a partner why the program does not need to look at every state change to know the direction.

### Assessment

- Students write the clockwise sequence of A and B from memory.
- Students predict the value of B at a falling edge of A for each direction.
- Students explain what would happen if A and B were wired the other way round.

## References

1. [Rotary encoder: incremental encoders](https://en.wikipedia.org/wiki/Incremental_encoder) - Wikipedia article on quadrature outputs and direction
2. [Gray code](https://en.wikipedia.org/wiki/Gray_code) - the sequence in which only one bit changes at a time
3. [MicroPython Pin.irq()](https://docs.micropython.org/en/latest/library/machine.Pin.html#machine.Pin.irq) - official reference for falling-edge interrupts
