# Lab 11: An Analog Clock Face

![A round clock face on a black screen, with 60 tick marks around the edge and the numbers 1 to 12. The white hour hand points just past the 10 and the white minute hand points at the 2, so the time is 10:10. A thin red second hand ticks from 7 seconds to 12 seconds, crossing the 2 on the way.](img/11-analog-clock-face.gif){ width="336" }

An **analog** clock shows the time with hands that sweep around a dial.
This lab draws one: 60 tick marks, the numbers 1 to 12, and three moving
hands. It also sets its own time from the internet.

!!! mascot-welcome "Welcome to Lab 11"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Now your kit looks like a clock you could hang on a wall. You will
    aim a hand at any spot on the dial and move it with no flicker.
    Let's make time tick!

## What You Will Learn

- how to turn a time into an angle for each hand
- how to move a hand without redrawing the whole screen
- why the layout of a clock face matters to the program

## Run It

1. Open `11-analog-clock-face.py` in Thonny and click **Run**.
2. The screen says `Setting clock` while it asks the internet for the
   time, as in [lab 10](10-wifi-sync-time.md).
3. The clock face appears, and the red second hand starts to tick.

!!! mascot-tip "No WiFi?"
    ![Chrono giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    Near the top of the program, change `SYNC_WITH_WIFI = True` to
    `SYNC_WITH_WIFI = False`. The clock then skips the internet and uses
    the time Thonny set.

## Every Hand Has an Angle

A hand starts at the center and points out at an **angle**, which is how
far it has turned. This clock measures angles clockwise from 12 o'clock.
A full turn is 360 degrees.

- The second hand takes 60 seconds for a full turn. So each second is
  360 ÷ 60 = 6 degrees. The minute hand moves 6 degrees a minute.
- The hour hand takes 12 hours, so each hour is 360 ÷ 12 = 30 degrees.
  It also creeps forward as the minutes pass.

Check it on the picture at the top, which shows 10:10:

| Hand | The math | Angle | On the picture |
|---|---|---|---|
| Minute | 10 minutes × 6 | 60 degrees | right on the 2, which sits at 2 × 30 = 60 |
| Hour | 10 hours × 30, plus one sixth of 30 for the 10 minutes | 305 degrees | just past the 10, which sits at 300 |

The program does the same math:

```python
def hour_angle(hour, minute):
    # The hour hand creeps forward as the minutes pass: at 3:30 it points
    # halfway between the 3 and the 4.
    return ((hour % 12) + minute / 60) * TWO_PI / 12


def minute_angle(minute):
    return minute * TWO_PI / 60
```

- `TWO_PI` is a full turn. MicroPython's math measures angles in units
  called **radians**, and a full turn is about 6.28 of them. So
  `TWO_PI / 60` is the same slice of the circle as 6 degrees.
- `minute / 60` is the creep. Thirty minutes adds half an hour.

## From an Angle to a Spot on the Screen

To draw a hand, the program needs an x and a y for each end. A function
named `point()` finds them. You give it a direction and a distance, and
it answers with the x and y of that spot.

```python
def draw_second_hand(display, second, color):
    angle = second * TWO_PI / 60
    x0, y0 = point(angle, -SECOND_TAIL)
    x1, y1 = point(angle, SECOND_LENGTH)
    display.line(x0, y0, x1, y1, color)
```

The hand is one line. It runs from a short tail, 9 pixels out the
opposite way (`-SECOND_TAIL`), to the tip, 52 pixels out
(`SECOND_LENGTH`).

Inside, `point()` uses two math functions called sine and cosine. You
will meet them in a later grade.

## Erase, Repair, Draw

!!! mascot-encourage "The Tricky Part"
    ![Chrono giving a thumbs-up](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    This next idea is the hardest in the kit so far, and it is normal to
    read it twice. You did a small version in lab 07, when you repainted
    one box and left the rest alone. Take the three steps one at a time.

Some screens have a **frame buffer**: memory where a program builds the
whole picture before showing it all at once. This kit has none. Every
shape goes straight to the glass, so drawing the whole face again each
second would flicker.

So the dial is drawn only once. After that, the program does three small
jobs each second:

1. **Erase** the old second hand by drawing it again in black.
2. **Repair** the number that the black line cut through.
3. **Draw** all three hands in their new places.

It is like rubbing one chalk line off a chalkboard drawing. The eraser
also wipes a bit of whatever the line crossed, so you draw that bit back.

```python
def update_hands(display, now, last):
    """Move the hands from `last` (hour, minute, second) to `now`.
    `last` is None the first time, when there is nothing to erase."""
    hour, minute, second = now
    if last is not None:
        last_hour, last_minute, last_second = last
        draw_second_hand(display, last_second, BLACK)
        if (hour, minute) != (last_hour, last_minute):
            draw_minute_hand(display, last_minute, BLACK)
            draw_hour_hand(display, last_hour, last_minute, BLACK)
        draw_numeral(display, numeral_under(last_second))

    draw_hour_hand(display, hour, minute, HAND_COLOR)
    draw_minute_hand(display, minute, HAND_COLOR)
    draw_second_hand(display, second, SECOND_COLOR)
    shapes.circle(display, CX, CY, CAP_RADIUS, SECOND_COLOR, config.FILL)
```

- The first `draw_second_hand(...)` is the erase. It draws the old hand
  again in `BLACK`.
- The minute and hour hands are erased only when the minute changes.
- `draw_numeral(...)` is the repair. `numeral_under()` finds the number
  the old second hand lay across.
- The last four lines draw the three hands and the red dot. The white
  hands are drawn every second, in case the black line cut through one.

Only one number needs a repair because of where things sit on the dial.
The tick marks are farther out than any hand reaches. The numbers are
farther out than the hour and minute hands. So only the second hand ever
crosses a number.

!!! tip "Try This"
    1. Change `SECOND_COLOR = config.RED` to `config.CYAN`. Why does the
       dot in the middle change too?
    2. In `draw_numeral()`, change `WHITE, BLACK)` to
       `config.YELLOW, BLACK)`. The numbers stay yellow, even after a
       repair.
    3. Break it on purpose. Change `SECOND_LENGTH = 52` to `60` and watch
       for a minute. The second hand now reaches the tick marks, and its
       black eraser line chews them up. Nothing repairs a tick. Change
       it back when you finish.

## If It Doesn't Work

- **The screen says `Try 3 failed` or `No secrets.py found`, and then
  the time is wrong.** The clock could not reach the internet. Get
  lab 10 working, or use the tip above.
- **A number or a tick has a piece missing.** A hand is too long. Set
  `SECOND_LENGTH` back to 52.

!!! mascot-celebration "Your Clock Has Hands!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You turned hours, minutes, and seconds into angles. You moved three
    hands with no flicker: erase, repair, draw. Next, you will set the
    time by hand with the knob.

**Next:** [Lab 12: Set the Time with the Knob](12-set-time.md)
