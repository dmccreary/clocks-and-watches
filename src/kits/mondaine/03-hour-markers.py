# Lab 03: Twelve Bars
# Replaces the dots with the twelve heavy black bars of a Swiss railway
# clock.
#
# NEW IDEAS: writing your own FUNCTIONS with def, and a design UNIT that
# makes a whole drawing scale together.
#
# The railway clock was designed so that every size is a multiple of one
# unit, "a", that is 1/100 of the dial's diameter. A five-minute bar is
# 12 a long and 3.5 a wide; it ends 48.5 a from the center. Change A below
# and every bar grows or shrinks with it.
#
# Two functions do the work. point() is lab 02's sine-and-cosine math, with
# one new trick: `across` slides a point sideways, at right angles to the
# line from the center. bar() uses it to find the four corners of a
# rectangle pointing out at any angle, and shapes.poly() fills them in.

NAME = "03-hour-markers.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
from array import array
import config
import shapes

A = 3.4                 # one design unit, in pixels (the dial is 100 a)
CENTER_X = config.CENTER_X
CENTER_Y = config.CENTER_Y


def point(angle, along, across=0):
    """The screen position `along` pixels out from the center in the
    direction of `angle` degrees, and `across` pixels to the right of that
    line."""
    a = math.radians(angle)
    x = CENTER_X + along * math.sin(a) + across * math.cos(a)
    y = CENTER_Y - along * math.cos(a) + across * math.sin(a)
    return round(x), round(y)


def bar(display, angle, inner, outer, half_width, color):
    """A black rectangle pointing at `angle`, from `inner` to `outer`
    pixels out, and 2 x half_width pixels wide."""
    x0, y0 = point(angle, inner, -half_width)
    x1, y1 = point(angle, outer, -half_width)
    x2, y2 = point(angle, outer, half_width)
    x3, y3 = point(angle, inner, half_width)
    corners = array('h', [x0, y0, x1, y1, x2, y2, x3, y3])
    shapes.poly(display, 0, 0, corners, color, config.FILL)


display = config.init_display()
display.fill(config.WHITE)

for hour in range(12):
    bar(display, hour * 30, 36.5 * A, 48.5 * A, 1.75 * A, config.BLACK)
