# Lab 15: Time and a Quote of the Day
# A clock with a quote under it -- a new one every day. They are proverbs
# and lines from long-ago writers, all old enough to be free for anyone
# to use.
#
#   K0    (GP11)      a new quote, picked at random
#   KNOB  (GP8, GP9)  turn to read the next or the previous quote
#   PUSH  (GP10)      back to today's quote
#
# Today's quote is white. While you are reading another day's, it turns
# orange, and today's comes back when you press PUSH -- or at midnight,
# when there is a new one.
#
# WHICH QUOTE IS TODAY'S? time.localtime() gives the day of the year,
# 1 to 366, as its eighth number. The quote is
#
#     QUOTES[day_of_year % len(QUOTES)]
#
# The % (remainder) wraps the day around the list, so the quotes take
# turns all year, and everyone running this lab sees the same quote on
# the same day. The quotes are in quotes.py -- add your own there; the
# program works out how many there are by itself.
#
# A RANDOM QUOTE. K0 asks the random module for a number from 0 to
# len(QUOTES) - 2 and steps that many quotes PLUS ONE past the one on the
# screen. Stepping at least one, and never all the way round, means K0
# always shows a different quote -- a plain random pick would sometimes
# choose the one you are already reading, and the press would seem to do
# nothing.
#
# WORD WRAP. A quote is too long for one line, so wrap() fills each line
# with as many whole words as fit, then starts the next. On this
# rectangular screen every line holds the same number of characters --
# the round-screen kit has to work out a shorter line for each row as
# the circle narrows.

NAME = "15-time-and-quote.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import random
import time

import config
from timerow import TimeRow, DAYS, MONTHS, ampm
from watchparts import TextLine, Button, Knob
from quotes import QUOTES


DATE_COLOR = config.YELLOW
QUOTE_COLOR = config.WHITE
AUTHOR_COLOR = config.CYAN
OTHER_DAY_COLOR = config.color565(255, 200, 120)   # a quote that is not today's
SMALL = config.SMALL_FONT

# Layout. A digit's height must be 3 x its thickness plus an even number.
DATE_Y = 4
SIZE = (52, 90, 12)      # digit width, height, thickness
DIGIT_TOP = 24
FIRST_LINE_Y = DIGIT_TOP + SIZE[1] + 8     # 122
LINE_HEIGHT = 18
LINES = 6                # the quote and its author: the last ends at 228
LINE_CHARS = 36          # 36 x 8 = 288 px, centered on the 320-px screen

display = config.init_display()
display.fill(config.BLACK)
a, b, push, k0 = config.init_controls()
push_button = Button(push)
k0_button = Button(k0)
knob = Knob(a, b, config.ENCODER_STEPS_PER_CLICK)

row = TimeRow(display, SIZE, DIGIT_TOP)
date_line = TextLine(display, SMALL, config.CENTER_X, DATE_Y, 24, DATE_COLOR)
lines = [TextLine(display, SMALL, config.CENTER_X,
                  FIRST_LINE_Y + i * LINE_HEIGHT, LINE_CHARS, QUOTE_COLOR)
         for i in range(LINES)]

if time.localtime()[0] < 2025:
    print("The Pico's clock has not been set. Connect with Thonny, which")
    print("sets it from your computer, or run lab 06 to set it over WiFi.")


def wrap(text, width):
    """Split text into lines of whole words, none longer than width
    characters."""
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


def show_quote(i, is_today):
    """Quote number i, wrapped, with "- author" under it, the whole block
    in the middle of the lines."""
    text, author = QUOTES[i % len(QUOTES)]
    rows = wrap(text, LINE_CHARS)[:LINES - 1]
    rows.append("- " + author)
    skip = (LINES - len(rows)) // 2           # blank lines above it
    color = QUOTE_COLOR if is_today else OTHER_DAY_COLOR
    for k in range(LINES):
        n = k - skip
        if n < 0 or n >= len(rows):
            lines[k].show("")
        elif n == len(rows) - 1:
            lines[k].show(rows[n], AUTHOR_COLOR)
        else:
            lines[k].show(rows[n], color)
    print(text, "-", author)


today = None             # the day of the year now showing
index = None             # the quote now showing
shown_second = None

while True:
    now = time.ticks_ms()
    t = time.localtime()
    day_of_year = t[7]
    if day_of_year != today:                  # a new day: a new quote
        today = day_of_year
        index = today
        show_quote(index, True)

    clicks = knob.turned()
    if k0_button.pressed(now):
        index += 1 + random.randrange(len(QUOTES) - 1)
        show_quote(index, index % len(QUOTES) == today % len(QUOTES))
    elif clicks:
        index += clicks
        show_quote(index, index % len(QUOTES) == today % len(QUOTES))
    elif push_button.pressed(now) and index != today:
        index = today
        show_quote(index, True)

    if t[5] != shown_second:
        shown_second = t[5]
        hour, minute = t[3], t[4]
        row.show(hour, minute, colon=t[5] % 2 == 0)
        text = "{} {} {}".format(DAYS[t[6]], MONTHS[t[1] - 1], t[2])
        if config.TWELVE_HOUR:
            text += "  " + ampm(hour)
        date_line.show(text)

    time.sleep_ms(20)
