# watchparts.py -- reusable parts for building clock faces.
#
# Labs 06, 07, 12 and 13 built these parts one step at a time, inside the
# lab. This module packages the same ideas so any face can use them:
#
#   Digit      a seven-segment digit that repaints only the pieces that change
#   TickFrame  60 ticks around the edge of the screen, each repainted only
#              when its color changes
#   TextLine   a fixed-width line of text that repaints only changed characters
#   Button     a push button with debounce, hold-to-repeat, short and long
#              presses, and an interrupt that catches quick taps
#   Knob       the rotary encoder, counted in clicks by interrupts
#
#     from watchparts import Digit, TickFrame, TextLine, Button, Knob, DIGITS
#     ones = Digit(display, 100, 40, 28, 51, 5, WHITE, GHOST)
#     ones.show(DIGITS[7])
#
# Every display part remembers what it last put on the glass, so calling
# show() again with the same value sends nothing at all. If something else
# paints over a part (say, display.fill()), call its forget() so the next
# show() repaints it completely.
#
# The name, and most of the code, come from the sw-gc9b72 smartwatch kit.
# TickFrame is that kit's TickRing bent to fit a rectangle, and Knob is
# new here.

import time

from machine import Pin

# ---------------------------------------------------------------------
# Digit
# ---------------------------------------------------------------------
#      aaa        Bit 0 is segment a, bit 1 is b, ... bit 6 is g.
#     f   b       Each digit is a 7-bit pattern, so old ^ new has a 1
#      ggg        bit for every segment that switched. Lab 13 explains
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
    a real LCD clock; use the background color to hide them.

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
# TickFrame
# ---------------------------------------------------------------------
class TickFrame:
    """60 ticks around the edge of the screen, one per second.

    A round watch has a ring of ticks around its rim. This is the same
    ring bent into a rectangle: tick 0 is at the middle of the top edge,
    and the ticks run clockwise, evenly spaced along the edge. So tick 15
    is at the middle of the right side, 30 at the bottom, and 45 on the
    left -- the same places as 3, 6 and 9 o'clock. Every fifth tick
    reaches further in.

    Each tick is one small rectangle, so painting one is a single
    fill_rect(). Long ticks reach `depth_five` pixels in from the edge;
    keep everything else on the screen at least that far from it."""

    def __init__(self, display, width, height, depth=3, depth_five=6,
                 length=5):
        self.display = display
        self.rects = []
        top = width // 2                 # distance left along the top edge
        for second in range(60):
            # How far round the edge this tick is, clockwise from the
            # middle of the top.
            d = second * 2 * (width + height) // 60
            deep = depth_five if second % 5 == 0 else depth
            if d < top:                                 # top, right half
                rect = (top + d - length // 2, 0, length, deep)
            elif d < top + height:                      # right side
                rect = (width - deep, d - top - length // 2, deep, length)
            elif d < top + height + width:              # bottom
                x = width - (d - top - height)
                rect = (x - length // 2, height - deep, length, deep)
            elif d < top + 2 * height + width:          # left side
                y = height - (d - top - height - width)
                rect = (0, y - length // 2, deep, length)
            else:                                       # top, left half
                x = d - top - 2 * height - width
                rect = (x - length // 2, 0, length, deep)
            # Keep ticks next to a corner on the screen, and keep the
            # side ticks out of the rows the top and bottom ticks use, so
            # that no two ticks share a pixel.
            x, y, w, h = rect
            x = max(0, min(x, width - w))
            if w == deep:                               # a side tick
                y = max(depth, min(y, height - depth - h))
            else:
                y = max(0, min(y, height - h))
            self.rects.append((x, y, w, h))
        self.forget()

    def forget(self):
        """Make the next paint() of every tick actually repaint it."""
        self.colors = [None] * 60

    def paint(self, second, color):
        """Paint one tick, unless it already shows that color."""
        if self.colors[second] != color:
            x, y, w, h = self.rects[second]
            self.display.fill_rect(x, y, w, h, color)
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
    held: K0, or the knob's own PUSH switch. It solves three problems:

      BOUNCE: the contacts rattle for a few milliseconds, so any change
      that comes sooner than DEBOUNCE_MS after the last one is ignored.

      HOLD TO REPEAT: with pressed(repeat=True), a button held for HOLD_MS
      "presses" itself again every REPEAT_MS until it is let go.

      QUICK TAPS WHILE THE LOOP IS BUSY: a program only notices a button
      when it looks at it. If the loop spends 200 ms drawing a clock face,
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


# ---------------------------------------------------------------------
# Knob
# ---------------------------------------------------------------------
# The four positions of (A, B), in the order a clockwise turn visits
# them. Lab 06 explains.
_CLOCKWISE = ((0, 0), (1, 0), (1, 1), (0, 1))


class Knob:
    """The rotary encoder's A and B outputs, counted in clicks.

    Lab 06 showed how (A, B) walks around a loop of four positions, one
    step at a time, and lab 07 why the steps have to be counted by
    interrupts: a step that came and went while the loop was busy drawing
    would otherwise be lost.

        knob = Knob(a, b, config.ENCODER_STEPS_PER_CLICK)
        clicks = knob.turned()

    turned() gives the clicks since the last time you asked: 2 for two
    clicks clockwise, -1 for one click back, 0 if the knob has not moved.
    Add it to whatever the knob is setting."""

    def __init__(self, a, b, steps_per_click=2):
        self.a = a
        self.b = b
        self.per_click = steps_per_click
        self.steps = 0
        self.reported = 0
        self.last = _CLOCKWISE.index((a.value(), b.value()))
        a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._moved)
        b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self._moved)

    def _moved(self, pin):
        """The interrupt handler: runs the moment A or B changes."""
        now = _CLOCKWISE.index((self.a.value(), self.b.value()))
        move = (now - self.last) % 4
        self.last = now
        if move == 1:
            self.steps += 1
        elif move == 3:
            self.steps -= 1

    def turned(self):
        """Clicks since the last call: positive is clockwise."""
        # Round the step count to the nearest whole click.
        clicks = (self.steps + self.per_click // 2) // self.per_click
        moved = clicks - self.reported
        self.reported = clicks
        return moved
