---
title: Sense-Think-Act Clock Sorter
description: Drag eight clock parts into Sensors, Microcontroller, and Actuators columns, get a hint for every wrong drop, then step one signal through the sense-think-act loop.
image: /sims/sense-think-act-clock/sense-think-act-clock.png
og:image: /sims/sense-think-act-clock/sense-think-act-clock.png
twitter:image: /sims/sense-think-act-clock/sense-think-act-clock.png
social:
   cards: false
quality_score: 100
---

# Sense-Think-Act Clock Sorter

<iframe src="main.html" height="522px" width="100%" scrolling="no"></iframe>

[Run the Sense-Think-Act Clock Sorter Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

Every device in this book follows the same pattern: **sense, think, act**. A **sensor** measures the world and sends information *to* the microcontroller. The **microcontroller** runs the program and decides what to do. An **actuator** receives a signal *from* the microcontroller and changes the world by lighting up, beeping, or drawing on a screen.

In this MicroSim you sort eight real clock parts into those three roles. A correct drop snaps into the column with a green outline and a short explanation. A wrong drop slides back to the tray with a hint. The question that sorts every part is the same one Chrono asks in the chapter: *does information flow toward the microcontroller or away from it?*

Once all eight parts are sorted, you can step one signal through the auto-dimming clock example from the chapter: the light sensor senses a dark room, the Pico thinks, and the LED display acts.

## How to Use

- **Drag** a card from the parts tray and drop it in the Sensors, Microcontroller, or Actuators column.
- Read the message under the columns. Green means correct; red is a hint to try again.
- **Hover** over a placed card to see a one-line description of the part.
- When all eight cards are placed, press **Next step** to move the orange dot from sensor to Pico to display, one step at a time.
- Press **Reset** to shuffle the cards back into the tray.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/sense-think-act-clock/main.html"
        height="522px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Classify clock parts as sensors, a microcontroller, or actuators.
- Explain the direction information flows between each part and the Pico.
- Describe one full sense-think-act cycle in an auto-dimming clock.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Read the Sensors and Actuators section of Chapter 1.

### Activities

1. **Sort (5 min):** Students sort all eight parts. Ask them to say out loud, for each card, whether information goes to the Pico or comes from it.
2. **Tricky cases (3 min):** Discuss the DS3231 real-time clock and the OLED screen. Why is a chip that "keeps time" an input? Why is a screen that "shows the time" an output?
3. **Trace the loop (3 min):** Press Next step three times and have students describe each step in their own words. Then ask them to invent a different loop, such as "button pressed, Pico adds one minute, display changes."
4. **Extend (4 min):** Students name two more parts (for example a temperature sensor and a motor) and say which column each belongs in.

### Assessment

- Students sort all eight parts with no more than one hint.
- Students can explain, using the words "to the Pico" or "from the Pico," why each part is a sensor or an actuator.
- Students can describe a sense-think-act cycle for a clock feature not shown in the MicroSim.

## References

1. [Sensor (Wikipedia)](https://en.wikipedia.org/wiki/Sensor) - Definition and examples of sensors.
2. [Actuator (Wikipedia)](https://en.wikipedia.org/wiki/Actuator) - Definition and examples of actuators.
3. [Microcontroller (Wikipedia)](https://en.wikipedia.org/wiki/Microcontroller) - What a microcontroller is and where it is used.
4. [Raspberry Pi Pico documentation](https://www.raspberrypi.com/documentation/microcontrollers/pico-series.html) - Official documentation for the Pico board.
