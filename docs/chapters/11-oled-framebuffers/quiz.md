# Quiz: OLED Displays and Framebuffers

Test your understanding of OLED displays, the SSD1306 driver, framebuffers, and baudrate tuning with these review questions.

---

#### 1. How many bytes of RAM does a framebuffer for a 128 × 64 monochrome OLED need?

<div class="upper-alpha" markdown>
1. 1,024 bytes
2. 8,192 bytes
3. 128 bytes
4. 64 bytes
</div>

??? question "Show Answer"
    The correct answer is **A**. A monochrome pixel needs 1 bit, so the memory is 128 × 64 × 1 / 8 = 1,024 bytes. The value 8,192 is the number of pixels, not bytes, since eight pixels share each byte. This small buffer is why the OLED can keep a full copy of its screen in RAM, while large color displays sometimes cannot.

    **Concept Tested:** Display Resolution

    **See:** [Display Resolution](index.md#display-resolution)

---

#### 2. Which call copies the framebuffer to the OLED so that the picture becomes visible?

<div class="upper-alpha" markdown>
1. `oled.fill(0)`
2. `oled.pixel(x, y, 1)`
3. `oled.text("Hi", 0, 0)`
4. `oled.show()`
</div>

??? question "Show Answer"
    The correct answer is **D**. Drawing calls such as `fill()`, `pixel()`, and `text()` change only the framebuffer in RAM. Nothing appears on the panel until `show()` sends the buffer across the bus. A blank OLED very often means the `show()` call is missing. Every frame should end with exactly one `show()`, after the buffer has been cleared and all drawing is done.

    **Concept Tested:** Display Show Command

    **See:** [Display Show Command](index.md#display-show-command)

---

#### 3. What is the main benefit of drawing into a framebuffer first and then calling `show()`?

<div class="upper-alpha" markdown>
1. The framebuffer makes the OLED panel brighter than direct drawing
2. Viewers never see half-drawn frames because the whole picture appears at once
3. The framebuffer removes the need to wire a bus to the display
4. Drawing into memory uses no RAM, so the Pico saves energy
</div>

??? question "Show Answer"
    The correct answer is **B**. A framebuffer is a block of RAM holding a copy of every pixel. You can draw a hundred things in it, and then one fast transfer shows them all at the same instant, like a painter who finishes a canvas behind a curtain. The design avoids flicker and keeps drawing code simple. The cost is the RAM, which is only 1,024 bytes for this OLED.

    **Concept Tested:** Framebuffer

    **See:** [Framebuffer](index.md#framebuffer)

---

#### 4. A 1.3-inch OLED shows its image shifted about two pixels to the side, with garbage at the edge, when using the SSD1306 driver. What is the likely cause?

<div class="upper-alpha" markdown>
1. The I2C address was set to `0x3D` instead of `0x3C`
2. The framebuffer was never cleared with `fill(0)`
3. The module has an SH1106 controller whose memory is 132 columns wide
4. The baudrate was set too high for the SPI bus
</div>

??? question "Show Answer"
    The correct answer is **C**. The SH1106 controller looks the same and uses the same wiring, but its memory is 132 columns wide instead of 128. The SSD1306 driver therefore puts the picture two pixels off. The fix is the `sh1106.py` driver, which has the same methods. Check the controller name in the product listing before you buy. A wrong address or baudrate would give a blank or garbled screen, not a clean shift.

    **Concept Tested:** SH1106 Driver

    **See:** [SH1106 Driver](index.md#sh1106-driver)

---

#### 5. Why should you call `show()` once per frame rather than after every drawing call?

<div class="upper-alpha" markdown>
1. The OLED can only accept one command per second
2. Calling `show()` more than once erases the framebuffer
3. The driver ignores any drawing done after the first `show()`
4. It is the slowest step because it moves the whole buffer over the bus
</div>

??? question "Show Answer"
    The correct answer is **D**. The `show()` call transfers all 1,024 bytes across I2C or SPI, which is the slowest step in your drawing code. Calling it after every line multiplies that cost for no benefit. Do all your drawing first and reveal the finished frame once. The routine for every frame is to clear, draw everything, and then show.

    **Concept Tested:** Display Show Command

    **See:** [Display Show Command](index.md#display-show-command)

---

#### 6. How much memory does a 360 × 360 color display need at 16 bits per pixel?

<div class="upper-alpha" markdown>
1. 259,200 bytes
2. 129,600 bytes
3. 16,200 bytes
4. 2,073,600 bytes
</div>

??? question "Show Answer"
    The correct answer is **A**. Use memory = W × H × bpp / 8, which gives 360 × 360 × 16 / 8 = 259,200 bytes. That is almost the entire 264 KB of RAM on the Pico, which explains why large color displays often cannot keep a full framebuffer. Option B counts two bytes fewer per pixel, option C divides the pixel count by eight, and option D forgets to divide by 8 bits per byte.

    **Concept Tested:** Display Resolution

    **See:** [Display Resolution](index.md#display-resolution)

---

#### 7. On a 128-wide `MONO_VLSB` buffer, which byte index and bit hold the pixel at (50, 13)?

<div class="upper-alpha" markdown>
1. Index 63, bit 5
2. Index 178, bit 5
3. Index 178, bit 1
4. Index 306, bit 5
</div>

??? question "Show Answer"
    The correct answer is **B**. The formula is index = x + floor(y / 8) × width, and bit = y mod 8. Here y = 13 gives page 1 and bit 5, so the index is 50 + 1 × 128 = 178. Option A simply adds x and y, option C confuses the page with the bit, and option D uses page 2 by mistake. You never compute this by hand because `pixel()` does it for you.

    **Concept Tested:** Pixel Coordinate Mapping

    **See:** [Pixel Coordinate Mapping](index.md#pixel-coordinate-mapping)

---

#### 8. About how long does one `show()` take to send the 1,024-byte OLED buffer over I2C at 400 kHz, using 9 clock cycles per byte?

<div class="upper-alpha" markdown>
1. About 0.8 ms
2. About 2.3 ms
3. About 23 ms
4. About 230 ms
</div>

??? question "Show Answer"
    The correct answer is **C**. The time is 1,024 × 9 / 400,000, which is about 0.023 seconds, or 23 ms. That allows up to roughly 43 frames per second, which is plenty for a clock that changes once per second. The 0.8 ms figure belongs to SPI at 10 MHz. You can measure the real time with `ticks_us()` and `ticks_diff()`.

    **Concept Tested:** Display Refresh Rate

    **See:** [Display Refresh Rate](index.md#display-refresh-rate)

---

#### 9. A counter program draws a new number each second, but the digits pile up into an unreadable blob. What is the most likely cause?

<div class="upper-alpha" markdown>
1. The `fill(0)` call is missing, so each number is drawn over the old one
2. The `show()` call is missing, so the screen never updates at all
3. The baudrate is too low, so the digits arrive out of order
4. The display is an SH1106, so the digits draw in the wrong place
</div>

??? question "Show Answer"
    The correct answer is **A**. Without clearing, each new value is drawn on top of the previous one in the framebuffer, so overlapping digits smear together. The routine for each frame is always `fill(0)`, then draw, then `show()`. If `show()` were missing, the screen would not update at all, rather than showing overlapping digits, so the clearing step is the one to check first.

    **Concept Tested:** Screen Clearing

    **See:** [Screen Clearing](index.md#screen-clearing)

---

#### 10. In a baudrate test, the picture is clean at 4 MHz and 8 MHz but garbled at 10 MHz. What speed should the final program use?

<div class="upper-alpha" markdown>
1. 10 MHz, because it is the fastest speed that was tried
2. About 8 MHz, which is safely below the first speed that showed errors
3. 20 MHz, because faster speeds always work after a warm-up
4. 1 MHz, because no display is reliable at higher speeds
</div>

??? question "Show Answer"
    The correct answer is **B**. The recommended procedure is to find the first speed that shows errors, here 10 MHz, and then use a value about 20 to 30 percent below it, which is roughly 7 to 8 MHz. That margin matters because a setup that works on your desk can fail with longer wires or a warmer chip. Using the failing speed, or a faster one, would risk garbled pixels.

    **Concept Tested:** Baudrate Tuning

    **See:** [Baudrate Tuning](index.md#baudrate-tuning)
