---
title: Communication Buses: I2C, SPI, and UART
description: I2C, SPI, and UART: how chips communicate, with pins, addressing, speed, bit ordering, and signal integrity.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:36:05
version: 1.10
---

# Communication Buses: I2C, SPI, and UART

## Summary

Students compare I2C and SPI wiring, addressing, and speed, and use an I2C scanner to find devices. They learn bit ordering and data packets. After this chapter they can choose and wire the right bus for a display or sensor.

## Concepts Covered

This chapter covers the following 23 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| I2C SDA Pin | 119 |
| I2C SCL Pin | 119 |
| SPI Clock Pin | 43 |
| SPI Data Pin | 43 |
| UART Protocol | 6 |
| I2C Bus | 118 |
| SPI Bus | 42 |
| Byte and Bit Operations | 11 |
| I2C Device Addressing | 13 |
| I2C Pull-Up Resistors | 1 |
| I2C Bus Speed | 1 |
| SPI Chip Select | 1 |
| SPI DC Pin | 1 |
| SPI Reset Pin | 1 |
| SPI Baudrate | 15 |
| Bus Speed Comparison | 1 |
| Bit Ordering | 3 |
| Clock Polarity | 1 |
| I2C Scanner | 11 |
| Signal Integrity | 3 |
| Data Packet Structure | 1 |
| MSB and LSB | 1 |
| Crosstalk | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Computational Thinking and Physical Computing](../01-foundations/index.md)
- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)
- [Chapter 5: The Pico Platform: Pins, Files, and Firmware](../05-pico-platform/index.md)

---

!!! mascot-welcome "How Chips Talk to Each Other"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Displays, clock chips, and sensors all need to trade messages with your Pico, and this chapter shows you the two main languages they use. Learn I2C and SPI and you can plug in almost any chip you find. Let's make time tick!

## Why We Need a Bus

Your Pico has only 26 usable pins, but a clock project might include a display, a real-time clock chip, and a temperature sensor. Connecting every chip with its own bundle of wires would use up the pins in no time. The solution is a **bus**: a small set of shared wires that many chips use to exchange data.

Buses send information **serially**, meaning one bit after another on a single wire, rather than in parallel on eight wires at once. Serial buses need few wires, which keeps circuits simple. This chapter covers the three you will use most:

| Bus | Wires | Speed | Best for |
|-----|-------|-------|----------|
| I2C | 2 (plus power) | Moderate | Many slow devices: small OLEDs, RTC chips, sensors |
| SPI | 4 or more | Fast | Displays and memory |
| UART | 2 | Slow | Serial text, GPS, debugging |

## Byte and Bit Operations

Before looking at any bus, you need to know what travels on it. A **bit** is a single 0 or 1. A **byte** is a group of 8 bits and can hold a value from 0 to 255. Everything a bus carries is a stream of bytes.

Programmers write byte values in **hexadecimal** (base 16), using digits 0 to 9 and letters A to F, with the prefix `0x`. Hex is compact because one hex digit equals exactly four bits:

| Decimal | Binary | Hex |
|---------|--------|-----|
| 10 | `0b00001010` | `0x0A` |
| 60 | `0b00111100` | `0x3C` |
| 104 | `0b01101000` | `0x68` |
| 255 | `0b11111111` | `0xFF` |

You will often need to look at or change individual bits. Python has **bitwise operators** for that:

| Operator | Name | Example | Result |
|----------|------|---------|--------|
| `&` | AND | `0b1100 & 0b1010` | `0b1000` |
| `|` | OR | `0b1100 | 0b1010` | `0b1110` |
| `^` | XOR | `0b1100 ^ 0b1010` | `0b0110` |
| `<<` | Shift left | `1 << 3` | `0b1000` (8) |
| `>>` | Shift right | `0b1000 >> 3` | `1` |

Three patterns cover most needs. Here `x` is a byte and `n` is a bit position counted from 0 on the right:

```python
x = 0b00000000
x = x | (1 << 3)        # set bit 3      -> 0b00001000
x = x & ~(1 << 3)       # clear bit 3    -> 0b00000000
is_set = (x >> 3) & 1   # test bit 3     -> 0 or 1
```

MicroPython also has `bytes` and `bytearray` types for holding sequences of bytes, such as `bytes([0x00, 0xFF, 0x3C])`.

### MSB and LSB

