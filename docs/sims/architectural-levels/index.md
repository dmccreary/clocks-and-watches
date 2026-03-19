---
title: Architectural Levels Zoom
description: Interactive visualization showing progressive zoom levels of clock system architecture from high-level to component details
quality_score: 70
---

# Architectural Levels Zoom

<iframe src="main.html" width="100%" height="520px" scrolling="no"></iframe>

**Copy this iframe to your website:**

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/architectural-levels/main.html" width="100%" height="520px" scrolling="no"></iframe>
```

[Run the Architectural Levels MicroSim in fullscreen](main.html){ .md-button .md-button--primary }

## Description

This MicroSim demonstrates the hierarchical architecture of a digital clock system through progressive zoom levels. Starting with a simple "Clock" component, each level reveals more internal components and their interconnections, helping students understand how complex systems are built from simpler parts.

Key features:

- 10 progressive zoom levels showing increasing detail
- Color-coded components for easy identification
- Labeled connections between components (SPI Bus, I2C Bus)
- Smooth transitions between levels
- Both p5.js and React implementations available

### How to Use

1. Use the slider at the bottom to adjust the zoom level (1-10)
2. Observe how new components appear at each level
3. Note the connections between components as they are revealed

## Zoom Levels

| Level | Components Shown |
|-------|------------------|
| 1 | Clock (single component) |
| 2 | Display + Microcontroller |
| 3 | Display + SPI Bus + Microcontroller |
| 4 | Display + SPI Bus + Microcontroller + RTC |
| 5 | Level 4 + I2C Bus connection |
| 6 | Level 5 + Buttons |
| 7 | Level 6 + Power system |
| 8 | Level 7 + Speaker |
| 9 | Level 8 + Core 1 and Core 2 inside Microcontroller |
| 10 | Level 9 + PIO inside Microcontroller |

## Alternative Implementations

- [P5.js Version](./main.html) - Uses p5.js for rendering
- [React Version](./react.html) - Uses React with SVG for crisp rendering

## Sample Prompt

```
Create a MicroSim that shows different levels of Zoom. The highest level shows a single component and as you increase the Zoom level it shows more components.

Level 1: Just the Clock as a rectangle centered on the canvas with the label "Clock" in a large font in the center
Level 2: The architecture drawing now shows two rectangular components: a "Display" at the top and "Microcontroller" at the bottom
...
```

## Lesson Plan

### Learning Objectives

After completing this lesson, students will be able to:

- Identify the major components of a digital clock system
- Explain how components communicate via buses (SPI, I2C)
- Describe the hierarchical nature of system architecture

### Target Audience

- Grade level: High school to undergraduate (grades 10-14)
- Prerequisites: Basic understanding of electronic components

### Activities

1. **Exploration Activity**: Navigate through all 10 levels and identify each new component
2. **Guided Investigation**: Draw a block diagram showing all components and their connections
3. **Extension Activity**: Research one component (e.g., RTC, SPI Bus) and present its function

### Assessment

- Can students name all components visible at level 10?
- Can students explain the difference between SPI and I2C buses?
- Can students describe why the microcontroller has multiple cores?

## References

- [SPI Bus Protocol](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface) - Serial Peripheral Interface explanation
- [I2C Bus Protocol](https://en.wikipedia.org/wiki/I%C2%B2C) - Inter-Integrated Circuit communication
- [Raspberry Pi Pico Architecture](https://www.raspberrypi.com/documentation/microcontrollers/rp2040.html) - RP2040 microcontroller documentation
