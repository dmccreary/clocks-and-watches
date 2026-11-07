# mode_temp.py -- mode 1: the time and the temperature outside.
#
# Slightly smaller digits than the Big Clock, with the temperature right
# now underneath, for the place in config.py (CITY, LATITUDE, LONGITUDE).
# The weather comes from Open-Meteo (see forecast.py) and is fetched again
# every 30 minutes. Mode 2 shares the same download (it lives in shared.py).
#
#   UP          get the weather again now
#
# The clock stands still for the few seconds a download takes, then
# catches up.
#
# Every mode has the same functions -- see mode-template.py.

import time

import config
import forecast
import shared
import shapes
from timerow import TimeRow, DAYS, MONTHS, ampm
from watchparts import TickRing, TextLine

ACCENT = config.CYAN
TICK_OFF = config.color565(40, 40, 40)
DATE_COLOR = config.YELLOW
TEMP_COLOR = config.color565(255, 150, 40)
DIM = config.color565(140, 140, 140)
REFRESH_MINUTES = 30
RETRY_MINUTES = 5

SIZE = (52, 100, 14) if config.TWELVE_HOUR else (46, 88, 12)
TOP_LINE_Y = 66
DIGIT_TOP = 92
TEMP_Y = 206
WORDS_Y = 246
STATUS_Y = 268


def start(display, up, down, saved):
    global _display, _up, row, ring, top_line, temp_line, words_line
    global status_line, shown, shown_weather, fetch_due, last_try
    _display = display
    _up = up
    display.fill(config.BLACK)
    row = TimeRow(display, SIZE, DIGIT_TOP)
    ring = TickRing(display, config.CENTER_X, config.CENTER_Y,
                    config.SAFE_RADIUS - 2, config.SAFE_RADIUS - 10,
                    config.SAFE_RADIUS - 16)
    small = config.SMALL_FONT
    big = config.BIG_FONT
    top_line = TextLine(display, small, config.CENTER_X, TOP_LINE_Y, 22,
                        DATE_COLOR)
    # The temperature: a 3-character number, a degree ring, and F or C.
    cx = config.CENTER_X
    temp_line = TextLine(display, big, cx - 16, TEMP_Y, 3, TEMP_COLOR)
    shapes.ring(display, cx + 14, TEMP_Y + 6, 4, TEMP_COLOR, 2)
    display.text(big, forecast.unit_letter(), cx + 22, TEMP_Y, TEMP_COLOR,
                 config.BLACK)
    words_line = TextLine(display, small, cx, WORDS_Y, 26, config.WHITE)
    status_line = TextLine(display, small, cx, STATUS_Y, 24, DIM)
    shown = None
    shown_weather = 0           # matches nothing, so the first draw happens
    fetch_due = shared.fresh_weather(REFRESH_MINUTES) is None
    last_try = None
    show_weather()


def show_weather():
    global shown_weather
    weather = shared.weather
    if weather is shown_weather:
        return
    shown_weather = weather
    if weather is None:
        temp_line.show(" --")
        words_line.show(config.CITY)
        status_line.show("getting weather ...")
        return
    temp_line.show("%3d" % weather["temp"])
    words_line.show("{} in {}".format(forecast.describe(weather["code"]),
                                      config.CITY))
    show_age()


def show_age():
    age = shared.weather_minutes()
    if age is None:
        status_line.show("no weather yet")
    elif age < 1:
        status_line.show("just updated")
    else:
        status_line.show("updated {} min ago".format(age))


def get_weather(now):
    global fetch_due, last_try, shown_weather
    last_try = now
    status_line.show("getting weather ...")
    if shared.fetch_weather() is not None:
        fetch_due = False
        shown_weather = 0        # redraw
    show_weather()
    show_age()


def update(now):
    global shown, fetch_due
    if _up.pressed(now):
        get_weather(now)

    t = time.localtime()
    if t[5] != shown:
        shown = t[5]
        hour, minute, second = t[3], t[4], t[5]
        row.show(hour, minute, colon=second % 2 == 0)
        for i in range(60):
            ring.paint(i, ACCENT if i <= second else TICK_OFF)
        text = "{} {} {}".format(DAYS[t[6]], MONTHS[t[1] - 1], t[2])
        if config.TWELVE_HOUR:
            text += "  " + ampm(hour)
        top_line.show(text)
        if second == 0:
            show_age()
            if shared.fresh_weather(REFRESH_MINUTES) is None:
                fetch_due = True

    # Fetch after the face is drawn, and not more than once per retry gap.
    if fetch_due and (last_try is None or time.ticks_diff(
            now, last_try) >= RETRY_MINUTES * 60000):
        get_weather(now)
    else:
        show_weather()


def stop():
    return None
