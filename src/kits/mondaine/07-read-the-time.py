# Lab 07: Show the Real Time
# Reads the Pico's real-time clock and points the three hands at it.
#
# NEW IDEAS: tuples and unpacking, formatted text, and using a module
# somebody else wrote -- in this case, the one you just finished.
#
# Labs 02 to 06 built the clock face piece by piece. lib/mondaine.py
# packages all of it, so from here on a lab can start with just:
#
#     face = mondaine.Face(display)
#     face.draw_dial()                      # white dial with 60 bars
#     face.show(hour_deg, minute_deg, second_deg)
#
# time.localtime() returns a TUPLE of eight numbers:
#
#     (year, month, day, hour, minute, second, weekday, day of year)
#
# Python can UNPACK a tuple into eight variables in one line, as below.
#
# The Pico forgets the time when it loses power. If Thonny started this
# program, Thonny set the clock for you and the face will be right. On a
# battery or a wall plug it starts at midnight on January 1, until lab 08
# teaches it to ask the internet.

NAME = "07-read-the-time.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import config
import mondaine

display = config.init_display()
face = mondaine.Face(display)
face.draw_dial()

year, month, day, hour, minute, second, weekday, day_of_year = time.localtime()
print("%d-%02d-%02d  %02d:%02d:%02d" % (year, month, day, hour, minute, second))

# The same angle rules as lab 05 and lab 06.
hour_angle = (hour % 12) * 30 + minute * 0.5
minute_angle = minute * 6
second_angle = second * 6

face.show(hour_angle, minute_angle, second_angle)
