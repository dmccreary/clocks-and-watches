# References: Buttons, Interrupts, and State Machines

1. [Finite-state machine](https://en.wikipedia.org/wiki/Finite-state_machine) - Wikipedia - Defines states, transitions, and inputs, with state diagrams and examples. It gives the formal vocabulary behind the chapter's clock mode state machine and run, set hour, and set minute cycling.

2. [Interrupt](https://en.wikipedia.org/wiki/Interrupt) - Wikipedia - Explains how a hardware signal pauses normal code so a handler can respond at once. It provides the background for this chapter's interrupt handlers, callbacks, and falling-edge triggers on button pins.

3. [Rotary encoder](https://en.wikipedia.org/wiki/Rotary_encoder) - Wikipedia - Describes incremental encoders and their two-channel quadrature signals, which reveal rotation direction. It supports the chapter's encoder direction logic and the knob used to set the time.

4. Practical UML Statecharts in C/C++ (2nd Edition) - Miro Samek - Newnes (Elsevier) - Samek teaches state machines as event-driven code, building from basic automata to hierarchical statecharts with a small framework. It shows how a mode-cycling clock can be organized cleanly.

5. The Art of Designing Embedded Systems (2nd Edition) - Jack Ganssle - Newnes (Elsevier) - Ganssle, known for documenting real switch bounce on an oscilloscope, covers debouncing and its firmware implications. This book is chosen as the clearest practical treatment of why buttons chatter.

6. [A Guide to Debouncing](https://www.ganssle.com/debouncing.htm) - The Ganssle Group - Presents oscilloscope captures showing how real switches bounce for varying times, plus the reasoning behind fixing it. It is a vivid companion to the chapter's bounce oscilloscope diagram and software debounce.

7. [Writing interrupt handlers](https://docs.micropython.org/en/latest/reference/isr_rules.html) - MicroPython Documentation - Official guidance on keeping handlers short, avoiding memory allocation, and sharing data safely with the main loop. It applies directly to the chapter's button callbacks and flag-based design.

8. [Getting Started with Rotary Encoders: Examples with Raspberry Pi Pico](https://core-electronics.com.au/guides/getting-started-with-rotary-encoders-examples-with-raspberry-pi-pico/) - Core Electronics - Walks through wiring an encoder to Pico pins and reading its turns in MicroPython, including how swapping the A and B pins reverses direction.

9. [Button and Switch Basics](https://learn.sparkfun.com/tutorials/button-and-switch-basics) - SparkFun Learn - Covers switch types, poles and throws, and pull-up resistors that keep an input at a known level. It reinforces the chapter's push button wiring between a GPIO pin and ground.

10. [Sequential Logic: SR Flip-flop](https://www.electronics-tutorials.ws/sequential/seq_1.html) - Electronics Tutorials - Includes a hardware switch debouncing circuit built from an SR latch. It shows one way to clean a bouncing contact before the signal reaches the microcontroller, as in the chapter's hardware debounce section.
