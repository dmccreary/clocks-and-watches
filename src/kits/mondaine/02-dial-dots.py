# Lab 02: Twelve Dots in a Circle
# Puts twelve black dots around a white dial, one for every hour.
#
# NEW IDEAS: variables, the for loop, and sine and cosine -- the two math
# tools that turn an ANGLE into a position on the screen.
#
# A clock measures angles from 12 o'clock, going clockwise. Twelve hours
# share a full circle of 360 degrees, so each hour is 360 / 12 = 30
# degrees past the one before it.
#
#     x = CENTER_X + distance * sin(angle)
#     y = CENTER_Y - distance * cos(angle)
#
# Why the minus sign on y? On a screen, y grows DOWNWARD. The minus flips
# it, so angle 0 points UP, at the 12.

NAME = "02-dial-dots.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import config
import shapes

CENTER_X = config.CENTER_X
CENTER_Y = config.CENTER_Y
DISTANCE = 150          # how far each dot sits from the center, in pixels
DOT_RADIUS = 7

display = config.init_display()
display.fill(config.WHITE)

for hour in range(12):                  # hour is 0, 1, 2, ... 11
    degrees = hour * 30
    angle = math.radians(degrees)       # sin() and cos() want radians
    x = round(CENTER_X + DISTANCE * math.sin(angle))
    y = round(CENTER_Y - DISTANCE * math.cos(angle))
    print("hour", hour, "angle", degrees, "dot at", x, y)
    shapes.circle(display, x, y, DOT_RADIUS, config.BLACK, config.FILL)
