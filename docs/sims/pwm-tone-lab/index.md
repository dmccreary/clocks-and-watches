---
title: PWM Tone Lab
description: Change the frequency and duty cycle of a PWM square wave, see it on an oscilloscope and a piano keyboard, and hear it through the browser.
image: /sims/pwm-tone-lab/pwm-tone-lab.png
og:image: /sims/pwm-tone-lab/pwm-tone-lab.png
twitter:image: /sims/pwm-tone-lab/pwm-tone-lab.png
social:
   cards: false
quality_score: 0
---

# PWM Tone Lab

<iframe src="main.html" height="562px" width="100%" scrolling="no"></iframe>

[Run the PWM Tone Lab MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A Pico makes sound by switching a pin on and off quickly. This is **PWM** (pulse-width
modulation). Two numbers control the result:

- **Frequency** is how many on/off cycles happen each second. It sets the **pitch**.
- **Duty cycle** is the fraction of each cycle that the pin is on. It changes the
  character of the tone, but not its pitch.

The black oscilloscope shows 10 milliseconds of the signal (1 ms per grid division). The
readout above it gives the period (\( T = 1/f \)) and the on and off times. The piano
keyboard highlights the musical note closest to the frequency, and **Show formula** prints
\( f = 440 \times 2^{n/12} \) for that note, where \( n \) is the number of semitones above
or below A4.

The MicroSim opens silent. Sound starts only when you press **Play**. A browser's plain
square-wave oscillator is always 50% duty, so this MicroSim builds the tone from a custom
waveform that matches the duty cycle you choose.

## How to Use

1. Press **Play** to hear the tone, and **Stop** to silence it.
2. Drag the **Frequency** slider. Count how many cycles fit in the 10 ms window and watch
   the highlighted piano key move.
3. Use **Jump to a note** to go straight to A4, C5, and other notes.
4. Drag the **Duty cycle** slider. The cycles stay the same width while the on part grows
   or shrinks. Try 0% and 100%: the pin never switches, so there is no sound.
5. Check **Show formula** to see how the note's frequency is calculated.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/pwm-tone-lab/main.html"
        height="562px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- What a GPIO pin's high (3.3 V) and low (0 V) states mean
- Frequency measured in hertz

### Learning Objectives

Students will be able to:

- Explain that frequency sets pitch and duty cycle sets how long each cycle is on
- Calculate the period, on time and off time for a given frequency and duty cycle
- Apply \( f = 440 \times 2^{n/12} \) to find the frequency of a note

### Activities

1. **Explore** (4 min): Press **Play** and jump between A4 and A5. Read both frequencies. What
   happens to the frequency when the note goes up one octave?
2. **Calculate, then check** (6 min): At 1,000 Hz and 25% duty, calculate the period, on time and
   off time by hand. Set the sliders and compare with the readout.
3. **Listen for duty** (5 min): Keep the frequency at 440 Hz and move the duty cycle from 50% to
   10%. Does the pitch change? Describe how the sound changes. Then use the formula to predict
   the frequency of C6 (\( n = 15 \)) and check it with the note menu.

### Assessment

- The student explains why a 2,000 Hz wave shows twice as many cycles in 10 ms as a 1,000 Hz wave.
- The student calculates that a 500 Hz wave has a 2 ms period, and that 25% duty gives 0.5 ms on.
- The student uses the formula to find middle C (\( n = -9 \)): about 261.6 Hz.

## References

1. [Pulse-width modulation](https://en.wikipedia.org/wiki/Pulse-width_modulation) - Wikipedia article on PWM signals, frequency and duty cycle.
2. [Piano key frequencies](https://en.wikipedia.org/wiki/Piano_key_frequencies) - Wikipedia table and formula for the frequency of every note relative to A440.
3. [MicroPython PWM class](https://docs.micropython.org/en/latest/library/machine.PWM.html) - Official documentation for `freq()` and `duty_u16()` on the Pico.
4. [OscillatorNode (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/OscillatorNode) - How the browser's Web Audio API generates the tone you hear.
