# mode_phrase.py -- mode 8: a medium clock with a phrase of the day.
#
# A new phrase every day, chosen by the day of the year, so everyone with
# this kit sees the same one on the same day. They are proverbs and lines
# from long-ago writers, all old enough to be free for anyone to use.
#
#   UP / DOWN   look at the next / previous phrase (today's comes back
#               at midnight, or when you leave and return to this mode)
#
# WRAPPING ON A ROUND SCREEN. On a square screen every line of text can
# be the same length. Here each line lower down is shorter, because the
# circle narrows. fit_lines() works out how many characters fit on each
# row, then fills the rows a word at a time.
#
# Every mode has the same functions -- see mode-template.py.

import math
import time

import config
from timerow import TimeRow, DAYS, MONTHS, ampm
from watchparts import TextLine

PHRASES = (
    ("Well done is better than well said.", "Benjamin Franklin"),
    ("The journey of a thousand miles begins with a single step.",
     "Lao Tzu"),
    ("It does not matter how slowly you go as long as you do not stop.",
     "Confucius"),
    ("Lost time is never found again.", "Benjamin Franklin"),
    ("Do what you can, with what you have, where you are.",
     "Theodore Roosevelt"),
    ("Nothing is impossible to a willing heart.", "Old English proverb"),
    ("Write it on your heart that every day is the best day in the year.",
     "Ralph Waldo Emerson"),
    ("Little by little, one travels far.", "Spanish proverb"),
    ("Knowing is not enough; we must apply.", "Goethe"),
    ("A smooth sea never made a skillful sailor.", "English proverb"),
    ("Fall seven times, stand up eight.", "Japanese proverb"),
    ("Be kind, for everyone you meet is fighting a hard battle.",
     "Ian Maclaren"),
    ("Energy and persistence conquer all things.", "Benjamin Franklin"),
    ("Go confidently in the direction of your dreams.",
     "Henry David Thoreau"),
    ("The best way out is always through.", "Robert Frost"),
    ("Every artist was first an amateur.", "Ralph Waldo Emerson"),
    ("Patience is bitter, but its fruit is sweet.", "Rousseau"),
    ("Where there is a will, there is a way.", "Proverb"),
    ("An investment in knowledge pays the best interest.",
     "Benjamin Franklin"),
    ("If you want to go fast, go alone. If you want to go far, go "
     "together.", "African proverb"),
    ("The best time to plant a tree was twenty years ago. The second best "
     "time is now.", "Chinese proverb"),
    ("Happiness depends upon ourselves.", "Aristotle"),
    ("Act as if what you do makes a difference. It does.", "William James"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("The harder the conflict, the more glorious the triumph.",
     "Thomas Paine"),
    ("Great things are done by a series of small things brought "
     "together.", "Vincent van Gogh"),
    ("Wherever you go, go with all your heart.", "Confucius"),
    ("Luck is what happens when preparation meets opportunity.", "Seneca"),
    ("Kindness is the language which the deaf can hear and the blind can "
     "see.", "Mark Twain"),
    ("Well begun is half done.", "Aristotle"),
    ("Today is a gift. That is why it is called the present.", "Proverb"),
)

DATE_COLOR = config.YELLOW
PHRASE_COLOR = config.WHITE
AUTHOR_COLOR = config.CYAN
OTHER_DAY_COLOR = config.color565(255, 200, 120)   # a phrase that is not today's

SIZE = (52, 100, 14) if config.TWELVE_HOUR else (46, 88, 12)
TOP_LINE_Y = 66
DIGIT_TOP = 88
FIRST_LINE_Y = 204
LINE_HEIGHT = 18
LINES = 6                  # the last ends at y 310, just above the mode dots
TEXT_RADIUS = 150          # keep text this close to the center
MAX_CHARS = 32


def chars_on_row(y):
    """How many small-font characters fit on a text row whose top is y."""
    font = config.SMALL_FONT
    dy = max(abs(y - config.CENTER_Y), abs(y + font.HEIGHT - config.CENTER_Y))
    if dy >= TEXT_RADIUS:
        return 0
    half = math.sqrt(TEXT_RADIUS * TEXT_RADIUS - dy * dy)
    return min(MAX_CHARS, int(2 * half) // font.WIDTH)


def fit_lines(text, limits):
    """Fill rows with whole words. limits[i] is the room on row i. Returns
    the rows, or None if the words do not all fit."""
    rows = []
    line = ""
    for word in text.split():
        if len(rows) >= len(limits):
            return None
        candidate = word if not line else line + " " + word
        if len(candidate) <= limits[len(rows)]:
            line = candidate
            continue
        rows.append(line)
        line = word
        if len(rows) >= len(limits) or len(word) > limits[len(rows)]:
            return None
    rows.append(line)
    return rows


def start(display, up, down, saved):
    global _up, _down, row, top_line, lines, limits, shown, today, index
    _up = up
    _down = down
    display.fill(config.BLACK)
    row = TimeRow(display, SIZE, DIGIT_TOP)
    top_line = TextLine(display, config.SMALL_FONT, config.CENTER_X,
                        TOP_LINE_Y, 22, DATE_COLOR)
    limits = []
    lines = []
    for i in range(LINES):
        y = FIRST_LINE_Y + i * LINE_HEIGHT
        limits.append(chars_on_row(y))
        lines.append(TextLine(display, config.SMALL_FONT, config.CENTER_X, y,
                              limits[-1], PHRASE_COLOR))
    shown = None
    today = None
    index = None


def show_phrase(i, is_today):
    """Wrap phrase i into the rows, author last, centered as a block."""
    text, author = PHRASES[i % len(PHRASES)]
    color = PHRASE_COLOR if is_today else OTHER_DAY_COLOR
    rows = None
    # Start lower for a short phrase, so the block sits in the middle.
    for skip in (1, 0):
        rows = fit_lines(text, limits[skip:LINES - 1])
        if rows is not None and (skip == 0 or len(rows) <= 2):
            rows = [""] * skip + rows
            break
        rows = None
    if rows is None:
        rows = [text[:limits[0]]]
    for k in range(LINES):
        if k < len(rows):
            lines[k].show(rows[k], color)
        elif k == len(rows):
            lines[k].show("- " + author, AUTHOR_COLOR)
        else:
            lines[k].show("")


def update(now):
    global shown, today, index
    t = time.localtime()
    yday = t[7]
    if yday != today:                 # a new day: today's phrase
        today = yday
        index = yday
        show_phrase(index, True)
    step = 1 if _up.pressed(now) else -1 if _down.pressed(now) else 0
    if step:
        index += step
        show_phrase(index, index % len(PHRASES) == today % len(PHRASES))

    if t[5] != shown:
        shown = t[5]
        hour, minute = t[3], t[4]
        row.show(hour, minute, colon=t[5] % 2 == 0)
        text = "{} {} {}".format(DAYS[t[6]], MONTHS[t[1] - 1], t[2])
        if config.TWELVE_HOUR:
            text += "  " + ampm(hour)
        top_line.show(text)


def stop():
    return None
