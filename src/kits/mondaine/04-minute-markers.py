# Lab 04: Sixty Bars
# Adds the 48 small minute bars between the 12 big ones, to make the whole
# dial.
#
# NEW IDEAS: the remainder operator % and the if / else decision.
#
#     minute % 5   is the REMAINDER left over after dividing by 5.
#
# Minutes 0, 5, 10, 15 ... leave a remainder of 0, so they are the big
# bars. Every other minute leaves 1, 2, 3, or 4, and gets a small bar.
# One loop of 60 laps draws all of them, with an `if` choosing the size.
#
# Compare the two sizes, in design units "a" (see lab 03):
#
#     five-minute bar    36.5 a to 48.5 a   3.5 a wide
#     minute bar         45.0 a to 48.5 a   1.4 a wide

NAME = "04-minute-markers.py"
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


display = config.init_display()
display.fill(config.WHITE)

for minute in range(60):                # 0, 1, 2, ... 59
    angle = minute * 6                  # 360 degrees / 60 minutes
    if minute % 5 == 0:
        bar(display, angle, 36.5 * A, 48.5 * A, 1.75 * A, config.BLACK)
    else:
        bar(display, angle, 45.0 * A, 48.5 * A, 0.7 * A, config.BLACK)
