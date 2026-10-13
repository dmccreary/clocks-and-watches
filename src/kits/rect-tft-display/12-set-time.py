# Lab 12: Set the Time with the Knob
# A digital clock you can set by hand -- for when there is no WiFi.
#
#   PUSH  (press the knob)  steps through:
#                           run -> set hour -> set minute -> run
#   TURN  (the knob)        changes the highlighted field: clockwise adds,
#                           counter-clockwise subtracts
#
# Every click that changes the minute also zeroes the seconds, so you can
# match another clock: stop one click short of the next minute, then make
# that last click the moment the other clock reaches it.
#
# The time is written straight into the Pico's real-time clock (RTC), so
# lab 09 and lab 11 pick it up after a soft reset -- as long as the Pico
# stays powered.
#
# Labs 05 and 06 read the knob raw. This one has to deal with two things
# raw reading gets wrong:
#
#   BOUNCE. A switch's metal contacts rattle for a few milliseconds when
#   they close, so the pin flickers 0-1-0-1 before it settles. Counted
#   naively, one press of the knob would skip straight past "set hour".
#   The Button class below ignores any change that comes less than
#   DEBOUNCE_MS after the last one.
#
#   TURNS THAT COME FASTER THAN THE LOOP. Spin the knob and several
#   clicks go by while the loop is busy drawing the time. The Knob class
#   (lab 07's interrupt code, packaged in lib/watchparts.py) counts every
#   click as it happens, and turned() hands over however many there have
#   been since the loop last asked -- so going from 0 to 45 minutes is
#   one quick spin, not 45 presses of a button.

NAME = "12-set-time.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import RTC
import config
from watchparts import Knob

DEBOUNCE_MS = 40

RUN, SET_HOUR, SET_MINUTE = 0, 1, 2
MODE_NAMES = ("", "Set hour", "Set minute")
HINTS = ("Press knob to set", "Turn, then press", "Turn, then press")

TITLE_Y = 8
TIME_Y = 36
AMPM_Y = 72
MODE_Y = 92
HINT_Y = 114

HIGHLIGHT_FG = config.BLACK
HIGHLIGHT_BG = config.YELLOW


class Button:
    """One push button, with debounce."""

    def __init__(self, pin):
        self.pin = pin
        self.held = False
        self.changed_at = time.ticks_ms()

    def pressed(self, now):
        """True once, when the button goes down."""
        down = self.pin.value() == 0
        if (down != self.held
                and time.ticks_diff(now, self.changed_at) > DEBOUNCE_MS):
            self.held = down
            self.changed_at = now
            return down
        return False


def draw_time(display, hour, minute, second, mode):
    """Draw HH:MM:SS field by field, so the field being set can have its
    own colors. Every field is a fixed width, so each one exactly covers
    the old one and nothing needs erasing first."""
    font = config.BIG_FONT
    x = (config.WIDTH - 8 * font.WIDTH) // 2
    hour12 = hour % 12 or 12
    fields = (
        ("%2d" % hour12, mode == SET_HOUR),
        (":", False),
        ("%02d" % minute, mode == SET_MINUTE),
        (":", False),
        ("%02d" % second, False),
    )
    for text, selected in fields:
        if selected:
            display.text(font, text, x, TIME_Y, HIGHLIGHT_FG, HIGHLIGHT_BG)
        else:
            display.text(font, text, x, TIME_Y, config.WHITE, config.BLACK)
        x += len(text) * font.WIDTH
    config.centered_text(display, config.SMALL_FONT,
                         "AM" if hour < 12 else "PM", AMPM_Y, config.CYAN)


def draw_mode(display, mode):
    """Say what is being set, and what the knob does right now. Both
    lines change length, so each row is cleared before it is redrawn."""
    display.fill_rect(8, MODE_Y, config.WIDTH - 16, 16, config.BLACK)
    config.centered_text(display, config.SMALL_FONT, MODE_NAMES[mode],
                         MODE_Y, HIGHLIGHT_BG)
    display.fill_rect(8, HINT_Y, config.WIDTH - 16, 8, config.BLACK)
    config.centered_text(display, config.TINY_FONT, HINTS[mode], HINT_Y,
                         config.GRAY)


def set_rtc(hour, minute, second):
    """Change the time of day, keeping the date the RTC already has.
    rtc.datetime() is (year, month, day, weekday, hour, minute, second,
    subseconds) -- note weekday sits in the MIDDLE, unlike localtime()."""
    year, month, day, weekday = rtc.datetime()[:4]
    rtc.datetime((year, month, day, weekday, hour, minute, second, 0))


rtc = RTC()
display = config.init_display()
a, b, push, k0 = config.init_controls()
push_button = Button(push)
knob = Knob(a, b, config.ENCODER_STEPS_PER_CLICK)

display.fill(config.BLACK)
display.rect(0, 0, config.WIDTH, config.HEIGHT, config.BLUE)
display.rect(1, 1, config.WIDTH - 2, config.HEIGHT - 2, config.BLUE)
config.centered_text(display, config.SMALL_FONT, "Set the Time", TITLE_Y,
                     config.GRAY)

mode = RUN
draw_mode(display, mode)
last_drawn = None

while True:
    now = time.ticks_ms()
    t = time.localtime()
    hour, minute, second = t[3], t[4], t[5]

    if push_button.pressed(now):
        mode = (mode + 1) % len(MODE_NAMES)
        draw_mode(display, mode)
        last_drawn = None                  # the highlight moved: redraw

    # Clicks since the last pass: 3 means three clicks clockwise. Asking
    # also empties the count, so turns made while the clock is running
    # are thrown away instead of being saved up.
    step = knob.turned()

    if step and mode == SET_HOUR:
        hour = (hour + step) % 24
        set_rtc(hour, minute, second)
    elif step and mode == SET_MINUTE:
        minute = (minute + step) % 60
        second = 0
        set_rtc(hour, minute, second)

    if (hour, minute, second) != last_drawn:
        draw_time(display, hour, minute, second, mode)
        last_drawn = (hour, minute, second)

    time.sleep_ms(10)
