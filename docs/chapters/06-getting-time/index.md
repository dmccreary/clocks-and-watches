---
title: Getting the Time in MicroPython
description: Reading the time with localtime(), splitting the time tuple, formatting time and dates, and timing with sleep and ticks.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:33:19
version: 1.10
---

# Getting the Time in MicroPython

## Summary

Students read time tuples, extract hours, minutes, and seconds, and format them as text. They use sleep and tick functions to pace programs and learn about epoch time. After this chapter they can produce a correctly formatted time string.

## Concepts Covered

This chapter covers the following 22 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Time Tuple | 79 |
| Localtime Function | 78 |
| Year Month Day | 3 |
| Hour Minute Second | 5 |
| Weekday Number | 2 |
| Day of Year | 1 |
| Time Formatting | 9 |
| Date Formatting | 1 |
| Utime Module | 24 |
| Epoch Time | 2 |
| Time Math | 1 |
| 12 Hour Format | 2 |
| 24 Hour Format | 1 |
| Weekday Labels | 1 |
| Month Labels | 1 |
| Sleep Function | 7 |
| Ticks Ms Function | 16 |
| Unix Timestamp | 1 |
| Leap Year Handling | 1 |
| Seconds Since Midnight | 1 |
| AM PM Conversion | 1 |
| Ticks Diff Function | 7 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)
- [Chapter 4: Control Flow, Functions, and Modules](../04-control-flow-functions/index.md)

---

!!! mascot-welcome "Time to Read the Time"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Every clock starts with one question: what time is it right now? In this chapter you'll ask the Pico, pull the answer apart, and print it as a clean `Mon 3:07 PM`. Let's make time tick!

## Asking the Pico for the Time

A clock's first job is to *know* the time. MicroPython gives you a small toolkit for that: a function that returns the current time, a way to split it into hours, minutes, and seconds, and timers for pacing a program. This chapter covers reading time, formatting it for humans, and measuring short intervals. Where the time comes from (an internet server or a battery-backed chip) is the topic of later chapters.

## Localtime Function

The **`localtime()` function** returns the current date and time as a tuple. You get it from the `time` module:

```python
import time
print(time.localtime())
```

A typical result looks like this:

```python
(2026, 9, 28, 14, 5, 9, 0, 271)
```

The Pico does not have a calendar built from scratch. It counts seconds in an internal clock (the RTC, covered in Chapter 13). When you connect with Thonny, Thonny sets that clock from your computer, so `localtime()` matches your computer's local time. If you power the Pico from a wall adapter with no computer, the time starts at a default date (early 2021) and drifts from there until you set it, which is why later chapters add a real-time clock chip and internet sync.

!!! mascot-warning "Wrong Date After Unplugging?"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If your clock shows a date in 2021 after a power cycle, the Pico simply forgot the time. Plain MicroPython has no clock battery, and the fix is a time source: a DS3231 real-time clock (Chapter 13) or WiFi time sync (Chapter 14).

On the Pico, `localtime()` and `gmtime()` return the same thing, because MicroPython does not apply time zones by itself. Converting between time zones is something you will do in Chapter 14.

## Time Tuple

The result of `localtime()` is a **time tuple**: an immutable group of eight integers in a fixed order.

| Index | Name | Range | Example |
|-------|------|-------|---------|
| 0 | year | 2000 and up | 2026 |
| 1 | month | 1 to 12 | 9 |
| 2 | mday (day of month) | 1 to 31 | 28 |
| 3 | hour | 0 to 23 | 14 |
| 4 | minute | 0 to 59 | 5 |
| 5 | second | 0 to 59 | 9 |
| 6 | weekday | 0 to 6 (Monday is 0) | 0 |
| 7 | yearday | 1 to 366 | 271 |

You can pull out one value by its index, or unpack several at once:

```python
now = time.localtime()
print(now[3])                 # the hour
year, month, day = now[0], now[1], now[2]
```

The most convenient trick is **slicing**, which takes a range of positions and returns a smaller tuple:

```python
hour, minute, second = time.localtime()[3:6]   # positions 3, 4, 5
```

This one line is the heart of nearly every clock program in the book.

#### Diagram: Time Tuple Explorer

<details markdown="1">
<summary>Time Tuple Explorer</summary>
Type: interactive infographic
**sim-id:** time-tuple-explorer<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *identify* each field of the time tuple and *apply* slicing to extract fields (Bloom: Remembering, Applying).

**Visual elements:** The eight-field tuple drawn as eight labeled boxes with a live value from the browser's clock, and a small analog and digital clock alongside.

**Interactions:**

