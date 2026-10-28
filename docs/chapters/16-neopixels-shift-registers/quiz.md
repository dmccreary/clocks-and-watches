# Quiz: NeoPixels and Shift Register Clocks

Test your understanding of NeoPixels, HSV color, LED power budgeting, and the 74HC595 shift register with these review questions.

---

#### 1. What supply voltage does a WS2812B NeoPixel strip use?

<div class="upper-alpha" markdown>
1. 3.3 V
2. 5 V
3. 12 V
4. 1.8 V
</div>

??? question "Show Answer"
    The correct answer is **B**. The WS2812B runs from 5 V power, receives data on a single wire at 800 kHz, and takes 24 bits per pixel, which is 8 each for green, red, and blue. The strip wants a data signal near its supply voltage, while the Pico gives 3.3 V. For short wires this usually works, and a level shifter helps if the first pixels flicker.

    **Concept Tested:** WS2812B Standard

    **See:** [WS2812B Standard](index.md#ws2812b-standard)

---

#### 2. Which call sends the pixel colors you set to a NeoPixel strip?

<div class="upper-alpha" markdown>
1. `np.show()`
2. `np.fill()`
3. `np.update()`
4. `np.write()`
</div>

??? question "Show Answer"
    The correct answer is **D**. Setting `np[0] = (255, 0, 0)` changes only the colors stored in memory. Nothing lights up until `np.write()` sends the data down the strip, so you can update every pixel and then show them all at the same instant. The `fill()` method sets all pixels to one color in memory. The `show()` name belongs to OLED framebuffer displays, not to NeoPixels.

    **Concept Tested:** NeoPixel Library

    **See:** [The NeoPixel Library](index.md#the-neopixel-library)

---

#### 3. Why must the NeoPixel strip's ground be connected to the Pico's ground?

<div class="upper-alpha" markdown>
1. It lets the strip draw its power from the Pico's 3.3 V pin
2. It makes the strip brighter than it would be otherwise
3. The data signal is measured relative to ground, so the strip ignores it without a shared ground
4. It lets the Pico read the colors that the strip is currently showing
</div>

??? question "Show Answer"
    The correct answer is **C**. A voltage is always measured between two points, so the strip needs the same ground reference as the Pico to interpret the data signal. Without a shared ground the strip lights randomly or not at all. Connect ground first, add a 300 to 500 ohm resistor on the data line, and then apply power. A large capacitor across the strip's supply absorbs the surge when the LEDs switch on.

    **Concept Tested:** NeoPixel Wiring

    **See:** [NeoPixel Wiring](index.md#neopixel-wiring)

---

#### 4. What is the job of the latch pin on a 74HC595?

<div class="upper-alpha" markdown>
1. It copies the shifted bits to the outputs all at once, so outputs do not flicker while data moves in
2. It sets the speed at which data is shifted into the chip
3. It selects whether the chip receives data most significant bit first or least significant bit first
4. It turns the eight outputs off to save power between updates
</div>

??? question "Show Answer"
    The correct answer is **A**. The 74HC595 has a shift register that collects bits and a separate storage register that drives the outputs. Pulsing the latch pin copies the shift register into the storage register in one instant, so all eight outputs change at exactly the same moment. Without the latch, the outputs would flicker as bits slid along. The clock pin, not the latch, controls the shifting.

    **Concept Tested:** Latch Pin

    **See:** [Latch Pin](index.md#latch-pin)

---

#### 5. Why is the HSV color model a good choice for making a rainbow on a NeoPixel ring?

<div class="upper-alpha" markdown>
1. HSV uses fewer bits than RGB, so the strip draws less current
2. MicroPython can send HSV values to the strip without any conversion
3. HSV colors are always brighter than the same colors in RGB
4. Hue is an angle on a color wheel, so changing only hue moves through the rainbow
</div>

??? question "Show Answer"
    The correct answer is **D**. HSV describes a color with hue, saturation, and value. Changing only the hue moves around the color wheel, and changing only the value changes the brightness. Giving pixel `i` of `N` the hue 360 × i / N paints a rainbow, and a growing offset rotates it. The strip itself still needs RGB, so the program converts with `hsv_to_rgb()`.

    **Concept Tested:** HSV Color Model

    **See:** [HSV Color Model](index.md#hsv-color-model)

---

#### 6. About how much current can 30 NeoPixels draw if all are white at 50 percent brightness, using 60 mA per pixel at full brightness?

<div class="upper-alpha" markdown>
1. About 90 mA
2. About 900 mA
3. About 1.8 A
4. About 450 mA
</div>

??? question "Show Answer"
    The correct answer is **B**. Use I = N × 60 mA × brightness fraction, which gives 30 × 60 × 0.5 = 900 mA. That is more than a USB port can supply, so this design would need a separate 5 V supply with its ground tied to the Pico's ground. Option C is the current at full brightness, and the plan should always cover the maximum your program can light up.

    **Concept Tested:** LED Power Calculation

    **See:** [LED Power Calculation](index.md#led-power-calculation)

---

#### 7. An 8 × 8 NeoPixel matrix is wired in a zigzag, where odd rows run backward. Using `index = y * width + (x if y % 2 == 0 else width - 1 - x)`, what is the strip index of the pixel at x = 2, y = 3?

<div class="upper-alpha" markdown>
1. 26
2. 21
3. 29
4. 18
</div>

??? question "Show Answer"
    The correct answer is **C**. Row 3 is odd, so the row runs backward and x becomes 8 − 1 − 2 = 5. The index is 3 × 8 + 5 = 29. Option A, 26, forgets the reversal and uses x directly. Converting (x, y) coordinates to a strip index lets you draw on the matrix with the same coordinate ideas used for displays in Chapter 12.

    **Concept Tested:** NeoPixel Matrix

    **See:** [NeoPixel Matrix](index.md#neopixel-matrix)

---

#### 8. On a binary clock row for minutes, which place-value pixels are lit to show the minute value 45?

<div class="upper-alpha" markdown>
1. The 32, 8, 4, and 1 pixels
2. The 32, 16, 8, and 4 pixels
3. The 32, 8, 2, and 1 pixels
4. The 16, 8, 4, and 1 pixels
</div>

??? question "Show Answer"
    The correct answer is **A**. Break 45 into place values: 32 + 8 + 4 + 1 = 45. Minutes need 6 bits because the maximum of 59 is 32 + 16 + 8 + 2 + 1. A lit pixel is a 1 and an unlit pixel is a 0, so bits 5, 3, 2, and 0 are on. Option B sums to 60, option C to 43, and option D to 29.

    **Concept Tested:** Binary Clock

    **See:** [Binary Clock](index.md#binary-clock)

---

#### 9. Four 74HC595 chips are chained to drive a four-digit seven-segment clock with 32 outputs. How many Pico pins are needed, and why?

<div class="upper-alpha" markdown>
1. 32 pins, because each output needs its own wire from the Pico
2. 12 pins, because each chip needs data, clock, and latch wires
3. 8 pins, because each byte needs eight data wires
4. 3 pins, because the chips share clock and latch lines and pass data along through QH'
</div>

??? question "Show Answer"
    The correct answer is **D**. The QH' output passes the bit that falls off the end to the next chip's SER input, and the chips share the clock and latch lines. Together they act as one long register, so you send four bytes and update all 32 outputs using only data, clock, and latch pins. This design needs no multiplexing because every segment stays lit on its own.

    **Concept Tested:** Shift Register Chaining

    **See:** [Shift Register Chaining](index.md#shift-register-chaining)

---

#### 10. A 30-pixel strip lights all pixels at full white from the Pico's USB 5 V pin, and the Pico keeps resetting. What is the best fix?

<div class="upper-alpha" markdown>
1. Add a 10 kΩ resistor in series with the data line
2. Lower the brightness and power the strip from a separate 5 V supply with a shared ground
3. Power the strip from the 3.3 V pin so it draws less current
4. Raise the data rate so the pixels update faster
</div>

??? question "Show Answer"
    The correct answer is **B**. Thirty pixels at full white can draw 30 × 60 mA = 1.8 A, far more than the roughly 500 mA that USB provides, so the supply sags and the Pico resets. Lower the brightness, since values of 10 to 60 are plenty for an indoor clock, and power the strip from a separate 5 V supply whose ground is tied to the Pico's ground. A larger data resistor or a faster data rate does not reduce current.

    **Concept Tested:** LED Power Calculation

    **See:** [LED Power Calculation](index.md#led-power-calculation)
