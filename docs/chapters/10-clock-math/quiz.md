# Quiz: Coordinates, Trigonometry, and Clock Geometry

Test your understanding of screen coordinates, radians, sine and cosine, and clock hand geometry with these review questions.

---

#### 1. Where is the origin (0, 0) on a display's coordinate system?

<div class="upper-alpha" markdown>
1. At the bottom-left corner of the screen
2. At the center of the screen
3. At the top-left corner of the screen
4. At the top-right corner of the screen
</div>

??? question "Show Answer"
    The correct answer is **C**. On a display, x is the column counted from the left and y is the row counted from the top, so the origin is the top-left pixel. On a 240 by 240 screen the bottom-right pixel is (239, 239). This differs from a math class graph, where the origin is at the bottom-left and y increases upward. A point that looks higher on the screen has a smaller y.

    **Concept Tested:** X Y Coordinate System

    **See:** [X Y Coordinate System](index.md#x-y-coordinate-system)

---

#### 2. What unit of angle do MicroPython's `math.sin()` and `math.cos()` expect?

<div class="upper-alpha" markdown>
1. Radians
2. Degrees
3. Clock positions from 0 to 59
4. Pixels along the arc
</div>

??? question "Show Answer"
    The correct answer is **A**. Like most programming languages, MicroPython's math functions work in radians, where a full circle is about 6.283. Use `math.radians()` to convert from degrees. Passing a degree value directly gives an answer, but the wrong one, which makes this a classic mistake. Degrees, which split a circle into 360 parts, are what people use when thinking about angles.

    **Concept Tested:** Radians vs Degrees

    **See:** [Radians vs Degrees](index.md#radians-vs-degrees)

---

#### 3. Why does the formula for the screen position of a clock hand tip subtract the cosine term, as in `y = cy - r * cos(θ)`?

<div class="upper-alpha" markdown>
1. Cosine always returns a negative number for clock angles
2. Subtraction keeps the result inside the display's pixel range
3. The hand length must be reduced as the angle increases
4. The screen's y-axis points down, so moving up means a smaller y
</div>

??? question "Show Answer"
    The correct answer is **D**. Clock angles start at 12 o'clock and go clockwise. At 0 degrees the tip should be straight above the center, which on the screen means a smaller y value. Because screen y increases downward, the cosine term is subtracted. Sine goes with x, since at 3 o'clock the tip moves right by the full radius. This pair of lines places every hand, tick mark, and number on a round face.

    **Concept Tested:** Polar Coordinates

    **See:** [Polar Coordinates](index.md#polar-coordinates)

---

#### 4. Why does the hour hand angle formula include the extra term `0.5 * m`?

<div class="upper-alpha" markdown>
1. It converts the hour from 24-hour form to 12-hour form
2. It lets the hand creep smoothly instead of jumping from one hour to the next
3. It adds the angle of the second hand to the hour hand
4. It keeps the hour hand shorter than the minute hand
</div>

??? question "Show Answer"
    The correct answer is **B**. The hour hand turns 30 degrees per hour, which is 0.5 degrees per minute. Adding `0.5 * m` moves it a little each minute. Without it, the hand would sit exactly on the 3 until it jumped to the 4 on the hour, which looks wrong at 3:59. The conversion from 24-hour form is done by `h % 12`, and hand length is a separate matter.

    **Concept Tested:** Angle Calculation

    **See:** [Angle Calculation](index.md#angle-calculation)

---

#### 5. Why is it better to write each hand length as a fraction of the face radius than as a fixed number of pixels?

<div class="upper-alpha" markdown>
1. The design scales automatically to any display size
2. The Pico can only draw lines whose length is less than one
3. Fractions are drawn faster than whole numbers on the screen
4. The hour, minute, and second hands must all have the same length
</div>

??? question "Show Answer"
    The correct answer is **A**. If the hour hand is 0.50 of the radius, the minute hand 0.75, and the second hand 0.90, the same program works on a 240 pixel face or a 360 pixel face with no changes. Fixed pixel lengths would need editing for every screen. The hands also have different lengths on purpose, so you can tell them apart at a glance.

    **Concept Tested:** Clock Hand Length

    **See:** [Clock Hand Length](index.md#clock-hand-length)

---

#### 6. What is the angle of the hour hand at 9:15:00, using `30 * (h % 12) + 0.5 * m`?

<div class="upper-alpha" markdown>
1. 270 degrees
2. 285 degrees
3. 277.5 degrees
4. 315 degrees
</div>

??? question "Show Answer"
    The correct answer is **C**. The hour part is 30 × 9 = 270 degrees, and the minute part is 0.5 × 15 = 7.5 degrees, for a total of 277.5. The hour hand has moved a quarter of the way from the 9 toward the 10. The minute hand at that time is at 6 × 15 = 90 degrees, pointing at the 3. A value of exactly 270 would ignore the minutes.

    **Concept Tested:** Angle Calculation

    **See:** [Angle Calculation](index.md#angle-calculation)

---

#### 7. A hand of length 100 starts at the center (120, 120) and points at 6 o'clock, which is 180 degrees. Where is its tip?

<div class="upper-alpha" markdown>
1. (220, 120)
2. (120, 20)
3. (20, 120)
4. (120, 220)
</div>

??? question "Show Answer"
    The correct answer is **D**. At 180 degrees, sine is 0 and cosine is −1, so x = 120 + 100 × 0 = 120 and y = 120 − 100 × (−1) = 220. The tip is straight below the center, which is correct for 6 o'clock because y grows downward. Option A is the 3 o'clock position, option B is 12 o'clock, and option C is 9 o'clock.

    **Concept Tested:** Cosine Function

    **See:** [Polar Coordinates](index.md#polar-coordinates)

---

#### 8. A fixed-point lookup table uses `SCALE = 256`. Which integer is stored for the sine of 30 degrees?

<div class="upper-alpha" markdown>
1. 64
2. 128
3. 256
4. 0
</div>

??? question "Show Answer"
    The correct answer is **B**. The sine of 30 degrees is 0.5, and multiplying by the scale factor of 256 gives 128. To get the real value back, you divide by 256 or shift right by 8. Storing sine and cosine for the 60 possible angles at startup means each frame needs only integer multiplication and shifts. A stored value of 256 would stand for a sine of 1, which happens at 90 degrees.

    **Concept Tested:** Fixed Point Arithmetic

    **See:** [Fixed Point Arithmetic](index.md#fixed-point-arithmetic)

---

#### 9. A student's clock draws the hand pointing straight down at 12:00, and straight up at 6:00. What is the most likely cause?

<div class="upper-alpha" markdown>
1. The angle was left in degrees instead of being changed to radians
2. The center point was calculated with `/` instead of `//`
3. The student added `r * cos(θ)` to `cy` instead of subtracting it
4. The hand length was set larger than the radius of the face
</div>

??? question "Show Answer"
    The correct answer is **C**. Adding the cosine term instead of subtracting it flips the vertical direction, because the screen's y-axis points down. The hand then points in exactly the opposite vertical direction, as if the math-class convention had been used. A degree-versus-radian error would produce hands pointing in seemingly random directions, not a clean mirror image, and an oversized length would only make the hand too long.

    **Concept Tested:** X Y Coordinate System

    **See:** [X Y Coordinate System](index.md#x-y-coordinate-system)

---

#### 10. Why does a lookup table with fixed-point integers speed up drawing an analog face on the RP2040?

<div class="upper-alpha" markdown>
1. The RP2040 has no floating-point hardware, so a precomputed table avoids slow software sine and cosine
2. The table lets the Pico skip the drawing step for the tick marks entirely
3. Integers use less flash memory than floats, so programs load faster
4. The RP2040 can only perform sine and cosine on whole-number angles
</div>

??? question "Show Answer"
    The correct answer is **A**. Every `sin()` and `cos()` call on the RP2040 runs in software, which is relatively slow, and calling them for 60 tick marks each frame wastes time. Computing the values once at startup and storing them as scaled integers means each frame needs only multiplication and bit shifts. The rounding error is at most 1/256 of the length, less than half a pixel for a 120-pixel hand.

    **Concept Tested:** Integer Math Tricks

    **See:** [Integer Math Tricks](index.md#integer-math-tricks)
