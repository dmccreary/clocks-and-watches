# Lab 09: Tick Tock
# The clock runs. The red hand jumps ahead once a second, like an ordinary
# quartz clock, and the black hands follow the minutes.
#
# NEW IDEAS: the while True loop, and DOING WORK ONLY WHEN SOMETHING
# CHANGED.
#
# The loop below runs about 50 times a second, but the clock only needs to
# change when the second does. Remembering the last second shown
# (last_second) and comparing it to the new one is the oldest trick in
# animation: don't redraw what is already right.
#
# THIS DISPLAY HAS NO FRAME BUFFER, so a careless redraw is expensive: the
# whole face is 129,600 pixels, and every one has to travel down the SPI
# wire. face.show() is careful. It works out which rows of pixels the
# moving hand actually touches and repaints only those, so a tick costs a
# fraction of a redraw.
#
# Run it and watch the minute hand: at the top of every minute it jumps a
# whole 6 degrees at once, in the same instant the red hand starts a new
# lap. Real railway clocks do something far more graceful. That is what
# labs 10 to 12 build.

NAME = "09-tick-tock.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import config
import mondaine

display = config.init_display()
face = mondaine.Face(display)
face.draw_dial()

last_second = -1

while True:
    t = time.localtime()
    hour, minute, second = t[3], t[4], t[5]

    if second != last_second:
        last_second = second
        face.show((hour % 12) * 30 + minute * 0.5,   # hour hand
                  minute * 6,                         # minute hand
                  second * 6)                         # second hand

    time.sleep_ms(20)
