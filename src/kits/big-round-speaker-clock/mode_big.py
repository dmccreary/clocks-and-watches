# mode_big.py -- mode 0, the Big Clock: the face of main-template.py as a
# mode for mode-template.py. "HOW BIG CAN THE DIGITS BE?" in
# main-template.py explains the sizes.
#
#   UP / DOWN   volume up / down (hold to keep going), with a beep
#
# Every mode has the same functions -- see mode-template.py.

import time

import config
import shared
from timerow import TimeRow, date_text, ampm
from watchparts import TickRing, TextLine

ACCENT = config.CYAN
TICK_OFF = config.color565(40, 40, 40)
DATE_COLOR = config.YELLOW
NOTE_COLOR = config.GREEN
NOTE_MS = 2000

SIZE_12 = (64, 130, 16)
SIZE_24 = (56, 98, 14)


def start(display, up, down, saved):
    global _up, _down, row, ring, ampm_line, date_line, note_until, shown
    _up = up
    _down = down
    display.fill(config.BLACK)
    size = SIZE_12 if config.TWELVE_HOUR else SIZE_24
    row = TimeRow(display, size, config.CENTER_Y - size[1] // 2)
    ring = TickRing(display, config.CENTER_X, config.CENTER_Y,
                    config.SAFE_RADIUS - 2, config.SAFE_RADIUS - 10,
                    config.SAFE_RADIUS - 16)
    small = config.SMALL_FONT
    ampm_line = TextLine(display, small, config.CENTER_X, row.top - 34, 2,
                         ACCENT)
    date_line = TextLine(display, small, config.CENTER_X, row.bottom + 18, 22,
                         DATE_COLOR)
    note_until = None
    shown = None


def update(now):
    global note_until, shown
    change = 0
    if _up.pressed(now, repeat=True):
        change = shared.VOLUME_STEP
    elif _down.pressed(now, repeat=True):
        change = -shared.VOLUME_STEP
    if change:
        level = shared.speaker.volume(change)
        shared.speaker.beep()
        date_line.show("volume {}".format(level), NOTE_COLOR)
        note_until = time.ticks_add(now, NOTE_MS)

    t = time.localtime()
    if t[5] == shown and note_until is None:
        return
    shown = t[5]
    hour, minute, second = t[3], t[4], t[5]
    row.show(hour, minute, colon=second % 2 == 0)
    # Ticks 0 to `second` are lit; paint() skips ticks that already have
    # the right color, so normally only one is sent.
    for i in range(60):
        ring.paint(i, ACCENT if i <= second else TICK_OFF)
    if config.TWELVE_HOUR:
        ampm_line.show(ampm(hour))
    if note_until is not None:
        if time.ticks_diff(now, note_until) < 0:
            return
        note_until = None
    if shared.synced:
        date_line.show(date_text(t), DATE_COLOR)
    else:
        date_line.show("time not set", config.RED)


def stop():
    return None
