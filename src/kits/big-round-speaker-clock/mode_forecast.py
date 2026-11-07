# mode_forecast.py -- mode 2: the time, the temperature now, and the
# forecast for today and tomorrow.
#
# Smaller digits at the top make room for two columns underneath, each
# with a high, a low, and a few words. It shares its weather with mode 1
# (the download lives in shared.py) and refreshes it every 30 minutes.
#
#   UP          get the weather again now
#
# Every mode has the same functions -- see mode-template.py.

import time

import config
import forecast
import shared
from timerow import TimeRow, DAYS, MONTHS, ampm
from watchparts import TextLine

DATE_COLOR = config.YELLOW
NOW_COLOR = config.WHITE
LABEL_COLOR = config.color565(170, 170, 170)
LINE_COLOR = config.color565(60, 60, 70)
HIGH_COLOR = config.color565(255, 150, 40)
LOW_COLOR = config.color565(90, 170, 255)
WORDS_COLOR = config.YELLOW
DIM = config.color565(140, 140, 140)
REFRESH_MINUTES = 30
RETRY_MINUTES = 5

SIZE = (38, 72, 8) if config.TWELVE_HOUR else (34, 64, 8)
DIGIT_TOP = 58
DATE_Y = DIGIT_TOP + SIZE[1] + 6          # 136
NOW_Y = 160
DIVIDER_Y = 200
LABEL_Y = 206
TEMPS_Y = 226
WORDS_Y = 262
COLUMN_X = (118, 242)


def start(display, up, down, saved):
    global _up, row, date_line, now_line, columns, shown, shown_weather
    global fetch_due, last_try
    _up = up
    display.fill(config.BLACK)
    row = TimeRow(display, SIZE, DIGIT_TOP)
    small = config.SMALL_FONT
    big = config.BIG_FONT
    date_line = TextLine(display, small, config.CENTER_X, DATE_Y, 20,
                         DATE_COLOR)
    now_line = TextLine(display, big, config.CENTER_X, NOW_Y, 14, NOW_COLOR)
    display.hline(70, DIVIDER_Y, 220, LINE_COLOR)
    display.vline(config.CENTER_X, DIVIDER_Y + 6,
                  WORDS_Y + small.HEIGHT - DIVIDER_Y - 6, LINE_COLOR)
    columns = []
    for cx, label in zip(COLUMN_X, ("Today", "Tomorrow")):
        display.text(small, label, cx - len(label) * small.WIDTH // 2,
                     LABEL_Y, LABEL_COLOR, config.BLACK)
        display.text(small, "/", cx - small.WIDTH // 2, TEMPS_Y + 8,
                     LABEL_COLOR, config.BLACK)
        # High to the left of the slash, low to the right, 3 characters
        # each: x from cx - 52 to cx + 52, clear of the divider at 180.
        columns.append((TextLine(display, big, cx - 28, TEMPS_Y, 3,
                                 HIGH_COLOR),
                        TextLine(display, big, cx + 28, TEMPS_Y, 3,
                                 LOW_COLOR),
                        TextLine(display, small, cx, WORDS_Y, 9,
                                 WORDS_COLOR)))
    shown = None
    shown_weather = 0
    fetch_due = shared.fresh_weather(REFRESH_MINUTES) is None
    last_try = None
    show_weather()


def show_weather():
    global shown_weather
    weather = shared.weather
    if weather is shown_weather:
        return
    shown_weather = weather
    unit = forecast.unit_letter()
    if weather is None:
        now_line.show("getting ...", DIM)
        for high, low, words in columns:
            high.show(" --")
            low.show("-- ")
            words.show("")
        return
    now_line.show("{}{} {}".format(weather["temp"], unit,
                                   forecast.describe(weather["code"])))
    for (high, low, words), day in zip(columns, weather["days"]):
        high.show("%3d" % day[0])
        low.show("%-3d" % day[1])
        words.show(forecast.describe(day[2]))


def get_weather(now):
    global fetch_due, last_try, shown_weather
    last_try = now
    if shared.weather is None:
        now_line.show("getting ...", DIM)
    if shared.fetch_weather() is not None:
        fetch_due = False
        shown_weather = 0
    show_weather()


def update(now):
    global shown, fetch_due
    if _up.pressed(now):
        get_weather(now)

    t = time.localtime()
    if t[5] != shown:
        shown = t[5]
        hour, minute, second = t[3], t[4], t[5]
        row.show(hour, minute, colon=second % 2 == 0)
        text = "{} {} {}".format(DAYS[t[6]], MONTHS[t[1] - 1], t[2])
        if config.TWELVE_HOUR:
            text += "  " + ampm(hour)
        date_line.show(text)
        if second == 0 and shared.fresh_weather(REFRESH_MINUTES) is None:
            fetch_due = True

    if fetch_due and (last_try is None or time.ticks_diff(
            now, last_try) >= RETRY_MINUTES * 60000):
        get_weather(now)
    else:
        show_weather()


def stop():
    return None
