# Quiz: Getting the Time in MicroPython

Test your understanding of the time tuple, time formatting, epoch time, and timing functions with these review questions.

---

#### 1. In the time tuple returned by `localtime()`, which weekday number represents Monday?

<div class="upper-alpha" markdown>
1. 1
2. 7
3. 6
4. 0
</div>

??? question "Show Answer"
    The correct answer is **D**. The weekday field runs from 0 to 6, where Monday is 0 and Sunday is 6. It is not Sunday-first as in some calendars. For example, September 28, 2026 is a Monday, so its weekday number is 0. Because the weekday already starts at 0, it can be used directly as an index into a list of day names.

    **Concept Tested:** Weekday Number

    **See:** [Weekday Number](index.md#weekday-number)

---

#### 2. Which slice of `time.localtime()` returns the hour, minute, and second?

<div class="upper-alpha" markdown>
1. `[3:6]`
2. `[0:3]`
3. `[4:7]`
4. `[3:5]`
</div>

??? question "Show Answer"
    The correct answer is **A**. The tuple fields are year (0), month (1), day (2), hour (3), minute (4), second (5), weekday (6), and yearday (7). A slice stops before its end index, so `[3:6]` returns positions 3, 4, and 5. The slice `[0:3]` returns the calendar date, `[3:5]` misses the seconds, and `[4:7]` starts at the minute. Writing `hour, minute, second = time.localtime()[3:6]` is the heart of nearly every clock program.

    **Concept Tested:** Time Tuple

    **See:** [Time Tuple](index.md#time-tuple)

---

#### 3. A clock shows a date in 2021 after the Pico is powered from a wall adapter. Why?

<div class="upper-alpha" markdown>
1. The `localtime()` function always returns a Unix timestamp from 1970
2. Thonny erases the stored date whenever the Pico is disconnected
3. Plain MicroPython has no clock battery, so it forgets the time without power
4. The WiFi chip resets the date every time the program starts running
</div>

??? question "Show Answer"
    The correct answer is **C**. The Pico counts seconds in an internal clock but has no battery to keep it running. When connected, Thonny sets the clock from your computer, but a power cycle with no computer leaves it at a default date in early 2021. The fix is a time source: a DS3231 real-time clock chip (Chapter 13) or WiFi time sync (Chapter 14).

    **Concept Tested:** Localtime Function

    **See:** [Localtime Function](index.md#localtime-function)

---

#### 4. Why must you write `months[month - 1]` when looking up a month name in a list?

<div class="upper-alpha" markdown>
1. The tuple stores the months in reverse order
2. Month numbers start at 1, but list positions start at 0
3. The month field counts from zero, so January is 0
4. The list holds only eleven names, so one must be skipped
</div>

??? question "Show Answer"
    The correct answer is **B**. The month field runs from 1 to 12, but a list is indexed from 0, so January sits at position 0 and December at position 11. Forgetting the subtraction is an off-by-one error that shows the wrong month, and in December it crashes with `IndexError`. The weekday needs no adjustment because it already starts at 0.

    **Concept Tested:** Month Labels

    **See:** [Weekday Labels and Month Labels](index.md#weekday-labels-and-month-labels)

---

#### 5. What is the main difference between `sleep()` and checking `ticks_diff()` in a loop?

<div class="upper-alpha" markdown>
1. `sleep()` measures time of day, while `ticks_diff()` only counts seconds
2. `sleep()` works only on the Pico W, while `ticks_diff()` works on every board
3. `sleep()` blocks the program, while `ticks_diff()` lets it keep working while waiting
4. `sleep()` is accurate to a microsecond, while `ticks_diff()` is accurate to a second
</div>

??? question "Show Answer"
    The correct answer is **C**. While a program is sleeping it does nothing else, so it cannot read a button or update a display. With `ticks_diff()`, the loop runs thousands of times per second and each pass asks whether enough time has passed, so other work continues. This shift from blocking to checking lets one Pico handle buttons, displays, and a clock at the same time.

    **Concept Tested:** Sleep Function

    **See:** [Sleep Function](index.md#sleep-function)

---

#### 6. How should the 24-hour time 0:15 be shown in 12-hour format?

<div class="upper-alpha" markdown>
1. 0:15 AM
2. 12:15 PM
3. 11:15 PM
4. 12:15 AM
</div>

??? question "Show Answer"
    The correct answer is **D**. Using `(hour + 11) % 12 + 1` with hour 0 gives 12, and because 0 is before noon the suffix is AM, so midnight is 12:15 AM. A 12-hour clock never shows 0. Noon, hour 12, also gives 12 but with PM. Clock bugs hide at these boundaries, so test hours 0, 11, 12, 13, and 23 by hand before trusting a conversion.

    **Concept Tested:** AM PM Conversion

    **See:** [AM/PM Conversion](index.md#ampm-conversion)

---

#### 7. How many seconds since midnight is the time 14:05:09?

<div class="upper-alpha" markdown>
1. 50,709
2. 14,509
3. 50,790
4. 8,709
</div>

??? question "Show Answer"
    The correct answer is **A**. The formula is 3600 × hours + 60 × minutes + seconds. Here that is 3600 × 14 + 60 × 5 + 9, which equals 50,400 + 300 + 9 = 50,709. Reducing the time to one integer between 0 and 86,399 makes comparisons simple, such as checking whether the time has passed a 7:30 alarm. Option B just joins the digits together, which is not a count of seconds.

    **Concept Tested:** Seconds Since Midnight

    **See:** [Seconds Since Midnight](index.md#seconds-since-midnight)

---

#### 8. A web service sends the Unix timestamp 1,800,000,000. What value represents the same moment on the Pico, whose epoch starts in 2000?

<div class="upper-alpha" markdown>
1. 2,746,684,800
2. 853,315,200
3. 1,800,000,000
4. 946,684,800
</div>

??? question "Show Answer"
    The correct answer is **B**. A Unix timestamp counts from January 1, 1970, while the Pico counts from January 1, 2000, and the two differ by 946,684,800 seconds. Subtract that offset: 1,800,000,000 − 946,684,800 = 853,315,200. Adding the offset instead gives option A, and leaving the value alone gives option C, which would put your clock about 30 years off.

    **Concept Tested:** Unix Timestamp

    **See:** [Unix Timestamp](index.md#unix-timestamp)

---

#### 9. Why can subtracting two `ticks_ms()` values with the `-` operator sometimes give a wrong or negative answer?

<div class="upper-alpha" markdown>
1. The counter holds only seconds, so milliseconds are lost in the subtraction
2. The counter resets to zero every time the program calls `sleep()`
3. The counter wraps back to zero after about 12.4 days, which `ticks_diff()` handles correctly
4. The counter counts down instead of up, so the result is always reversed
</div>

??? question "Show Answer"
    The correct answer is **C**. The `ticks_ms()` counter is not endless. It wraps back to zero after 2^30 milliseconds, which is about 12.4 days. If the wrap falls between your two readings, plain subtraction gives a wrong, even negative, result. The `ticks_diff(new, old)` function subtracts correctly across the wrap, so always use it instead of `-` in timing code.

    **Concept Tested:** Ticks Difference Function

    **See:** [Ticks Difference Function](index.md#ticks-difference-function)

---

#### 10. A clock adds 1 to a seconds counter after each `sleep(1)` and slowly runs behind real time. What is the cause and the best fix?

<div class="upper-alpha" markdown>
1. Each pass takes slightly over one second, so the error grows; read the real time with `localtime()` each pass
2. The `sleep()` function wakes up early, so the fix is to call it twice per pass
3. The seconds counter overflows after 60, so the fix is to store it in a tuple
4. The display refreshes too often, so the fix is to remove the loop entirely
</div>

??? question "Show Answer"
    The correct answer is **A**. The loop spends extra time running its other instructions, so each pass takes a little more than one second, and the error adds up with every tick. A better approach is to ask for the actual time on each pass, as the chapter's clock loop does with `localtime()`. Then `sleep(1)` only controls how often the screen is redrawn, not how time is counted.

    **Concept Tested:** Time Math

    **See:** [Sleep Function](index.md#sleep-function)
