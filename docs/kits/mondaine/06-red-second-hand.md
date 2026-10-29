# Lab 06: The Red Second Hand

![The complete Swiss railway clock face at 10:10:25, with a thin red second hand ending in a round red disc pointing toward the 5](img/06-red-second-hand.png){ width="360" }

The most famous part of a Swiss station clock is its red second hand: a
thin rod that ends in a round disc, like the signal paddle a train
dispatcher used to hold up. This lab adds it, and your face is **done**,
frozen at 10:10:25.

!!! mascot-welcome "Welcome to Lab 06"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    This is the finished picture, the face you'll animate for the rest of
    the kit. Only one idea is new here, and it decides what lies on top of
    what. Let's make time tick!

## What You Will Learn

- why **drawing order** matters
- how a hand can be built from two shapes
- how the red disc is sized so it just touches the bars

## Run It

Open `06-red-second-hand.py` in Thonny and click **Run**. The dial and
black hands appear, and the red hand arrives last, lying on top of the
black ones where they cross near the center.

## Two Shapes Make One Hand

The second hand is a thin stem and a disc:

| Part | Size in *a* |
|---|---|
| Stem width | 1.4 |
| Stem reaches back (the tail) | 16.5 behind the center pin |
| Disc diameter | 10.5 |
| Disc center | 31.25 out from the center |

```python
def second_hand(display, angle, color):
    bar(display, angle, -16.5 * A, 31.25 * A, 0.7 * A, color)
    x, y = point(angle, 31.25 * A)
    shapes.circle(display, x, y, round(5.25 * A), color, config.FILL)
```

The stem is a `bar()` from lab 03, with a *negative* start so it reaches
behind the center. The disc is a filled circle at the point 31.25 *a* along
the hand.

## A Tidy Detail

The disc's outer edge is 31.25 + 5.25 = **36.5** *a* from the center. That
is exactly where the heavy five-minute bars *begin*. So when the red hand
points straight at an hour, the disc just touches the bar, as if the clock
had been designed so that the two fit like puzzle pieces. They were.

## Draw Order

The program draws things in this order, and the order is the whole point:

1. the dial and its 60 bars
2. the black hour and minute hands
3. the red second hand

```python
second = 25
...
second_hand(display, second * 6, config.RAIL_RED)    # last, so it is on top
```

Whatever is drawn last lies on top, like laying paper cutouts on a table.
If you drew the red hand *first*, the black hands would cover it near the
center. A display with no memory of what is under each shape, like this
one, has no way to fix that afterward.

!!! mascot-warning "The Red Hand Disappeared!"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If the red hand vanishes under the black ones, you moved its drawing
    to *before* the hour and minute hands. Each new shape paints over
    whatever came before, so put `second_hand(...)` back at the bottom of
    the file.

!!! tip "Try This"
    1. Change `second = 25` to `second = 45`. Where does the disc land?
    2. Move the `second_hand(...)` line above the black hands. What
       changes near the center?
    3. Set `second = 0`, then `second = 15`. Notice the disc just touching
       a big bar each time.

!!! mascot-celebration "The Face Is Finished!"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You built a Swiss-railway face from design units, loops, functions, and
    draw order. Next, you'll stop typing the time into the program and read
    it from the Pico instead.

**Next:** [Lab 07: Show the Real Time](07-read-the-time.md)