The **MSB** (most significant bit) is the leftmost bit of a byte, worth 128, and the **LSB** (least significant bit) is the rightmost, worth 1. In `0b10110001` the MSB is 1 and the LSB is also 1. Changing the MSB changes the value the most, and changing the LSB changes it the least.

### Bit Ordering

**Bit ordering** is the choice of which bit goes onto the wire first. In **MSB-first** order the leftmost bit is sent first; in **LSB-first** order the rightmost goes first. Sending `0xC1` (`0b11000001`) looks like this:

| Order | Bits on the wire, first to last |
|-------|--------------------------------|
| MSB first | 1 1 0 0 0 0 0 1 |
| LSB first | 1 0 0 0 0 0 1 1 |

Sender and receiver must agree on the order or every byte will arrive scrambled. Most SPI displays use MSB first, which is the MicroPython default.

#### Diagram: Byte Bit Explorer

<details markdown="1">
<summary>Byte Bit Explorer</summary>
Type: MicroSim
**sim-id:** byte-bit-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* bit operations and *predict* how MSB-first and LSB-first ordering changes a transmission (Bloom: Applying).

**Visual elements:** Eight clickable bit boxes (labeled 128 down to 1) with a live decimal, hex, and binary readout. Below, a serial wire animation sends the byte bit by bit.

**Controls:** Click bits to toggle them; buttons for "Set bit," "Clear bit," and "Shift left/right"; a toggle "MSB first / LSB first" reorders the animation; a "Predict" mode asks the student to type the resulting value after an operation.

**Responsive design:** Bit boxes shrink to fit the container width.

Implementation: p5.js with integer bit math.
</details>

## The I2C Bus

**I2C** (Inter-Integrated Circuit, pronounced "I squared C") is a two-wire bus invented in the 1980s that lets one **controller** talk to many **peripheral** devices. The controller is the Pico, and it starts every conversation. Peripherals such as an OLED display or a clock chip only answer when they are spoken to.

An I2C connection has four wires: power, ground, and two signal wires. Every device is wired to the *same* two signal wires, so adding a device costs no extra pins.

### I2C Data Pin (SDA)

**SDA** (serial data) is the wire that carries the actual bytes. It is **bidirectional**: the controller sends data on it, and a peripheral answers on the same wire. Only one side speaks at a time.

### I2C Clock Pin (SCL)

**SCL** (serial clock) is the wire that carries the timing pulses. The controller generates them, and data on SDA is read on each pulse. Because the clock comes from the controller, the devices never fall out of step with each other.

The Pico has two I2C peripherals, **I2C0** and **I2C1**, and specific pins can serve as SDA and SCL. The pattern is easy to remember: SDA pins are even-numbered, SCL pins are odd, and they come in pairs.

| Bus | SDA options | SCL options |
|-----|-------------|-------------|
| I2C0 | GP0, GP4, GP8, GP12, GP16, GP20 | GP1, GP5, GP9, GP13, GP17, GP21 |
| I2C1 | GP2, GP6, GP10, GP14, GP18, GP26 | GP3, GP7, GP11, GP15, GP19, GP27 |

This code creates an I2C bus on I2C0 using GP0 for data and GP1 for clock, at 400 kHz:

```python
from machine import Pin, I2C
i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
```

### I2C Device Addressing

Since many devices share two wires, each one needs a name so the controller can say who it is talking to. That name is a **7-bit address**, a number from 0 to 127 that the chip's maker sets. Every message starts with the address, and only the matching device pays attention.

| Device | Typical address |
|--------|-----------------|
| SSD1306 OLED display | `0x3C` (60) |
| DS3231 real-time clock | `0x68` (104) |
| AT24C32 memory on RTC boards | `0x57` (87) |
| BME280 temperature sensor | `0x76` (118) |

Two devices with the same address on the same bus will conflict. Many chips offer a jumper to change their address for this reason.

### I2C Pull-Up Resistors

I2C lines are **open-drain**: devices can only pull a wire *down* to ground and never push it up. The wire returns to 3.3 V through **pull-up resistors**, the same idea you met for buttons in Chapter 5. Typical values are 2.2 kΩ to 10 kΩ, with 4.7 kΩ common.

Nearly all I2C modules for hobbyists already include the pull-ups on the board, so you do not need to add any. The Pico's internal pull-ups (about 50 kΩ) are too weak for reliable 400 kHz operation. If a bus mysteriously fails, a missing or too-weak pull-up is one of the first things to suspect.

