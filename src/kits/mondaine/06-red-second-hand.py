# Lab 06: The Red Second Hand
# Adds the red hand with the round disc on its end -- the part of the
# clock that everyone remembers. The face is now complete, frozen at
# 10:10:25.
#
# NEW IDEA: DRAW ORDER. Whatever you draw last lies on top. The red hand
# crosses the black hands near the center, and it only looks right if the
# red is painted AFTER the black. Swap the last two blocks and see.
#
# The second hand is two shapes:
#
#   a thin stem   1.4 a wide, from 16.5 a behind the center pin to the
#                 middle of the disc, 31.25 a out
#   a solid disc  10.5 a across, centered 31.25 a out
#
# The numbers are chosen so the disc's outer edge reaches exactly 36.5 a
# from the center -- the INNER end of the big bars. When the hand points at
# a bar, the disc just touches it.
#
# The second hand moves 6 degrees a second: 360 degrees / 60 seconds.

NAME = "06-red-second-hand.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
from array import array
import config
import shapes

A = 3.4                 # one design unit, in pixels (the dial is 100 a)
CENTER_X = config.CENTER_X
CENTER_Y = config.CENTER_Y

HOUR_HAND = (12, 3.2, 32, 2.6)
MINUTE_HAND = (12, 2.6, 46, 1.8)

hour = 10
minute = 10
second = 25


def point(angle, along, across=0):
    a = math.radians(angle)
    x = CENTER_X + along * math.sin(a) + across * math.cos(a)
    y = CENTER_Y - along * math.cos(a) + across * math.sin(a)
    return round(x), round(y)


def bar(display, angle, inner, outer, half_width, color):
    x0, y0 = point(angle, inner, -half_width)
    x1, y1 = point(angle, outer, -half_width)
    x2, y2 = point(angle, outer, half_width)
    x3, y3 = point(angle, inner, half_width)
    corners = array('h', [x0, y0, x1, y1, x2, y2, x3, y3])
    shapes.poly(display, 0, 0, corners, color, config.FILL)


def hand(display, angle, size, color):
    tail, tail_half, tip, tip_half = size
    x0, y0 = point(angle, -tail * A, -tail_half * A)
    x1, y1 = point(angle, tip * A, -tip_half * A)
    x2, y2 = point(angle, tip * A, tip_half * A)
    x3, y3 = point(angle, -tail * A, tail_half * A)
    corners = array('h', [x0, y0, x1, y1, x2, y2, x3, y3])
    shapes.poly(display, 0, 0, corners, color, config.FILL)


def second_hand(display, angle, color):
    """The stem, then the disc on top of it."""
    bar(display, angle, -16.5 * A, 31.25 * A, 0.7 * A, color)
    x, y = point(angle, 31.25 * A)
    shapes.circle(display, x, y, round(5.25 * A), color, config.FILL)


display = config.init_display()
display.fill(config.WHITE)

for tick in range(60):
    if tick % 5 == 0:
        bar(display, tick * 6, 36.5 * A, 48.5 * A, 1.75 * A, config.BLACK)
    else:
        bar(display, tick * 6, 45.0 * A, 48.5 * A, 0.7 * A, config.BLACK)

hand(display, (hour % 12) * 30 + minute * 0.5, HOUR_HAND, config.BLACK)
hand(display, minute * 6, MINUTE_HAND, config.BLACK)

# Last, so it lies on top of everything.
second_hand(display, second * 6, config.RAIL_RED)
