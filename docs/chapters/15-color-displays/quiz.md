# Quiz: Color Displays and Smartwatch Faces

Test your understanding of RGB565 colors, round displays, direct write drawing, and smartwatch faces with these review questions.

---

#### 1. How many bits does the RGB565 format use for red, green, and blue, in that order?

<div class="upper-alpha" markdown>
1. 5 bits, 6 bits, and 5 bits
2. 6 bits, 5 bits, and 5 bits
3. 8 bits, 8 bits, and 8 bits
4. 4 bits, 4 bits, and 4 bits
</div>

??? question "Show Answer"
    The correct answer is **A**. RGB565 packs a color into 16 bits: 5 for red, 6 for green, and 5 for blue. That gives 32 × 64 × 32 = 65,536 possible colors, and each pixel takes exactly 2 bytes. A standard true color image uses 8 bits per channel, or 24 bits per pixel, so RGB565 cuts the memory by a third at the cost of slightly less smooth gradients.

    **Concept Tested:** RGB565 Color Encoding

    **See:** [RGB565 Color Encoding](index.md#rgb565-color-encoding)

---

#### 2. Which RGB565 value represents pure red?

<div class="upper-alpha" markdown>
1. `0x001F`
2. `0x07E0`
3. `0xF800`
4. `0xFFFF`
</div>

??? question "Show Answer"
    The correct answer is **C**. Red occupies the top five bits of the 16-bit value, so full red is `0xF800`. Pure blue, in the lowest five bits, is `0x001F`, and pure green, in the middle six bits, is `0x07E0`. The value `0xFFFF` has every bit set, which is white. Black is `0x0000`. These values are worth memorizing.

    **Concept Tested:** RGB565 Color Encoding

    **See:** [RGB565 Color Encoding](index.md#rgb565-color-encoding)

---

#### 3. Why does RGB565 give the extra bit to green instead of red or blue?

<div class="upper-alpha" markdown>
1. Green pixels use more power, so they need finer control
2. The human eye is most sensitive to green, so extra detail there is most noticeable
3. Green is the only color that most displays can produce at full brightness
4. The `color565()` function needs one spare bit to mark the green channel
</div>

??? question "Show Answer"
    The correct answer is **B**. The eye notices small changes in green more easily than in red or blue, so giving green 6 bits (64 levels) while red and blue get 5 bits (32 levels) makes the best use of only 16 bits per pixel. The `color565()` function keeps the top 5 or 6 bits of each 0 to 255 channel value and shifts them into their places.

    **Concept Tested:** Color565 Function

    **See:** [The color565 Function](index.md#the-color565-function)

---

#### 4. Why does the 360 × 360 GC9B72 display draw directly instead of using a framebuffer with `show()`?

<div class="upper-alpha" markdown>
1. Direct writing makes the colors brighter than a framebuffer would
2. The GC9B72 chip cannot store any pixel colors of its own
3. SPI displays are not able to receive a whole frame at once
4. A full framebuffer needs 259,200 bytes, nearly all of the Pico's 264 KB of RAM
</div>

??? question "Show Answer"
    The correct answer is **D**. At 2 bytes per pixel, 360 × 360 pixels need 259,200 bytes, leaving almost no room for anything else. A direct write display sends pixels straight to the display's own memory, so every call such as `fill_rect()` or `text()` changes the glass at once and there is no `show()`. The cost is that you must draw static parts once and update only what changed.

    **Concept Tested:** Direct Write Display

    **See:** [Direct Write Display](index.md#direct-write-display)

---

#### 5. Why is an IPS panel the better choice for a wearable watch display?

<div class="upper-alpha" markdown>
1. You rarely look at a wrist straight-on, and IPS keeps its colors at wide angles
2. IPS panels need no backlight, so a watch battery lasts longer
3. IPS panels have a contrast ratio of exactly 21 to 1
4. IPS panels use a framebuffer, which keeps the picture from flickering
</div>

??? question "Show Answer"
    The correct answer is **A**. Viewing angle is how far off-center you can look before the colors wash out or invert. IPS panels, common on round watch displays, hold their colors to about 160 degrees or more, while older, cheaper TN panels fade quickly when viewed from above or below. Because a wrist watch is always glanced at from an angle, a wide viewing angle matters. IPS panels still need a backlight.

    **Concept Tested:** Viewing Angle

    **See:** [Viewing Angle](index.md#viewing-angle)

---

#### 6. A round display has a safe radius of 168 pixels. About how wide is the usable row 140 pixels above the center, using w = 2√(R² − d²)?

<div class="upper-alpha" markdown>
1. About 336 pixels
2. About 56 pixels
3. About 186 pixels
4. About 280 pixels
</div>

??? question "Show Answer"
    The correct answer is **C**. Compute 168² − 140² = 28,224 − 19,600 = 8,624. The square root is about 92.9, and doubling it gives about 186 pixels. A row near the top of a round screen is much narrower than the full width. The value 336 would be the width at the center row, and 280 would simply double the distance from the center.

    **Concept Tested:** Round Display

    **See:** [Round Display](index.md#round-display)

---

#### 7. What does `color565(0, 255, 255)`, which is cyan, return?

<div class="upper-alpha" markdown>
1. `0xFFFF`
2. `0x07FF`
3. `0xF81F`
4. `0xFFE0`
</div>

??? question "Show Answer"
    The correct answer is **B**. Red is 0, so the top five bits are zero. Green at 255 keeps its top six bits, which gives `0x07E0`, and blue at 255 keeps its top five bits, which gives `0x001F`. Combining them gives `0x07FF`. The value `0xF81F` is red plus blue, which is magenta, and `0xFFE0` is red plus green, which is yellow.

    **Concept Tested:** Color565 Function

    **See:** [The color565 Function](index.md#the-color565-function)

---

#### 8. A digital face shows an 8-character time with 16-pixel-wide characters, and `CENTER_X` is 180. What `x` position centers the text?

<div class="upper-alpha" markdown>
1. 52
2. 100
3. 164
4. 116
</div>

??? question "Show Answer"
    The correct answer is **D**. The text width is 8 × 16 = 128 pixels. Half of that is 64, so the starting position is 180 − 64 = 116. This matches the chapter's formula `x = CENTER_X - (len(msg) * 16) // 2`. Formatting the time to a constant width with zero padding means each new value covers the old one exactly, so the screen never needs clearing.

    **Concept Tested:** Digital Clock Face

    **See:** [Digital Clock Face](index.md#digital-clock-face)

---

#### 9. On a direct write display, erasing the old second hand also cuts a gap in a numeral it crossed. What is the best design response?

<div class="upper-alpha" markdown>
1. Lay out the dial so hands never reach the ticks and numerals, avoiding repairs
2. Redraw the entire screen every second so any damage is hidden
3. Call `show()` after each erase so the gap is filled in
4. Lower the SPI baudrate so the erase happens more slowly
</div>

??? question "Show Answer"
    The correct answer is **A**. Every overlap between a moving hand and a static item costs an extra repair step. The kit's dial is designed so the ticks sit outside the longest hand and the numerals lie outside the minute and hour hands, so few things can be damaged by an erase. Redrawing everything each second flickers on a direct write display, and the GC9B72 has no `show()` call.

    **Concept Tested:** Rotating Hands

    **See:** [Rotating Hands](index.md#rotating-hands)

---

#### 10. On a new color display, reds appear blue and blues appear red. What is the most likely cause?

<div class="upper-alpha" markdown>
1. RGB565 is not able to store the color red
2. The display expects BGR channel order, or the two bytes of each color are swapped
3. The backlight pin is wired to 3.3 V instead of a GPIO pin
4. The viewing angle of the panel is set too wide
</div>

??? question "Show Answer"
    The correct answer is **B**. When red and blue trade places, the display expects the channels in a different order (BGR instead of RGB), or the two bytes of each 16-bit color are swapped. Most drivers have a setting for this, so check the driver's options before rewriting any of your colors. The backlight wiring affects brightness only, and viewing angle changes how colors look from the side.

    **Concept Tested:** Color Display

    **See:** [RGB565 Color Encoding](index.md#rgb565-color-encoding)
