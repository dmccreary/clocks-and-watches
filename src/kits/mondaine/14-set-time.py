# Lab 14: Set the Time with the Buttons
# A railway clock you can set by hand -- for when there is no WiFi.
#
#   MODE  (GP13)  steps through:  run -> set hour -> set minute -> run
#   UP    (GP14)  adds one to the hand being set
#   DOWN  (GP15)  subtracts one
#
# NEW IDEAS: a CLASS (a bundle of data and the functions that use it),
# and a program with MODES.
#
# Hold UP or DOWN and the hand keeps moving, faster than you could press.
# Every press that changes the minute also zeroes the seconds, so you can
# match another clock: stop one press short of the next minute, then make
# that last UP press the moment the other clock reaches it. While you set
# the time, the red hand waits at 12.
#
# The time is written straight into the Pico's real-time clock (RTC), so
# lab 09 and lab 12 pick it up after a soft reset -- as long as the Pico
# stays powered.
#
# Lab 13 read the buttons raw. This one has to deal with two things raw
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
#
# Lab 15 uses lib/buttons.py, which is this class plus two more tricks.

NAME = "14-set-time.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import RTC
import config
import mondaine

DEBOUNCE_MS = 40
HOLD_MS = 500
REPEAT_MS = 120

RUN, SET_HOUR, SET_MINUTE = 0, 1, 2
LABELS = ("", " SET HOUR ", "SET MINUTE")     # the same width, 10 characters
LABEL_Y = 240


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

face = mondaine.Face(display)
face.draw_dial()

mode = RUN
last_drawn = None

while True:
    now = time.ticks_ms()
    t = time.localtime()
    hour, minute, second = t[3], t[4], t[5]

    if mode_button.pressed(now):
        mode = (mode + 1) % 3
        if mode == RUN:
            face.draw_dial()               # wipes the label off the dial
        last_drawn = None

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

    shown_second = second if mode == RUN else 0     # the red hand waits
    if (hour, minute, shown_second, mode) != last_drawn:
        face.show((hour % 12) * 30 + minute * 0.5,
                  minute * 6,
                  shown_second * 6)
        if mode != RUN:
            # Painted last, so it lies on top of whatever the hands did.
            config.centered_text(display, config.SMALL_FONT, LABELS[mode],
                                 LABEL_Y, config.YELLOW, config.BLACK)
        last_drawn = (hour, minute, shown_second, mode)

    time.sleep_ms(10)
