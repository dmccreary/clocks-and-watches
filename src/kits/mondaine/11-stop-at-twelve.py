# Lab 11: Stop at Twelve
# The red hand glides once around the dial in 58.5 seconds, then STOPS at
# the top and waits 1.5 seconds before it sets off again.
#
# NEW IDEAS: if / elif / else to choose between phases of a cycle, and
# constants that name what a number means.
#
# Why wait? On a real Swiss station clock, the second hand is driven by
# its own little motor, and it runs a hair fast. It circles the dial in
# about 58.5 seconds and then parks at 12 until the next minute pulse
# arrives from the master clock. That keeps thousands of clocks in step
# without any of them having to be perfect. It has become the most loved
# detail of the design.
#
# A minute therefore has two phases:
#
#     0 ms ........ 58,500 ms     SWEEP: angle grows from 0 to 360 degrees
#     58,500 ms ... 60,000 ms     HOLD:  the hand rests at the top
#
# mondaine.SweepClock is lab 10's wait-for-the-RTC-tick code in a box.
# clock.now() hands back the hour, the minute, and the milliseconds into
# the minute.
#
# The minute hand does not know about the pause yet. It jumps at the same
# instant the red hand restarts. Lab 12 fixes that.

NAME = "11-stop-at-twelve.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import config
import mondaine

SWEEP_MS = 58500                # one lap takes 58.5 seconds...
FRAME_MS = 50                   # ...drawn up to 20 times a second

display = config.init_display()
face = mondaine.Face(display)
face.draw_dial()
clock = mondaine.SweepClock()

while True:
    frame_start = time.ticks_ms()
    hour, minute, ms = clock.now()

    if ms < SWEEP_MS:
        second_angle = ms / SWEEP_MS * 360      # gliding
    else:
        second_angle = 0                        # waiting at the top

    face.show((hour % 12) * 30 + minute * 0.5, minute * 6, second_angle)

    spent = time.ticks_diff(time.ticks_ms(), frame_start)
    time.sleep_ms(max(1, FRAME_MS - spent))
