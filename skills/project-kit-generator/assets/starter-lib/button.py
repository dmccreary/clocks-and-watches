# button.py -- a push button that never misses a press.
#
# Wiring: one leg of the button to a GP pin, the other leg to GND. There is
# no outside resistor. We switch on the Pico's own PULL_UP resistor, which
# holds the pin at 3.3 V (reads as 1). Pressing the button connects the pin
# to GND (reads as 0).
#
# WHY AN INTERRUPT?  Drawing on the round screen can take a good fraction of
# a second. If the program only checked the button between drawings, a quick
# tap could come and go while the screen was busy. An interrupt is different:
# the Pico stops what it is doing the instant the button changes, jots down
# the time, and goes straight back to work. Nothing is missed.
#
# WHY "BOUNCE" IS TRICKY.  A real button does not switch cleanly. For a few
# thousandths of a second the contacts chatter on and off ("bounce"), so one
# push makes a whole burst of changes. Worse, the interrupt does not run at the
# exact instant of a change. It runs a moment later, and by then the button
# may have bounced to the OPPOSITE state. So the interrupt must NOT look at the
# pin and guess "that was a press" or "that was a release". A first version of
# this file did exactly that, and it lost about one press in three!
#
# HOW IT WORKS NOW
#   * The interrupt only writes down WHEN something changed. It never looks at
#     the pin. A burst of chatter counts as one change, stamped with the time
#     the burst began.
#   * The main program calls next_press() often. When the button has been
#     quiet for debounce_ms, next_press() looks at where the button ended
#     up. Now the answer is stable, so there is nothing to guess.
#   * If the screen was busy and a whole tap came and went, the written-down
#     times still tell us how long the press lasted.
#
# Every completed press (finger down, then finger up) puts its length in
# milliseconds into a small waiting line. next_press() takes them out one at
# a time.
import time
from machine import Pin

_RING = 16  # how many changes we remember at once. Must be a power of 2.


class Button:
    def __init__(self, pin_number, debounce_ms):
        self.pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
        self.debounce_ms = debounce_ms

        # Written by the interrupt.
        self._last_edge = time.ticks_add(time.ticks_ms(), -1000)
        self._bursts = 0                    # how many bursts of chatter so far
        self._burst_times = [0] * _RING     # when each recent burst began

        # Used by the main program.
        self._seen = 0                      # bursts we have already dealt with
        self._down = False                  # do we think the button is held?
        self._down_at = 0                   # when the current press began
        self._ignore = False                # True if it was already held at startup
        if self.pin.value() == 0:
            self._down = True               # held while starting: ignore that press
            self._ignore = True
        self._queue = [0] * _RING
        self._head = 0
        self._tail = 0

        self.pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING,
                     handler=self._on_change)

    def _on_change(self, pin):
        # This runs inside the interrupt, so it must be quick and it must not
        # build any new objects. It does NOT read the pin. It only writes
        # down the time.
        now = time.ticks_ms()
        if time.ticks_diff(now, self._last_edge) >= self.debounce_ms:
            self._burst_times[self._bursts & (_RING - 1)] = now   # a new burst begins
            self._bursts += 1
        self._last_edge = now

    def _flip(self, when, sure):
        """The button changed state at time `when`.

        sure is False when we are guessing (we lost track of some changes). A
        guessed release has no trustworthy length, so we throw it away. A
        missed tap is better than a fake long press!"""
        if self._down:
            self._down = False              # it was released
            if self._ignore:
                self._ignore = False
                return
            if not sure:
                return
            length = time.ticks_diff(when, self._down_at)
            if length < 1:
                length = 1                  # 0 is reserved for "no press waiting"
            next_head = (self._head + 1) & (_RING - 1)
            if next_head == self._tail:     # the line is full: forget the oldest
                self._tail = (self._tail + 1) & (_RING - 1)
            self._queue[self._head] = length
            self._head = next_head
        else:
            self._down = True               # it was pressed
            self._down_at = when

    def _look(self):
        """Work out what the button did, once it has stopped bouncing."""
        bursts = self._bursts
        if bursts == self._seen:
            return                          # nothing has happened
        last = self._last_edge
        now = time.ticks_ms()
        if time.ticks_diff(now, last) < self.debounce_ms:
            return                          # still bouncing. Look again soon.
        pressed = self.pin.value() == 0     # the button has settled, so this is the truth
        if bursts != self._bursts or last != self._last_edge:
            return                          # it moved while we looked. Try again.

        count = bursts - self._seen
        self._seen = bursts

        # Each burst is one change, and changes take turns: press, release,
        # press, release... If the number of changes fits with where the
        # button ended up, replay them all in order. That is how a quick tap
        # that happened while the screen was busy is still counted.
        fits = False
        if count <= _RING:
            was_down = self._down
            if count % 2 == 1:
                was_down = not was_down
            fits = (was_down == pressed)

        if fits:
            for i in range(count):
                self._flip(self._burst_times[(bursts - count + i) & (_RING - 1)], True)
        elif pressed != self._down:
            # The count does not fit (stray electrical noise, perhaps). Trust
            # the button itself: it is not where we thought it was.
            self._flip(self._burst_times[(bursts - 1) & (_RING - 1)], False)
        # Otherwise it was only noise, and the button is where we thought.

    def next_press(self):
        """Return the length of the oldest press in milliseconds, or 0 if none."""
        self._look()
        if self._tail == self._head:
            return 0
        length = self._queue[self._tail]
        self._tail = (self._tail + 1) & (_RING - 1)
        return length

    def is_down(self):
        """True while the button is being held down right now."""
        return self.pin.value() == 0
