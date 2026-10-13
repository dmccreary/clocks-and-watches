# Lab 13: A Digital Clock Face

![The clock screen showing 10:09 in tall white digits with a blinking colon. AM is above in cyan and Sun, Oct 11, 2026 is below in yellow. Cyan ticks are lit around the edge, from the top center clockwise to partway up the left side. The unlit ticks and the unlit bars of the digits are faint gray.](img/13-digital-clock-face.gif){ width="336" }

This face has digits 57 pixels tall, big enough to read from across the
room. The date sits below them, and 60 ticks around the edge light up one
by one as the seconds pass.

It never flickers, because it follows one rule: **only send the pixels
that change**.

!!! mascot-welcome "Welcome to Lab 13"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This is the face you can read from the far side of the room. Build it,
    and you'll know how a clock changes a number without a single flicker.
    Let's make time tick!

## What You Will Learn

- how one number can hold seven on/off switches
- how the `^` operator spots the bars that changed
- why unlit bars get a faint "ghost" color
- how 60 ticks fit around a rectangle

## Run It

1. Open `13-digital-clock-face.py` in Thonny and click **Run**.
2. Wait while the screen says `Setting clock`. The Pico gets the time
   over WiFi, as in [lab 10](10-wifi-sync-time.md).
3. Find the time in white, `AM` or `PM` above it, and the date below it.
4. Watch the edge for a full minute. A tick lights up each second, and
   the count starts over with each new minute.

## Seven Switches in One Number

In [lab 09](09-digital-clock.md) you built digits from seven bars,
lettered a to g:

```text
     aaa
    f   b
    f   b
     ggg
    e   c
    e   c
     ddd
```

This lab stores a digit as one number made of seven **bits**. A bit is a
tiny switch: 1 for on, 0 for off. Each bar gets one bit. Here is the
start of the table:

```python
DIGIT_SEGMENTS = (
    0b0111111,  # 0: a b c d e f
    0b0000110,  # 1: b c
    0b1011011,  # 2: a b d e g
    0b1001111,  # 3: a b c d g
    0b1100110,  # 4: b c f g
    ...
)
```

The `0b` means the number is written in **binary**, with only 1s and 0s.
Read the bits from the **right**: a comes first, and g is last on the
left.

Check the 4 by hand. It lights bars b, c, f and g:

| Bar | g | f | e | d | c | b | a |
|---|---|---|---|---|---|---|---|
| Lit in a 4? | yes | yes | no | no | yes | yes | no |
| Bit | 1 | 1 | 0 | 0 | 1 | 1 | 0 |

The bottom row reads `1100110`, just like the 4 in the code.

!!! mascot-encourage "Right to Left Feels Odd"
    ![Chrono encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    Reading bits from right to left feels backward at first, and that's
    normal. You already know which bars make each digit, and a bit is
    just a yes or no for one bar. Write the bits for a 1 on paper, then
    check them against the code.

## Change Only What Changes

When 10:03 becomes 10:04, the last digit changes from a 3 to a 4. Which
bars need new paint? Compare the two patterns, one bit at a time:

| Bar | g | f | e | d | c | b | a |
|---|---|---|---|---|---|---|---|
| Old digit, 3 | 1 | 0 | 0 | 1 | 1 | 1 | 1 |
| New digit, 4 | 1 | 1 | 0 | 0 | 1 | 1 | 0 |
| Different? | 0 | 1 | 0 | 1 | 0 | 0 | 1 |

The bottom row has a 1 wherever the rows above it disagree. Python works
out that row in one step, with an operator called **XOR**, written `^`.
It is a spot-the-difference game for bits.

Only bars f, d and a get new paint. Bars b, c and g are lit in both
digits, so the program never touches them and they cannot flicker. This
part of `draw_digit()` does the work:

```python
    lit = pieces(new)
    if old is None:
        changed = DIGIT_PIECES[i]
    else:
        changed = lit ^ pieces(old)
    for bit in range(13):
        if changed & (1 << bit):
            px, py, w, h = PIECES[bit]
            color = DIGIT_COLOR if lit & (1 << bit) else GHOST
            display.fill_rect(DIGIT_X[i] + px, DIGIT_TOP + py, w, h, color)
```

- `pieces(new)` takes the digit's seven bits and adds six more. They are
  for small squares that fill the corners where bars meet. That makes 13
  pieces.
- `old is None` is true only the first time, when every piece is painted.
- `changed = lit ^ pieces(old)` is the XOR: a 1 for each piece that is
  different.
- `if changed & (1 << bit)` asks, "Is this piece's bit a 1?" If not, the
  loop skips that piece.
- The last two lines pick white or `GHOST`, then paint one small
  rectangle.

## Ghosts and a Half Digit

Look closely at the picture. The faint gray bars behind the digits are
the unlit ones, painted in a **ghost** color that is nearly black. To
turn a bar off, the program paints it in that color. It never clears an
area first, so nothing flashes black.

The first digit is special. On a 12-hour clock it is only ever a 1 or
blank, so it needs just bars b and c. The program draws a narrow **half
digit** there, only 5 pixels wide.

## Sixty Ticks Around a Rectangle

A round clock has a ring of 60 marks. Here the ring is bent to fit the
edge of the screen. Tick 0 is at the top center, and the ticks run
clockwise.

Picture an ant walking around the edge, starting at the top center. All
the way around is 160 + 128 + 160 + 128 = 576 pixels. By tick 15 the ant
has walked 15 × 576 ÷ 60 = 144 pixels. That is 80 to the top right
corner, then 64 down the right side. It is halfway down, where the 3 sits
on a round clock. Ticks 30 and 45 land where the 6 and the 9 sit.

```python
def draw_tick(display, second, lit):
    """Paint one seconds tick, lit or unlit. Both use exactly the same
    pixels, so switching a tick only ever repaints its own pixels."""
    x, y, w, h = TICKS[second]
    display.fill_rect(x, y, w, h, ACCENT if lit else TICK_OFF)
```

`TICKS` holds all 60 rectangles, worked out once at the start. Each tick
is one small rectangle, so a single `fill_rect()` paints it.

In a normal second the face sends only the colon and one tick. That is
65 pixels out of the 20,480 on the screen.

!!! tip "Try This"
    1. Near the top, change `BLINK_COLON = True` to `False`. What stops
       moving?
    2. Change `GHOST = config.color565(24, 24, 30)` to
       `GHOST = config.BLACK`. Which look do you like better?
    3. Change `TWELVE_HOUR = True` to `False` for a 24-hour clock. Why
       does the first digit need all seven bars now?
    4. On paper, compare the patterns for 5 (`0b1101101`) and 6
       (`0b1111101`). How many bars change when a 5 becomes a 6?

## If It Doesn't Work

- **The screen says `No secrets.py found`.** The clock still starts after
  3 seconds, with the time Thonny gave the Pico. To use WiFi time, make
  `secrets.py` as [lab 10](10-wifi-sync-time.md) shows.
- **The time is wrong by a whole hour or more.** Check `TIMEZONE_HOURS`
  in `config.py`. Central time is -6.
- **You have no WiFi.** Change `SYNC_WITH_WIFI = True` to `False`.

!!! mascot-celebration "Big Digits, No Flicker!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You packed a digit into seven bits and used XOR to find the bars that
    changed. You also walked 60 ticks around a rectangle. Next, your clock
    learns to read the weather forecast.

**Next:** [Lab 14: Weather Clock](14-weather-clock.md)
