---
title: Real-Time Clocks and the DS3231
description: The DS3231 real-time clock: I2C wiring, BCD registers, battery backup, temperature compensation, and clock accuracy.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:42:30
version: 1.10
---

# Real-Time Clocks and the DS3231

## Summary

Students wire a DS3231 over I2C, read and write its BCD registers, and use its coin-cell backup. They compare it with the Pico's internal clock. After this chapter they can build a clock that keeps time through power outages.

## Concepts Covered

This chapter covers the following 11 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Real-Time Clock | 38 |
| DS3231 RTC | 37 |
| Internal Pico RTC | 3 |
| RTC Battery Backup | 1 |
| Temperature Compensation | 1 |
| BCD Format | 9 |
| RTC I2C Address | 1 |
| Clock Accuracy | 8 |
| RTC Registers | 8 |
| Clock Precision | 2 |
| RTC Temperature Sensor | 6 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Computational Thinking and Physical Computing](../01-foundations/index.md)
- [Chapter 2: Electronics Fundamentals and Breadboard Wiring](../02-electronics-fundamentals/index.md)
- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)
- [Chapter 6: Getting the Time in MicroPython](../06-getting-time/index.md)
- [Chapter 8: Communication Buses: I2C, SPI, and UART](../08-communication-buses/index.md)

---

!!! mascot-welcome "A Clock That Never Forgets"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Unplug your Pico and it forgets what time it is. This chapter fixes that with a tiny chip and a coin battery that keep counting, even in a power outage, and it drifts by only about five seconds a month. Let's make time tick!

## Why a Separate Clock Chip?

In Chapter 6 you saw that the Pico's time resets to a default date after power is lost. A clock that forgets the time every time it is unplugged is not much of a clock. The fix is a **real-time clock** chip that runs on its own battery and hands the time to the Pico whenever asked. This chapter shows how to wire the popular DS3231, read and set its time through its registers, and understand how accurate it is.

## Real-Time Clock

A **real-time clock (RTC)** is a small chip whose only job is to count time: seconds, minutes, hours, and the calendar date. It has its own crystal oscillator to provide the beat, and it has a connection for a **backup battery**, so it keeps counting when the main power is off. The Pico asks it for the time over I2C.

An RTC chip is a good example of the decomposition idea from Chapter 1. Timekeeping is split off from the microcontroller into a specialist part that does one thing extremely well and uses almost no power.

| Job | Who does it |
|-----|-------------|
| Keep counting while power is off | RTC chip with backup battery |
| Decide what to show | Pico |
| Display it | OLED or LED display |

!!! mascot-thinking "Separate the Timekeeper"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    A microcontroller is busy and turns off; a timekeeper must never stop. Moving the counting to a chip with its own battery means your program can crash, restart, or lose power and the true time is still waiting.

## Internal Pico RTC

The Pico already has a small RTC built into the RP2040 chip. It is the clock that `time.localtime()` reads. You can set it from your program with the `machine.RTC` class:

```python
from machine import RTC
rtc = RTC()
rtc.datetime((2026, 9, 28, 0, 14, 5, 9, 0))   # set the time
print(rtc.datetime())                          # read it back
```

The tuple order for `RTC.datetime()` is **different** from `localtime()`: it is `(year, month, day, weekday, hours, minutes, seconds, subseconds)`, with the weekday in the fourth slot.

The internal RTC has two weaknesses. It has **no battery**, so it forgets the time at power-off, and it is driven by the Pico's ordinary crystal, so it is **not temperature compensated**. A typical crystal's accuracy of about 30 parts per million drifts a couple of seconds per day. That is fine to keep time between syncs to the internet, but it is not enough by itself.

## DS3231 RTC

The **DS3231** is a highly accurate RTC chip that costs about three dollars on a ready-made module. It combines four things in one package: a crystal, temperature compensation, a battery input, and an I2C interface. It also has a built-in temperature sensor and two programmable alarms.

