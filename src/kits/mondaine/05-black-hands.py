# Lab 05: The Hour and Minute Hands
# Draws the two black hands, pointing at 10:10.
#
# NEW IDEAS: turning a time into angles, and a function with MANY
# arguments that draws a tapered shape.
#
# The minute hand turns 360 degrees in 60 minutes: 6 degrees a minute.
# The hour hand turns 360 degrees in 12 hours: 30 degrees an hour. But it
# does not wait until the hour is over to move. At 10:30 it points halfway
# between the 10 and the 11, so it also creeps 0.5 degrees every minute
# (30 degrees / 60 minutes).
#
# Both hands are a little wider at the center than at the tip, and both
# stick out a short way BEHIND the center pin. Those four numbers describe
# any hand (design units "a" again):
#
#     hand      tail   tail width   tip    tip width
#     hour       12      6.4         32      5.2
#     minute     12      5.2         46      3.6

NAME = "05-black-hands.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
from array import array
import config
import shapes

A = 3.4                 # one design unit, in pixels (the dial is 100 a)
CENTER_X = config.CENTER_X
CENTER_Y = config.CENTER_Y

# (tail length, tail half width, tip length, tip half width), in units of a
HOUR_HAND = (12, 3.2, 32, 2.6)
MINUTE_HAND = (12, 2.6, 46, 1.8)

hour = 10
minute = 10


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
    """A tapered hand: wide at the tail, narrower at the tip."""
    tail, tail_half, tip, tip_half = size
    x0, y0 = point(angle, -tail * A, -tail_half * A)
    x1, y1 = point(angle, tip * A, -tip_half * A)
    x2, y2 = point(angle, tip * A, tip_half * A)
    x3, y3 = point(angle, -tail * A, tail_half * A)
    corners = array('h', [x0, y0, x1, y1, x2, y2, x3, y3])
    shapes.poly(display, 0, 0, corners, color, config.FILL)


display = config.init_display()
display.fill(config.WHITE)

# The dial from lab 04.
for tick in range(60):
    if tick % 5 == 0:
        bar(display, tick * 6, 36.5 * A, 48.5 * A, 1.75 * A, config.BLACK)
    else:
        bar(display, tick * 6, 45.0 * A, 48.5 * A, 0.7 * A, config.BLACK)

# Time to angles.
minute_angle = minute * 6
hour_angle = (hour % 12) * 30 + minute * 0.5
print("minute hand at", minute_angle, "degrees; hour hand at", hour_angle)

hand(display, hour_angle, HOUR_HAND, config.BLACK)
hand(display, minute_angle, MINUTE_HAND, config.BLACK)
