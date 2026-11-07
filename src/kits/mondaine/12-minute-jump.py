# Lab 12: The Minute Jump
# The best part. While the red hand waits at 12, the minute hand hops
# ahead one minute -- with a smooth start and a soft landing -- and the
# hour hand creeps a half degree with it. Then the red hand sets off again.
#
# NEW IDEAS: a function that returns a number, an EASING CURVE, and
# clamping a value to a range.
#
# The hop takes 720 ms and begins 150 ms after the red hand stops, so the
# timeline of each minute is:
#
#     0 ............. 58,500   red hand glides around the dial
#     58,500 ........ 58,650   everything is still (a beat)
#     58,650 ........ 59,370   MINUTE HAND HOPS
#     59,370 ........ 60,000   everything is still again
#     60,000 = 0 ..............red hand sets off
#
# progress is how far through the hop we are, from 0.0 to 1.0. Moving the
# hand in a straight line (hop = progress) starts and stops with a jerk,
# like a machine. smootherstep() bends that line into an S: slow, fast,
# slow. The hand seems to have weight.
#
#     progress:    0.0  0.25  0.5  0.75  1.0
#     smootherstep 0.0  0.10  0.5  0.90  1.0
#
# While everything is at rest, the clock re-checks itself against the RTC
# (clock.sync()). That keeps the face from ever drifting from the real
# time, and it makes the red hand set off at exactly the top of the minute.

NAME = "12-minute-jump.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import config
import mondaine

SWEEP_MS = 58500
HOP_START_MS = 58650
HOP_MS = 720
RESYNC_MS = 59400               # the hop is over; nothing is moving
FRAME_MS = 50


def smootherstep(x):
    """Map 0..1 onto an S-shaped curve from 0 to 1."""
    x = max(0.0, min(1.0, x))           # clamp: never below 0 or above 1
    return x * x * x * (x * (x * 6 - 15) + 10)


def hop(ms):
    """0.0 until the hop starts, 1.0 once it is over, an S-curve between."""
    return smootherstep((ms - HOP_START_MS) / HOP_MS)


display = config.init_display()
face = mondaine.Face(display)
face.draw_dial()
clock = mondaine.SweepClock()
synced = False

while True:
    frame_start = time.ticks_ms()
    hour, minute, ms = clock.now()

    step = hop(ms)                               # 0.0 ... 1.0
    minute_angle = (minute + step) * 6
    hour_angle = (hour % 12) * 30 + (minute + step) * 0.5
    second_angle = min(ms, SWEEP_MS) / SWEEP_MS * 360

    face.show(hour_angle, minute_angle, second_angle)

    if ms >= RESYNC_MS and not synced:
        clock.sync()                    # waits for the top of the minute
        synced = True
    elif ms < RESYNC_MS:
        synced = False

    spent = time.ticks_diff(time.ticks_ms(), frame_start)
    time.sleep_ms(max(1, FRAME_MS - spent))
