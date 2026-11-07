# mode_mondaine.py -- mode 7, the Swiss-railway-style clock from the
# mondaine kit (src/kits/mondaine). lib/mondaine.py is copied from there
# unchanged; its header explains the face and the famous stop-and-go red
# hand, which glides round in 58.5 s, waits at 12, and lets the minute
# hand hop.
#
# What this mode changes:
#   - The heavy bar at 6 o'clock is drawn as a thin minute bar, which
#     starts below the mode dots instead of running through them.
#   - The dots are black and gray, because the dial is white (mode-template
#     reads DOT_ON and DOT_OFF from here).
#   - The minute hand is long enough to cross the dots around half past
#     the hour, and repainting the face behind it would rub them out. So
#     once a minute, after it has hopped, update() returns True and
#     mode-template.py draws the dots again.
#
# No buttons of its own: tap MODE for the next mode.
#
# Every mode has the same functions -- see mode-template.py.

import time

import config
import mondaine
import shared

DOT_ON = config.BLACK
DOT_OFF = config.color565(190, 190, 190)
FRAME_MS = 50                        # up to 20 frames a second


def start(display, up, down, saved):
    global face, clock, last_frame, at_rest
    face = mondaine.Face(display, band=shared.band)
    # Swap the five-minute bar at 6 o'clock for a minute bar.
    u = face.unit
    inner, outer, half = mondaine.MINUTE_BAR
    face.bars[30] = face._corners(180, inner * u, outer * u, half * u,
                                  half * u)
    face.bar_tops[30] = min(p[1] for p in face.bars[30])
    face.bar_bottoms[30] = max(p[1] for p in face.bars[30])
    face.draw_dial()
    clock = mondaine.SweepClock()    # waits up to a second for the RTC tick
    last_frame = None
    at_rest = False


def update(now):
    global last_frame, at_rest
    if last_frame is not None and time.ticks_diff(now, last_frame) < FRAME_MS:
        return False
    last_frame = now
    hour, minute, ms = clock.now()
    face.show(*mondaine.hand_angles(hour, minute, ms))
    if ms >= mondaine.RESYNC_MS:
        if not at_rest:
            # Every hand is still: line the milliseconds up with the RTC
            # again (it may have been set over WiFi), and ask for the dots.
            at_rest = True
            clock.sync()
            return True
    else:
        at_rest = False
    return False


def stop():
    return None
