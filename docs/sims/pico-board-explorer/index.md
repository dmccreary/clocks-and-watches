---
title: Pico Board Explorer
description: Hover and click the main parts of a Raspberry Pi Pico W drawing to learn what each one does, then take a quiz that hides the labels and tracks the parts you missed.
image: /sims/pico-board-explorer/pico-board-explorer.png
og:image: /sims/pico-board-explorer/pico-board-explorer.png
twitter:image: /sims/pico-board-explorer/pico-board-explorer.png
social:
   cards: false
quality_score: 100
---

# Pico Board Explorer

<iframe src="main.html" height="582px" width="100%" scrolling="no"></iframe>

[Run the Pico Board Explorer Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

The **Raspberry Pi Pico W** is the board that runs every clock in this book. Before you start wiring, it helps to know your way around it. This MicroSim shows a top-down drawing of the board with six labeled parts:

- the **RP2040 chip**, the microcontroller that runs your program,
- the **USB connector** for power and for sending programs from Thonny,
- the **BOOTSEL button** used to install MicroPython,
- the **on-board LED** that your first blink program controls,
- the **wireless module** (the metal can and zigzag antenna) that adds WiFi,
- the **two rows of 20 pins** where you attach displays, buttons, and sensors.

Click a part to read a two-sentence description and a "Used in this book for..." line. When you think you know them all, press **Quiz me**.

## How to Use

- **Hover** over the board to see the name of the part under the pointer.
- **Click** a part to show its description in the box under the board.
- Press **Quiz me** to hide the labels. The prompt above the board names a part; click it. A wrong click outlines the correct part in red so you can learn it.
- After six questions you see your score and the list of parts to review. Press **Explore** (or **Stop quiz** at any time) to bring the labels back.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/pico-board-explorer/main.html"
        height="582px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Identify the RP2040 chip, USB connector, BOOTSEL button, on-board LED, wireless module, and pin rows on a Pico W.
- Recall the purpose of each of those parts.
- Recall which later projects in the book use each part.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Read the Raspberry Pi Pico section of Chapter 1.

### Activities

1. **Explore (4 min):** Students click every part and read its description. Ask them to point to the same parts on a real Pico W if one is available.
2. **Quiz (3 min):** Students take the quiz and write down any part they missed.
3. **Retake (2 min):** Students review their missed parts in Explore mode, then retake the quiz until they score 6 out of 6.
4. **Connect (3 min):** Ask: which part would you use to install MicroPython? Which part do you need for internet time? Which part will a display connect to?

### Assessment

- Students score 6 out of 6 on the built-in quiz.
- Students can name the part needed for each task: installing firmware (BOOTSEL), WiFi time sync (wireless module), and wiring a display (pins).
- Students can explain the difference between the RP2040 chip and the Pico W board.

## References

1. [Raspberry Pi Pico series documentation](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) - Official board documentation, including the Pico W.
2. [RP2040 (Wikipedia)](https://en.wikipedia.org/wiki/RP2040) - Background on the microcontroller chip used on the Pico.
3. [Raspberry Pi Pico W datasheet](https://datasheets.raspberrypi.com/picow/pico-w-datasheet.pdf) - Board layout, pinout, and the wireless module.
4. [Getting started with MicroPython on the Pico](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) - How the BOOTSEL button is used to install firmware.
