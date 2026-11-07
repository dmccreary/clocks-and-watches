---
title: BCD Converter
description: Compare ordinary binary with BCD for the numbers 0 to 59, decode raw RTC register bytes, see the read-as-integer mistake, and practice encoding numbers as BCD bytes.
image: /sims/bcd-converter/bcd-converter.png
og:image: /sims/bcd-converter/bcd-converter.png
twitter:image: /sims/bcd-converter/bcd-converter.png
social:
   cards: false
quality_score: 100
---

# BCD Converter

<iframe src="main.html" height="537px" width="100%" scrolling="no"></iframe>

[Run the BCD Converter MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/bcd-converter/main.html"
        height="537px"
        width="100%"
        scrolling="no"></iframe>
```

## About This MicroSim

The DS3231 real-time clock stores seconds, minutes, and hours in **BCD** (binary-coded decimal). BCD gives each decimal digit its own four-bit **nibble**: the tens digit goes in the high nibble and the ones digit goes in the low nibble. Ordinary binary stores the whole number as one pattern instead.

This MicroSim shows the same number both ways, one above the other:

- The **Regular binary** row uses the place values 128, 64, 32, 16, 8, 4, 2, 1.
- The **BCD** row uses 80, 40, 20, 10 for the tens nibble (purple) and 8, 4, 2, 1 for the ones nibble (green).

Below the bit lights, the panel shows both bytes in binary and hex, plus the two MicroPython conversion functions from Chapter 13 with the current numbers filled in:

```python
def bcd_to_dec(b):
    return (b >> 4) * 10 + (b & 0x0F)

def dec_to_bcd(d):
    return ((d // 10) << 4) | (d % 10)
```

## How to Use

1. Drag the **Number** slider from 0 to 59. Notice that the BCD byte in hex always looks like the decimal number (45 becomes `0x45`), while the binary byte does not (45 is `0x2D`).
2. Type a raw register byte in the **BCD byte: 0x** box, such as `30`, the seconds byte from the chapter. The MicroSim decodes it as BCD and moves the slider. Try `4A` to see why it is not valid BCD.
3. Check **Read BCD byte as integer** to see the classic bug: `0x45` read as an ordinary integer is 69, not 45. The panel shows the fix.
4. Press **Predict** to get a random number. The BCD row turns into question marks. Type the BCD byte in hex in the **Answer** box and press **Check**. Press **Exit Predict** to leave the mode.

## Lesson Plan

### Learning Objective

Students will apply BCD encoding and decoding and compare it with ordinary binary (Bloom: Applying, Analyzing).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Binary place values and hexadecimal (Chapter 8)
- The shift (`>>`, `<<`) and mask (`&`, `|`) operators (Chapter 8)
- The DS3231 time registers (Chapter 13)

### Activities

1. **Compare** (4 min): Students set the slider to 9, 10, 30, and 59 and record the binary and BCD bytes in a table. At which number do the two rows first differ? (10.)
2. **Decode** (4 min): Students type the bytes `0x27`, `0x30`, and `0x59` in the hex box and predict the decoded value before they press anything else.
3. **Find the bug** (3 min): With **Read BCD byte as integer** checked, students explain why the clock in the chapter printed 48 seconds when the time was really 30.
4. **Practice** (4 min): Students use **Predict** mode until they get five correct answers in a row.

### Assessment

- Convert 38 to BCD by hand and give the answer in hex. (`0x38`, binary `0011 1000`.)
- A seconds register reads `0x52`. What is the actual number of seconds? (52.)
- Explain why `0x5A` can never appear in a DS3231 seconds register.
- Compare: how many of the eight bits does BCD actually need to store 0 to 59, and how many does ordinary binary need? (7 versus 6.)

## References

1. [Binary-coded decimal](https://en.wikipedia.org/wiki/Binary-coded_decimal) - Wikipedia overview of BCD and its uses in clocks and calculators.
2. [DS3231 Datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/DS3231.pdf) - Analog Devices; Figure 1 shows the BCD layout of every time register.
3. [Nibble](https://en.wikipedia.org/wiki/Nibble) - Wikipedia article on four-bit groups.
4. [Bitwise operation](https://en.wikipedia.org/wiki/Bitwise_operation) - Wikipedia; explains the shifts and masks used by the conversion functions.
