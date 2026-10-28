# Quiz: Drawing Shapes, Text, and Animation

Test your understanding of drawing shapes, rendering text and fonts, animation, and partial screen updates with these review questions.

---

#### 1. In the call `rect(x, y, w, h, c)`, what do the third and fourth arguments mean?

<div class="upper-alpha" markdown>
1. The x and y position of the second corner of the rectangle
2. The horizontal and vertical radii of the rectangle
3. The color of the outline and a flag that fills the rectangle
4. The width and height of the rectangle
</div>

??? question "Show Answer"
    The correct answer is **D**. A rectangle takes its top-left corner followed by a width and a height, not a second corner. So `rect(10, 10, 50, 30, 1)` draws a box 50 wide and 30 tall that ends at (59, 39). Mixing up size with a second corner is the most common shape bug, and the giveaway is a rectangle that is too big or too small by exactly the starting offset.

    **Concept Tested:** Rectangle Drawing

    **See:** [Rectangle Drawing](index.md#rectangle-drawing)

---

#### 2. How wide in pixels is the string `"09:45"` drawn with the built-in `text()` method at normal size?

<div class="upper-alpha" markdown>
1. 5 pixels
2. 40 pixels
3. 45 pixels
4. 80 pixels
</div>

??? question "Show Answer"
    The correct answer is **B**. The built-in font uses an 8 by 8 pixel cell for every character, so the width is `8 * len(string)`. The string has 5 characters, giving 8 × 5 = 40 pixels. That means 16 characters fit across the 128-pixel OLED. Because the width is so predictable, you can center text with `x = (128 - 8 * len(msg)) // 2`.

    **Concept Tested:** Text Rendering

    **See:** [Text Rendering](index.md#text-rendering)

---

#### 3. Why does `oled.ellipse(64, 32, 31, 31, 1)` draw a circle centered on a 128 × 64 screen?

<div class="upper-alpha" markdown>
1. The first two numbers are the top-left corner, and the last two are the screen size
2. The `ellipse` method always draws a circle no matter what radii are given
3. Equal radii make a circle, and (64, 32) is the center of the shape and of the screen
4. The value 31 is the diameter, so the circle fills the entire screen height
</div>

??? question "Show Answer"
    The correct answer is **C**. The `ellipse(x, y, xr, yr, c)` call takes the center of the shape and the horizontal and vertical radii. When both radii are 31, the shape is a circle, and the point (64, 32) is the middle of a 128 by 64 screen. A radius of 31 fits the 64-pixel height. Unlike rectangles, an ellipse is positioned by its center, not its corner.

    **Concept Tested:** Circle Drawing

    **See:** [Circle Drawing](index.md#circle-drawing)

---

#### 4. What is the benefit of drawing a clock face into a second buffer and copying it with `blit()` each frame?

<div class="upper-alpha" markdown>
1. The unchanging parts are drawn once, so each frame only adds the moving hands
2. The second buffer makes the OLED panel brighter and sharper
3. The `blit()` call sends the picture to the display without needing `show()`
4. It removes the need to clear the screen at the start of each frame
</div>

??? question "Show Answer"
    The correct answer is **A**. A second buffer holds the parts that never change, such as the tick marks. Each frame you copy that ready-made face into the main buffer with `blit()` and draw only the hands on top. This saves the time of redrawing 60 ticks every second. You still have to call `show()` to send the finished frame to the display.

    **Concept Tested:** Double Buffering

    **See:** [Double Buffering](index.md#double-buffering)

---

#### 5. On the OLED, what does a partial screen update save, and what does it not save?

<div class="upper-alpha" markdown>
1. It saves bus time, but drawing still takes the same time
2. It saves both drawing time and bus time, because only the changed bytes are sent
3. It saves drawing time, but `show()` still sends the entire 1,024-byte buffer
4. It saves nothing, because the whole screen must be redrawn to change a digit
</div>

??? question "Show Answer"
    The correct answer is **C**. With the OLED's framebuffer, you can erase and redraw only the region that changed, which saves drawing time. But `show()` still transfers the whole 1,024 bytes, so the bus time stays the same. On larger color displays, whose drivers can send just a window of pixels, a partial update also cuts the bus time a great deal.

    **Concept Tested:** Partial Screen Update

    **See:** [Partial Screen Update](index.md#partial-screen-update)

---

#### 6. A student draws `09:45` with scaled digits at `scale = 4` on a 128-pixel-wide OLED. What happens?

<div class="upper-alpha" markdown>
1. The time fits exactly because 128 divided by 4 is 32
2. The width is 160 pixels, so it does not fit and a scale of 3 is needed
3. The digits shrink automatically to fit the screen width
4. The width is 80 pixels, so there is room left for the date
</div>

??? question "Show Answer"
    The correct answer is **B**. Each character is 8 pixels wide before scaling, so the width is 8 × scale × the number of characters. For five characters at scale 4, that is 8 × 4 × 5 = 160 pixels, which is wider than the 128-pixel screen. At scale 3 the width is 120 pixels, which fits. Nothing resizes the digits for you, so check the width before choosing a scale.

    **Concept Tested:** Scaled Digits

    **See:** [Scaled Digits](index.md#scaled-digits)

---

#### 7. Which tuple is the bounding box `(x, y, w, h)` of the text `"12:34"` drawn at (80, 40) with the built-in font?

<div class="upper-alpha" markdown>
1. (80, 40, 5, 1)
2. (80, 40, 8, 40)
3. (40, 8, 80, 40)
4. (80, 40, 40, 8)
</div>

??? question "Show Answer"
    The correct answer is **D**. The bounding box is the smallest rectangle that encloses the object. The text starts at (80, 40), is 8 × 5 = 40 pixels wide, and is 8 pixels tall. That gives (80, 40, 40, 8). With this box you can erase the old text exactly using `fill_rect(*box, 0)` and then draw the new value, which is the core of a partial update.

    **Concept Tested:** Bounding Box

    **See:** [Bounding Box](index.md#bounding-box)

---

#### 8. Which call draws a filled rectangle 40 pixels wide and 10 pixels tall with its top-left corner at (20, 30)?

<div class="upper-alpha" markdown>
1. `oled.fill_rect(20, 30, 40, 10, 1)`
2. `oled.fill_rect(20, 30, 60, 40, 1)`
3. `oled.fill_rect(40, 10, 20, 30, 1)`
4. `oled.rect(20, 30, 40, 10, 0)`
</div>

??? question "Show Answer"
    The correct answer is **A**. The `fill_rect(x, y, w, h, c)` call takes the top-left corner, then the width and height, then the color, where 1 means on. Option B treats the numbers as a second corner, option C swaps the order of the arguments, and option D draws only an outline in the off color, which would erase pixels instead of lighting them.

    **Concept Tested:** Rectangle Drawing

    **See:** [Rectangle Drawing](index.md#rectangle-drawing)

---

#### 9. A scrolling message must stay inside a 40 × 8 area and not spill onto other parts of the screen. How can you clip it with `framebuf`?

<div class="upper-alpha" markdown>
1. Call `hline()` and `vline()` around the area to block the extra text
2. Draw into a small buffer the size of the region, then `blit()` it into place
3. Use a smaller font so the message never reaches the edge of the area
4. Call `show()` twice so that the extra pixels are overwritten
</div>

??? question "Show Answer"
    The correct answer is **B**. The `framebuf` module clips only at the edges of the whole buffer, so it has no built-in smaller clipping rectangle. Drawing into a small buffer the size of the region discards anything that falls outside it automatically, and `blit()` then copies the buffer into place on the main screen. Lines drawn around the area would not hide text, and `show()` cannot erase pixels.

    **Concept Tested:** Clipping Region

    **See:** [Clipping Region](index.md#clipping-region)

---

#### 10. A program raises a `MemoryError` after importing six large font modules. What is the best analysis and fix?

<div class="upper-alpha" markdown>
1. The fonts are written in the wrong language, so convert them to C
2. The OLED cannot display more than one font, so remove all but one
3. Each font module uses flash and RAM, so include only needed characters and limit the number of fonts
4. The Pico needs a faster baudrate to load that many fonts at once
</div>

??? question "Show Answer"
    The correct answer is **C**. A loaded font is stored as Python data, so each module takes flash space and RAM when imported, and big fonts with many characters can use tens of kilobytes. The `font_to_py.py` option `-c 0123456789:` keeps the output small by including only the digits and colon. Two or three fonts is a practical ceiling on the Pico, which has 264 KB of RAM.

    **Concept Tested:** Multiple Font Support

    **See:** [Multiple Font Support](index.md#multiple-font-support)