Compared with its older, cheaper cousin the DS1307, it is far more accurate.

| Feature | DS1307 | DS3231 |
|---------|--------|--------|
| Accuracy | ±20 ppm | ±2 ppm |
| Drift per month | about ±52 seconds | about ±5 seconds |
| Temperature compensation | No | Yes |
| Approximate price | \$1 | \$3 |

The module has six pins: **32K** and **SQW** (special outputs you can leave unconnected), **SCL**, **SDA**, **VCC**, and **GND**. Connect VCC to 3.3 V, GND to ground, and SDA and SCL to the same I2C pins as your other I2C devices. The module has a holder for a **CR2032 coin cell**.

| DS3231 pin | Pico pin |
|------------|----------|
| VCC | 3V3(OUT), pin 36 |
| GND | GND, pin 38 |
| SDA | GP0 |
| SCL | GP1 |

### RTC I2C Address

The DS3231 answers at I2C address **`0x68`** (104 in decimal), and the address cannot be changed. Run the I2C scanner from Chapter 8 after wiring: a result of `[104]` proves the chip is connected. If you share the bus with an OLED, the scan shows `[60, 104]`. Many RTC modules also carry a small memory chip at `0x57`, which is why you may see `[87, 104]`. The DS1307 uses the same `0x68`, so you cannot use both on one bus.

### RTC Battery Backup

**Battery backup** is how the RTC survives a power loss. When the main supply voltage falls below the battery's voltage, the chip automatically switches to the coin cell and keeps counting on it. The chip uses only a few microamps in this mode. A typical CR2032 stores about 225 mAh, so at a worst-case 3 µA:

\[ \frac{225\ \text{mAh}}{0.003\ \text{mA}} = 75{,}000\ \text{hours} \approx 8.6\ \text{years} \]

In practice the cell lasts several years. It only matters when the main power is off, because the chip runs from the main supply the rest of the time.

!!! mascot-warning "Check Your Battery Type"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Many cheap DS3231 modules include a small charging circuit meant for rechargeable LIR2032 batteries. Putting a non-rechargeable CR2032 into such a module can cause it to heat up or leak. Use an LIR2032, or remove the charging resistor from the module, and never leave a suspiciously warm battery in place.

### Temperature Compensation

Quartz crystals change frequency slightly as temperature changes, so an ordinary crystal clock runs a little fast or slow in a hot or cold room. **Temperature compensation** corrects for this. The DS3231 measures its own temperature, and every 64 seconds it adjusts the crystal's frequency to cancel the effect. This chip is called a TCXO, a temperature-compensated crystal oscillator. That is why it stays within ±2 ppm from 0 to 40 °C, better than the plain crystal on the Pico by a factor of about 15.

## RTC Registers

A **register** is a numbered storage slot inside a chip. To read the time, you ask the DS3231 for the contents of specific registers; to set the time, you write to them. The DS3231's time registers are stored in a row starting at address 0:

| Register | Holds | Range |
|----------|-------|-------|
| `0x00` | Seconds | 0 to 59 |
| `0x01` | Minutes | 0 to 59 |
| `0x02` | Hours | 0 to 23 |
| `0x03` | Day of week | 1 to 7 |
| `0x04` | Day of month | 1 to 31 |
| `0x05` | Month | 1 to 12 |
| `0x06` | Year | 00 to 99 (2000 to 2099) |
| `0x11`, `0x12` | Temperature | see below |

The other registers hold two alarms, configuration bits, and a status flag, which you can ignore for now.

The `readfrom_mem` method reads a number of bytes starting at a register:

```python
data = i2c.readfrom_mem(0x68, 0x00, 7)    # device, start register, count
print(list(data))                          # e.g. [48, 5, 20, 1, 40, 9, 38]
```

Wait: the seconds byte says 48, but the actual time was 30 seconds. The numbers are not what they seem, because the chip stores them in **BCD**.

#### Diagram: DS3231 Register Map

