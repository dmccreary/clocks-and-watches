# Lab 10: Stopwatch
# A stopwatch with lap times, run by the three buttons:
#
#   UP    (GP14)  start / stop
#   MODE  (GP13)  lap -- while running, record how long this lap took
#   DOWN  (GP15)  reset -- only while stopped, so a bump can't wipe a run
#
# A line near the top always shows what the buttons do right now. Once
# there are two laps, the fastest one turns green, and the best and
# average lap times appear just under the digits.
#
# HOW A STOPWATCH KEEPS TIME. It never counts up by adding a little each
# time around the loop -- the loop's speed changes every time it draws
# something, and the errors would pile up. Instead it remembers WHEN it
# started, and every time it needs the elapsed time it asks the Pico's
# millisecond clock:
#
#     elapsed = banked_ms + ticks_diff(now, run_started)
#
# banked_ms holds the time from earlier runs, so stopping and starting
# again carries on from where it left off.
#
# The digits, the ring, and the text lines come from lib/watchparts.py,
# which packages the "only repaint what changed" parts from labs 07 and 08.
# The hundredths digit changes on almost every pass of the loop, but it
# is one small digit, so each pass sends only a few rectangles.

NAME = "10-stopwatch.py"
VERSION = "1.1"
print("{} v{}".format(NAME, VERSION))

import time

import config
from watchparts import Digit, TickRing, TextLine, Button, DIGITS

BLACK = config.BLACK
DIGIT_COLOR = config.WHITE
GHOST = config.color565(24, 24, 30)
ACCENT = config.CYAN
TICK_OFF = config.color565(40, 40, 40)
HINT_COLOR = config.color565(150, 150, 150)
NEW_LAP_COLOR = config.YELLOW
OLD_LAP_COLOR = config.color565(170, 170, 120)
FASTEST_COLOR = config.GREEN
AVERAGE_COLOR = config.CYAN
SMALL = config.SMALL_FONT

READY, RUNNING, STOPPED = 0, 1, 2
STATE_NAMES = ("READY", "RUNNING", "STOPPED")
STATE_COLORS = (HINT_COLOR, config.GREEN, config.YELLOW)
HINTS = ("UP start", "UP stop  MODE lap", "UP go  DOWN reset")

MAX_MS = 100 * 60 * 1000 - 10     # 99:59.99, the most these digits can show
LAP_ROWS = 3

# ---------------------------------------------------------------------
# Layout: MM:SS in 71 px digits, then .hh in 40 px digits, as one row
# centered on the screen with the small digits sitting on the baseline.
# ---------------------------------------------------------------------
MAIN_W, MAIN_H, MAIN_T = 40, 71, 9
SMALL_W, SMALL_H, SMALL_T = 22, 40, 6
PAIR_GAP = 7            # between the two digits of a pair
COLON_GAP = 8           # each side of the colon
POINT_GAP = 5           # each side of the decimal point

_row = (4 * MAIN_W + 2 * PAIR_GAP + 2 * COLON_GAP + MAIN_T
        + POINT_GAP + SMALL_T + POINT_GAP + 2 * SMALL_W + PAIR_GAP)
_x = (config.WIDTH - _row) // 2
MAIN_X = []
MAIN_X.append(_x)
MAIN_X.append(_x + MAIN_W + PAIR_GAP)
COLON_X = MAIN_X[1] + MAIN_W + COLON_GAP
MAIN_X.append(COLON_X + MAIN_T + COLON_GAP)
MAIN_X.append(MAIN_X[2] + MAIN_W + PAIR_GAP)
POINT_X = MAIN_X[3] + MAIN_W + POINT_GAP
SMALL_X = (POINT_X + SMALL_T + POINT_GAP,
           POINT_X + SMALL_T + POINT_GAP + SMALL_W + PAIR_GAP)

