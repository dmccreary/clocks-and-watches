---
title: Accuracy vs Precision Targets
description: A dartboard target where the bullseye is the true time and each dot is a clock reading. Bias and spread sliders show the difference between an accurate clock and a precise one.
image: /sims/accuracy-vs-precision/accuracy-vs-precision.png
og:image: /sims/accuracy-vs-precision/accuracy-vs-precision.png
twitter:image: /sims/accuracy-vs-precision/accuracy-vs-precision.png
social:
   cards: false
quality_score: 100
---

# Accuracy vs Precision Targets

<iframe src="main.html" height="537px" width="100%" scrolling="no"></iframe>

[Run the Accuracy vs Precision Targets MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

People often use *accurate* and *precise* as if they meant the same thing. For clocks they do not.

- An **accurate** clock shows the right time on average.
- A **precise** clock gives very consistent readings, even if every reading is off by the same amount.

This MicroSim turns clock error into a dartboard. The red bullseye is the true time, and each ring is one more second of error. Every yellow dot is one reading of the clock. The purple **X** marks the average of the twenty readings.

Two kinds of error move the dots:

- **Bias** is error that is the same every time, like a clock that always runs 3 seconds fast. It slides the whole cloud of dots away from the bullseye.
- **Spread** is random error that changes from reading to reading. It scatters the dots.

The label in the panel classifies the readings. A set counts as accurate when the average lands within 1 second of the true time, and as precise when the readings have a standard deviation under 1 second.

## How to Use

1. Look at the opening target. It already shows twenty readings with a small bias and a small spread.
2. Drag **Bias (consistently off)** to the right. The whole cloud moves away from the bullseye but stays tight. Watch the label change to "Precise but not accurate."
3. Set bias back to 0 and drag **Spread (random error)** to the right. The cloud stays centered but spreads out: "Accurate on average but not precise."
4. Press **Take 20 readings** to drop a fresh set of random readings with the same settings. Notice that the average and spread change a little each time.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/accuracy-vs-precision/main.html"
        height="537px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objective

Students will differentiate accuracy from precision using a clock-error analogy (Bloom: Understanding, Analyzing).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
10-15 minutes

### Prerequisites

- Clock drift and parts per million (ppm) from Chapter 13
- The idea of an average

### Activities

1. **Predict** (3 min): Before touching the sliders, ask students which slider will move the purple X and which one will spread the dots. Record the predictions.
2. **Explore** (5 min): Students find settings that produce each of the four labels and sketch each target in their notebooks.
3. **Connect to clocks** (5 min): Match each label to a real clock. A DS3231 that is 2 seconds fast after a month is precise but not accurate. A clock read by hand from a blurry photo might be accurate on average but not precise.
4. **Discuss** (2 min): Which kind of error can you fix with one correction? (Bias: subtract the known offset. Spread cannot be removed with a single correction.)

### Assessment

- Give students a target picture and have them name the result and say which slider caused it.
- Ask: "A clock is always exactly 5 seconds fast. Is it accurate? Is it precise?"
- Ask students to explain why taking more readings helps you find the bias but does not reduce the spread.

## References

1. [Accuracy and precision](https://en.wikipedia.org/wiki/Accuracy_and_precision) - Wikipedia article with the classic target diagrams.
2. [DS3231 Datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/DS3231.pdf) - Analog Devices; lists the ±2 ppm accuracy of the DS3231.
3. [Normal distribution](https://en.wikipedia.org/wiki/Normal_distribution) - Wikipedia; the random readings use a normal (Gaussian) distribution.
4. [p5.js randomGaussian() reference](https://p5js.org/reference/p5/randomGaussian/) - The function used to generate the readings.