- Hovering a box shows its name and range; clicking shows the Python expression that extracts it, such as `now[3]`.
- A "Slice" control lets the student drag a bracket over boxes to select `[3:6]`, and the sim shows the resulting tuple and the unpacking line.
- A "Quiz me" mode asks for the index of the field named at random.

**Responsive design:** Boxes wrap to two rows on narrow screens.

Implementation: p5.js using JavaScript `Date` to fill values.
</details>

### Year, Month, and Day

Three fields give the **calendar date**: `year` (a four-digit number), `month` (1 for January through 12 for December), and `mday` (the day of the month, 1 to 31). Note that months and days start at 1, not 0, unlike most Python positions.

```python
year, month, day = time.localtime()[:3]
```

### Hour, Minute, and Second

The **clock time** comes from three fields: hour (0 to 23), minute (0 to 59), and second (0 to 59). The hour is always in 24-hour form. Midnight is hour 0, and 11 PM is hour 23. Every display formatting step starts from these three numbers.

### Weekday Number

The **weekday number** is a value from 0 to 6, where **Monday is 0** and Sunday is 6. It is *not* Sunday-first as in some calendars. September 28, 2026 is a Monday, so its weekday is 0. You will use the weekday number as an index into a list of names, next.

### Day of Year

The **day of year** (yearday) counts days from January 1, which is day 1. September 28 is day 271 in 2026, since the eight full months before it contain 243 days and \( 243 + 28 = 271 \). It is useful for programs that count days until a date or draw a year progress bar.

## Weekday Labels and Month Labels

The tuple gives numbers, but people want names. The standard approach is a **label list** you index with the number.

```python
days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

year, month, day, hour, minute, second, weekday, yearday = time.localtime()
print(days[weekday])          # Mon
print(months[month - 1])      # Sep
```

Notice the `month - 1`. The month number starts at 1 but the list index starts at 0, so you must subtract one. Forgetting this **off-by-one** error shows the wrong month, or crashes in December with `IndexError`. The weekday needs no adjustment because it already starts at 0.

## Time Formatting

**Time formatting** turns the numbers into readable text. The tools are the f-strings and zero-padding from Chapter 3:

```python
hour, minute, second = time.localtime()[3:6]
print(f"{hour:02d}:{minute:02d}:{second:02d}")    # 14:05:09
```

The same numbers can be displayed several ways depending on what the user expects.

| Style | Example | Code |
|-------|---------|------|
| 24-hour with seconds | 14:05:09 | `f"{h:02d}:{m:02d}:{s:02d}"` |
| Short | 14:05 | `f"{h:02d}:{m:02d}"` |
| Blinking colon (odd seconds) | 14 05 | `":" if s % 2 == 0 else " "` |

### 24-Hour Format

**24-hour format** counts hours from 0 to 23. It has no AM or PM, and it is what `localtime()` returns. It is unambiguous, so it is used in computing, aviation, and much of the world. The hour after 12:59 is 13:00.

### 12-Hour Format

**12-hour format** shows hours from 1 to 12 and adds AM or PM. It is common in the United States. The conversion, from Chapter 3, is one line:

```python
hour12 = (hour + 11) % 12 + 1
```

### AM/PM Conversion

Once you have the 12-hour value, the AM or PM suffix depends only on whether the original 24-hour value is before noon:

```python
suffix = "AM" if hour < 12 else "PM"
print(f"{hour12}:{minute:02d} {suffix}")
```

The tricky moments are the boundaries. Test them:

| 24-hour | 12-hour | Suffix |
|---------|---------|--------|
| 0 | 12 | AM (midnight) |
| 9 | 9 | AM |
| 12 | 12 | PM (noon) |
| 15 | 3 | PM |
| 23 | 11 | PM |

!!! mascot-tip "Test the Edges"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Clock bugs hide at midnight and noon. Whenever you write a time conversion, try hours 0, 11, 12, 13, and 23 by hand before you trust it.

### Date Formatting

**Date formatting** works the same way for the calendar fields. Different regions order them differently, and you should choose one style and stay consistent.

| Style | Example | Code |
|-------|---------|------|
| ISO (year first) | 2026-09-28 | `f"{y}-{mo:02d}-{d:02d}"` |
| US style | 9/28/2026 | `f"{mo}/{d}/{y}"` |
| With labels | Mon Sep 28 | `f"{days[wd]} {months[mo-1]} {d}"` |

The ISO order (year, month, day) is the international standard and sorts correctly as text, which makes it the best choice for log files.

## Seconds Since Midnight

Sometimes it is easier to represent the time of day as **one number**: the total seconds since midnight. It compresses hours, minutes, and seconds into a single integer between 0 and 86,399:

