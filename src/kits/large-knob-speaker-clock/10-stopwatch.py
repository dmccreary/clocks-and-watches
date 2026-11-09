# Lab 10: Stopwatch
# A stopwatch with lap times, run by the two push buttons:
#
#   K0    (GP11)  start / stop
#   PUSH  (GP10)  lap -- while running, record how long this lap took
#                 reset -- only while stopped, so a bump can't wipe a run
#
# PUSH is the knob itself: press it straight down. Turning the knob does
# nothing in this lab.
#
# The line at the top always shows what the buttons do right now: gray
# when ready, green while running, yellow when stopped. Once there are
# two laps, the fastest one turns green, and the best and average lap
# times appear under the laps. Every press gets a beep from the speaker
# -- a different one for start, stop, lap and reset -- so you can work
# it without looking.
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
# The digits, the frame of ticks, and the text lines come from
# lib/watchparts.py, which only repaints the parts that changed. The
# hundredths digit changes on almost every pass of the loop, but it is
# one small digit, so each pass sends only a few rectangles.

NAME = "10-stopwatch.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import sound
from watchparts import Digit, TickFrame, TextLine, Button, DIGITS

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
TITLE_COLOR = config.CYAN
SMALL = config.SMALL_FONT

READY, RUNNING, STOPPED = 0, 1, 2
STATE_COLORS = (HINT_COLOR, config.GREEN, config.YELLOW)
HINTS = ("K0 start", "K0 stop   PUSH lap", "K0 go   PUSH reset")

MAX_MS = 100 * 60 * 1000 - 10     # 99:59.99, the most these digits can show
LAP_ROWS = 3

# The beeps: (frequency, milliseconds).
START_BEEP = (1320, 40)
STOP_BEEP = (880, 60)
LAP_BEEP = (1760, 30)
RESET_BEEP = (660, 80)

# ---------------------------------------------------------------------
# Layout: MM:SS in 42 x 70 digits, then .hh in 24 x 40 digits, as one
# row centered on the screen with the small digits sitting on the
# baseline. The ticks use the outer 10 pixels of the screen, so
# everything else stays clear of them. A digit's height must be
# 3 x its thickness plus an even number.
# ---------------------------------------------------------------------
MAIN_W, MAIN_H, MAIN_T = 42, 70, 10
SMALL_W, SMALL_H, SMALL_T = 24, 40, 6
PAIR_GAP = 8            # between the two digits of a pair
COLON_GAP = 8           # each side of the colon
POINT_GAP = 6           # each side of the decimal point

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

TITLE_Y = 14            # "STOPWATCH", so you know what this is
HINT_Y = 32
MAIN_TOP = 52
BASELINE = MAIN_TOP + MAIN_H            # 122
SMALL_TOP = BASELINE - SMALL_H
COLON_Y = (MAIN_TOP + MAIN_H // 3 - MAIN_T // 2,
           MAIN_TOP + 2 * MAIN_H // 3 - MAIN_T // 2)
LINE_SPACING = 18
LAP_Y = BASELINE + 8                    # first of LAP_ROWS lines
STATS_Y = LAP_Y + LINE_SPACING * LAP_ROWS + 4   # "Best" and "Average"

# The frame of ticks: short ticks 5 px deep, every fifth one 10 px.
TICK_DEPTH, TICK_DEPTH_FIVE, TICK_LENGTH = 5, 10, 8

# ---------------------------------------------------------------------
# Set up the screen, the buttons and the speaker
# ---------------------------------------------------------------------
display = config.init_display()
display.fill(BLACK)
config.centered_text(display, SMALL, "STOPWATCH", TITLE_Y, TITLE_COLOR)

main_digits = [Digit(display, x, MAIN_TOP, MAIN_W, MAIN_H, MAIN_T,
                     DIGIT_COLOR, GHOST) for x in MAIN_X]
small_digits = [Digit(display, x, SMALL_TOP, SMALL_W, SMALL_H, SMALL_T,
                      DIGIT_COLOR, GHOST) for x in SMALL_X]
hint = TextLine(display, SMALL, config.CENTER_X, HINT_Y, 20, HINT_COLOR)
lap_lines = [TextLine(display, SMALL, config.CENTER_X,
                      LAP_Y + LINE_SPACING * row, 16, OLD_LAP_COLOR)
             for row in range(LAP_ROWS)]
best_line = TextLine(display, SMALL, config.CENTER_X, STATS_Y, 16,
                     FASTEST_COLOR)          # "Best    00:01.50"
average_line = TextLine(display, SMALL, config.CENTER_X,
                        STATS_Y + LINE_SPACING, 16,
                        AVERAGE_COLOR)       # "Average 00:01.83"
frame = TickFrame(display, config.WIDTH, config.HEIGHT, TICK_DEPTH,
                  TICK_DEPTH_FIVE, TICK_LENGTH)

a, b, push, k0 = config.init_controls()     # a and b, the knob, are not used
k0_button = Button(k0)
push_button = Button(push)
sound.init()

# The colon and the decimal point never change.
for y in COLON_Y:
    display.fill_rect(COLON_X, y, MAIN_T, MAIN_T, DIGIT_COLOR)
display.fill_rect(POINT_X, BASELINE - SMALL_T, SMALL_T, SMALL_T, DIGIT_COLOR)
for second in range(60):
    frame.paint(second, TICK_OFF)

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


def beep(spec):
    freq, ms = spec
    sound.tone(freq, ms, wave=sound.SQUARE, level=0.3, attack=2, release=8)


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
        best_line.show("Best    " + format_ms(min(laps)))
        average_line.show("Average " + format_ms(sum(laps) // len(laps)))
    else:
        best_line.show("")
        average_line.show("")


show_laps()

while True:
    now = time.ticks_ms()
    k0_pressed = k0_button.pressed(now)
    push_pressed = push_button.pressed(now)

    if k0_pressed:
        if state == RUNNING:
            banked_ms += time.ticks_diff(now, run_started)
            state = STOPPED
            beep(STOP_BEEP)
        else:                                   # READY or STOPPED: go
            run_started = now
            state = RUNNING
            beep(START_BEEP)
    elif push_pressed and state == RUNNING:     # lap
        total = min(elapsed_ms(now), MAX_MS)
        laps.append(total - lap_started_ms)
        lap_started_ms = total
        beep(LAP_BEEP)
        show_laps()
    elif push_pressed and state == STOPPED:     # reset
        banked_ms = 0
        lap_started_ms = 0
        laps = []
        state = READY
        beep(RESET_BEEP)
        show_laps()

    ms = min(elapsed_ms(now), MAX_MS)
    show_time(ms)

    # One lit tick runs around the edge of the screen, once a minute.
    second = ms // 1000 % 60
    if second != shown_second:
        if shown_second is not None:
            frame.paint(shown_second, TICK_OFF)
        frame.paint(second, ACCENT)
        shown_second = second

    if state != shown_state:
        hint.show(HINTS[state], STATE_COLORS[state])
        shown_state = state

    time.sleep_ms(5)
