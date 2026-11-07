# Lab 10: A Smooth Sweep
# The red hand glides around the dial instead of ticking. It makes one lap
# a minute, in up to twenty little steps a second -- as many as the display
# can draw.
#
# NEW IDEAS: milliseconds, fractions, and a program that measures its own
# speed.
#
# The Pico's real-time clock (RTC) only counts WHOLE seconds. A gliding
# hand needs finer time than that, so:
#
#   1. wait for the instant the RTC's seconds change
#   2. write down time.ticks_ms(), a counter that adds one every
#      millisecond
#   3. from then on, milliseconds since that instant = ticks_ms() now
#      minus the number we wrote down. time.ticks_diff() does the
#      subtraction, and it keeps working even when the counter wraps.
#
# The hand's angle is then a FRACTION of a lap, times 360 degrees:
#
#     angle = milliseconds into the minute / 60000 * 360
#
# The loop does not draw a fixed number of frames a second. It draws one,
# measures how long that took, and sleeps for whatever is left of
# FRAME_MS. A slow frame just means fewer frames, and the hand is always
# where the clock says it should be. The shell prints the frame rate every
# five seconds, so you can see what your display manages.

NAME = "10-smooth-sweep.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import config
import mondaine

FRAME_MS = 50                   # try for 20 frames a second

display = config.init_display()
face = mondaine.Face(display)
face.draw_dial()

# Line up with the RTC: wait for its seconds to change.
first = time.localtime()[5]
while time.localtime()[5] == first:
    time.sleep_ms(1)
start_tick = time.ticks_ms()
start_second = time.localtime()[5]

frames = 0
report_at = time.ticks_add(start_tick, 5000)

while True:
    frame_start = time.ticks_ms()

    elapsed = time.ticks_diff(frame_start, start_tick)
    ms_into_minute = (start_second * 1000 + elapsed) % 60000
    second_angle = ms_into_minute / 60000 * 360

    t = time.localtime()
    hour, minute = t[3], t[4]
    face.show((hour % 12) * 30 + minute * 0.5, minute * 6, second_angle)

    frames += 1
    if time.ticks_diff(frame_start, report_at) >= 0:
        print("%.1f frames a second" % (frames / 5))
        frames = 0
        report_at = time.ticks_add(report_at, 5000)

    spent = time.ticks_diff(time.ticks_ms(), frame_start)
    time.sleep_ms(max(1, FRAME_MS - spent))