<details markdown="1">
<summary>DS3231 Register Map</summary>
Type: interactive infographic
**sim-id:** ds3231-register-map<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *identify* which register holds each time field and *interpret* raw register bytes (Bloom: Remembering, Understanding).

**Visual elements:** A vertical list of the registers `0x00` to `0x12` as labeled rows, each showing its byte in hex, binary, and (when decoded) its meaning. Color bands separate time, alarm, control, and temperature groups.

**Interactions:**

- Hovering a row shows the field name and range. Clicking a row opens an infobox about its bits.
- A "Live values" toggle fills the time registers from the browser's clock, encoded in BCD.
- A "Quiz me" mode shows a raw byte such as `0x45` and asks the student to type the decoded value.

**Responsive design:** Rows compress to a two-column layout on narrow screens.

Implementation: p5.js with a register data array.
</details>

## BCD Format

**BCD** (binary-coded decimal) stores each decimal digit in its own group of four bits, called a **nibble**. Ordinary binary stores the whole number in one pattern. In BCD, the number 45 is stored as the digit 4 (`0100`) followed by the digit 5 (`0101`), which is `0100 0101`, written `0x45`. If you read that byte as an ordinary integer, you get 69, which is wrong.

| Decimal | Regular binary | BCD | Byte read as integer |
|---------|----------------|-----|----------------------|
| 9 | `0000 1001` | `0000 1001` | 9 |
| 30 | `0001 1110` | `0011 0000` | 48 |
| 45 | `0010 1101` | `0100 0101` | 69 |
| 59 | `0011 1011` | `0101 1001` | 89 |

That is exactly why the seconds byte in the example above shows 48 when the true value is 30: the byte is `0x30`. BCD was chosen for RTC chips because each digit maps directly to one displayed digit, which is easy for simple hardware.

You need two conversion functions. To decode BCD, take the tens digit from the high nibble and the ones digit from the low nibble. To encode, do the reverse. This is where the shift and mask operations from Chapter 8 pay off.

```python
def bcd_to_dec(b):
    return (b >> 4) * 10 + (b & 0x0F)

def dec_to_bcd(d):
    return ((d // 10) << 4) | (d % 10)

print(bcd_to_dec(0x45))     # 45
print(hex(dec_to_bcd(59)))  # 0x59
```

