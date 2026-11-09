# Lab 14: Calendar
# A month calendar with the US holidays marked, and the next holidays
# listed underneath.
#
#   KNOB  (GP8, GP9)  turn to page forward or back through the months
#   PUSH  (GP10)      back to this month
#
# Today is a white box. Federal holidays (the days government offices
# close) are red boxes; other holidays people celebrate are blue. Under
# the grid: the next three holidays from today -- or, when you are
# looking at another month, that month's holidays.
#
# HOW DO YOU KNOW WHEN THANKSGIVING IS? Most holidays move: Thanksgiving
# is "the fourth Thursday in November", Memorial Day is "the last Monday
# in May", and Easter follows the moon. So lib/holidays.py does not keep
# a list of dates that would run out -- it keeps the RULES, and works the
# dates out for any year you page to.
#
# WHICH COLUMN IS THE 1ST IN? holidays.weekday() works out the day of
# the week for any date with nothing but arithmetic (Sakamoto's method),
# so the calendar never needs the internet or a table of years.

NAME = "14-calendar.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import holidays
from watchparts import TextLine, Button, Knob

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

MONTH_Y = 4              # "November 2026", in the big font
WEEK_Y = 40              # S M T W T F S
GRID_Y = 58              # the first week
ROW_H = 20               # six weeks at most: the grid ends at 178
CELL_W = 32
GRID_X = config.CENTER_X - 7 * CELL_W // 2     # 48
LIST_Y = (182, 200, 218)
LIST_CHARS = 36

WEEK_LETTERS = "SMTWTFS"     # a US calendar starts on Sunday
MONTH_ABBREVIATIONS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
                       "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

display = config.init_display()
display.fill(config.BLACK)
a, b, push, k0 = config.init_controls()
push_button = Button(push)
knob = Knob(a, b, config.ENCODER_STEPS_PER_CLICK)

list_lines = [TextLine(display, SMALL, config.CENTER_X, y, LIST_CHARS,
                       config.WHITE) for y in LIST_Y]

if time.localtime()[0] < 2025:
    print("The Pico's clock has not been set. Connect with Thonny, which")
    print("sets it from your computer, or run lab 06 to set it over WiFi.")


def draw_month():
    """Clear everything above the list, and draw year/month's grid."""
    display.fill_rect(0, 0, config.WIDTH, LIST_Y[0], config.BLACK)
    config.centered_text(display, BIG, "{} {}".format(
        holidays.MONTH_NAMES[month - 1], year), MONTH_Y, HEADER_COLOR)
    for c in range(7):
        color = WEEKEND_COLOR if c in (0, 6) else WEEKDAY_COLOR
        display.text(SMALL, WEEK_LETTERS[c],
                     GRID_X + c * CELL_W + (CELL_W - SMALL.WIDTH) // 2,
                     WEEK_Y, color, config.BLACK)

    marks = {}               # day -> True for federal, False for other
    for day, name, federal in holidays.for_month(year, month):
        marks[day] = federal
    # The column of the 1st. holidays.weekday() counts Monday as 0, and
    # this calendar starts on Sunday, so shift by one.
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
    """The next three holidays -- or, for another month, its holidays."""
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


t = time.localtime()
today = (t[0], t[1], t[2])
year, month = t[0], t[1]
draw_month()

while True:
    now = time.ticks_ms()
    clicks = knob.turned()
    if clicks:
        # Count months from year 0, add the clicks, and split it back up:
        # that handles going past December or before January for free.
        months = year * 12 + (month - 1) + clicks
        year, month = months // 12, months % 12 + 1
        draw_month()
    elif push_button.pressed(now) and (year, month) != today[:2]:
        year, month = today[0], today[1]
        draw_month()

    t = time.localtime()
    if (t[0], t[1], t[2]) != today:            # midnight: move the box
        today = (t[0], t[1], t[2])
        draw_month()

    time.sleep_ms(20)