MAIN_TOP = config.CENTER_Y - MAIN_H // 2
BASELINE = MAIN_TOP + MAIN_H
SMALL_TOP = BASELINE - SMALL_H
COLON_Y = (MAIN_TOP + MAIN_H // 3 - MAIN_T // 2,
           MAIN_TOP + 2 * MAIN_H // 3 - MAIN_T // 2)

TITLE_Y = 56
HINT_Y = 84
STATE_Y = 112
STATS_Y = BASELINE + 10  # "Best ..." and "Avg ...", side by side
LAP_Y = STATS_Y + 22    # first of LAP_ROWS lines, 18 px apart

# ---------------------------------------------------------------------
# Set up the screen
# ---------------------------------------------------------------------
display = config.init_display()
display.fill(BLACK)

main_digits = [Digit(display, x, MAIN_TOP, MAIN_W, MAIN_H, MAIN_T,
                     DIGIT_COLOR, GHOST) for x in MAIN_X]
small_digits = [Digit(display, x, SMALL_TOP, SMALL_W, SMALL_H, SMALL_T,
                      DIGIT_COLOR, GHOST) for x in SMALL_X]
title = TextLine(display, SMALL, config.CENTER_X, TITLE_Y, 9, HINT_COLOR)
hint = TextLine(display, SMALL, config.CENTER_X, HINT_Y, 20, HINT_COLOR)
status = TextLine(display, SMALL, config.CENTER_X, STATE_Y, 7, HINT_COLOR)
lap_lines = [TextLine(display, SMALL, config.CENTER_X, LAP_Y + 18 * row, 16,
                      OLD_LAP_COLOR) for row in range(LAP_ROWS)]
best_line = TextLine(display, SMALL, config.CENTER_X - 58, STATS_Y, 13,
                     FASTEST_COLOR)          # "Best 00:01.50"
average_line = TextLine(display, SMALL, config.CENTER_X + 56, STATS_Y, 12,
                        AVERAGE_COLOR)       # "Avg 00:01.83"
ring = TickRing(display, config.CENTER_X, config.CENTER_Y,
                config.SAFE_RADIUS - 2, config.SAFE_RADIUS - 10,
                config.SAFE_RADIUS - 16)

mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]

# The colon, the decimal point, and the title never change.
for y in COLON_Y:
    display.fill_rect(COLON_X, y, MAIN_T, MAIN_T, DIGIT_COLOR)
display.fill_rect(POINT_X, BASELINE - SMALL_T, SMALL_T, SMALL_T, DIGIT_COLOR)
title.show("STOPWATCH")
for second in range(60):
    ring.paint(second, TICK_OFF)

# ---------------------------------------------------------------------
# The stopwatch
# ---------------------------------------------------------------------
state = READY
run_started = 0     # ticks_ms() when the current run began
banked_ms = 0       # time from earlier runs, before the last stop
laps = []           # how long each lap took, in ms
lap_started_ms = 0  # the elapsed time when the current lap began

shown_state = None
shown_second = None


def elapsed_ms(now):
    if state == RUNNING:
        return banked_ms + time.ticks_diff(now, run_started)
    return banked_ms


def format_ms(ms):
    return "%02d:%02d.%02d" % (ms // 60000, ms // 1000 % 60, ms // 10 % 100)


def show_time(ms):
    minutes = ms // 60000
    seconds = ms // 1000 % 60
    hundredths = ms // 10 % 100
    for digit, value in zip(main_digits, (minutes // 10, minutes % 10,
                                          seconds // 10, seconds % 10)):
        digit.show(DIGITS[value])
    small_digits[0].show(DIGITS[hundredths // 10])
    small_digits[1].show(DIGITS[hundredths % 10])


def show_laps():
    """List the newest laps, newest on top, and the best and average lap.

    With two or more laps, the fastest one is green -- if it is still one
    of the rows on screen. The "Best" line always shows it, even after it
    has scrolled off the list."""
    fastest = 0                      # lap number of the fastest lap, 0 = none
    if len(laps) >= 2:
        fastest = laps.index(min(laps)) + 1
    for row in range(LAP_ROWS):
        number = len(laps) - row     # the lap shown on this row
        if number >= 1:
            if number == fastest:
                color = FASTEST_COLOR
            elif row == 0:
                color = NEW_LAP_COLOR
            else:
                color = OLD_LAP_COLOR
            lap_lines[row].show("Lap %3d %s" % (number,
                                                format_ms(laps[number - 1])),
                                color)
        else:
            lap_lines[row].show("")
    if fastest:
        best_line.show("Best " + format_ms(min(laps)))
        average_line.show("Avg " + format_ms(sum(laps) // len(laps)))
    else:
        best_line.show("")
        average_line.show("")


show_laps()

while True:
    now = time.ticks_ms()
    up = up_button.pressed(now)
    down = down_button.pressed(now)
    mode = mode_button.pressed(now)

    if up:
        if state == RUNNING:
            banked_ms += time.ticks_diff(now, run_started)
            state = STOPPED
        else:                                   # READY or STOPPED: go
            run_started = now
            state = RUNNING
    elif mode and state == RUNNING:
        total = min(elapsed_ms(now), MAX_MS)
        laps.append(total - lap_started_ms)
        lap_started_ms = total
        show_laps()
    elif down and state == STOPPED:
        banked_ms = 0
        lap_started_ms = 0
        laps = []
        state = READY
        show_laps()

    ms = min(elapsed_ms(now), MAX_MS)
    show_time(ms)

    # One lit tick runs around the rim, once a minute.
    second = ms // 1000 % 60
    if second != shown_second:
        if shown_second is not None:
            ring.paint(shown_second, TICK_OFF)
        ring.paint(second, ACCENT)
        shown_second = second

    if state != shown_state:
        status.show(STATE_NAMES[state], STATE_COLORS[state])
        hint.show(HINTS[state])
        shown_state = state

    time.sleep_ms(5)
