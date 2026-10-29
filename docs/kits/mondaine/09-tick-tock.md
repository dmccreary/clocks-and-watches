# Lab 09: Tick Tock

![The railway clock face. Four pictures, one second apart, show the red second hand jumping from 22 seconds to 23, 24, and 25](img/09-tick-tock.gif){ width="360" }

At last, the clock runs. Once a second the red hand jumps ahead six
degrees, like an ordinary quartz clock, and the black hands follow along
as the minutes pass.

!!! mascot-welcome "Welcome to Lab 09"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Your face has been a picture until now. In this lab it comes alive, and
    you'll learn the oldest trick in animation. Let's make time tick!

## What You Will Learn

- how a **while loop** keeps a program running forever
- how to **do work only when something changed**
- why drawing on this display costs real time

## Run It

Open `09-tick-tock.py` in Thonny and click **Run**. The red hand ticks
once a second. Watch the minute hand at the top of a minute: it jumps a
whole 6° in the same instant the red hand starts its next lap. That's a
little abrupt, and the next three labs fix it.

## The Loop

The heart of the program is short:

```python
last_second = -1

while True:
    t = time.localtime()
    hour, minute, second = t[3], t[4], t[5]

    if second != last_second:
        last_second = second
        face.show((hour % 12) * 30 + minute * 0.5, minute * 6, second * 6)

    time.sleep_ms(20)
```

`while True:` repeats forever. Each time around, the program asks the Pico
for the time. Then comes the key question: **is this a different second
than last time?** (`!=` means "is not equal to.") The loop goes around about
50 times a second, but the answer is "yes" only once a second.

!!! mascot-thinking "Remember What You Showed"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    The variable `last_second` is the program's memory of what is already
    on the screen. When the new value matches it, there is nothing to do,
    and doing nothing is the fastest thing a program can do.

## Why Not Just Redraw Everything?

This display has no memory of its own for the picture. Each pixel has to
be sent down a wire, and the whole face is 129,600 of them. On a Pico 2 W
that takes about a tenth of a second, so redrawing the whole face over
and over would make the screen flash.

`face.show()` is careful instead. It works out which rows of pixels the
moving hand covers, and repaints only those. You'll find out how in the
[Notes for Teachers](teacher-notes.md#how-the-face-moves-without-flicker).

!!! tip "Try This"
    1. Change `time.sleep_ms(20)` to `time.sleep_ms(1000)`. What goes
       wrong, and why? (Hint: the loop can now miss a second.)
    2. Add `print(second)` inside the `if`. How often does it print?
    3. Change `second * 6` to `second * 12`. What does the clock do now?

!!! mascot-celebration "The Clock Runs!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You wrote a loop that keeps time and only redraws when the second
    changes. Next, you'll make the red hand glide instead of jump.

**Next:** [Lab 10: A Smooth Sweep](10-smooth-sweep.md)
