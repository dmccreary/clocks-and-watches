# References: Real-Time Clocks and the DS3231

1. [Real-time clock](https://en.wikipedia.org/wiki/Real-time_clock) - Wikipedia - Explains how a dedicated timekeeping chip with a crystal oscillator and backup battery keeps the date and time when main power is off. It frames why the DS3231 is added to the Pico.

2. [Binary-coded decimal](https://en.wikipedia.org/wiki/Binary-coded_decimal) - Wikipedia - Describes how each decimal digit is stored in four bits, including the packed form. It explains why the DS3231 registers need conversion code when reading or setting hours, minutes, and seconds.

3. [Accuracy and precision](https://en.wikipedia.org/wiki/Accuracy_and_precision) - Wikipedia - Distinguishes closeness to the true value from consistency of repeated measurements, with target-style diagrams. It supports the chapter's clock accuracy and clock precision sections and its accuracy versus precision targets.

4. An Introduction to Error Analysis (2nd Edition) - John R. Taylor - University Science Books - Taylor teaches measurement uncertainty through everyday examples and worked problems for beginners. This helps students reason about drift and how far a clock can be off. This is a widely praised choice, not a claim of origination.

5. The Art of Electronics (3rd Edition) - Paul Horowitz and Winfield Hill - Cambridge University Press - No single author originated crystal timing, so this is chosen as the most praised practical electronics text, with a hands-on style that helps explain oscillators, crystals, and I2C chips like the DS3231.

6. [Adafruit DS3231 Precision RTC Breakout](https://learn.adafruit.com/adafruit-ds3231-precision-rtc-breakout) - Adafruit Learning System - Covers the DS3231's temperature-compensated crystal, its roughly one minute per year accuracy, coin cell backup, and I2C wiring. It maps closely to this chapter's hardware sections.

7. [Raspberry Pi Pico: DS3231 RTC, Get Time and Set Alarms (MicroPython)](https://randomnerdtutorials.com/raspberry-pi-pico-ds3231-rtc-micropython/) - Random Nerd Tutorials - Shows wiring a DS3231 to the Pico, the 0x68 I2C address, setting the time from a tuple, reading temperature, and using alarms. Direct hands-on practice for this chapter.

8. [machine.RTC](https://docs.micropython.org/en/latest/library/machine.RTC.html) - MicroPython Documentation - Documents the built-in RTC class, including datetime for reading and setting time and alarm functions. Students use it to compare the Pico's internal clock with the external DS3231.

9. [machine.I2C](https://docs.micropython.org/en/latest/library/machine.I2C.html) - MicroPython Documentation - Explains scan, readfrom_mem, and writeto_mem, the calls used to find the DS3231 address and read or write its registers. It underpins the register map and BCD exercises.

10. [Time and Frequency from A to Z: St to Sy](https://www.nist.gov/time-and-frequency-services/time-and-frequency-z-st-sy) - NIST - A glossary from the national timekeeping lab defining stability as how steadily an oscillator holds one frequency, regardless of whether it is correct. It sharpens the chapter's accuracy and precision discussion.