### I2C Bus Speed

I2C runs at a speed chosen by the controller with the `freq` argument:

| Mode | Speed |
|------|-------|
| Standard | 100 kHz |
| Fast | 400 kHz |
| Fast-plus | 1 MHz |

Each byte takes 9 clock cycles (8 data bits plus one acknowledge bit), so a 400 kHz bus moves about 44,000 bytes per second. A 128 by 64 OLED holds 1,024 bytes of pixel data, so redrawing it takes at least:

\[ \frac{1024 \times 9}{400{,}000} \approx 23\ \text{ms} \]

That is fast enough for a clock, but not for video.

!!! mascot-thinking "One Road, Many Houses"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Picture I2C as a single street with two lanes: SDA carries the mail and SCL keeps time. Every device is a house with its own street number. The controller shouts an address first, and only the house with that number opens the door.

#### Diagram: I2C Conversation Animator

<details markdown="1">
<summary>I2C Conversation Animator</summary>
Type: MicroSim
**sim-id:** i2c-conversation-animator<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *understand* the sequence of an I2C write transaction (Bloom: Understanding).

**Visual elements:** A Pico on the left, three devices on the right (OLED 0x3C, RTC 0x68, sensor 0x76) all attached to two shared lines. Below, SDA and SCL waveform traces scroll.

**Controls:** A dropdown selects the target device and a byte value. "Send" animates START, the 7-bit address with the write bit, the device's ACK, the data byte, ACK, and STOP. Only the addressed device lights up. A "Wrong address" option shows no ACK.

**Behavior:** Steps are labeled on the waveform. A speed slider slows the animation.

**Responsive design:** The layout compresses to a vertical stack below 600 px.

Implementation: p5.js with a scripted timeline.
</details>

### I2C Scanner

An **I2C scanner** is a short program that asks every possible address "are you there?" and lists the ones that answer. It is the first thing to run after wiring any I2C device, because it proves the wiring works before you write any driver code.

```python
NAME = "08-i2c-scan.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin, I2C

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
devices = i2c.scan()

if devices:
    for addr in devices:
        print("Found device at", hex(addr))
else:
    print("No I2C devices found. Check wiring.")
```

The `scan()` method returns a list of addresses as integers. An OLED at `0x3C` shows up as `[60]`, and adding a DS3231 gives `[60, 104]`.

!!! mascot-tip "Scan Before You Code"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    When a new I2C device does not work, run the scanner *first*. An empty list means the problem is the wiring (or a wrong pin pair), not your display code, and that saves you an hour of debugging in the wrong place.

If the scan finds nothing, work through this checklist:

1. Are SDA and SCL swapped?
2. Are power and ground connected?
3. Do the SDA and SCL pins you chose belong to the same I2C bus (I2C0 or I2C1)?
4. Does the module have pull-ups?

## The SPI Bus

**SPI** (Serial Peripheral Interface) is a faster bus that uses separate wires for sending and receiving. It needs more wires than I2C, but it can move data many times faster, which is why color displays use it.

An SPI connection uses these signals:

| Signal | Also called | Direction | Job |
|--------|------------|-----------|-----|
| SCK | Clock, CLK | Controller to device | Timing pulses |
| MOSI | Data, SDA, SDI, DIN | Controller to device | Bytes out |
| MISO | SDO | Device to controller | Bytes back (often unused by displays) |
| CS | Chip select, SS | Controller to device | Picks which device listens |

The naming is confusing because different manufacturers label the same wire differently. A display's **SDA** or **DIN** pin is *not* I2C; on an SPI display it is the MOSI data input.

### SPI Clock Pin

The **SPI clock pin (SCK)** carries a steady stream of pulses from the controller. On each pulse, one bit moves along the data wire. Because the controller decides when the clock ticks, the speed is under your control, which leads to the baudrate below.

### SPI Data Pin

The **SPI data pin (MOSI)** carries bytes from the controller to the peripheral, one bit per clock pulse. Most displays only receive, so they need no return wire. On the Pico, both buses use fixed pin groups:

| Bus | SCK | MOSI (TX) | MISO (RX) |
|-----|-----|-----------|-----------|
| SPI0 | GP2, GP6, GP18 | GP3, GP7, GP19 | GP0, GP4, GP16 |
| SPI1 | GP10, GP14, GP26 | GP11, GP15, GP27 | GP8, GP12, GP28 |

