# Lab 07: Set the Time with the Buttons
# A digital clock you can set by hand -- for when there is no WiFi.
#
#   MODE  (GP13)  steps through:  run -> set hour -> set minute -> run
#   UP    (GP14)  adds one to the highlighted field
#   DOWN  (GP15)  subtracts one
#
# Hold UP or DOWN and the number keeps changing, faster than you could
# press. Setting the minute also zeroes the seconds, so you can match
# another clock: set the minute one ahead, then press MODE the moment
# the other clock reaches it.
#
# The time is written straight into the Pico's real-time clock (RTC), so
# lab 03 and lab 05 pick it up after a soft reset -- as long as the Pico
# stays powered.
#
# Lab 06 read the buttons raw. This one has to deal with two things raw
# reading gets wrong:
#
#   BOUNCE. A button's metal contacts rattle for a few milliseconds when
#   they close, so the pin flickers 0-1-0-1 before it settles. Counted
#   naively, one press would move the hour three places. The Button class
#   ignores any change that comes less than DEBOUNCE_MS after the last one.
#
#   HOLD TO REPEAT. Stepping from 0 to 45 minutes one press at a time is
#   miserable. After a button has been held for HOLD_MS, it "presses"
#   itself again every REPEAT_MS until you let go.

NAME = "07-set-time.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import RTC
import config
import shapes

DEBOUNCE_MS = 40
HOLD_MS = 500
REPEAT_MS = 120

RUN, SET_HOUR, SET_MINUTE = 0, 1, 2
MODE_NAMES = ("", "Set hour", "Set minute")

TIME_Y = 150
AMPM_Y = 190
MODE_Y = 230
HINT_Y = 110

HIGHLIGHT_FG = config.BLACK
HIGHLIGHT_BG = config.YELLOW


class Button:
    """One push button, with debounce and hold-to-repeat."""

    def __init__(self, pin):
        self.pin = pin
        self.held = False
        self.changed_at = time.ticks_ms()
        self.next_repeat = 0

    def pressed(self, now, repeat=False):
        """True once when the button goes down -- and, if repeat is True,
        again every REPEAT_MS for as long as it stays down."""
        down = self.pin.value() == 0
        if (down != self.held
                and time.ticks_diff(now, self.changed_at) > DEBOUNCE_MS):
            self.held = down
            self.changed_at = now
            if down:
                self.next_repeat = time.ticks_add(now, HOLD_MS)
                return True
            return False
        if (self.held and repeat
                and time.ticks_diff(now, self.next_repeat) >= 0):
            self.next_repeat = time.ticks_add(now, REPEAT_MS)
            return True
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
    # "Set minute" is the longest label: 10 x 8 = 80 px. Clear a bit more.
    display.fill_rect(130, MODE_Y, 100, 16, config.BLACK)
    config.centered_text(display, config.SMALL_FONT, MODE_NAMES[mode],
                         MODE_Y, HIGHLIGHT_BG)


def set_rtc(hour, minute, second):
    """Change the time of day, keeping the date the RTC already has.
    rtc.datetime() is (year, month, day, weekday, hour, minute, second,
    subseconds) -- note weekday sits in the MIDDLE, unlike localtime()."""
    year, month, day, weekday = rtc.datetime()[:4]
    rtc.datetime((year, month, day, weekday, hour, minute, second, 0))


rtc = RTC()
display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]

display.fill(config.BLACK)
shapes.ring(display, config.CENTER_X, config.CENTER_Y,
            config.SAFE_RADIUS, config.BLUE, 3)
config.centered_text(display, config.SMALL_FONT, "MODE  UP  DOWN", HINT_Y,
                     config.GRAY)

mode = RUN
last_drawn = None

while True:
    now = time.ticks_ms()
    t = time.localtime()
    hour, minute, second = t[3], t[4], t[5]

    if mode_button.pressed(now):
        mode = (mode + 1) % len(MODE_NAMES)
        draw_mode(display, mode)
        last_drawn = None                  # the highlight moved: redraw

    step = 0
    if up_button.pressed(now, repeat=True):
        step = 1
    elif down_button.pressed(now, repeat=True):
        step = -1

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
