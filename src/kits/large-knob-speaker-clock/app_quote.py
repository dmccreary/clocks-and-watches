# app_quote.py -- lab 15's clock with a quote of the day, as a mode for
# 20-mode-main.py.
#
#   K0 (short press)   a new quote, picked at random
#   KNOB               turn to read the next or the previous quote
#   PUSH               back to today's quote
#
# The quotes are in quotes.py, shared with lab 15 -- read lab 15 for how
# today's is chosen and how a random pick always finds a different one.
# See 20-mode-main.py for the three functions every mode has.

import random
import time

import config
from quotes import QUOTES
from timerow import TimeRow, DAYS, MONTHS, ampm
from watchparts import TextLine

DATE_COLOR = config.YELLOW
QUOTE_COLOR = config.WHITE
AUTHOR_COLOR = config.CYAN
OTHER_DAY_COLOR = config.color565(255, 200, 120)
SMALL = config.SMALL_FONT

# Lab 15's layout.
DATE_Y = 4
SIZE = (52, 90, 12)
DIGIT_TOP = 24
FIRST_LINE_Y = DIGIT_TOP + SIZE[1] + 8     # 122
LINE_HEIGHT = 18
LINES = 6
LINE_CHARS = 36


def start(display, k0, push, knob, saved):
    global _k0, _push, _knob, row, date_line, lines
    global today, index, shown_second
    _k0 = k0
    _push = push
    _knob = knob
    display.fill(config.BLACK)
    row = TimeRow(display, SIZE, DIGIT_TOP)
    date_line = TextLine(display, SMALL, config.CENTER_X, DATE_Y, 24,
                         DATE_COLOR)
    lines = [TextLine(display, SMALL, config.CENTER_X,
                      FIRST_LINE_Y + i * LINE_HEIGHT, LINE_CHARS, QUOTE_COLOR)
             for i in range(LINES)]
    today = None             # update() shows today's quote straight away
    index = None
    shown_second = None


def wrap(text, width):
    rows = []
    line = ""
    for word in text.split():
        if not line:
            line = word
        elif len(line) + 1 + len(word) <= width:
            line += " " + word
        else:
            rows.append(line)
            line = word
    if line:
        rows.append(line)
    return rows


def show_quote(i):
    text, author = QUOTES[i % len(QUOTES)]
    rows = wrap(text, LINE_CHARS)[:LINES - 1]
    rows.append("- " + author)
    skip = (LINES - len(rows)) // 2
    is_today = i % len(QUOTES) == today % len(QUOTES)
    color = QUOTE_COLOR if is_today else OTHER_DAY_COLOR
    for k in range(LINES):
        n = k - skip
        if n < 0 or n >= len(rows):
            lines[k].show("")
        elif n == len(rows) - 1:
            lines[k].show(rows[n], AUTHOR_COLOR)
        else:
            lines[k].show(rows[n], color)


def update(now):
    global today, index, shown_second
    t = time.localtime()
    if t[7] != today:                          # a new day: a new quote
        today = t[7]
        index = today
        show_quote(index)

    clicks = _knob.turned()
    if _k0.pressed(now):
        index += 1 + random.randrange(len(QUOTES) - 1)
        show_quote(index)
    elif clicks:
        index += clicks
        show_quote(index)
    elif _push.pressed(now) and index != today:
        index = today
        show_quote(index)

    if t[5] != shown_second:
        shown_second = t[5]
        hour, minute = t[3], t[4]
        row.show(hour, minute, colon=t[5] % 2 == 0)
        text = "{} {} {}".format(DAYS[t[6]], MONTHS[t[1] - 1], t[2])
        if config.TWELVE_HOUR:
            text += "  " + ampm(hour)
        date_line.show(text)


def stop():
    return None
