# mode_stopwatch.py -- the stopwatch of lab 10, as a mode for
# 12-main-template.py. Lab 10 explains how it keeps time.
#
# The MODE button belongs to the watch here -- it switches modes -- so the
# stopwatch runs on the other two buttons, like most two-button stopwatches:
#
#   UP    start / stop
#   DOWN  lap while running, reset while stopped
#
# Switching to another mode does not stop it. stop() hands back when it
# started and what it had banked, and because the time always comes from
# the Pico's millisecond clock, it is still right when you come back.
#
# Every mode has the same four functions -- see 12-main-template.py.

import time

import config
from watchparts import Digit, TickRing, TextLine, DIGITS

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
HINTS = ("UP start", "UP stop  DOWN lap", "UP go  DOWN reset")

MAX_MS = 100 * 60 * 1000 - 10     # 99:59.99
LAP_ROWS = 3

# Layout, the same as lab 10.
MAIN_W, MAIN_H, MAIN_T = 40, 71, 9
SMALL_W, SMALL_H, SMALL_T = 22, 40, 6
PAIR_GAP = 7
COLON_GAP = 8
POINT_GAP = 5
MAIN_TOP = config.CENTER_Y - MAIN_H // 2
BASELINE = MAIN_TOP + MAIN_H
TITLE_Y = 56
HINT_Y = 84
STATE_Y = 112
STATS_Y = BASELINE + 10
LAP_Y = STATS_Y + 22


def start(display, up, down, saved):
    global _up, _down, main_digits, small_digits, hint, status, lap_lines
    global best_line, average_line, ring
    global state, run_started, banked_ms, laps, lap_started_ms
    global shown_state, shown_second
    _up = up
    _down = down
    display.fill(config.BLACK)

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

    TextLine(display, SMALL, config.CENTER_X, TITLE_Y, 9,
             HINT_COLOR).show("STOPWATCH")
    hint = TextLine(display, SMALL, config.CENTER_X, HINT_Y, 20, HINT_COLOR)
    status = TextLine(display, SMALL, config.CENTER_X, STATE_Y, 7, HINT_COLOR)
    lap_lines = [TextLine(display, SMALL, config.CENTER_X, LAP_Y + 18 * row,
                          16, OLD_LAP_COLOR) for row in range(LAP_ROWS)]
    best_line = TextLine(display, SMALL, config.CENTER_X - 58, STATS_Y, 13,
                         FASTEST_COLOR)
    average_line = TextLine(display, SMALL, config.CENTER_X + 56, STATS_Y, 12,
                            AVERAGE_COLOR)
    ring = TickRing(display, config.CENTER_X, config.CENTER_Y,
                    config.SAFE_RADIUS - 2, config.SAFE_RADIUS - 10,
                    config.SAFE_RADIUS - 16)
    for second in range(60):
        ring.paint(second, TICK_OFF)

    if saved is None:
        state, run_started, banked_ms, laps, lap_started_ms = READY, 0, 0, [], 0
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
    """Newest lap on top; the fastest is green; best and average above."""
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
        best_line.show("Best " + format_ms(min(laps)))
        average_line.show("Avg " + format_ms(sum(laps) // len(laps)))
    else:
        best_line.show("")
        average_line.show("")


def update(now):
    global state, run_started, banked_ms, laps, lap_started_ms
    global shown_state, shown_second
    if _up.pressed(now):
        if state == RUNNING:
            banked_ms += time.ticks_diff(now, run_started)
            state = STOPPED
        else:
            run_started = now
            state = RUNNING
    elif _down.pressed(now):
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
            ring.paint(shown_second, TICK_OFF)
        ring.paint(seconds, ACCENT)
        shown_second = seconds

    if state != shown_state:
        status.show(STATE_NAMES[state], STATE_COLORS[state])
        hint.show(HINTS[state])
        shown_state = state


def stop():
    """Keep everything, so a running stopwatch keeps running."""
    return {"state": state, "run_started": run_started, "banked_ms": banked_ms,
            "laps": laps, "lap_started_ms": lap_started_ms}
