---
title: Sampling Rate Explorer
description: Sample a sine wave at different rates and bit depths to see the Nyquist limit, aliasing, and the bytes per second each choice costs.
image: /sims/sampling-rate-explorer/sampling-rate-explorer.png
og:image: /sims/sampling-rate-explorer/sampling-rate-explorer.png
twitter:image: /sims/sampling-rate-explorer/sampling-rate-explorer.png
social:
   cards: false
quality_score: 0
---

# Sampling Rate Explorer

<iframe src="main.html" height="547px" width="100%" scrolling="no"></iframe>

[Run the Sampling Rate Explorer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A digital sound is a list of numbers called **samples**, each one a measurement of the
sound wave at one instant. This MicroSim samples a sine wave and shows three things at
once:

- the **original wave** (blue), the smooth sound you want to play,
- the **samples** (orange dots) and the **staircase** a simple DAC builds from them by
  holding each value until the next sample arrives,
- the **cost**: the Nyquist limit, the data rate in bytes per second, and how much RAM
  one second of mono sound needs.

When the wave frequency goes above half the sampling rate (the **Nyquist limit**), the
samples no longer describe the original wave. They describe a lower, wrong frequency.
This is **aliasing**, and a red warning appears. Turn on *Show the wave you hear* to see
the dashed wave that a smoothing filter would rebuild from the same samples.

## How to Use

1. Move the **Wave frequency** slider (100 to 4,000 Hz) to change the pitch.
2. Move the **Sampling rate** slider (2,000 to 44,100 samples per second). Watch the dots
   spread out or crowd together, and watch the data-rate bar grow.
3. Choose **8-bit** or **16-bit** samples to see how bit depth changes the data rate.
4. Check **Show the wave you hear** to compare the original wave with the wave that comes
   out of the speaker after filtering.
5. Push the frequency above half the sampling rate and read the **You hear** line.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/sampling-rate-explorer/main.html"
        height="547px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Frequency and pitch measured in hertz (Chapter 17, PWM Sound)
- The idea of a sample as one measurement of a wave
- Bits and bytes (8 bits = 1 byte)

### Learning Objectives

Students will be able to:

- Analyze how the sampling rate changes the number of samples per cycle and the shape of the rebuilt wave
- Predict the heard frequency when a tone is above the Nyquist limit
- Calculate the data rate with rate x (bits / 8) x channels and compare it with the Pico's RAM

### Activities

1. **Explore** (4 min): Start at 440 Hz and 8,000 samples per second. Slowly lower the
   sampling rate. At what rate do there stop being at least two dots per cycle?
2. **Predict, then test** (6 min): Set the rate to 4,000 samples per second. Before moving the
   frequency to 3,500 Hz, predict what you will hear using \( f_{heard} = f_s - f \). Then
   check *Show the wave you hear*. Was your prediction right?
3. **Cost check** (5 min): Find the lowest sampling rate that plays a 3,000 Hz alarm beep
   correctly. Record its data rate at 8 and 16 bits. How many seconds of that sound fit in
   100 KB of RAM?

### Assessment

- Given a sampling rate, the student states the Nyquist limit and whether a tone will alias.
- The student explains why the 3,500 Hz tone sampled at 4,000 samples per second sounds like 500 Hz.
- The student calculates the data rate for 16 kHz, 16-bit mono audio (32,000 bytes per second)
  and explains why long sounds must be streamed instead of stored in RAM.

## References

1. [Nyquist-Shannon sampling theorem](https://en.wikipedia.org/wiki/Nyquist%E2%80%93Shannon_sampling_theorem) - Wikipedia article on the rule that a rate must be more than twice the highest frequency.
2. [Aliasing](https://en.wikipedia.org/wiki/Aliasing) - Wikipedia article explaining why undersampled signals appear at a lower frequency.
3. [Zero-order hold](https://en.wikipedia.org/wiki/Zero-order_hold) - Wikipedia article on the staircase output of a simple DAC.
4. [MicroPython I2S class](https://docs.micropython.org/en/latest/library/machine.I2S.html) - Official documentation for sending audio samples from the Pico to a DAC.
