# Quiz: Communication Buses: I2C, SPI, and UART

Test your understanding of I2C, SPI, UART, bit ordering, and signal integrity with these review questions.

---

#### 1. What is the typical I2C address of an SSD1306 OLED display?

<div class="upper-alpha" markdown>
1. `0x68`
2. `0x76`
3. `0x57`
4. `0x3C`
</div>

??? question "Show Answer"
    The correct answer is **D**. An SSD1306 OLED normally answers at `0x3C`, which is 60 in decimal. The DS3231 real-time clock uses `0x68`, the memory chip on RTC boards uses `0x57`, and the BME280 temperature sensor uses `0x76`. Every I2C message starts with the 7-bit address, and only the matching device pays attention to the rest of it.

    **Concept Tested:** I2C Device Addressing

    **See:** [I2C Device Addressing](index.md#i2c-device-addressing)

---

#### 2. Which bit of a byte is the MSB?

<div class="upper-alpha" markdown>
1. The rightmost bit, which is worth 1
2. The leftmost bit, which is worth 128
3. The middle bit, which is worth 16
4. Whichever bit currently holds a 1
</div>

??? question "Show Answer"
    The correct answer is **B**. The most significant bit is the leftmost bit of a byte and is worth 128, while the least significant bit is the rightmost and is worth 1. In `0b10110001` both the MSB and the LSB happen to be 1. Changing the MSB changes the value the most, and changing the LSB changes it the least. Bit ordering decides which of the two goes onto the wire first.

    **Concept Tested:** MSB and LSB

    **See:** [MSB and LSB](index.md#msb-and-lsb)

---

#### 3. Why do I2C lines need pull-up resistors?

<div class="upper-alpha" markdown>
1. Devices can only pull a wire down, so the resistors return it to 3.3 V
2. They slow the clock so that devices at different speeds stay in step
3. They give every device on the bus its own unique 7-bit address
4. They convert the 3.3 V signals into 5 V signals for the peripherals
</div>

??? question "Show Answer"
    The correct answer is **A**. I2C lines are open-drain, meaning a device can pull a wire down to ground but never push it up. The pull-up resistors, commonly 4.7 kΩ, bring the wire back to 3.3 V. Most hobbyist modules already include them. The Pico's internal pull-ups of about 50 kΩ are too weak for reliable 400 kHz operation, so a missing pull-up is a prime suspect when a bus fails.

    **Concept Tested:** I2C Pull-Up Resistors

    **See:** [I2C Pull-Up Resistors](index.md#i2c-pull-up-resistors)

---

#### 4. How does SPI make sure only one peripheral listens when several share the same clock and data wires?

<div class="upper-alpha" markdown>
1. Each peripheral is given a unique 7-bit address at the start of every message
2. The controller changes the baudrate to a different value for each peripheral
3. The controller pulls one device's chip select low while the others stay high
4. Each peripheral takes turns based on the order in which it was plugged in
</div>

??? question "Show Answer"
    The correct answer is **C**. SPI has no addresses. Each peripheral gets its own chip select (CS) wire. The controller pulls CS low to wake one device, and the devices whose CS stays high ignore the traffic. After the transfer, CS goes back high. This is why SPI needs one extra pin per device, while I2C devices share the same two signal wires.

    **Concept Tested:** SPI Chip Select

    **See:** [SPI Chip Select](index.md#spi-chip-select)

---

#### 5. Why must a round color display use SPI instead of I2C?

<div class="upper-alpha" markdown>
1. I2C cannot carry color information on its two wires
2. SPI uses fewer wires than I2C and so costs less
3. Color displays have no I2C address, so the controller cannot find them
4. SPI moves far more data per second, sending a 240 by 240 frame in about 23 ms
</div>

??? question "Show Answer"
    The correct answer is **D**. A 240 by 240 frame at 2 bytes per pixel is 115,200 bytes. At 40 MHz SPI that takes about 23 ms, but over I2C at 400 kHz it takes about 2.6 seconds, far too slow for animation. Small monochrome OLEDs have only 1,024 bytes to send, so I2C is fast enough for them. Speed, not color support or wire count, is the deciding factor.

    **Concept Tested:** Bus Speed Comparison

    **See:** [Bus Speed Comparison](index.md#bus-speed-comparison)

---

#### 6. How should a Pico be connected to a GPS module over UART?

<div class="upper-alpha" markdown>
1. Pico TX to the module's RX, and Pico RX to the module's TX
2. Pico TX to the module's TX, and Pico RX to the module's RX
3. Pico TX and RX both to the module's single data pin
4. Pico TX to the module's clock pin, and Pico RX to ground
</div>

??? question "Show Answer"
    The correct answer is **A**. UART uses two data wires, TX and RX, and the connection is crossed so that what one side transmits, the other receives. UART has no clock wire, so both ends must also agree in advance on a baud rate such as 9600 or 115200 bits per second. Connecting TX to TX leaves both devices talking and nobody listening.

    **Concept Tested:** UART Protocol

    **See:** [UART Protocol](index.md#uart-protocol)

---

#### 7. Which line sets bit 5 of the byte `x` without changing any of the other bits?

<div class="upper-alpha" markdown>
1. `x = x & (1 << 5)`
2. `x = x | (1 << 5)`
3. `x = x ^ 0xFF`
4. `x = x >> 5`
</div>

??? question "Show Answer"
    The correct answer is **B**. The expression `1 << 5` makes a byte with only bit 5 set. OR-ing it with `x` turns that bit on and leaves every other bit as it was. The AND in option A would clear every other bit, XOR with `0xFF` flips all eight bits, and shifting right by 5 moves the whole byte instead of changing a single bit. Use `x & ~(1 << 5)` to clear a bit.

    **Concept Tested:** Byte and Bit Operations

    **See:** [Byte and Bit Operations](index.md#byte-and-bit-operations)

---

#### 8. In what order do the bits of `0xC1` (`0b11000001`) appear on the wire when sent LSB first?

<div class="upper-alpha" markdown>
1. 1 1 0 0 0 0 0 1
2. 0 0 0 0 0 1 1 1
3. 1 0 0 0 0 0 1 1
4. 1 1 1 0 0 0 0 0
</div>

??? question "Show Answer"
    The correct answer is **C**. LSB-first order sends the rightmost bit first and the leftmost bit last, so the byte 11000001 is read from right to left as 1 0 0 0 0 0 1 1. Option A is the MSB-first order. Sender and receiver must agree on the order or every byte arrives scrambled. Most SPI displays use MSB first, which is the MicroPython default.

    **Concept Tested:** Bit Ordering

    **See:** [Bit Ordering](index.md#bit-ordering)

---

#### 9. An OLED and a DS3231 clock chip are both wired to the same SDA and SCL pins, but the scanner shows only `[60]`. What does this most strongly suggest?

<div class="upper-alpha" markdown>
1. The Pico's I2C pins are damaged and cannot find any device
2. The bus works, so the fault is in the clock chip's own power or wiring
3. Both devices use address 60, so the scanner lists them once
4. The scanner can detect only one device on a bus at a time
</div>

??? question "Show Answer"
    The correct answer is **B**. The OLED at `0x3C` (60) answered, which proves the Pico's pins, the shared wires, and the pull-ups all work. The DS3231 should appear at `0x68` (104), so the problem is specific to that module: its power, its ground, or its own SDA and SCL connections. The scanner lists every address that answers, and two devices with the same address would conflict, not merge.

    **Concept Tested:** I2C Scanner

    **See:** [I2C Scanner](index.md#i2c-scanner)

---

#### 10. A color display shows flickering pixels when the SPI baudrate is 40 MHz and 30 cm jumper wires are used. What is the best first step?

<div class="upper-alpha" markdown>
1. Add I2C pull-up resistors to the SPI clock and data wires
2. Switch the byte order from MSB first to LSB first
3. Hold the chip select wire low permanently to keep the display awake
4. Lower the baudrate and shorten the signal wires
</div>

??? question "Show Answer"
    The correct answer is **D**. Long wires, loose connections, and very high speeds distort the signal edges, so the receiver may read a 0 as a 1. Shortening the wires and lowering the baudrate are the simplest fixes for signal integrity. Also check that grounds are shared and add a 0.1 µF capacitor near the chip's power pins. Pull-ups belong to I2C, and a wrong bit order would scramble the image rather than make pixels flicker.

    **Concept Tested:** Signal Integrity

    **See:** [Signal Integrity](index.md#signal-integrity)
