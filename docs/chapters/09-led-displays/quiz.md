# Quiz: LED Displays and the First Digital Clock

Test your understanding of seven-segment displays, multiplexing, the TM1637 driver, and other LED displays with these review questions.

---

#### 1. How many wires does a TM1637 four-digit display module need to connect to the Pico?

<div class="upper-alpha" markdown>
1. Two
2. Four
3. Eight
4. Twelve
</div>

??? question "Show Answer"
    The correct answer is **B**. The TM1637 needs power, ground, and two signal wires called CLK and DIO. The driver chip does all the multiplexing for you. Wiring the digits directly would take about 12 pins, which is why the TM1637 module is the first clock display in this course. It costs only about one to two dollars.

    **Concept Tested:** TM1637 Wiring

    **See:** [TM1637 Wiring](index.md#tm1637-wiring)

---

#### 2. Which segment of a seven-segment digit is the one in the middle of the figure 8?

<div class="upper-alpha" markdown>
1. Segment a
2. Segment d
3. Segment g
4. Segment dp
</div>

??? question "Show Answer"
    The correct answer is **C**. The segments are labeled `a` through `g`, starting at the top and going clockwise, with `g` in the middle. Segment `d` is the bottom bar, and `a` is the top bar. Many displays add an eighth dot, `dp`, for the decimal point. A program stores each digit as one byte with one bit per segment, so bit 6 controls segment `g`.

    **Concept Tested:** Seven Segment Display

    **See:** [Seven-Segment Display](index.md#seven-segment-display)

---

#### 3. How does segment multiplexing let a four-digit display work with only about 12 pins?

<div class="upper-alpha" markdown>
1. Only one digit is lit at a time, cycling so fast that persistence of vision makes all look lit
2. Each digit is wired to its own driver chip, which reduces the pin count
3. The segments are lit at only half brightness, so fewer wires are needed
4. The display remembers its pattern and no longer needs to be refreshed
</div>

??? question "Show Answer"
    The correct answer is **A**. All four digits share the same 8 segment lines, and each digit has its own select wire, giving 8 + 4 = 12 pins. The controller lights one digit at a time, cycling more than 100 times per second, and persistence of vision blends them. The cost is that each digit is on only a quarter of the time, so each segment needs about four times the current, and something must keep cycling.

    **Concept Tested:** Segment Multiplexing

    **See:** [Segment Multiplexing](index.md#segment-multiplexing)

---

#### 4. A TM1637 is wired to GP2 and GP3, but an I2C scan finds nothing. Why?

<div class="upper-alpha" markdown>
1. The module must be broken, because every working module appears in the scan
2. The scanner only lists devices that use 5 V power
3. GP2 and GP3 are not allowed to be used with the TM1637
4. The TM1637 uses its own protocol with no device address, so a scan cannot find it
</div>

??? question "Show Answer"
    The correct answer is **D**. The TM1637's CLK and DIO wires look like I2C, but it has its own protocol and no device address. That also means it can connect to any two GPIO pins. A scan that finds nothing does not prove the module is bad. To test it, run the driver library's `numbers()` call and look at the display instead of using the scanner.

    **Concept Tested:** TM1637 Driver

    **See:** [TM1637 Driver](index.md#tm1637-driver)

---

#### 5. Why does a character LCD such as the LCD1602 need a backlight?

<div class="upper-alpha" markdown>
1. The backlight supplies the 5 V that the HD44780 chip needs to run
2. An LCD makes no light of its own and only blocks or passes light
3. The backlight refreshes the characters so they do not fade
4. Without a backlight the text appears in the wrong font
</div>

??? question "Show Answer"
    The correct answer is **B**. Unlike an LED display, where each LED glows by itself, a liquid crystal display does not produce light. It blocks or passes light that already exists, so in the dark it needs a backlight to be readable. The LCD1602 has 16 columns and 2 rows and uses the HD44780 controller. An I2C backpack reduces its wiring from about 10 pins to four wires.

    **Concept Tested:** Character LCD

    **See:** [Character LCD and the LCD1602](index.md#character-lcd-and-the-lcd1602)

---

#### 6. Which segments are lit to show the digit 1, and what is its segment byte?

<div class="upper-alpha" markdown>
1. Segments a and b, with byte `0x03`
2. Segments e and f, with byte `0x30`
3. Segments b and c, with byte `0x06`
4. All seven segments, with byte `0x7F`
</div>

??? question "Show Answer"
    The correct answer is **C**. The digit 1 uses the two right-hand bars, segments `b` and `c`. Bit 1 is segment `b` and bit 2 is segment `c`, so the byte is `0b00000110`, which is `0x06`. All seven segments lit with `0x7F` makes the digit 8. Remember that a 1 bit turns a segment on, which is the bit manipulation idea from Chapter 8 in action.

    **Concept Tested:** Seven Segment Display

    **See:** [Seven-Segment Display](index.md#seven-segment-display)

---

#### 7. A clock uses `tm.numbers(h, m, colon=(s % 2 == 0))`. What is the colon doing at 14:05:07?

<div class="upper-alpha" markdown>
1. Off, because 7 is odd and the test is false
2. On, because 7 is greater than zero
3. On, because the minute is odd
4. Off, because the colon only lights at the top of each minute
</div>

??? question "Show Answer"
    The correct answer is **A**. The expression `s % 2 == 0` is true only for even seconds, so the colon is on for even seconds and off for odd ones. At second 7 the remainder is 1, the test is false, and the colon is off. Because the state comes from the real seconds value instead of a toggled variable, the blink can never get out of step with the time.

    **Concept Tested:** Colon Flashing

    **See:** [Colon Flashing](index.md#colon-flashing)

---

#### 8. You want to move a TM1637 to GP10 for CLK and GP11 for DIO. What do you need to do?

<div class="upper-alpha" markdown>
1. Nothing can be done, because the module only works on GP2 and GP3
2. Create the display with `I2C(0, sda=Pin(10), scl=Pin(11))` instead
3. Connect it to the SPI0 pins and set a baudrate for the display
4. Wire CLK and DIO to those pins and pass `Pin(10)` and `Pin(11)` to the constructor
</div>

??? question "Show Answer"
    The correct answer is **D**. Since the TM1637 protocol has no address and no special hardware requirements, it works on any two GPIO pins. Wire the pins as you like, then create the object with `tm1637.TM1637(clk=Pin(10), dio=Pin(11))`. Update the wiring table or `config.py` too, so your documentation matches the build. Using the I2C or SPI classes would not work, because the TM1637 is neither.

    **Concept Tested:** TM1637 Wiring

    **See:** [TM1637 Wiring](index.md#tm1637-wiring)

---

#### 9. A bare multiplexed display freezes on one digit when the program pauses for five seconds, but a TM1637 module keeps showing all four digits. What explains the difference?

<div class="upper-alpha" markdown>
1. The TM1637 uses larger LEDs that glow even after power is removed
2. The TM1637 lights all four digits at the same time instead of multiplexing
3. The TM1637 chip does the cycling by itself, so the program does not need to
4. The TM1637 stores the digits in the Pico's flash memory
</div>

??? question "Show Answer"
    The correct answer is **C**. Multiplexing demands that something keeps cycling through the digits constantly. If your own program does that and then stops to do other work, the display flickers or freezes on one digit. The TM1637 driver chip handles the multiplexing internally. You send it the digits once and it keeps them lit, which leaves your program free to sleep or do other tasks.

    **Concept Tested:** Segment Multiplexing

    **See:** [TM1637 Driver](index.md#tm1637-driver)

---

#### 10. Why is it risky to connect an LCD1602 with an I2C backpack straight to the Pico's SDA and SCL pins?

<div class="upper-alpha" markdown>
1. The LCD1602 uses SPI, so I2C pins can never carry its signals
2. Many backpacks pull the lines up to 5 V, which can damage the Pico's 3.3 V pins
3. The backpack address of `0x27` is reserved for the Pico itself
4. The backlight drains so much current that the pins burn out
</div>

??? question "Show Answer"
    The correct answer is **B**. LCD1602 modules normally run on 5 V, and many backpacks include pull-up resistors that raise SDA and SCL to 5 V. The Pico's GPIO pins are only 3.3 V tolerant, so this can send 5 V into them and cause damage. Use a level shifter or a module with 3.3 V pull-ups, as you learned in Chapter 2. The backpack normally appears at `0x27` or `0x3F` on the scanner.

    **Concept Tested:** LCD1602 Display

    **See:** [Character LCD and the LCD1602](index.md#character-lcd-and-the-lcd1602)
