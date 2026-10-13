# watchparts.py -- reusable parts for building watch faces.
#
# Labs 07 and 08 built these parts one step at a time, inside the lab.
# This module packages the same ideas so any face can use them:
#
#   Digit     a seven-segment digit that repaints only the pieces that change
#   TickRing  60 ticks around the rim, each repainted only when its color changes
#   TextLine  a fixed-width line of text that repaints only changed characters
#   Button    a push button with debounce, hold-to-repeat, short and long
#             presses, and an interrupt that catches quick taps
#
#     from watchparts import Digit, TickRing, TextLine, Button, DIGITS
#     ones = Digit(display, 100, 120, 40, 71, 9, WHITE, GHOST)
#     ones.show(DIGITS[7])
#
# Every display part remembers what it last put on the glass, so calling
# show() again with the same value sends nothing at all. If something else
# paints over a part (say, display.fill()), call its forget() so the next
# show() repaints it completely.

import math
import time
from array import array

from machine import Pin

import shapes

# ---------------------------------------------------------------------
# Digit
# ---------------------------------------------------------------------
#      aaa        Bit 0 is segment a, bit 1 is b, ... bit 6 is g.
#     f   b       Each digit is a 7-bit pattern, so old ^ new has a 1
#      ggg        bit for every segment that switched. Lab 08 explains
#     e   c       the whole idea.
#      ddd
SEG_A, SEG_B, SEG_C, SEG_D, SEG_E, SEG_F, SEG_G = 1, 2, 4, 8, 16, 32, 64
ALL_SEGMENTS = 0b1111111
BLANK = 0
DIGITS = (
    0b0111111,  # 0
    0b0000110,  # 1
    0b1011011,  # 2
    0b1001111,  # 3
    0b1100110,  # 4
    0b1101101,  # 5
    0b1111101,  # 6
    0b0000111,  # 7
    0b1111111,  # 8
    0b1101111,  # 9
)

# The six joints where segments meet, and the segments that meet there.
# A joint is lit whenever any of its segments is, so a lit digit reads as
# one solid stroke.
_JOINTS = (SEG_A | SEG_F, SEG_A | SEG_B, SEG_F | SEG_G | SEG_E,
           SEG_B | SEG_G | SEG_C, SEG_E | SEG_D, SEG_C | SEG_D)


def pieces(segments):
    """7 segment bits -> 13 piece bits: the segments, then one bit for
    each joint that touches a lit segment."""
    bits = segments
    for j in range(6):
        if segments & _JOINTS[j]:
            bits |= 1 << (7 + j)
    return bits


class Digit:
    """One seven-segment digit.

    (x, y) is the top-left corner of a width x height box, and thickness
    is how thick each segment is. height must be 3 * thickness plus an
    even number, so the upper and lower halves come out the same size.
    Unlit segments are painted `ghost`, like the faint unlit segments of
    a real LCD watch; use the background color to hide them.

    half=True makes a half digit that can only show 1 or blank -- just the
    right-hand column, with its left edge at x. It is the leftmost digit
    of a 12-hour clock, whose hour is never more than 12."""

    def __init__(self, display, x, y, width, height, thickness, color, ghost,
                 half=False):
        t = thickness
        run = (height - 3 * t) // 2          # length of a vertical segment
        if 3 * t + 2 * run != height:
            raise ValueError("height must be 3 * thickness + an even number")
        middle = t + run
        bottom = 2 * t + 2 * run
        right = width - t
        if half:
            x -= right                       # only the right column is drawn
        across = width - 2 * t
        self.rects = tuple((x + px, y + py, w, h) for px, py, w, h in (
            (t, 0, across, t),               # a
            (right, t, t, run),              # b
            (right, middle + t, t, run),     # c
            (t, bottom, across, t),          # d
            (0, middle + t, t, run),         # e
            (0, t, t, run),                  # f
            (t, middle, across, t),          # g
            (0, 0, t, t),                    # joint: a f
            (right, 0, t, t),                # joint: a b
            (0, middle, t, t),               # joint: f g e
            (right, middle, t, t),           # joint: b g c
            (0, bottom, t, t),               # joint: e d
            (right, bottom, t, t),           # joint: c d
        ))
        self.present = pieces(SEG_B | SEG_C if half else ALL_SEGMENTS)
        self.display = display
        self.color = color
        self.ghost = ghost
        self.forget()

    def forget(self):
        """Make the next show() repaint every piece."""
        self.shown = None
        self.shown_color = None

    def show(self, segments, color=None):
        """Show a segment pattern -- DIGITS[n], BLANK, or any 7-bit mix --
        in `color`, or in the digit's own color if none is given."""
        if color is None:
            color = self.color
        lit = pieces(segments) & self.present
        if self.shown is None:
            changed = self.present
        else:
            changed = lit ^ self.shown
            if color != self.shown_color:
                changed |= lit               # lit before and after: new color
        for bit in range(13):
            if changed & (1 << bit):
                x, y, w, h = self.rects[bit]
                self.display.fill_rect(
                    x, y, w, h, color if lit & (1 << bit) else self.ghost)
        self.shown = lit
        self.shown_color = color


