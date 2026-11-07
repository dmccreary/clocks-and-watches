# mode_calendar.py -- mode 9: a month calendar with the US holidays in it,
# and the next holidays listed underneath.
#
#   UP / DOWN   next / previous month (hold to flip quickly)
#
# Today is a white box. Federal holidays (the days government offices
# close) are red boxes; other holidays people celebrate are blue. Under the
# grid: the next three holidays from today -- or, when you are looking at
# another month, that month's holidays.
#
# holidays.py works the dates out from rules ("the fourth Thursday in
# November"), so the calendar never runs out of years.
#
# Every mode has the same functions -- see mode-template.py.

import time

import config
import holidays
from timerow import MONTHS
from watchparts import TextLine

TODAY_BOX = config.WHITE
FEDERAL_BOX = config.color565(170, 0, 0)
OTHER_BOX = config.color565(0, 70, 140)
WEEKDAY_COLOR = config.WHITE
WEEKEND_COLOR = config.color565(150, 150, 150)
HEADER_COLOR = config.YELLOW
DIM = config.color565(140, 140, 140)
FEDERAL_TEXT = config.color565(255, 110, 110)
OTHER_TEXT = config.color565(110, 180, 255)

MONTH_Y = 54
YEAR_Y = 88
WEEK_Y = 106
GRID_Y = 124
ROW_H = 19
CELL_W = 28
GRID_X = config.CENTER_X - 7 * CELL_W // 2     # 82
LIST_Y = (246, 264, 282)
LIST_CHARS = 23
CLEAR_TOP = 50
CLEAR_BOTTOM = 300            # stays clear of the mode dots at y 312

WEEK_LETTERS = "SMTWTFS"     # a US calendar starts on Sunday


def start(display, up, down, saved):
    global _display, _up, _down, list_lines, year, month, today
    _display = display
    _up = up
    _down = down
    display.fill(config.BLACK)
    list_lines = [TextLine(display, config.SMALL_FONT, config.CENTER_X, y,
                           LIST_CHARS, config.WHITE) for y in LIST_Y]
    t = time.localtime()
    today = (t[0], t[1], t[2])
    year, month = t[0], t[1]
    draw_month()


def draw_month():
    display = _display
    small = config.SMALL_FONT
    big = config.BIG_FONT
    display.fill_rect(30, CLEAR_TOP, config.WIDTH - 60,
                      LIST_Y[0] - CLEAR_TOP, config.BLACK)
    config.centered_text(display, big, holidays.MONTH_NAMES[month - 1],
                         MONTH_Y, HEADER_COLOR)
    config.centered_text(display, small, str(year), YEAR_Y, DIM)
    for c in range(7):
        color = WEEKEND_COLOR if c in (0, 6) else WEEKDAY_COLOR
        display.text(small, WEEK_LETTERS[c], GRID_X + c * CELL_W + 10,
                     WEEK_Y, color, config.BLACK)

    marks = {}
    for day, name, federal in holidays.for_month(year, month):
        marks[day] = federal
    # Sunday-first column of the 1st: holidays.weekday() is Monday 0.
    column = (holidays.weekday(year, month, 1) + 1) % 7
    row = 0
    for day in range(1, holidays.days_in_month(year, month) + 1):
        x = GRID_X + column * CELL_W
        y = GRID_Y + row * ROW_H
        is_today = (year, month, day) == today
        if is_today or day in marks:
            box = TODAY_BOX if is_today else (
                FEDERAL_BOX if marks[day] else OTHER_BOX)
            display.fill_rect(x + 1, y - 1, CELL_W - 2, ROW_H - 1, box)
            background = box
            color = config.BLACK if is_today else config.WHITE
        else:
            background = config.BLACK
            color = WEEKEND_COLOR if column in (0, 6) else WEEKDAY_COLOR
        label = "%2d" % day
        display.text(small, label, x + (CELL_W - 2 * small.WIDTH) // 2, y + 1,
                     color, background)
        column += 1
        if column == 7:
            column = 0
            row += 1
    draw_list()


def draw_list():
    if (year, month) == today[:2]:
        found = holidays.upcoming(today[0], today[1], today[2], len(LIST_Y))
        entries = [(m, d, name, federal) for _, m, d, name, federal in found]
    else:
        entries = [(month, d, name, federal)
                   for d, name, federal in holidays.for_month(year, month)]
    for i, line in enumerate(list_lines):
        if i < len(entries):
            m, d, name, federal = entries[i]
            line.show("{} {:2d} {}".format(MONTHS[m - 1], d, name),
                      FEDERAL_TEXT if federal else OTHER_TEXT)
        elif i == 0:
            line.show("no holidays this month", DIM)
        else:
            line.show("")


def update(now):
    global year, month, today
    step = 0
    if _up.pressed(now, repeat=True):
        step = 1
    elif _down.pressed(now, repeat=True):
        step = -1
    if step:
        month += step
        if month > 12:
            month, year = 1, year + 1
        elif month < 1:
            month, year = 12, year - 1
        draw_month()
        return
    t = time.localtime()
    if (t[0], t[1], t[2]) != today:            # midnight: move the box
        today = (t[0], t[1], t[2])
        draw_month()


def stop():
    return None
