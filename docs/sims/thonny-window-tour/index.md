---
title: Thonny Window Tour
description: "A clickable mockup of the Thonny IDE with numbered hotspots for the interpreter selector, editor, Run and Stop buttons, Shell, and the two Files panes, plus a quiz mode."
image: /sims/thonny-window-tour/thonny-window-tour.png
og:image: /sims/thonny-window-tour/thonny-window-tour.png
twitter:image: /sims/thonny-window-tour/thonny-window-tour.png
social:
   cards: false
quality_score: 100
---

# Thonny Window Tour

<iframe src="main.html" height="567px" width="100%" scrolling="no"></iframe>

[Run the Thonny Window Tour MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

**Thonny** is the beginner-friendly IDE this book uses to write MicroPython and send it to the Raspberry Pi Pico. Its window has a handful of areas that you will use every day, and knowing their names makes following lab instructions much easier.

This MicroSim is a drawn model of the Thonny window with seven numbered hotspots. Hover over one to see its name, and click it to read what it does and get a short "Try this" step to do in the real Thonny. The two **Files** panes matter most later in the course: a program in the top pane lives on your laptop, but a `main.py` in the bottom pane lives on the Pico and runs by itself at power-up. When you are ready, **Quiz me** asks questions such as "Where would you type a quick test line?" and you answer by clicking the right area.

This MicroSim supports the chapter [MicroPython Basics: Variables and Data Types](../../chapters/03-micropython-basics/index.md).

## How to Use

1. Hover over an orange numbered area to see its name.
2. Click an area to read a two-sentence description and a "Try this" step for the real Thonny.
3. Check **Quiz me** to switch to quiz mode. Read the question and click the area that answers it. The correct area is outlined in blue after each answer.
4. Press **Next question** for another question. Your score appears beside the button.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/thonny-window-tour/main.html"
        height="567px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Identify the editor, Shell, Run button, Stop button, interpreter selector and Files panes in Thonny
- Explain what each part of the Thonny window is used for
- Distinguish files stored on "This computer" from files stored on the MicroPython device

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- Thonny installed on the computer (see Desktop Setup)
- A Raspberry Pi Pico connected with a data USB cable

### Activities

1. **Exploration** (5 min): Click all seven areas and read each description. Open Thonny on your own computer and find each one.
2. **Guided Practice** (5 min): Do three of the "Try this" steps in the real Thonny: type `2 + 3` in the Shell, run a one-line program, and stop a loop.
3. **Assessment** (5 min): Turn on Quiz me and answer all seven questions. Aim for 7 out of 7.

### Assessment

- Students answer all seven quiz questions correctly.
- Students explain the difference between saving to "This computer" and to the MicroPython device.
- Students can stop a running program from Thonny without unplugging the Pico.

## References

1. [Thonny: Python IDE for beginners](https://thonny.org/) - official Thonny site and downloads
2. [Getting started with MicroPython on the Raspberry Pi Pico](https://www.raspberrypi.com/documentation/microcontrollers/micropython.html) - Raspberry Pi documentation, including Thonny setup
3. [Integrated development environment](https://en.wikipedia.org/wiki/Integrated_development_environment) - Wikipedia article on IDEs
