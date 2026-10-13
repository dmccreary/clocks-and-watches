# mode_digital.py -- the digital clock face of lab 13, as a mode for
# 17-main-template.py. Lab 13 explains how it works; this version builds
# the same face from the parts in lib/watchparts.py.
#
# Every mode has the same four functions -- see 17-main-template.py. A
# mode only gets rows 0 to 119 of the screen, because the mode dots go
# below, so this face is 8 rows shorter than lab 13's.

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

# Layout, the same as lab 13 but fitted into 120 rows.
MODE_ROWS = 120         # rows 0 to 119
DIGIT_W, DIGIT_H, DIGIT_T = 29, 57, 5
PAIR_GAP = 5
COLON_GAP = 6
AMPM_Y = 11
DIGIT_TOP = 30
DATE_Y = 92

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

    frame = TickFrame(display, config.WIDTH, MODE_ROWS)
    ampm = TextLine(display, config.SMALL_FONT, config.CENTER_X, AMPM_Y, 2,
                    ACCENT)
    date_line = TextLine(display, config.SMALL_FONT, config.CENTER_X,
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
