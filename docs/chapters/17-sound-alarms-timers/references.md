# References: Sound, Alarms, and Timers

1. [Pulse-width modulation](https://en.wikipedia.org/wiki/Pulse-width_modulation) - Wikipedia - Explains duty cycle and how rapidly switching a signal on and off controls average power. It underlies the chapter's PWM tone generation, where frequency sets pitch and duty cycle shapes the sound.

2. [I²S](https://en.wikipedia.org/wiki/I%C2%B2S) - Wikipedia - Describes the Inter-IC Sound bus for digital audio, with its bit clock, word select, and serial data lines carrying left and right channel samples. It supports the chapter's I2S protocol and PCM5102 sections.

3. [Sampling (signal processing)](https://en.wikipedia.org/wiki/Sampling_(signal_processing)) - Wikipedia - Explains sampling rate, the Nyquist frequency, and aliasing when a signal is measured too slowly. It gives the background for the chapter's audio sampling rate explorer and playback quality choices.

4. The Scientist and Engineer's Guide to Digital Signal Processing - Steven W. Smith - California Technical Publishing - No single author originated sampling theory; Smith's book is chosen because reviewers praise its plain-language, math-light explanations. Its chapters on ADC and DAC clarify why higher sampling rates sound better.

5. Making Embedded Systems (2nd Edition) - Elecia White - O'Reilly - White teaches firmware through reusable design patterns, such as timers and state machines for managing the flow of activity. That framing maps onto alarm, snooze, and stopwatch logic. Pattern emphasis taken from the first edition's contents.

6. [machine.PWM](https://docs.micropython.org/en/latest/library/machine.PWM.html) - MicroPython Documentation - Official reference for the PWM class, covering freq, duty_u16, and duty_ns, plus hardware limits on frequency and resolution. Students use it directly to drive a piezo buzzer at musical pitches.

7. [machine.I2S](https://docs.micropython.org/en/latest/library/machine.I2S.html) - MicroPython Documentation - Documents the I2S constructor with sck, ws, and sd pins, sampling rate, bit depth, and write() for sending audio buffers. It is the reference for playing sound through the PCM5102 DAC.

8. [time module](https://docs.micropython.org/en/latest/library/time.html) - MicroPython Documentation - Explains ticks_ms() and ticks_diff(), which handle counter wraparound safely. These functions are the basis for the chapter's elapsed time tracking, stopwatch, and countdown timer code.

9. [machine.RTC](https://docs.micropython.org/en/latest/library/machine.RTC.html) - MicroPython Documentation - Covers the RTC datetime tuple and the alarm(), alarm_left(), and irq() methods for timed events. It supports the chapter's RTC alarm feature, though hardware support varies by port.

10. [Pulse Width Modulation](https://learn.sparkfun.com/tutorials/pulse-width-modulation) - SparkFun Learn - A beginner tutorial on duty cycle with LED dimming and servo examples, showing how a digital pin can imitate analog control. It prepares students for the chapter's PWM Tone Lab.
