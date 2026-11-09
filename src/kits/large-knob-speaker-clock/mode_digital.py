# mode_digital.py -- a digital clock face, as a mode for 16-main-template.py.
#
# Big seven-segment digits built from the parts in lib/watchparts.py, a
# blinking colon, AM/PM, the date, and a frame of 60 ticks around the
# edge that fills up, one tick per second, as the minute goes by.
#
# The digits keep their unlit segments painted a faint "ghost" color,
# like a real LCD clock. A Digit remembers which segments it lit, so a
# new digit repaints only the segments that changed: going from 8 to 9
# repaints one bar, not the whole digit.
#
# Every mode has the same four functions -- see 16-main-template.py. A
# mode only gets rows 0 to 219 of the screen, because the mode dots go
# below.

import time

import config
from watchparts import Digit, TickFrame, TextLine, DIGITS, BLANK

TWELVE_HOUR = True
BLINK_COLON = True

DIGIT_COLOR = config.WHITE
GHOST = config.color565(24, 24, 30)
ACCENT = config.CYAN
TICK_OFF = config.color565(40, 40, 40)
TEXT_COLOR = config.YELLOW

# Layout. A digit's height must be 3 x its thickness plus an even number.
MODE_ROWS = 220         # rows 0 to 219
DIGIT_W, DIGIT_H, DIGIT_T = 58, 114, 10
PAIR_GAP = 10
COLON_GAP = 12
AMPM_Y = 20
DIGIT_TOP = 46
DATE_Y = 172

# The frame of ticks: short ticks 5 px deep, every fifth one 10 px.
TICK_DEPTH, TICK_DEPTH_FIVE, TICK_LENGTH = 5, 10, 8

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def start(display, k0, push, saved):
    global _display, digits, frame, ampm, date_line, colon_x, colon_y
    global shown_second, shown_colon
    _display = display
    display.fill_rect(0, 0, config.WIDTH, MODE_ROWS, config.BLACK)

    # One row, centered: a half digit (12-hour) or a full one, then the
    # other three digits with the colon between the pairs.
    first_width = DIGIT_T if TWELVE_HOUR else DIGIT_W
    row = first_width + 3 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T
    x = (config.WIDTH - row) // 2
    digits = [Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                    DIGIT_COLOR, GHOST, half=TWELVE_HOUR)]
    x += first_width + PAIR_GAP
    digits.append(Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                        DIGIT_COLOR, GHOST))
    x += DIGIT_W + COLON_GAP
    colon_x = x
    x += DIGIT_T + COLON_GAP
    for _ in range(2):
        digits.append(Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                            DIGIT_COLOR, GHOST))
        x += DIGIT_W + PAIR_GAP
    colon_y = (DIGIT_TOP + DIGIT_H // 3 - DIGIT_T // 2,
               DIGIT_TOP + 2 * DIGIT_H // 3 - DIGIT_T // 2)

    frame = TickFrame(display, config.WIDTH, MODE_ROWS, TICK_DEPTH,
                      TICK_DEPTH_FIVE, TICK_LENGTH)
    ampm = TextLine(display, config.SMALL_FONT, config.CENTER_X, AMPM_Y, 2,
                    ACCENT)
    date_line = TextLine(display, config.BIG_FONT, config.CENTER_X,
                         DATE_Y, 17, TEXT_COLOR)
    shown_second = None
    shown_colon = None


def update(now):
    global shown_second, shown_colon
    year, month, day, hour, minute, second, weekday = time.localtime()[:7]
    if second == shown_second:
        return
    shown_second = second

    shown_hour = (hour % 12 or 12) if TWELVE_HOUR else hour
    tens = shown_hour // 10
    first = DIGITS[tens] if (tens or not TWELVE_HOUR) else BLANK
    for digit, pattern in zip(digits, (first, DIGITS[shown_hour % 10],
                                       DIGITS[minute // 10],
                                       DIGITS[minute % 10])):
        digit.show(pattern)

    colon = (second % 2 == 0) if BLINK_COLON else True
    if colon != shown_colon:
        for y in colon_y:
            _display.fill_rect(colon_x, y, DIGIT_T, DIGIT_T,
                               DIGIT_COLOR if colon else GHOST)
        shown_colon = colon

    # Ticks 0 through `second` are lit. paint() skips ticks that already
    # have the right color, so this normally repaints just one.
    for i in range(60):
        frame.paint(i, ACCENT if i <= second else TICK_OFF)

    if TWELVE_HOUR:
        ampm.show("AM" if hour < 12 else "PM")
    date_line.show("%s, %s %d, %d" % (DAYS[weekday], MONTHS[month - 1],
                                      day, year))


def stop():
    return None
