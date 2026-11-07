---
title: DS3231 Register Map
description: An interactive map of the DS3231 real-time clock registers 0x00 to 0x12 showing each byte in hex, binary, and decoded form, with bit-field details, live BCD values, and a decoding quiz.
image: /sims/ds3231-register-map/ds3231-register-map.png
og:image: /sims/ds3231-register-map/ds3231-register-map.png
twitter:image: /sims/ds3231-register-map/ds3231-register-map.png
social:
   cards: false
quality_score: 100
---

# DS3231 Register Map

<iframe src="main.html" height="612px" width="100%" scrolling="no"></iframe>

[Run the DS3231 Register Map MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

The DS3231 keeps everything it knows in 19 numbered storage slots called **registers**, at addresses `0x00` to `0x12`. Your program reads the time by asking for the bytes in registers `0x00` to `0x06`, and it sets the time by writing new bytes there.

This MicroSim lists every register as a row. Each row shows:

- the register **address** and its **field** name,
- the raw byte in **hex** and in **binary**,
- what the byte **means** once it is decoded.

The colored band on the left of each row shows the register's group: **time** (blue), **alarms** (orange), **control and status** (purple), and **temperature** (pink). The opening values match the example in Chapter 13: `i2c.readfrom_mem(0x68, 0x00, 7)` returned `[48, 5, 20, 1, 40, 9, 38]`, which in hex is `0x30 0x05 0x14 0x01 0x28 0x09 0x26`, or 14:05:30 on Monday, September 28, 2026.

Most time registers use **BCD**, so `0x30` means thirty seconds, not forty-eight. Some registers mix BCD digits with control bits, which is why the chapter code masks the hours with `& 0x3F` and the month with `& 0x1F`. The temperature registers are not BCD at all; they hold a signed number.

## How to Use

1. **Hover** over any row to see the field name and its allowed range below the table.
2. **Click** a row to open its bit panel. The panel shows all eight bits, groups them into fields such as "10 Seconds" and "Seconds," and explains what the register does. Click the row again, or anywhere else, to close it.
3. Check **Live values** to fill the time registers from your computer's clock, encoded in BCD the way the DS3231 would store them. Watch the seconds byte count `0x58`, `0x59`, `0x00`.
4. Press **Quiz me**. One time register shows a random raw byte in red. Type the decoded decimal value in the **answer** box and press **Check**.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/ds3231-register-map/main.html"
        height="612px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objective

Students will identify which register holds each time field and interpret raw register bytes (Bloom: Remembering, Understanding).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- I2C addresses and `readfrom_mem()` (Chapters 8 and 13)
- Hexadecimal and binary numbers (Chapter 8)
- BCD encoding (Chapter 13)

### Activities

1. **Locate** (3 min): Without the MicroSim, students write down which register they think holds the minutes and which holds the year. Then they check by hovering.
2. **Decode the example** (4 min): Students click the Seconds, Hours, and Month rows and explain, using the bit panel, why each byte decodes the way it does. Why does the Hours register need `& 0x3F`?
3. **Watch it live** (3 min): With **Live values** on, students compare the hex bytes with the time on their computer and explain why the hex digits look just like the decimal time.
4. **Quiz** (5 min): Students use **Quiz me** until they get five right in a row. Then they click the Temperature MSB and LSB rows and compute the temperature from `0x19` and `0x40`.

### Assessment

- Which register would you read to find the day of the month? (`0x04`.)
- The minutes register reads `0x47`. What time field and value is that? (47 minutes.)
- The Status register reads `0x88`. What does bit 7 (OSF) tell you, and what should your program do? (The oscillator stopped at some point, so the time may be wrong and should be set again.)
- Explain why reading seven bytes starting at `0x00` gives you the complete date and time in one I2C transaction.

## References

1. [DS3231 Datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/DS3231.pdf) - Analog Devices; Figure 1 is the full timekeeping register map used here.
2. [Binary-coded decimal](https://en.wikipedia.org/wiki/Binary-coded_decimal) - Wikipedia overview of BCD.
3. [Processor register](https://en.wikipedia.org/wiki/Processor_register) - Wikipedia background on what a register is.
4. [MicroPython machine.I2C](https://docs.micropython.org/en/latest/library/machine.I2C.html) - Documentation for `readfrom_mem()` and `writeto_mem()`.