\[ t = 3600 \times h + 60 \times m + s \]

For 14:05:09 the value is \( 3600 \times 14 + 60 \times 5 + 9 = 50{,}709 \). Working in one number makes comparisons and arithmetic simple. To check whether the time is past a 7:30 alarm, compare `t >= 7*3600 + 30*60` instead of juggling two fields. To go back to hours, minutes, and seconds, use `//` and `%` exactly as in Chapter 3.

## The Utime Module

MicroPython puts timing tools in the **time module**, which older code and documentation call **utime** (the "u" stood for "micro"). Both names work on the Pico, but `import time` is preferred in current code, and it is what this book uses. If you find `import utime` in an example, the code works the same way.

The tools in this module fall into three groups:

| Group | Functions |
|-------|-----------|
| Reading time | `localtime()`, `gmtime()`, `time()`, `mktime()` |
| Waiting | `sleep()`, `sleep_ms()`, `sleep_us()` |
| Measuring intervals | `ticks_ms()`, `ticks_us()`, `ticks_diff()` |

## Sleep Function

The **`sleep()` function** pauses your program for a number of seconds, and it accepts fractions: `time.sleep(0.5)` waits half a second. For shorter waits, `sleep_ms(250)` waits 250 milliseconds and `sleep_us(100)` waits 100 microseconds.

```python
import time
time.sleep(1)       # wait one second
```

While a program is sleeping, it does *nothing else*. The Pico cannot read a button or update a display. That is fine for a simple blink, but it makes a poor way to keep time. If you add one second on each pass of a loop with `sleep(1)`, the loop also takes time to run its other instructions, so the clock runs slightly slow and the error grows with every second. A better approach is to read the real time on each pass, as this program does:

```python
NAME = "06-clock-loop.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

while True:
    h, m, s = time.localtime()[3:6]
    print(f"{h:02d}:{m:02d}:{s:02d}")
    time.sleep(1)
```

The clock always shows the true time because it asks for it each time. The `sleep(1)` only controls how often it redraws.

## Ticks Milliseconds Function

The **`ticks_ms()` function** returns a counter of milliseconds since an arbitrary starting point (usually the moment the Pico started). It does not tell you the time of day. Instead, you use it to measure **how long something took** or to schedule the next action without stopping the program.

```python
start = time.ticks_ms()
# ... do some work ...
elapsed = time.ticks_diff(time.ticks_ms(), start)
print(elapsed, "ms")
```

The counter is not endless: it wraps back to zero after \( 2^{30} \) milliseconds, about 12.4 days. That means simple subtraction can give a wrong (even negative) answer around the wrap, which is why the next function exists.

### Ticks Difference Function

The **`ticks_diff(new, old)` function** subtracts two tick values correctly, even across the wrap-around. Always use it instead of the `-` operator.

**Worked example: a non-blocking timer.** The program below toggles an LED every 500 ms *without* using `sleep()`, so it stays free to do other things, like watching a button, on every pass:

```python
NAME = "06-nonblocking-blink.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

from machine import Pin
from time import ticks_ms, ticks_diff

led = Pin("LED", Pin.OUT)
last = ticks_ms()

while True:
    now = ticks_ms()
    if ticks_diff(now, last) >= 500:   # 500 ms passed?
        led.toggle()
        last = now
    # other work could go here
```

The loop runs thousands of times per second, and each time it asks "has 500 ms passed since the last toggle?" This pattern, comparing ticks to a stored time, is used throughout later chapters for stopwatches and alarms.

!!! mascot-thinking "Wait Without Freezing"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    `sleep()` says "do nothing for this long." `ticks_diff()` says "keep working, and tell me when this long has passed." That shift, from blocking to checking, is how one Pico handles buttons, displays, and a clock at the same time.

#### Diagram: Sleep vs Ticks Timeline

<details markdown="1">
<summary>Sleep vs Ticks Timeline</summary>
Type: MicroSim
**sim-id:** sleep-vs-ticks<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *compare* blocking (`sleep`) and non-blocking (`ticks_diff`) timing by observing how a button press is handled (Bloom: Analyzing).

**Visual elements:** Two horizontal timelines running side by side. The top shows a program using `sleep(1)`, with long gray "sleeping" blocks. The bottom shows a program using ticks, with many small "checking" blocks. A blinking LED icon sits on each.

**Controls:** A "Press button" button and a speed slider. On the sleep timeline the press is ignored until the sleep ends (latency shown as a red bar), while the ticks timeline responds within a few milliseconds.

**Responsive design:** Timelines scale to container width and stack vertically.

