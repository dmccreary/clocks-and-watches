# Lab 05: The Hour and Minute Hands

![The railway dial with a thick black hour hand pointing at 10 and a thicker, longer black minute hand pointing at 2, showing ten past ten](img/05-black-hands.png){ width="360" }

The two black hands are bold, blunt, and a little wider near the center
than at the tip. This lab draws them at 10:10, the time you always see in
clock advertisements, because the hands frame the face like a smile.

!!! mascot-welcome "Welcome to Lab 05"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    A clock is mostly arithmetic: take a time, turn it into an angle, and
    point something at it. You're about to write that arithmetic yourself.
    Let's make time tick!

## What You Will Learn

- how to turn **a time into angles**
- why the hour hand also creeps as the minutes pass
- how a function with many arguments describes a shape

## Run It

Open `05-black-hands.py` in Thonny and click **Run**. The dial from lab 04
appears, and then the two hands. The shell prints the angles it used:

```
minute hand at 60 degrees; hour hand at 305.0
```

## Time to Angles

The minute hand makes a full 360° turn in 60 minutes, so it moves
**6° a minute**. At minute 10 it points at 60°, the 2 o'clock spot:

```python
minute_angle = minute * 6
```

The hour hand makes a full turn in 12 hours, so it moves **30° an hour**.
But it doesn't wait for the hour to end. At 10:30 it sits halfway between
the 10 and the 11, so it also moves **0.5° every minute** (30° ÷ 60):

```python
hour_angle = (hour % 12) * 30 + minute * 0.5
```

The `hour % 12` turns a 24-hour value like 22 into 10, using the remainder
from [lab 04](04-minute-markers.md). At 10:10, that gives 10 × 30 + 10 ×
0.5 = **305°**.

!!! mascot-thinking "A Hand Is Just a Number"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    The program never thinks about hands. It turns time into a number, an
    angle, and hands the number to a drawing function. Change the number
    and the picture follows.

## Describing a Hand

Both hands are four-sided shapes that taper: wide at the tail, narrower
at the tip. Four numbers (in design units *a*, like the bars) describe
either one:

| Hand | Tail length | Tail width | Tip length | Tip width |
|---|---|---|---|---|
| Hour | 12 | 6.4 | 32 | 5.2 |
| Minute | 12 | 5.2 | 46 | 3.6 |

The *tail* is the short stub that sticks out behind the center pin. The
program stores each hand's four numbers in a **tuple**, a fixed list in
parentheses:

```python
HOUR_HAND = (12, 3.2, 32, 2.6)     # half widths, to make the corners easy
```

and `hand()` unpacks them with one line, `tail, tail_half, tip, tip_half =
size`, then finds the four corners the same way `bar()` did in lab 03.

!!! mascot-tip "Check Your Arithmetic"
    ![Chrono giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    To check your arithmetic, change `hour` and `minute` near the top and
    look at the picture. At 3:00 the minute hand should point straight up
    and the hour hand straight right.

!!! tip "Try This"
    1. Set `hour = 3` and `minute = 0`. Are the hands where you expect?
    2. Set `hour = 6` and `minute = 30`. Why is the hour hand *not* exactly
       on the 6?
    3. Make the hour hand red by changing its color argument.

!!! mascot-celebration "Telling Time with Math!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You turned a time into two angles and drew tapered hands with one
    reusable function. Next, the part everyone remembers: the red second
    hand.

**Next:** [Lab 06: The Red Second Hand](06-red-second-hand.md)
