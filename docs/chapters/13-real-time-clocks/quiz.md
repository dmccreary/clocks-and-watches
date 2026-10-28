# Quiz: Real-Time Clocks and the DS3231

Test your understanding of real-time clocks, BCD registers, battery backup, and clock accuracy with these review questions.

---

#### 1. At which I2C address does the DS3231 real-time clock answer?

<div class="upper-alpha" markdown>
1. `0x3C`
2. `0x68`
3. `0x57`
4. `0x76`
</div>

??? question "Show Answer"
    The correct answer is **B**. The DS3231 answers at `0x68`, which is 104 in decimal, and the address cannot be changed. An I2C scan that shows `[104]` proves the chip is wired correctly, and sharing the bus with an OLED gives `[60, 104]`. The address `0x3C` belongs to the OLED, `0x57` to the memory chip found on many RTC modules, and `0x76` to the BME280 sensor.

    **Concept Tested:** RTC I2C Address

    **See:** [RTC I2C Address](index.md#rtc-i2c-address)

---

#### 2. How is the decimal number 45 stored in BCD format?

<div class="upper-alpha" markdown>
1. `0010 1101`
2. `0011 0100`
3. `0000 0101`
4. `0100 0101`
</div>

??? question "Show Answer"
    The correct answer is **D**. BCD stores each decimal digit in its own four-bit nibble. The digit 4 becomes `0100` and the digit 5 becomes `0101`, giving `0100 0101`, which is written `0x45`. Option A is ordinary binary for 45. Reading the BCD byte as a plain integer would give 69, which is why a conversion function is needed.

    **Concept Tested:** BCD Format

    **See:** [BCD Format](index.md#bcd-format)

---

#### 3. Why is timekeeping moved out of the Pico and into a separate RTC chip?

<div class="upper-alpha" markdown>
1. The chip has its own battery, so the time survives crashes and power loss
2. The Pico cannot count seconds at all without help from another chip
3. The RTC chip displays the time on the screen for the Pico
4. The RTC chip lets the Pico run at a faster processor speed
</div>

??? question "Show Answer"
    The correct answer is **A**. A microcontroller is busy and can be turned off, but a timekeeper must never stop. The RTC has its own crystal and a connection for a backup battery, so it keeps counting when the main power is off, and the Pico simply asks it for the time over I2C. The Pico can count seconds on its own, but its internal clock has no battery and forgets the time at power-off.

    **Concept Tested:** Real-Time Clock

    **See:** [Real-Time Clock](index.md#real-time-clock)

---

#### 4. How does the DS3231 achieve its high accuracy compared with an ordinary crystal?

<div class="upper-alpha" markdown>
1. It uses a larger crystal that vibrates at a much higher frequency
2. It is synchronized to an internet time server every few seconds
3. It measures its own temperature and adjusts the crystal frequency every 64 seconds
4. It stores the time in BCD, which removes rounding errors
</div>

??? question "Show Answer"
    The correct answer is **C**. Quartz crystals change frequency slightly as the temperature changes. The DS3231 is a temperature-compensated crystal oscillator: it measures the chip's temperature and corrects the frequency every 64 seconds. That keeps it within ±2 ppm from 0 to 40 °C, about 15 times better than the plain crystal on the Pico. It has no internet connection, and BCD affects only how numbers are stored.

    **Concept Tested:** Temperature Compensation

    **See:** [Temperature Compensation](index.md#temperature-compensation)

---

#### 5. A clock runs exactly 3 seconds fast, but its ticks are perfectly steady. How is it best described?

<div class="upper-alpha" markdown>
1. Accurate and precise
2. Precise but not accurate
3. Accurate but not precise
4. Neither accurate nor precise
</div>

??? question "Show Answer"
    The correct answer is **B**. Accuracy means the clock shows the right time, while precision means its ticks are consistent and repeatable. A clock that is steadily 3 seconds ahead does not show the right time, so it is not accurate, but its steady ticks make it precise. The DS3231 is both, because its drift is small and steady. Resolution is a separate idea, and an RTC's resolution is one second.

    **Concept Tested:** Clock Precision

    **See:** [Clock Precision](index.md#clock-precision)

---

#### 6. The DS3231 seconds register contains the byte `0x27`. How many seconds does it represent?

<div class="upper-alpha" markdown>
1. 39
2. 72
3. 2.7
4. 27
</div>

??? question "Show Answer"
    The correct answer is **D**. In BCD the high nibble is the tens digit and the low nibble is the ones digit, so `0x27` means 2 tens and 7 ones, which is 27. The function `bcd_to_dec(b)` computes `(b >> 4) * 10 + (b & 0x0F)` to do this. Reading the byte as an ordinary integer would give 39, because `0x27` is 39 in plain binary.

    **Concept Tested:** RTC Registers

    **See:** [RTC Registers](index.md#rtc-registers)

---

#### 7. To set the seconds to 38, which byte does `dec_to_bcd(38)` produce?

<div class="upper-alpha" markdown>
1. `0x26`
2. `0x83`
3. `0x38`
4. `0x1C`
</div>

??? question "Show Answer"
    The correct answer is **C**. The function computes `((38 // 10) << 4) | (38 % 10)`. The tens digit 3 shifted left four bits gives `0x30`, and OR-ing in the ones digit 8 gives `0x38`. Option A, `0x26`, is just 38 written in ordinary hexadecimal, which the chip would read as 26 seconds. The nibbles must hold the decimal digits themselves.

    **Concept Tested:** BCD Format

    **See:** [BCD Format](index.md#bcd-format)

---

#### 8. Using drift = ppm × elapsed seconds / 1,000,000, about how many seconds can a ±20 ppm DS1307 drift in one day?

<div class="upper-alpha" markdown>
1. About 1.7 seconds
2. About 0.17 seconds
3. About 17 seconds
4. About 2.6 seconds
</div>

??? question "Show Answer"
    The correct answer is **A**. One day has 86,400 seconds, so the drift is 20 × 86,400 / 1,000,000, which is about 1.7 seconds. The 0.17 second figure belongs to the DS3231 at ±2 ppm, and the 2.6 second figure belongs to the Pico's ±30 ppm crystal. Over a month the DS1307 can drift about 52 seconds, while the DS3231 drifts only about 5.

    **Concept Tested:** Clock Accuracy

    **See:** [Clock Accuracy](index.md#clock-accuracy)

---

#### 9. A program reads the DS3231 seconds register with `readfrom_mem` and gets 48, but the true time is 30 seconds. What explains this?

<div class="upper-alpha" markdown>
1. The RTC is running 18 seconds fast and needs to be reset
2. The byte is BCD `0x30`, which is 48 when read as an ordinary integer
3. The program read the temperature register instead of the seconds
4. The chip stores seconds in hexadecimal, so 30 appears as 48
</div>

??? question "Show Answer"
    The correct answer is **B**. The RTC stores 30 as BCD, with the digit 3 in the high nibble and 0 in the low nibble, which is the byte `0x30`. Read as an ordinary integer, `0x30` is 48. Passing the byte through `bcd_to_dec()` gives the right value. A drift of 18 seconds would not show up so neatly, and the temperature lives in registers `0x11` and `0x12`.

    **Concept Tested:** BCD Format

    **See:** [BCD Format](index.md#bcd-format)

---

#### 10. A DS3231 module holds a non-rechargeable CR2032 cell, and the battery feels warm. What is the likely cause and the right action?

<div class="upper-alpha" markdown>
1. This is normal, because the RTC chip heats the cell as it counts time
2. The Pico is sending 5 V into the cell, so a 5 V battery should be fitted
3. The module has a charging circuit made for LIR2032 cells, so use that type or remove the charging resistor
4. The cell is too weak to run the chip, so a larger coin cell should be used
</div>

??? question "Show Answer"
    The correct answer is **C**. Many cheap DS3231 modules include a small charging circuit meant for rechargeable LIR2032 batteries. Charging a non-rechargeable CR2032 can make it hot or cause it to leak. Install an LIR2032, or remove the charging resistor from the module, and never leave a suspiciously warm battery in place. The chip itself draws only a few microamps and does not warm the cell.

    **Concept Tested:** RTC Battery Backup

    **See:** [RTC Battery Backup](index.md#rtc-battery-backup)
