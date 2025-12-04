---
title: Shift Register
description: Interactive p5.js simulation of a 74HC594 shift register demonstrating serial-to-parallel data conversion
quality_score: 70
---

# Shift Register MicroSim

<iframe src="main.html" width="100%" height="480px" scrolling="no"></iframe>

**Copy this iframe to your website:**

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/shift-register/main.html" width="100%" height="480px" scrolling="no"></iframe>
```

[Run the Shift Register MicroSim in fullscreen](main.html){ .md-button .md-button--primary }

[Logic Analyzer View](https://editor.p5js.org/dmccreary/sketches/dgYs8vQ_Y){ .md-button }

## Description

This MicroSim demonstrates how a 74HC594 shift register works. Shift registers are essential components in digital electronics that convert serial data to parallel output, allowing microcontrollers to control many outputs with just a few pins.

Key features:

- Visual representation of the 74HC594 chip
- Interactive data input (0 or 1)
- Clock button to shift data through the register
- Latch button to transfer shift register to output
- 8-bit shift register and output register visualization

### How to Use

1. Select the data input value (0 or 1) using the radio buttons
2. Press "NEXT CLOCK" to shift data into the register
3. Observe how bits move through the 8-position shift register
4. Press "LATCH" to transfer the shift register contents to the output pins

## How Shift Registers Work

The 74HC594 contains two registers:

1. **Shift Register**: An internal 8-bit register that accepts serial data
2. **Output Register**: Holds the parallel output that drives the pins

Each clock pulse shifts all bits one position and loads the new data bit at position 0. The latch pulse copies the entire shift register to the output register.

## Lesson Plan

### Learning Objectives

After completing this lesson, students will be able to:

- Explain the purpose of a shift register in digital circuits
- Describe the difference between serial and parallel data transfer
- Demonstrate how clock and latch signals control data movement

### Target Audience

- Grade level: High school to undergraduate (grades 10-14)
- Prerequisites: Basic understanding of binary numbers and digital logic

### Activities

1. **Exploration Activity**: Load a specific 8-bit pattern (e.g., 10101010) into the shift register
2. **Guided Investigation**: Time how many clock pulses are needed to completely load 8 bits
3. **Extension Activity**: Research how shift registers are used to drive LED displays or expand I/O

### Assessment

- Can students predict the output after a series of clock and data inputs?
- Can students explain why we need both clock and latch signals?
- Can students describe a real-world application of shift registers?

## References

- [74HC595 Datasheet](https://www.ti.com/lit/ds/symlink/sn74hc595.pdf) - Texas Instruments datasheet
- [Shift Register Tutorial](https://www.arduino.cc/en/Tutorial/Foundations/ShiftOut) - Arduino shift register tutorial
- [p5.js Reference](https://p5js.org/reference/) - Documentation for the p5.js library
