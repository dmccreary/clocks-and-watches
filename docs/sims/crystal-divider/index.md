---
title: Crystal Divider MicroSim
description: Watch a 32,768 Hz quartz crystal get divided by two fifteen times into a 1 Hz tick, then see how a parts-per-million error makes a clock drift each day.
image: /sims/crystal-divider/crystal-divider.png
og:image: /sims/crystal-divider/crystal-divider.png
twitter:image: /sims/crystal-divider/crystal-divider.png
social:
   cards: false
quality_score: 100
---

# Crystal Divider MicroSim

<iframe src="main.html" height="482px" width="100%" scrolling="no"></iframe>

[Run the Crystal Divider MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

Almost every watch and clock chip keeps time with a quartz crystal that vibrates **32,768 times per second**. That number is \(2^{15}\), so a chain of 15 "divide by two" stages turns it into exactly one tick per second. This MicroSim draws that chain as 16 boxes: the crystal itself, then each stage at half the frequency of the one before it, ending at **1 Hz**.

Each box is a square wave. A box is gold for the first half of its cycle and white for the second half. The fast boxes change thousands of times a second, which no screen can show, so they are drawn pale yellow until you slow time down.

Two clocks count the 1 Hz ticks. The **perfect clock** uses the exact time. The **crystal clock** uses a crystal that runs a little fast by the number of **parts per million (ppm)** you set with the slider. The readout applies the formula from the chapter:

\[ \text{drift per day} = 86{,}400 \times \frac{\text{ppm}}{1{,}000{,}000} \]

At the default 30 ppm that is about 2.59 seconds per day.

## How to Use

The MicroSim opens paused.

- Press **Start** to run the chain in real time. Watch the 1 Hz box: it is gold for half a second and white for half a second, and both clocks count up once per second.
- Check **Slow motion** to run time 4,096 times slower. Now even the 32,768 Hz crystal box flashes slowly enough to see (8 times a second), and you can watch each box flash at half the rate of the box before it.
- Move the **Crystal error (ppm)** slider. The *Drift per day* readout updates right away.
- Press **Run one day** to fast-forward 24 hours in about three seconds. Compare the perfect clock with the crystal clock when it stops.
- Press **Reset** to set both clocks back to 00:00:00 and pause.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/crystal-divider/main.html"
        height="482px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Apply repeated division by two to find the frequency at any stage of a 32,768 Hz divider chain.
- Explain why 15 divide-by-two stages turn a 32,768 Hz crystal into a 1 Hz tick.
- Calculate the daily drift of a clock from its crystal error in parts per million.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Know that frequency is measured in hertz (repeats per second).
- Be comfortable multiplying and dividing by powers of two.

### Activities

1. **Predict the chain (3 min):** Before pressing Start, ask students to write down the frequency of the 5th and 10th boxes. Then turn on Slow motion, press Start, and check their answers against the labels.
2. **Count the flashes (4 min):** In Slow motion, students count how many times one box flashes while the next box flashes once. They should find exactly two, for every pair of boxes.
3. **Calculate the drift (5 min):** Set the slider to 10, 30, and 100 ppm. For each value, students calculate the drift per day by hand, then press Run one day to check. Ask: how many ppm would make a clock gain one full minute in a month?
4. **Discuss (3 min):** Why do clock builders add a real-time clock chip or internet time sync instead of just buying a better crystal?

### Assessment

- Students can state the frequency after any number of divide-by-two stages (for example, 32,768 Hz after 4 stages is 2,048 Hz).
- Students can calculate drift per day from a ppm value, such as 20 ppm giving about 1.73 seconds per day.
- Students can explain why 32,768 Hz was chosen: it is a power of two, so halving it 15 times lands exactly on 1 Hz.

## References

1. [Crystal oscillator (Wikipedia)](https://en.wikipedia.org/wiki/Crystal_oscillator) - How quartz crystals make a steady frequency, including the 32,768 Hz watch crystal.
2. [Frequency divider (Wikipedia)](https://en.wikipedia.org/wiki/Frequency_divider) - Explains divide-by-two flip-flop chains used to slow a fast signal down.
3. [Parts-per notation (Wikipedia)](https://en.wikipedia.org/wiki/Parts-per_notation) - What ppm means and how it is used to describe small errors.
4. [Quartz clock (Wikipedia)](https://en.wikipedia.org/wiki/Quartz_clock) - History and accuracy of quartz timekeeping.
