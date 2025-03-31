# TM1650

Based on your files, I can see you're working with a four-digit seven-segment display that uses direct digit addressing with I2C addresses 0x34, 0x35, 0x36, and 0x37. This appears to be a TM1650 display module. Let me search for more information about similar drivers and displays.

Based on your files and my search results, I can provide some information about your TM1650 display and similar drivers.

## Display Type

The display you're working with is a TM1650-based four-digit seven-segment display. The TM1650 is a dedicated LED driver circuit with a keypad scan interface manufactured by Titan Micro Electronics. It uses I2C-like communication (though not standard I2C) and features direct digit addressing via specific registers.

## Direct Addressing Approach

Your code in `tm1650-test-36.py` shows the direct addressing method with the following registers:
- Display addresses: `0x24, 0x25, 0x26, 0x27` (for setting segment patterns)
- Control addresses: `0x34, 0x35, 0x36, 0x37` (for actual digit control)

This approach is confirmed in one of the libraries I found. The TM1650 uses `0x24` as the control register base address and `0x34` as the display base address, with 4 segments total.

## Similar Drivers

While there are several MicroPython libraries for TM1650 displays, most use a different approach than your direct addressing method. Here are some examples:

1. **stonatm/tm1650_micropython** - A library for DFRobot TM1650 displays that uses a more abstracted API with methods like `display_integer()` rather than direct register addressing. This library offers simple methods like `on()`, `display_integer()`, and `display_clear()`.

2. **shaoziyang/microbit-lib** - Another implementation that provides an interface for Four Digit Display modules with TM1650 chips. It includes functionality for controlling display intensity and showing/hiding decimal points.

3. **maxint-rd/TM16xx** - A more comprehensive Arduino library that supports multiple TM16xx family chips including the TM1650. This library enables using print() on 7-segment displays and supports the TM1650 in both 8x4 or 7x4 display modes.

4. **arkhipenko/TM1650** - An Arduino library specifically for TM1650 displays, which might contain implementations you could adapt to MicroPython.

## Key Findings

1. Your approach using direct register addressing (0x34-0x37) for digit control is valid and confirmed in other implementations.

2. Many libraries use a higher-level abstraction rather than direct register manipulation.

3. The TM1650 communication protocol resembles I2C but lacks standard addressing, which is why most libraries implement their own bit-banging approach rather than using the standard I2C/Wire libraries.

4. Your test code is exploring an approach that writes patterns to display addresses (0x24-0x27) and then activates them via control addresses (0x34-0x37), which is consistent with how the TM1650 chip is designed to work.

If you'd like me to help you develop a more comprehensive driver based on your direct addressing approach, I'd be happy to assist with that.