# app_railway.py -- lab 12's railway clock, as a mode for 20-mode-main.py.
#
# No controls of its own: hold K0 for the next mode.
#
# The red hand glides round in 58.5 seconds, waits at 12, and lets the
# minute hand hop. lib/mondaine.py does the drawing -- read lab 12 and the
# top of lib/mondaine.py for how it moves three overlapping hands 20
# times a second without a frame buffer.
#
# update() is called far more often than 20 times a second, so it only
# draws a new frame once FRAME_MS has gone by. See 20-mode-main.py for
# the three functions every mode has.

import time

import config
import mondaine

FRAME_MS = 50            # up to 20 frames a second

BLACK = config.BLACK
CORNER_COLOR = config.WHITE
DIM = config.color565(150, 150, 150)
SMALL = config.SMALL_FONT
BIG = config.BIG_FONT
MARGIN = 4

DAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")


def draw_corners():
    """Day top left, date top right."""
    t = time.localtime()
    right = config.WIDTH - MARGIN
    _display.text(BIG, DAYS[t[6]], MARGIN, MARGIN, CORNER_COLOR, BLACK)
    _display.text(BIG, "%2d" % t[2], right - 2 * BIG.WIDTH, MARGIN,
                  CORNER_COLOR, BLACK)
    _display.text(SMALL, MONTHS[t[1] - 1], right - 3 * SMALL.WIDTH,
                  MARGIN + BIG.HEIGHT + 2, DIM, BLACK)
    return t[2]


def start(display, k0, push, knob, saved):
    global _display, face, clock, last_frame, at_rest, shown_day
    _display = display
    face = mondaine.Face(display)
    face.draw_dial()
    shown_day = draw_corners()
    clock = mondaine.SweepClock()    # waits up to a second for the RTC tick
    last_frame = None
    at_rest = False


def update(now):
    global last_frame, at_rest, shown_day
    if last_frame is not None and time.ticks_diff(now, last_frame) < FRAME_MS:
        return
    last_frame = now
    hour, minute, ms = clock.now()
    face.show(*mondaine.hand_angles(hour, minute, ms))
    if ms >= mondaine.RESYNC_MS:
        if not at_rest:
            # Every hand is still: line the milliseconds up with the
            # Pico's clock again, and check the date.
            at_rest = True
            clock.sync()
            if time.localtime()[2] != shown_day:
                shown_day = draw_corners()
    else:
        at_rest = False


def stop():
    return None