Implementation: p5.js frame loop with a simulated millisecond counter.
</details>

## Epoch Time

**Epoch time** is a way to represent a moment as a single count of seconds since a fixed starting date called the **epoch**. `time.time()` returns this count, and `time.localtime(secs)` turns it back into a tuple. It is compact and makes calculations easy.

The catch: **on the Pico the epoch is January 1, 2000, at 00:00:00**, not 1970.

```python
import time
now = time.time()          # seconds since 2000-01-01
print(time.localtime(now)) # converts back to a tuple
print(time.mktime(time.localtime()))   # tuple back to seconds
```

The functions `localtime()` and `mktime()` are inverses: one converts seconds to a tuple, the other a tuple to seconds.

### Unix Timestamp

A **Unix timestamp** is the same idea but counted from **January 1, 1970**. It is the standard on the internet and in most programming languages. The two epochs differ by exactly 946,684,800 seconds (30 years):

\[ \text{unix} = \text{pico\_time} + 946{,}684{,}800 \]

You have to convert whenever you exchange timestamps with a web service. For example, a weather site that sends a Unix timestamp of 1,790,000,000 corresponds to \( 1{,}790{,}000{,}000 - 946{,}684{,}800 = 843{,}315{,}200 \) on the Pico. Forgetting this offset produces dates 30 years off.

!!! mascot-warning "Two Epochs, One Mistake"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    Timestamps from the internet count from 1970, while `time.time()` on the Pico counts from 2000. Mix them and your clock jumps 30 years. When a time looks wildly wrong, check which epoch it uses and subtract or add 946,684,800.

## Time Math

**Time math** means adding to or subtracting from times. The easiest way is to work in seconds, then convert back to a tuple. This handles carrying between hours, days, months, and years automatically.

```python
import time

now = time.time()
in_90_minutes = now + 90 * 60
print(time.localtime(in_90_minutes)[3:6])     # hour, minute, second then

diff = time.time() - now                       # seconds elapsed
```

To find how long until a target, subtract two epoch values and divide. Working with tuples directly (adding 90 to the minute field) would leave values like minute 105, so convert to seconds first.

## Leap Year Handling

A **leap year** has an extra day, February 29, so that the calendar stays in step with the Earth's orbit. The rule has three parts:

1. A year divisible by 4 is a leap year.
2. Except a year divisible by 100 is *not*, 
3. Unless it is also divisible by 400, in which case it *is*.

So 2024 and 2000 are leap years, while 1900 and 2100 are not. As code:

```python
def is_leap(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

print(is_leap(2024), is_leap(2100))    # True False
```

You rarely need this yourself, because `localtime()` and `mktime()` already handle leap years and the tuple's yearday runs to 366 in a leap year. You need `is_leap()` only when you compute calendar values on your own, such as the number of days in February.

## Putting It Together

This program displays a full, friendly date and time using every idea in the chapter:

```python
NAME = "06-friendly-clock.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

days = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
months = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

while True:
    y, mo, d, h, m, s, wd, yd = time.localtime()
    h12 = (h + 11) % 12 + 1
    suffix = "AM" if h < 12 else "PM"
    print(f"{days[wd]} {months[mo-1]} {d}, {y}   {h12}:{m:02d}:{s:02d} {suffix}")
    time.sleep(1)
```

## Key Takeaways

- `time.localtime()` returns an 8-tuple: year, month, day, hour, minute, second, weekday (Monday is 0), and yearday.
- Slice the tuple with `[3:6]` to get hours, minutes, and seconds.
- Use label lists for names, and subtract 1 from the month to index them.
- Zero-pad with `:02d`; use `(h + 11) % 12 + 1` and `"AM" if h < 12 else "PM"` for 12-hour display.
- `sleep()` blocks; `ticks_ms()` with `ticks_diff()` measures time without stopping the program.
- The Pico's epoch is 2000, not 1970, so Unix timestamps differ by 946,684,800 seconds.

!!! mascot-celebration "Time, Decoded"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now read the time tuple, format `Mon Sep 28, 2026  2:05:09 PM`, and time events without freezing your program. That is the software heart of every clock. Every second counts!

## Practice Questions

1. What does `time.localtime()[3:6]` return, and how would you unpack it?
2. Write code that prints the weekday name for today using a list of labels.
3. Convert these 24-hour times to 12-hour with AM or PM: 0:15, 12:00, 18:45.
4. Why should you use `ticks_diff()` instead of subtracting two `ticks_ms()` values with `-`?
5. A web service sends the Unix timestamp 1,800,000,000. What value would the Pico's `time.localtime()` need to be given for the same moment?
