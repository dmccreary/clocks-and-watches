---
title: Binary Number
description: Interactive p5.js simulation for learning binary numbers with toggle buttons and decimal conversion display
image: /sims/binary-number/binary-number.png
og:image: /sims/binary-number/binary-number.png
quality_score: 80
---

# Binary Number

<iframe src="binary-number.html" width="350" height="140" scrolling="no"></iframe>

**Copy this iframe to your website:**

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/binary-number/binary-number.html" width="350" height="140" scrolling="no"></iframe>
```

[Run the 4-Bit Binary Number MicroSim in fullscreen](binary-number.html){ .md-button .md-button--primary }

## Description

A binary number is one where each of the digits can only be a 0 or a 1. The values double with each position. So the right-most digit is 0 or 1, the second bit is 0 or 2, the third is 0 or 4, and the fourth is 0 or 8. You can generate any number from 0 to 15 by adding the values.

Key features:

- Toggle buttons to flip individual bits
- Real-time decimal equivalent display
- Visual representation of binary place values

### How to Use

1. Click on "Bit 0", "Bit 1", "Bit 2", or "Bit 3" buttons to toggle each bit
2. Observe the binary digits (0 or 1) displayed above each button
3. Watch the decimal value update automatically

## Alternative Versions

- [Binary Number 4-Bit Demo](./binary-number.html) - 4 bits (0-15)
- [Binary Number 8-Bit Demo](./binary-number-8.html) - 8 bits (0-255)

## Sample Prompt

```
Create a simulation of a 4-bit binary number.
Add buttons that toggle each of the four bits.
Add a text output that shows the decimal equivalent of the binary number.
```

## Sample Code

```js
let canvasWidth = 330;
let canvasHeight = 120;
let bits = [0, 0, 0, 0];
let decimalValue = 0;

function setup() {
  createCanvas(canvasWidth, canvasHeight);
  textSize(24);
  background(245);

  for (let i = 0; i < 4; i++) {
    let btn = createButton('Bit ' + i);
    btn.position(20 + (3 - i) * 80, 50);
    btn.mousePressed(() => toggleBit(i));
  }
}

function draw() {
  clear();
  background(245);

  for (let i = 0; i < bits.length; i++) {
    text(bits[i], 40 + (3 - i) * 80, 30);
  }

  decimalValue = binaryToDecimal(bits);
  text('Decimal: ' + decimalValue, 20, 110);
}

function toggleBit(index) {
  bits[index] = bits[index] === 0 ? 1 : 0;
}

function binaryToDecimal(binaryArray) {
  let decimal = 0;
  for (let i = 0; i < binaryArray.length; i++) {
    decimal += binaryArray[i] * Math.pow(2, i);
  }
  return decimal;
}
```

## Key Learnings

1. How to set up an array of buttons each with different actions
2. How to use the `pow(2, i)` function to convert binary to decimal
3. How to setup a `toggleBit(index)` function using the ternary operator (`?` and `:`)

## Lesson Plan

### Objective

Students will understand the binary number system and how it is used in computer science. They will learn to convert binary numbers to decimal numbers and vice versa.

**Grade Level:** 9th Grade

**Duration:** 1-2 class periods (45-90 minutes)

### Materials

1. Computers with internet access (or offline environment set up with p5.js)
2. Projector to demonstrate the simulation
3. Link to the simulation
4. Worksheets or online notebooks for binary-to-decimal conversion exercises
5. Whiteboard and markers

### Lesson Outline

1. **Introduction to Binary Numbers (15 minutes):**
   - Begin with a discussion on number systems, focusing on the decimal system
   - Introduce the binary number system, explaining its base-2 nature
   - Discuss the significance of binary numbers in computer science

2. **Demonstration of the Simulation (10 minutes):**
   - Project the simulation on the screen
   - Explain the interface, pointing out the bits, their significance, and the decimal conversion
   - Demonstrate toggling the bits and observing the decimal output

3. **Interactive Session with Simulation (20 minutes):**
   - Allow students to experiment with the simulation on their computers
   - Encourage them to predict the decimal output before toggling the bits
   - Facilitate a discussion about their observations and insights

4. **Binary to Decimal Conversion Exercise (15 minutes):**
   - Distribute worksheets with binary numbers
   - Instruct students to convert them to decimal numbers using the simulation as a reference
   - Review the answers as a class, discussing any common errors or misconceptions

5. **Group Activity: Real-World Applications (15-30 minutes):**
   - Divide students into small groups
   - Assign each group to research and present a short explanation about a real-world application of binary numbers (e.g., digital storage, computer processors)
   - Facilitate a class discussion on these applications, linking them back to the simulation

6. **Wrap-up and Reflection (5-10 minutes):**
   - Summarize key takeaways from the lesson
   - Encourage students to reflect on what they learned and how they might see binary numbers in their daily lives
   - Answer any remaining questions

### Assessment

- Evaluate students based on their participation in activities and discussions
- Review their worksheets for accuracy in binary to decimal conversion
- Assess group presentations for understanding of real-world applications

### Extension Activities

- Extend the simulation to be 8, 16, 32, and 64 bits
- Discuss what the shift-left and shift-right functions will do. Hint: how would you double the number?
- Introduce the concept of hexadecimal numbers and how they relate to binary and decimal systems
- Create a project where students develop their own simple binary-based simulations or games using p5.js
- Discuss the process of adding binary numbers

## References

- [ChatGPT Transcript](https://chat.openai.com/share/e1e0beda-05cd-4d78-824e-ca8d5447c513) - Demonstrates the iterative nature of prompting
- [Binary Number System](https://www.mathsisfun.com/binary-number-system.html) - Math is Fun tutorial
- [p5.js Reference](https://p5js.org/reference/) - Documentation for the p5.js library