!!! mascot-encourage "Two Digits Per Byte Takes Practice"
    ![Chrono encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    BCD looks strange the first time, since `0x45` means forty-five, not sixty-nine. Try decoding three bytes by hand with the high nibble times ten plus the low nibble. After that, the two functions above become obvious.

#### Diagram: BCD Converter

<details markdown="1">
<summary>BCD Converter</summary>
Type: MicroSim
**sim-id:** bcd-converter<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* BCD encoding and decoding and *compare* it with ordinary binary (Bloom: Applying, Analyzing).

**Visual elements:** Two rows of eight bit-lights, one showing regular binary and one showing BCD for the same decimal number, with the high and low nibbles shaded separately.

**Controls:** A number slider (0 to 59) and a hex input; a toggle "Read BCD byte as integer" that shows the wrong value; a "Predict" mode asking the student to type the BCD byte for a given number.

**Responsive design:** Bit rows scale to container width.

Implementation: p5.js using `>>`, `&`, and `<<` on integers.
</details>

Now the full read and write. The hours register also has control bits, so mask it: bit 6 selects 12-hour mode and is left at 0 for 24-hour mode, and `& 0x3F` keeps only the hour bits. Month has a century flag in bit 7, so `& 0x1F` keeps the month.

```python
NAME = "13-ds3231-read.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin, I2C
from time import sleep

i2c = I2C(0, sda=Pin(0), scl=Pin(1), freq=400000)
RTC_ADDR = 0x68

def bcd_to_dec(b):
    return (b >> 4) * 10 + (b & 0x0F)

def dec_to_bcd(d):
    return ((d // 10) << 4) | (d % 10)

def read_time():
    d = i2c.readfrom_mem(RTC_ADDR, 0x00, 7)
    second = bcd_to_dec(d[0] & 0x7F)
    minute = bcd_to_dec(d[1])
    hour = bcd_to_dec(d[2] & 0x3F)
    weekday = d[3]                          # 1 to 7
    day = bcd_to_dec(d[4])
    month = bcd_to_dec(d[5] & 0x1F)
    year = 2000 + bcd_to_dec(d[6])
    return year, month, day, hour, minute, second, weekday

def set_time(year, month, day, hour, minute, second, weekday):
    data = bytes([dec_to_bcd(second), dec_to_bcd(minute), dec_to_bcd(hour),
                  weekday, dec_to_bcd(day), dec_to_bcd(month),
                  dec_to_bcd(year - 2000)])
    i2c.writeto_mem(RTC_ADDR, 0x00, data)

# Run set_time ONCE to set the clock, then comment it out:
# set_time(2026, 9, 28, 14, 5, 0, 1)

while True:
    y, mo, d, h, m, s, wd = read_time()
    print(f"{y}-{mo:02d}-{d:02d} {h:02d}:{m:02d}:{s:02d}")
    sleep(1)
```

Note that the RTC's weekday runs from 1 to 7, whereas the `localtime()` weekday runs from 0 to 6. The chip does not care which day is number 1; it just counts through the seven values, so pick a rule and stay consistent. Here Monday is 1.

!!! mascot-tip "Set Once, Then Comment It Out"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Run `set_time()` a single time, then comment the line out before your final upload. Otherwise your clock resets to the old time every time it restarts, which defeats the whole point of the battery.

A practical pattern is to read the RTC once at startup and copy the value into the Pico's internal clock with `machine.RTC().datetime(...)`. After that, the rest of your program can keep using `localtime()` as before, and the DS3231 acts as a battery-backed source of truth.

## RTC Temperature Sensor

The DS3231 needs to know its temperature to compensate its crystal, so it has a temperature sensor built in, and you can read it for free. It is stored in two registers: `0x11` holds the whole degrees Celsius as a signed number, and `0x12` holds the fraction in its top two bits, in steps of 0.25 degrees.

```python
def read_temperature():
    msb, lsb = i2c.readfrom_mem(RTC_ADDR, 0x11, 2)
    if msb & 0x80:                 # negative temperature (signed byte)
        msb -= 256
    return msb + (lsb >> 6) * 0.25

print(read_temperature(), "C")
```

Keep in mind that this sensor measures the temperature *inside the chip*, which sits on a board that warms itself and is next to your Pico. Its accuracy is about ±3 °C, so it is fine for a rough room reading but not for a weather station. A dedicated sensor is better for that, as in Chapter 19.

## Clock Accuracy

**Clock accuracy** is how close the clock's time is to the true time. It is usually stated in **parts per million (ppm)**: the error in seconds for every million seconds that pass. The drift is:

\[ \text{drift} = \text{ppm} \times \frac{\text{elapsed seconds}}{1{,}000{,}000} \]

| Source | Typical accuracy | Drift per day | Drift per month |
|--------|-----------------|---------------|-----------------|
| Pico crystal | ±30 ppm | 2.6 s | 78 s |
| DS1307 | ±20 ppm | 1.7 s | 52 s |
| DS3231 | ±2 ppm | 0.17 s | 5 s |
| Internet time (NTP) | Milliseconds | Effectively 0 | Effectively 0 |

**Worked example.** A DS3231 with ±2 ppm over 30 days (2,592,000 s) drifts up to \( 2 \times 2{,}592{,}000 / 1{,}000{,}000 \approx 5.2 \) seconds. That is roughly one minute per year, close enough for a wall clock that you correct twice a year.

The table shows why the DS3231 is the sweet spot for a clock that is not always online, while an internet-connected clock (Chapter 14) can correct itself and stay essentially perfect.

#### Diagram: Drift Calculator

<details markdown="1">
<summary>Drift Calculator</summary>
Type: chart
**sim-id:** clock-drift-calculator<br/>
**Library:** Chart.js<br/>
**Status:** Specified

**Learning objective:** Students will *calculate* and *compare* the accumulated drift of different clock sources (Bloom: Applying, Evaluating).

**Visual elements:** A line chart of accumulated drift (seconds) versus days, one line each for a Pico crystal (30 ppm), DS1307 (20 ppm), and DS3231 (2 ppm). A horizontal dotted line marks "1 minute off."

**Controls:** A slider for elapsed days (1 to 365), a custom ppm input that adds a fourth line, and a readout of "Days until 1 minute off" for each source.

**Interactions:** Hover for exact values; click a legend entry to hide a line.

**Responsive design:** The chart resizes to the container.

Implementation: Chart.js line chart with linear datasets.
</details>

### Clock Precision

**Clock precision** is how *consistent* the clock is, meaning how repeatable its ticks are, whether or not they match the true time. It is easy to confuse with accuracy, but the two are different.

- An **accurate** clock shows the right time.
- A **precise** clock ticks with very steady intervals, and it might still be consistently 3 seconds fast.

A clock can be precise but inaccurate. Because the DS3231's drift is small and steady, it is both precise and accurate. Resolution is a related idea: the resolution of an RTC is one second, since it does not count anything smaller.

| Clock | Accurate? | Precise? |
|-------|-----------|----------|
| Shows the exact time, but ticks unevenly | Yes | No |
| Runs 3 seconds fast, perfectly steady | No | Yes |
| DS3231 | Yes | Yes |

#### Diagram: Accuracy vs Precision Targets

<details markdown="1">
<summary>Accuracy vs Precision Targets</summary>
Type: MicroSim
**sim-id:** accuracy-vs-precision<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *differentiate* accuracy from precision using a clock-error analogy (Bloom: Understanding, Analyzing).

**Visual elements:** A dartboard-style target where the bullseye is the true time. Each "reading" is a dot.

**Controls:** Two sliders: "Bias (consistently off)" and "Spread (random error)". A "Take 20 readings" button drops dots. A label reports the result: "Accurate and precise," "Precise but not accurate," "Accurate on average but not precise," or "Neither."

**Responsive design:** The target scales to canvas width.

Implementation: p5.js with Gaussian random dots.
</details>

## Putting It Together

| Question | Answer |
|----------|--------|
| How does my clock survive a power outage? | DS3231 with a coin cell |
| How do I know the DS3231 is connected? | I2C scan shows `0x68` (104) |
| Why is the seconds byte 48 when it is 30 seconds? | The chip stores BCD; decode with `bcd_to_dec` |
| How far will it drift? | About 5 seconds per month |
| Can I use it as a thermometer? | Roughly, ±3 °C |

## Key Takeaways

- An RTC is a separate chip with its own crystal and battery that keeps time while power is off.
- The Pico's internal RTC has no battery and is less accurate.
- The DS3231 sits at address `0x68`, compensates for temperature, and drifts only about ±2 ppm.
- RTC registers store time in **BCD**, so decode with `(b >> 4) * 10 + (b & 0x0F)`.
- Drift is `ppm × seconds / 1,000,000`; accuracy means correct time, precision means steady ticks.
- Check the coin-cell type on your module before installing a battery.

!!! mascot-celebration "Time That Survives Blackouts"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now wire a DS3231, read its registers, decode BCD, and estimate how far a clock will drift. Your projects can keep the right time through a power outage. Every second counts!

## Practice Questions

1. Why does a clock need a backup battery, and how does the DS3231 use it?
2. The seconds register reads `0x27`. What is the actual number of seconds?
3. Write `dec_to_bcd(38)` by hand and give the result in hex.
4. Compute the drift in one year for a ±20 ppm crystal (31,536,000 seconds).
5. Explain the difference between an accurate clock and a precise clock with an example.
