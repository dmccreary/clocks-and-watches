# References: LED Displays and the First Digital Clock

1. [Seven-segment display](https://en.wikipedia.org/wiki/Seven-segment_display) - Wikipedia - Covers the seven-bar digit layout, segment labels, common anode and cathode types, and uses in clocks and calculators. It underpins this chapter's seven-segment display and segment pattern sections.

2. [Multiplexed display](https://en.wikipedia.org/wiki/Multiplexed_display) - Wikipedia - Explains lighting one digit at a time so persistence of vision makes all digits seem lit, saving pins. It clarifies the chapter's segment multiplexing and why driver chips help.

3. [Hitachi HD44780 LCD controller](https://en.wikipedia.org/wiki/Hitachi_HD44780_LCD_controller) - Wikipedia - Describes the controller chip behind most 16x2 character LCDs, including its pins, instruction set, and character fonts. It gives context for the chapter's character LCD and LCD1602 section.

4. Make: Electronics (3rd Edition) - Charles Platt - Make Community - Platt's "learning by discovery" method has readers run an experiment first and work out the theory afterward. That approach suits wiring and testing LEDs and segments before studying how drivers work.

5. Digital Design and Computer Architecture, RISC-V Edition - David Money Harris and Sarah L. Harris - Morgan Kaufmann - Chosen as a widely praised text; no originator is claimed. Its seven-segment decoder exercise (hex input, seven outputs) shows how digits map to segments; this attribution is moderately certain.

6. [7-segment Display Tutorial](https://www.electronics-tutorials.ws/blog/7-segment-display-tutorial.html) - Electronics Tutorials - Explains segments a through g, common anode versus common cathode wiring, and decoder chips such as the 7447. It deepens the chapter's explanation of how a digit lights.

7. [micropython-tm1637](https://github.com/mcauser/micropython-tm1637) - GitHub (mcauser) - The MicroPython driver for four-digit TM1637 modules, with numbers(), show(), brightness, and colon control. It is the library behind the chapter's TM1637 wiring and colon flashing code.

8. [Raspberry Pi Pico with I2C LCD Display (MicroPython)](https://randomnerdtutorials.com/raspberry-pi-pico-i2c-lcd-display-micropython/) - Random Nerd Tutorials - Shows wiring a 16x2 I2C LCD to the Pico, finding its 0x27 address with a scanner, and writing text. It extends the chapter's LCD1602 section with working code.

9. [neopixel - control of WS2812 / NeoPixel LEDs](https://docs.micropython.org/en/latest/library/neopixel.html) - MicroPython Documentation - Documents the NeoPixel class for addressable LEDs, including setting pixel colors and calling write(). It supports the chapter's addressable LEDs section and ring or strip clock ideas.

10. [Adafruit NeoPixel Uberguide](https://learn.adafruit.com/adafruit-neopixel-uberguide) - Adafruit Learning System - Explains WS2812 addressable LEDs, single data wire control, color order, and power limits. It adds practical wiring advice for the chapter's addressable LED and art clock projects.
