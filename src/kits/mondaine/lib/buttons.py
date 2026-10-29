# buttons.py -- a push button that behaves itself.
#
# Lab 14 built a simple version of this one problem at a time, inside the
# lab. This module packages the finished idea, and adds two more tricks:
#
#     import config
#     from buttons import Button, SHORT, LONG
#     mode, up, down = [Button(pin) for pin in config.init_buttons()]
#
#     if up.pressed(now, repeat=True):      # True once per press, and again
#         ...                               # every 120 ms while it is held
#     press = mode.short_or_long(now)       # SHORT, LONG, or None
#
# A button is a push button wired from a pull-up pin to GND, so it reads 0
# while it is held and 1 when it is not. Three problems get in the way:
#
#   BOUNCE: the metal contacts rattle for a few milliseconds, so any change
#   that comes sooner than DEBOUNCE_MS after the last one is ignored.
#
#   HOLD TO REPEAT: with pressed(repeat=True), a button held for HOLD_MS
#   "presses" itself again every REPEAT_MS until it is let go.
#
#   QUICK TAPS WHILE THE LOOP IS BUSY: a program only notices a button
#   when it looks at it. If the loop spends 200 ms redrawing a clock hand,
#   a quick tap can go down AND come back up before the loop looks, and
#   the press is lost. So each Button also asks the Pico for an INTERRUPT:
#   the moment the pin falls, a tiny function runs -- no matter what the
#   loop is doing -- and writes down the time. The next time the loop
#   looks, it sees that note and counts the tap.
#
# For a button that does two jobs, use short_or_long() instead of
# pressed(): a short press is reported when the button is let go, and a
# long press as soon as it has been held for LONG_PRESS_MS.

import time

from machine import Pin

DEBOUNCE_MS = 40
HOLD_MS = 500
REPEAT_MS = 120
LONG_PRESS_MS = 1000

SHORT = 1               # short_or_long() results
LONG = 2


class Button:
    def __init__(self, pin):
        self.pin = pin
        self.held = False
        self.changed_at = time.ticks_ms()
        self.next_repeat = 0
        self.long_sent = False
        self.tapped_at = None           # written by the interrupt
        self.release_pending = False
        pin.irq(trigger=Pin.IRQ_FALLING, handler=self._falling)

    def _falling(self, pin):
        """The interrupt handler: runs the moment the pin falls."""
        self.tapped_at = time.ticks_ms()

    def _edge(self, now):
        """1 when the button (debounced) goes down, -1 when it comes back
        up, 0 when nothing has changed."""
        if self.release_pending:
            # Second half of a quick tap caught by the interrupt.
            self.release_pending = False
            self.held = False
            self.changed_at = now
            return -1
        down = self.pin.value() == 0
        if (down != self.held
                and time.ticks_diff(now, self.changed_at) > DEBOUNCE_MS):
            self.held = down
            self.changed_at = now
            self.tapped_at = None
            return 1 if down else -1
        tapped_at = self.tapped_at
        if not self.held and tapped_at is not None:
            self.tapped_at = None
            # A fall soon after the last release is just the contacts
            # bouncing as they open. A later one was a real, quick tap.
            if time.ticks_diff(tapped_at, self.changed_at) > DEBOUNCE_MS:
                self.held = True
                self.changed_at = now
                self.release_pending = True
                return 1
        return 0

    def pressed(self, now=None, repeat=False):
        """True once when the button goes down -- and, with repeat=True,
        again every REPEAT_MS for as long as it stays down."""
        if now is None:
            now = time.ticks_ms()
        edge = self._edge(now)
        if edge == 1:
            self.next_repeat = time.ticks_add(now, HOLD_MS)
            return True
        if (edge == 0 and self.held and repeat
                and time.ticks_diff(now, self.next_repeat) >= 0):
            self.next_repeat = time.ticks_add(now, REPEAT_MS)
            return True
        return False

    def short_or_long(self, now=None):
        """SHORT when the button is let go after a short press, LONG the
        moment it has been held for LONG_PRESS_MS (and nothing when it is
        let go after that), otherwise None."""
        if now is None:
            now = time.ticks_ms()
        edge = self._edge(now)
        if edge == 1:
            self.long_sent = False
            return None
        if edge == -1:
            return None if self.long_sent else SHORT
        if (self.held and not self.long_sent
                and time.ticks_diff(now, self.changed_at) >= LONG_PRESS_MS):
            self.long_sent = True
            return LONG
        return None