```python
from machine import Pin, SPI
spi = SPI(0, baudrate=10_000_000, sck=Pin(2), mosi=Pin(3))
```

### SPI Chip Select

Unlike I2C, SPI has no addresses. Each peripheral instead gets its own **chip select** wire (CS). The controller pulls CS **low** to wake one device and leaves the others high, which tells them to ignore the traffic. After the transfer, CS goes back high.

```python
cs = Pin(6, Pin.OUT, value=1)   # idle high (not selected)
cs.value(0)                     # select the device
spi.write(b"\x01\x02")          # send two bytes
cs.value(1)                     # deselect
```

### SPI DC Pin

Most color displays need to know whether a byte is a **command** ("set the window") or **pixel data**. They cannot tell from the byte alone, so a **DC pin** (data/command) carries the answer: low means command, high means data. The driver flips this pin for you, but you must wire it and give its pin number.

### SPI Reset Pin

The **reset pin (RST)** lets the Pico restart the display chip. The driver pulses it low for a few milliseconds and then high when the program starts, which puts the display into a known state. If a display works on some runs and not others, a loose reset wire is a prime suspect. A few modules tie reset to 3.3 V and omit the pin.

!!! mascot-warning "Crossed SPI Wires"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A 7-wire display has many places to slip. One swapped or loose wire gives a blank or garbled screen, because the labels (SDA, DIN, MOSI) differ between makers. Compare each wire to the module's silkscreen labels one at a time, and follow the wire colors in your `config.py`.

### SPI Baudrate

**Baudrate** is the number of bits per second sent on the bus; for SPI it equals the clock frequency. It is set with the `baudrate` argument. Typical values for displays run from 10 MHz to 40 MHz, and the Pico can go higher.

A faster baudrate refreshes the screen faster, but too fast produces garbled images because wires and chips cannot keep up. Chapter 11 shows how to tune it by testing.

### Clock Polarity

**Clock polarity** (CPOL) describes whether the clock wire rests **low** (polarity 0) or **high** (polarity 1) when idle. It is paired with **clock phase** (CPHA), which decides whether data is read on the first or second clock edge. Together they form four **SPI modes**. Most displays use mode 0, the MicroPython default. If a datasheet says otherwise, pass `polarity=` and `phase=` when you create the bus.

## UART Protocol

**UART** (Universal Asynchronous Receiver-Transmitter) is the simplest bus. It uses two data wires, **TX** (transmit) and **RX** (receive), and **no clock wire**. Because there is no clock, the two ends must agree in advance on a **baud rate** such as 9600 or 115200 bits per second. Each byte is framed by a start bit and a stop bit, so a byte takes 10 bit-times and 115,200 baud moves about 11,500 bytes per second.

The connection is **crossed**: the Pico's TX goes to the other device's RX, and its RX goes to the other's TX.

```python
from machine import UART, Pin
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
uart.write("hello\n")
```

Clock projects use UART for GPS modules and for talking to other boards.

## Data Packet Structure

A **data packet** is the organized set of bytes sent in one transaction. Nearly every device follows the same pattern: *who*, *what*, and *value*. For I2C the packet is a **start** condition, the device address, a register or command byte, one or more data bytes, and a **stop** condition.

A common example writes a value into a register (a numbered storage slot) on the DS3231 clock chip:

```python
# writeto_mem(device_address, register, bytes)
i2c.writeto_mem(0x68, 0x00, bytes([0x30]))   # set the seconds register
```

Here `0x68` is the address, `0x00` is the register, and `0x30` is the value. Displays such as the SSD1306 add a **control byte** in front of the data that says whether the following bytes are commands (`0x00`) or pixel data (`0x40`). SPI packets follow the same idea, framed by CS going low and then high.

## Bus Speed Comparison

Which bus should you use? The deciding factor is how much data the device needs. Compare sending one full frame to a 240 by 240 color display at 2 bytes per pixel, which is 115,200 bytes:

| Bus | Speed | Time to send one frame |
|-----|-------|------------------------|
| UART at 115,200 baud | 11.5 KB/s | about 10 s |
| I2C at 400 kHz | about 44 KB/s | about 2.6 s |
| SPI at 40 MHz | about 5 MB/s | about 23 ms |

The SPI time comes from \( 115{,}200 \times 8 / 40{,}000{,}000 \approx 23 \) ms. That difference is why small monochrome OLEDs can use I2C, but round color displays must use SPI.

