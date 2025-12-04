---
title: Analog Clock
description: Interactive p5.js analog clock simulation with manual and automatic modes, demonstrating trigonometric functions for hand positioning
image: /sims/analog-clock/analog-clock.png
og:image: /sims/analog-clock/analog-clock.png
quality_score: 75
---

# Analog Clock

<iframe src="analog-clock.html" width="100%" height="550px" scrolling="no"></iframe>

**Copy this iframe to your website:**

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/analog-clock/analog-clock.html" width="100%" height="550px" scrolling="no"></iframe>
```

[Run the Analog Clock MicroSim in fullscreen](analog-clock.html){ .md-button .md-button--primary }

[Edit in the p5.js Editor](https://editor.p5js.org/dmccreary/sketches/){ .md-button }

## Description

This MicroSim simulates an analog clock face with hour, minute, and second hands. It demonstrates the practical application of trigonometric functions (sine and cosine) to calculate hand positions based on time values.

Key features:

- Real-time clock synchronized to local system time
- Manual mode with sliders to set custom time
- Automatic mode that displays current time
- Visual demonstration of polar-to-Cartesian coordinate conversion

### How to Use

1. **Automatic Mode**: Watch the clock display real-time
2. **Manual Mode**: Use the sliders to set hours (0-11), minutes (0-59), and seconds (0-59)
3. **Switch Mode Button**: Toggle between automatic and manual modes

## Trigonometry Demonstration

This is a wonderful lab to demonstrate the use of trigonometric functions sine() and cosine(). We ask the question:

*Write some code that will take in the seconds as a number from 0 to 59 and return the x and y positions of the tip of the second hand.*

```js
// Draw second hand
// convert seconds to radians
secondHand = map(sc, 0, 60, 0, TWO_PI) - HALF_PI;
// draw a line from the center of the canvas to the endpoint
line(0, 0, cos(secondHand) * canvasSize / 2.5,
           sin(secondHand) * canvasSize / 2.5);
```

## Full Program Source

```js
let canvasSize = 400;
let hourHand, minuteHand, secondHand;
let hourSlider, minuteSlider, secondSlider;
let manualMode = true;

function setup() {
  const canvas = createCanvas(400, 400);
  canvas.parent('canvas-container');
  background(0);

  // Create sliders for manual mode
  hourSlider = createSlider(0, 11, 0);
  hourSlider.position(10, canvasSize + 10);

  minuteSlider = createSlider(0, 59, 0);
  minuteSlider.position(10, canvasSize + 40);

  secondSlider = createSlider(0, 59, 0);
  secondSlider.position(10, canvasSize + 70);

  let modeButton = createButton('Switch Mode');
  modeButton.position(10, canvasSize + 100);
  modeButton.mousePressed(switchMode);
}

function draw() {
  background(0);
  translate(canvasSize / 2, canvasSize / 2);

  let hr, mn, sc;
  if (manualMode) {
    hr = hourSlider.value();
    mn = minuteSlider.value();
    sc = secondSlider.value();
  } else {
    let now = new Date();
    hr = now.getHours() % 12;
    mn = now.getMinutes();
    sc = now.getSeconds();
  }

  // Draw hour hand
  stroke(255);
  strokeWeight(10);
  hourHand = map(hr, 0, 12, 0, TWO_PI) - HALF_PI;
  line(0, 0, cos(hourHand) * canvasSize / 4, sin(hourHand) * canvasSize / 4);

  // Draw minute hand
  strokeWeight(8);
  minuteHand = map(mn, 0, 60, 0, TWO_PI) - HALF_PI;
  line(0, 0, cos(minuteHand) * canvasSize / 3, sin(minuteHand) * canvasSize / 3);

  // Draw second hand
  stroke(255, 0, 0);
  strokeWeight(4);
  secondHand = map(sc, 0, 60, 0, TWO_PI) - HALF_PI;
  line(0, 0, cos(secondHand) * canvasSize / 2.5, sin(secondHand) * canvasSize / 2.5);
}

function switchMode() {
  manualMode = !manualMode;
  hourSlider.attribute('disabled', !manualMode);
  minuteSlider.attribute('disabled', !manualMode);
  secondSlider.attribute('disabled', !manualMode);
}
```

## Version 2

[Version 2 - Blue clock with tick marks](./v2.html)

## Lesson Plan

### Learning Objectives

After completing this lesson, students will be able to:

- Apply sine and cosine functions to convert polar coordinates to Cartesian coordinates
- Explain how angles are mapped from time values to radians
- Modify code parameters to customize clock appearance

### Target Audience

- Grade level: High school (grades 9-12)
- Prerequisites: Basic trigonometry (understanding of sine, cosine, and radians)

### Activities

1. **Exploration Activity**: Use manual mode to observe how hand positions change with different time values
2. **Guided Investigation**: Calculate the expected (x, y) position for a given second value and verify with the simulation
3. **Extension Activity**: Modify the code to add tick marks or change hand colors

### Assessment

- Can students predict the angle of the second hand for a given second value?
- Can students explain why HALF_PI is subtracted in the angle calculation?
- Can students modify the code to display a 24-hour clock face?

## References

- [p5.js Reference](https://p5js.org/reference/) - Documentation for the p5.js library
- [Trigonometry for Games](https://www.mathsisfun.com/sine-cosine-tangent.html) - Math is Fun trigonometry tutorial
- [Polar Coordinates](https://en.wikipedia.org/wiki/Polar_coordinate_system) - Wikipedia article on polar coordinate systems
