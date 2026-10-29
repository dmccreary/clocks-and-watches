---
title: Byte Bit Explorer
description: Toggle the eight bits of a byte, apply set, clear and shift operations, predict the result, and watch the byte go onto a wire MSB-first or LSB-first.
image: /sims/byte-bit-explorer/byte-bit-explorer.png
og:image: /sims/byte-bit-explorer/byte-bit-explorer.png
twitter:image: /sims/byte-bit-explorer/byte-bit-explorer.png
social:
   cards: false
quality_score: 0
---

# Byte Bit Explorer

<iframe src="main.html" height="472px" width="100%" scrolling="no"></iframe>

[Run the Byte Bit Explorer MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

Everything a bus carries is a stream of bytes, and each byte is eight bits. The eight boxes at the
top are the bits of one byte, worth 128 down to 1. Click a box to flip that bit, and the decimal,
hex and binary readouts update instantly.

The buttons apply the same operations as the Python code in Chapter 8. The line under the
readouts shows the code for the last operation and the value before and after:

| Button | Python |
|--------|--------|
| Set bit | `x = x | (1 << n)` |
| Clear bit | `x = x & ~(1 << n)` |
| Shift left | `x = (x << 1) & 0xFF` |
| Shift right | `x = x >> 1` |

The lower panel shows the byte as a **data wire**: high for a 1, low for a 0, with time running
left to right. Switch between **MSB first** and **LSB first** to see the same byte sent in the
opposite order, and press **Send byte** to watch the bits leave one at a time.

In **Predict mode**, the result of each operation is hidden until you type the new decimal value
and press **Check**.

## How to Use

1. Click bit boxes to build a byte. Try to make 60 (0x3C), the OLED's I2C address.
2. Choose a bit with the **bit** dropdown and press **Set bit** or **Clear bit**.
3. Press **Shift left** a few times. What happens to the value each time? What happens to bit 7?
4. Change the order to **LSB first** and press **Send byte**. Compare the order of bits on the wire.
5. Turn on **Predict mode**, pick an operation, type your answer and press **Check**.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/byte-bit-explorer/main.html"
        height="472px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- Binary and hexadecimal numbers (Chapter 8)
- Python integers and variables

### Learning Objectives

Students will be able to:

- Apply set, clear and shift operations to a byte and state the new value
- Convert a byte between decimal, hexadecimal and binary
- Predict the order in which bits appear on the wire for MSB-first and LSB-first

### Activities

1. **Build the addresses** (4 min): Use the bit boxes to build 0x3C, 0x68 and 0x76. Record which bits are set for each.
2. **Predict mode practice** (6 min): Turn on Predict mode and complete five operations in a row correctly, including at least one shift that drops a bit off the end.
3. **Scrambled byte** (5 min): Send 0xC1 MSB first and LSB first. Explain what value a receiver expecting MSB first would read if the sender used LSB first.

### Assessment

- The student predicts that shift left doubles the value until bit 7 falls off.
- The student writes the Python expression to set or clear a given bit.
- The student explains why sender and receiver must agree on bit order.

## References

1. [Bitwise operation](https://en.wikipedia.org/wiki/Bitwise_operation) - Wikipedia article on AND, OR, XOR and shifts.
2. [Bit numbering](https://en.wikipedia.org/wiki/Bit_numbering) - Wikipedia article on MSB, LSB and bit order.
3. [Hexadecimal](https://en.wikipedia.org/wiki/Hexadecimal) - Wikipedia article on base 16 and why one hex digit is four bits.
4. [Python bitwise operators](https://docs.python.org/3/reference/expressions.html#binary-bitwise-operations) - Official Python documentation for &, | and ^.
