# app_calendar.py -- lab 14's calendar, as a mode for 20-mode-main.py.
#
#   KNOB   turn to page forward or back through the months
#   PUSH   back to this month
#
# Today is a white box, federal holidays are red and other holidays blue,
# with the next three holidays listed underneath. lib/holidays.py works
# the dates out from rules -- read lab 14 for how. K0's short press does
# nothing here. See 20-mode-main.py for the three functions every mode
# has.

import time

import config
import holidays
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
SMALL = config.SMALL_FONT
BIG = config.BIG_FONT

# Lab 14's layout.
MONTH_Y = 4
WEEK_Y = 40
GRID_Y = 58
ROW_H = 20
CELL_W = 32
GRID_X = config.CENTER_X - 7 * CELL_W // 2     # 48
LIST_Y = (182, 200, 218)
LIST_CHARS = 36

WEEK_LETTERS = "SMTWTFS"
MONTH_ABBREVIATIONS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def start(display, k0, push, knob, saved):
    global _display, _push, _knob, list_lines, today, year, month
    _display = display
    _push = push
    _knob = knob
    display.fill(config.BLACK)
    list_lines = [TextLine(display, SMALL, config.CENTER_X, y, LIST_CHARS,
                           config.WHITE) for y in LIST_Y]
    t = time.localtime()
    today = (t[0], t[1], t[2])
    year, month = t[0], t[1]           # always open on this month
    draw_month()


def draw_month():
    display = _display
    display.fill_rect(0, 0, config.WIDTH, LIST_Y[0], config.BLACK)
    config.centered_text(display, BIG, "{} {}".format(
        holidays.MONTH_NAMES[month - 1], year), MONTH_Y, HEADER_COLOR)
    for c in range(7):
        color = WEEKEND_COLOR if c in (0, 6) else WEEKDAY_COLOR
        display.text(SMALL, WEEK_LETTERS[c],
                     GRID_X + c * CELL_W + (CELL_W - SMALL.WIDTH) // 2,
                     WEEK_Y, color, config.BLACK)

    marks = {}
    for day, name, federal in holidays.for_month(year, month):
        marks[day] = federal
    column = (holidays.weekday(year, month, 1) + 1) % 7
    row = 0
    for day in range(1, holidays.days_in_month(year, month) + 1):
        x = GRID_X + column * CELL_W
        y = GRID_Y + row * ROW_H
        is_today = (year, month, day) == today
        if is_today or day in marks:
            box = TODAY_BOX if is_today else (
                FEDERAL_BOX if marks[day] else OTHER_BOX)
            display.fill_rect(x + 1, y, CELL_W - 2, ROW_H - 1, box)
            background = box
            color = config.BLACK if is_today else config.WHITE
        else:
            background = config.BLACK
            color = WEEKEND_COLOR if column in (0, 6) else WEEKDAY_COLOR
        display.text(SMALL, "%2d" % day,
                     x + (CELL_W - 2 * SMALL.WIDTH) // 2, y + 1,
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
            line.show("{} {:2d}  {}".format(MONTH_ABBREVIATIONS[m - 1], d,
                                            name),
                      FEDERAL_TEXT if federal else OTHER_TEXT)
        elif i == 0:
            line.show("no holidays this month", DIM)
        else:
            line.show("")


def update(now):
    global year, month, today
    clicks = _knob.turned()
    if clicks:
        months = year * 12 + (month - 1) + clicks
        year, month = months // 12, months % 12 + 1
        draw_month()
    elif _push.pressed(now) and (year, month) != today[:2]:
        year, month = today[0], today[1]
        draw_month()

    t = time.localtime()
    if (t[0], t[1], t[2]) != today:            # midnight: move the box
        today = (t[0], t[1], t[2])
        draw_month()


def stop():
    return None
