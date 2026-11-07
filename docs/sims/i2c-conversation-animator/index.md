---
title: I2C Conversation Animator
description: Step through one I2C write transaction - START, address and write bit, ACK, data byte, ACK, STOP - and see the SDA and SCL waveforms for each part.
image: /sims/i2c-conversation-animator/i2c-conversation-animator.png
og:image: /sims/i2c-conversation-animator/i2c-conversation-animator.png
twitter:image: /sims/i2c-conversation-animator/i2c-conversation-animator.png
social:
   cards: false
quality_score: 0
---

# I2C Conversation Animator

<iframe src="main.html" height="532px" width="100%" scrolling="no"></iframe>

[Run the I2C Conversation Animator MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A Pico, an OLED display (0x3C), a real-time clock (0x68) and a sensor (0x76) all share the same two
wires: **SDA** (data) and **SCL** (clock). This MicroSim shows how the Pico talks to just one of
them, one step at a time.

Each press of **Next step** adds the next part of the conversation to the waveform:

1. **START**: SDA falls while SCL is high. Every device starts listening.
2. **Address + write bit**: seven address bits, most significant bit first, then a 0 meaning
   "I want to write."
3. **ACK**: the one device whose address matches pulls SDA low for one clock. Only that device
   lights up.
4. **Data byte**: eight bits sent by the Pico.
5. **ACK**: the device confirms it got the byte.
6. **STOP**: SDA rises while SCL is high. The bus is free again.

Blue parts of the SDA trace are driven by the Pico and orange parts by the device. Choose
**Wrong address (0x50)** to see what happens when nobody answers: SDA stays high, which is a
**NACK**, and MicroPython reports an `OSError`.

The spec suggested a continuously scrolling animation with a speed slider. Because the goal is to
*understand* the order of the steps, this version uses **Next step** and **Back** buttons so you
can stop at each step, predict the next one, and read the bit values.

## How to Use

1. Choose a device in **Talk to** and a **data** byte.
2. Press **Next step** to add one part of the transaction. Read the explanation box each time.
3. Before each press, predict what SDA will do next and who will drive it.
4. Use **Back** to review a step, and **Reset** to return to the idle bus.
5. Select **Wrong address (0x50)** and step through again. Compare the ACK slot.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/i2c-conversation-animator/main.html"
        height="532px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
13 minutes

### Prerequisites

- Binary and hexadecimal numbers (Chapter 8)
- The SDA and SCL lines and device addresses (Chapter 8)

### Learning Objectives

Students will be able to:

- Describe the order of an I2C write: START, address + W, ACK, data, ACK, STOP
- Explain how the address lets only one device respond on a shared bus
- Identify a missing ACK as the sign of a wrong address or a wiring fault

### Activities

1. **Predict and step** (5 min): With the OLED selected, predict each step before pressing Next step. Write the seven address bits for 0x3C and check them against the waveform.
2. **Count the clocks** (4 min): Count the SCL pulses from START to STOP. Explain why one data byte costs 9 clocks, not 8.
3. **Wrong address** (4 min): Choose the wrong address and step through. Write what the I2C scanner from Chapter 8 would report and why.

### Assessment

- The student converts 0x68 to the seven bits 1101000 and finds them on the waveform.
- The student explains that the device, not the Pico, drives the ACK bit.
- The student links a NACK to an OSError and a wiring or address problem.

## References

1. [I2C](https://en.wikipedia.org/wiki/I%C2%B2C) - Wikipedia article with timing diagrams of START, STOP and ACK.
2. [MicroPython machine.I2C](https://docs.micropython.org/en/latest/library/machine.I2C.html) - Official documentation for writeto(), readfrom() and scan().
3. [Open collector](https://en.wikipedia.org/wiki/Open_collector) - Wikipedia article on open-drain outputs, which is why I2C needs pull-up resistors.
4. [UM10204 I2C-bus specification](https://www.nxp.com/docs/en/user-guide/UM10204.pdf) - The official I2C specification from NXP, for readers who want every detail.
