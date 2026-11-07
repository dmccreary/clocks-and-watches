# Lab 07: Show the Real Time

![The railway clock face showing the time 10:10:25, with the hour hand near 10, the minute hand at 2, and the red hand near 5](img/07-read-the-time.png){ width="360" }

So far the time was typed into the program. Now the program asks the
Pico what time it is, and points the hands there. It draws the face once,
so it's a photograph, not yet a moving clock.

!!! mascot-welcome "Welcome to Lab 07"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This is the first lab where your clock shows the *actual* time. You'll
    also meet the finished face as a ready-made part, so every lab from
    here on can be short. Let's make time tick!

## What You Will Learn

- how to read the Pico's clock with `time.localtime()`
- what a **tuple** is, and how to **unpack** it
- how to use a module you built, `mondaine`

## Run It

Open `07-read-the-time.py` in Thonny and click **Run**. If Thonny started
the program, Thonny has already set the Pico's clock to your computer's
time, and the face shows it. The shell prints it too:

```
2026-09-25  10:10:25
```

!!! mascot-warning "Why Is It Midnight?"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    The Pico forgets the time when it loses power. If you run this lab from
    a battery or a wall plug, it starts at midnight on January 1. Don't
    worry, because lab 08 teaches the Pico to ask the internet for the
    right time.

## A Tuple of Time

`time.localtime()` gives back eight numbers at once, grouped in a **tuple**:

```python
(2026, 9, 25, 10, 10, 25, 4, 268)
#  year month day hour minute second weekday day-of-year
```

Python can **unpack** a tuple into separate variables in one line:

```python
year, month, day, hour, minute, second, weekday, day_of_year = time.localtime()
```

The names line up with the numbers, one for one. Then the angles come
from lab 05 and lab 06's rules:

```python
hour_angle = (hour % 12) * 30 + minute * 0.5
minute_angle = minute * 6
second_angle = second * 6
```

## The Finished Face as a Module

Labs 02 to 06 drew the face piece by piece. The kit's file `lib/mondaine.py`
packages all those pieces. Three lines now draw the whole clock:

```python
face = mondaine.Face(display)       # make a face
face.draw_dial()                    # white dial and 60 bars
face.show(hour_angle, minute_angle, second_angle)     # the three hands
```

The shape of the hands, the bars, and the draw order are all in the module.
You can open `mondaine.py` and read it any time. Its top comments explain
how it works.

!!! tip "Try This"
    1. Run it twice, a few seconds apart. Does the red hand move?
    2. Print `weekday` as well. Monday is 0. What number is today?
    3. Try `face.show(0, 0, 0)` instead. What time does it say?

!!! mascot-celebration "A Clock That Reads the Time!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You read a tuple, unpacked it into variables, and put the real time on
    your face. Next, you'll make the Pico's time *correct* by asking the
    internet.

**Next:** [Lab 08: Set the Clock from the Internet](08-wifi-sync-time.md)
