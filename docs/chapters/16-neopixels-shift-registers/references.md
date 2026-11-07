# References: NeoPixels and Shift Register Clocks

1. [Shift register](https://en.wikipedia.org/wiki/Shift_register) - Wikipedia - Explains how chained flip-flops move bits one stage per clock pulse, including serial-in parallel-out designs. It underpins the 74HC595 and the chapter's serial-to-parallel conversion and chaining ideas.

2. [HSL and HSV](https://en.wikipedia.org/wiki/HSL_and_HSV) - Wikipedia - Describes the hue, saturation, and value color model as a cylindrical rearrangement of RGB, with conversion formulas. It explains why the chapter's color wheel makes rainbow animations on NeoPixels easy to program.

3. [Binary clock](https://en.wikipedia.org/wiki/Binary_clock) - Wikipedia - Surveys clocks that show time as binary-coded decimal or other binary patterns of lit and unlit lamps. It directly supports the chapter's binary clock project built from individually addressable LEDs.

4. Make: Electronics (2nd Edition) - Charles Platt - Make Community - Platt's learning-by-discovery method has readers build experiments first, including deliberately overheating an LED, before meeting the theory. That hands-on sequence makes current limits and the LED power budget memorable for beginners.

5. Digital Design and Computer Architecture (2nd Edition) - David Money Harris and Sarah L. Harris - Morgan Kaufmann - No single author originated shift registers; this widely used course text builds registers from flip-flops, which clarifies how a latch pin freezes bits. Section placement not independently verified.

6. [Adafruit NeoPixel Uberguide](https://learn.adafruit.com/adafruit-neopixel-uberguide) - Adafruit Learning System - Covers NeoPixel basics: single-wire control, chaining pixels, color order, and limits on strip length from memory, power, and update time. It supports the chapter's wiring and strip-type sections.

7. [neopixel module documentation](https://docs.micropython.org/en/latest/library/neopixel.html) - MicroPython Documentation - Official reference for the NeoPixel class used in the chapter, including fill(), indexed pixel assignment with color tuples, and write(), plus a short example. It is available on the RP2 port for the Pico.

8. [Digital Logic Shift Registers](https://www.electronics-tutorials.ws/sequential/seq_5.html) - Electronics Tutorials - Walks through serial-in parallel-out shifting with a 4-bit example and a clock-pulse table showing a bit travelling across the register. It reinforces the chapter's serial-to-parallel conversion explanation.

9. [Shift Registers](https://learn.sparkfun.com/tutorials/shift-registers) - SparkFun Learn - Introduces serial-in parallel-out and parallel-in serial-out chips for adding inputs or outputs, and shows daisy-chaining one register's serial output into the next. It supports the chapter's shift register chaining section.

10. [Adafruit Arduino Lesson 4: Eight LEDs](https://learn.adafruit.com/adafruit-arduino-lesson-4-eight-leds) - Adafruit Learning System - Shows the 74HC595 acting as a serial-to-parallel converter to drive eight LEDs from three control pins, and compares its speed with direct pin control. It matches the chapter's 74HC595 section.