| Feature | I2C | SPI |
|---------|-----|-----|
| Wires (signals) | 2 | 3 to 4 plus DC and reset |
| Devices per bus | Many, by address | One per CS pin |
| Speed | Up to about 1 MHz | 10 to 60+ MHz |
| Simplicity | Very easy | More wiring |

#### Diagram: Bus Speed Race

<details markdown="1">
<summary>Bus Speed Race</summary>
Type: chart
**sim-id:** bus-speed-race<br/>
**Library:** Chart.js<br/>
**Status:** Specified

**Learning objective:** Students will *compare* the time UART, I2C, and SPI need to send a screen of data (Bloom: Analyzing, Evaluating).

**Visual elements:** A horizontal bar chart on a logarithmic axis showing seconds per frame for each bus and each chosen display size.

**Controls:** A dropdown for the display (128x64 mono OLED, 240x240 color, 320x240 color), sliders for I2C frequency (100 kHz to 1 MHz) and SPI baudrate (1 to 62.5 MHz), and a readout "Max frames per second."

**Interactions:** Hovering a bar shows the exact time and the formula used. Bars turn green when the result reaches 20 frames per second or better.

**Responsive design:** The chart resizes with the container and the axis labels shorten on narrow screens.

Implementation: Chart.js with a computed dataset.
</details>

## Signal Integrity

**Signal integrity** means the electrical signal arrives clean, with sharp edges and correct voltage levels, so the receiver reads the right bits. A digital signal is a rapid rise and fall between 0 V and 3.3 V. Long wires, loose connections, and very high speeds distort the edges, causing the receiver to read a 0 as a 1.

The result is a display with flickering pixels or a sensor that occasionally returns garbage. Ways to protect signal integrity:

- Keep signal wires short, especially for SPI at high baudrates.
- Make solid connections, since jumper wires with weak crimps cause intermittent faults.
- Always share a good ground between all devices.
- Lower the baudrate if errors appear.
- Add a 0.1 µF capacitor near a chip's power pins (Chapter 2).

### Crosstalk

**Crosstalk** happens when a fast signal on one wire induces a small unwanted signal in a wire next to it, like hearing another conversation through a thin wall. Wires that run side by side over a long distance are the worst. Clock lines are the most troublesome because they change most often.

The display cable harness in this course reduces crosstalk by placing ground wires between signal wires and keeping cable runs short. The same idea explains why ribbon cables often alternate signal and ground.

!!! mascot-encourage "Bits and Bytes Feel Abstract"
    ![Chrono encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    Hex numbers and shifting bits look like secret code the first time, and that is normal. You already read `0x3C` in a scanner output; try setting and clearing a few bits by hand in the REPL and the pattern will click.

## Putting It Together

| Question | Answer |
|----------|--------|
| Which bus for a small OLED with an RTC? | I2C; both share two wires |
| Which bus for a color TFT or smartwatch? | SPI, for speed |
| How do I know a device is wired correctly? | Run the I2C scanner |
| A display shows garbage at high speed | Lower the SPI baudrate; shorten wires |
| Two I2C devices with the same address | Change one with its address jumper |

## Key Takeaways

- A bus lets many chips share a few wires; bits travel one after another.
- I2C uses SDA and SCL, addresses each device with 7 bits, and needs pull-up resistors.
- SPI uses a clock, a data line, and a chip select per device, plus DC and reset for displays, and is much faster.
- UART has no clock, so both sides must agree on baud rate.
- Bit operations (`&`, `|`, `<<`, `>>`) and bit ordering (MSB first or LSB first) describe exactly how bytes travel.
- Short wires, good grounds, and separated signal lines protect signal integrity.

!!! mascot-celebration "You Speak I2C and SPI"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now wire an I2C device, prove it works with a scanner, pick SPI pins, and explain why a color display needs the faster bus. That opens up every display in this course. Every second counts!

## Practice Questions

1. Why does I2C need only two signal wires for many devices while SPI needs a chip select for each?
2. An I2C scan returns `[60, 104]`. Which devices from the table does this probably show?
3. Write code to set bit 5 of a byte named `x` and to test whether bit 5 is set.
4. Send `0xC1` on the wire in MSB-first order, then in LSB-first order.
5. A 128 by 64 OLED on I2C at 100 kHz needs how long to receive 1,024 bytes? Use 9 clock cycles per byte.