# ---------------------------------------------------------------------
# TickRing
# ---------------------------------------------------------------------
class _RunRecorder:
    """Stands in for the display while shapes.poly() works out a shape,
    keeping its horizontal runs instead of drawing them."""

    def __init__(self):
        self.runs = []

    def hline(self, x, y, length, color):
        self.runs.append((x, y, length))


# Tick shapes already worked out, by ring size, so a second ring of the
# same size -- say, when the watch switches back to a mode it showed
# before -- reuses them instead of spending another 0.6 s.
_ring_cache = {}


class TickRing:
    """60 ticks around a circle, one per second, like the rim of lab 08.

    Every fifth tick reaches in further, to `inner_five`. Working out a
    tick's shape takes trigonometry and a scanline fill, so each one is
    worked out once, here, and replayed from then on (lab 08 explains
    why). The first ring of a size takes about 0.6 s and 50 KB of RAM;
    later rings of the same size reuse its shapes for free."""

    def __init__(self, display, center_x, center_y, outer, inner, inner_five,
                 half_width=2):
        self.display = display
        size = (center_x, center_y, outer, inner, inner_five, half_width)
        if size in _ring_cache:
            self.runs = _ring_cache[size]
            self.forget()
            return
        self.runs = []
        for second in range(60):
            angle = second * 2 * math.pi / 60
            s = math.sin(angle)
            c = math.cos(angle)
            start = inner_five if second % 5 == 0 else inner
            corners = []
            for along, across in ((start, -half_width), (outer, -half_width),
                                  (outer, half_width), (start, half_width)):
                corners.append(round(center_x + along * s + across * c))
                corners.append(round(center_y - along * c + across * s))
            recorder = _RunRecorder()
            shapes.poly(recorder, 0, 0, array('h', corners), 0, 1)
            self.runs.append(recorder.runs)
        _ring_cache[size] = self.runs
        self.forget()

    def forget(self):
        """Make the next paint() of every tick actually repaint it."""
        self.colors = [None] * 60

    def paint(self, second, color):
        """Paint one tick, unless it already shows that color."""
        if self.colors[second] != color:
            for x, y, length in self.runs[second]:
                self.display.hline(x, y, length, color)
            self.colors[second] = color


# ---------------------------------------------------------------------
# TextLine
# ---------------------------------------------------------------------
class TextLine:
    """A line of text with a fixed number of characters, centered on x.

    Shorter text is padded with spaces to fill the line. text() paints
    each character's background as well as its shape, so a new character
    completely covers the old one: nothing is ever cleared first, and
    only characters that changed are repainted.

    A new TextLine assumes its spot on the screen is already blank (the
    background color), as it is right after display.fill() -- so showing
    a short word, or nothing at all, sends only the characters it needs."""

    def __init__(self, display, font, center_x, y, chars, color,
                 background=0):
        self.display = display
        self.font = font
        self.x = center_x - chars * font.WIDTH // 2
        self.y = y
        self.chars = chars
        self.color = color
        self.background = background
        self.shown = " " * chars
        self.shown_color = color

    def forget(self):
        """Make the next show() repaint every character."""
        self.shown = None
        self.shown_color = None

    def show(self, text, color=None):
        if color is None:
            color = self.color
        text = text[:self.chars]
        pad = self.chars - len(text)
        text = " " * (pad // 2) + text + " " * (pad - pad // 2)
        redraw_all = self.shown is None or color != self.shown_color
        for i in range(self.chars):
            if redraw_all or text[i] != self.shown[i]:
                self.display.text(self.font, text[i],
                                  self.x + i * self.font.WIDTH, self.y,
                                  color, self.background)
        self.shown = text
        self.shown_color = color


# ---------------------------------------------------------------------
# Button
# ---------------------------------------------------------------------
DEBOUNCE_MS = 40
HOLD_MS = 500
REPEAT_MS = 120
LONG_PRESS_MS = 1000

SHORT = 1               # short_or_long() results
LONG = 2


class Button:
    """A push button wired from a pull-up pin to GND, so it reads 0 while
    held. Lab 07 explains the first two problems this solves:

      BOUNCE: the contacts rattle for a few milliseconds, so any change
      that comes sooner than DEBOUNCE_MS after the last one is ignored.

      HOLD TO REPEAT: with pressed(repeat=True), a button held for HOLD_MS
      "presses" itself again every REPEAT_MS until it is let go.

      QUICK TAPS WHILE THE LOOP IS BUSY: a program only notices a button
      when it looks at it. If the loop spends 200 ms drawing a watch face,
      a quick tap can go down AND come back up before the loop looks, and
      the press is lost. So each Button also asks the Pico for an
      INTERRUPT: the moment the pin falls, a tiny function runs -- no
      matter what the loop is doing -- and writes down the time. The next
      time the loop looks, it sees that note and counts the tap.

    For a button that does two jobs, use short_or_long() instead of
    pressed(): a short press is reported when the button is let go, and a
    long press as soon as it has been held for LONG_PRESS_MS."""

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
