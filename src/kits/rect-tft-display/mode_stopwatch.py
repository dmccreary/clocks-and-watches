# mode_stopwatch.py -- the stopwatch of lab 15, as a mode for
# 17-main-template.py. Lab 15 explains how it keeps time.
#
# The buttons do what they do in lab 15:
#
#   K0    start / stop
#   PUSH  lap while running, reset while stopped
#
# The knob belongs to the clock here: turning it switches modes. That
# does not stop the stopwatch. stop() hands back when it started and what
# it had banked, and because the time always comes from the Pico's
# millisecond clock, it is still right when you come back.
#
# Every mode has the same four functions -- see 17-main-template.py. A
# mode only gets rows 0 to 119 of the screen, because the mode dots go
# below, so the digits are shorter than lab 15's.

import time

import config
from watchparts import Digit, TickFrame, TextLine, DIGITS

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
TINY = config.TINY_FONT

READY, RUNNING, STOPPED = 0, 1, 2
STATE_COLORS = (HINT_COLOR, config.GREEN, config.YELLOW)
HINTS = ("K0 start", "K0 stop  PUSH lap", "K0 go  PUSH reset")

MAX_MS = 100 * 60 * 1000 - 10     # 99:59.99
LAP_ROWS = 2

# Layout, the same as lab 15 except for the height of the digits.
MODE_ROWS = 120         # rows 0 to 119
MAIN_W, MAIN_H, MAIN_T = 20, 33, 5
SMALL_W, SMALL_H, SMALL_T = 12, 19, 3
PAIR_GAP = 4
COLON_GAP = 4
POINT_GAP = 3
HINT_Y = 7
MAIN_TOP = 25
BASELINE = MAIN_TOP + MAIN_H
LAP_Y = BASELINE + 3
STATS_Y = LAP_Y + 16 * LAP_ROWS + 1


def start(display, k0, push, saved):
    global _k0, _push, main_digits, small_digits, hint, lap_lines
    global best_line, average_line, frame
    global state, run_started, banked_ms, laps, lap_started_ms
    global shown_state, shown_second
    _k0 = k0
    _push = push
    # Forget any press made while another mode was on the screen.
    k0.pressed()
    push.pressed()
    display.fill_rect(0, 0, config.WIDTH, MODE_ROWS, config.BLACK)

    row = (4 * MAIN_W + 2 * PAIR_GAP + 2 * COLON_GAP + MAIN_T
           + POINT_GAP + SMALL_T + POINT_GAP + 2 * SMALL_W + PAIR_GAP)
    x = (config.WIDTH - row) // 2
    main_x = [x, x + MAIN_W + PAIR_GAP]
    colon_x = main_x[1] + MAIN_W + COLON_GAP
    main_x.append(colon_x + MAIN_T + COLON_GAP)
    main_x.append(main_x[2] + MAIN_W + PAIR_GAP)
    point_x = main_x[3] + MAIN_W + POINT_GAP
    small_x = (point_x + SMALL_T + POINT_GAP,
               point_x + SMALL_T + POINT_GAP + SMALL_W + PAIR_GAP)

    main_digits = [Digit(display, x, MAIN_TOP, MAIN_W, MAIN_H, MAIN_T,
                         DIGIT_COLOR, GHOST) for x in main_x]
    small_digits = [Digit(display, x, BASELINE - SMALL_H, SMALL_W, SMALL_H,
                          SMALL_T, DIGIT_COLOR, GHOST) for x in small_x]
    for y in (MAIN_TOP + MAIN_H // 3 - MAIN_T // 2,
              MAIN_TOP + 2 * MAIN_H // 3 - MAIN_T // 2):
        display.fill_rect(colon_x, y, MAIN_T, MAIN_T, DIGIT_COLOR)
    display.fill_rect(point_x, BASELINE - SMALL_T, SMALL_T, SMALL_T,
                      DIGIT_COLOR)

    hint = TextLine(display, SMALL, config.CENTER_X, HINT_Y, 18, HINT_COLOR)
    lap_lines = [TextLine(display, SMALL, config.CENTER_X, LAP_Y + 16 * row,
                          16, OLD_LAP_COLOR) for row in range(LAP_ROWS)]
    best_line = TextLine(display, TINY, config.CENTER_X, STATS_Y, 16,
                         FASTEST_COLOR)
    average_line = TextLine(display, TINY, config.CENTER_X, STATS_Y + 10, 16,
                            AVERAGE_COLOR)
    frame = TickFrame(display, config.WIDTH, MODE_ROWS)
    for second in range(60):
        frame.paint(second, TICK_OFF)

    if saved is None:
        state, run_started, banked_ms = READY, 0, 0
        laps, lap_started_ms = [], 0
    else:
        state = saved["state"]
        run_started = saved["run_started"]
        banked_ms = saved["banked_ms"]
        laps = saved["laps"]
        lap_started_ms = saved["lap_started_ms"]
    shown_state = None
    shown_second = None
    show_laps()


def elapsed_ms(now):
    if state == RUNNING:
        return banked_ms + time.ticks_diff(now, run_started)
    return banked_ms


def format_ms(ms):
    return "%02d:%02d.%02d" % (ms // 60000, ms // 1000 % 60, ms // 10 % 100)


def show_laps():
    """Newest lap on top; the fastest is green; best and average below."""
    fastest = laps.index(min(laps)) + 1 if len(laps) >= 2 else 0
    for row in range(LAP_ROWS):
        number = len(laps) - row
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


def update(now):
    global state, run_started, banked_ms, laps, lap_started_ms
    global shown_state, shown_second
    if _k0.pressed(now):
        if state == RUNNING:
            banked_ms += time.ticks_diff(now, run_started)
            state = STOPPED
        else:
            run_started = now
            state = RUNNING
    elif _push.pressed(now):
        if state == RUNNING:                     # lap
            total = min(elapsed_ms(now), MAX_MS)
            laps.append(total - lap_started_ms)
            lap_started_ms = total
            show_laps()
        elif state == STOPPED:                   # reset
            banked_ms = 0
            lap_started_ms = 0
            laps = []
            state = READY
            show_laps()

    ms = min(elapsed_ms(now), MAX_MS)
    minutes = ms // 60000
    seconds = ms // 1000 % 60
    hundredths = ms // 10 % 100
    for digit, value in zip(main_digits, (minutes // 10, minutes % 10,
                                          seconds // 10, seconds % 10)):
        digit.show(DIGITS[value])
    small_digits[0].show(DIGITS[hundredths // 10])
    small_digits[1].show(DIGITS[hundredths % 10])

    if seconds != shown_second:
        if shown_second is not None:
            frame.paint(shown_second, TICK_OFF)
        frame.paint(seconds, ACCENT)
        shown_second = seconds

    if state != shown_state:
        hint.show(HINTS[state], STATE_COLORS[state])
        shown_state = state


def stop():
    """Keep everything, so a running stopwatch keeps running."""
    return {"state": state, "run_started": run_started, "banked_ms": banked_ms,
            "laps": laps, "lap_started_ms": lap_started_ms}
