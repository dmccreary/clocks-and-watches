# mondaine.py -- a Swiss-railway-style clock face, and its stop-and-go timing.
#
# Labs 02 to 06 build this face one piece at a time, inside the lab. This
# module packages the finished pieces so every lab after that can focus on
# one new idea:
#
#     import mondaine
#     face = mondaine.Face(display)
#     face.draw_dial()                          # white dial + 60 markers
#     face.show(hour_deg, minute_deg, second_deg)   # move the three hands
#
# and the timing that makes the clock special:
#
#     clock = mondaine.SweepClock()             # RTC seconds + milliseconds
#     hour, minute, ms = clock.now()            # ms = 0..59999 into the minute
#     face.show(*mondaine.hand_angles(hour, minute, ms))
#
# THE DESIGN. The proportions follow the Swiss station clock that Hans
# Hilfiker designed for the Swiss Federal Railways (SBB) in the 1940s: a
# white dial, no numbers, twelve heavy five-minute bars, forty-eight small
# minute bars, two tapered black hands, and a red second hand that ends in
# a disc, like a railway signal paddle. Every size below is a multiple of
# one design unit, "a", equal to 1/100 of the dial's diameter. Pick any
# UNIT and the whole face scales together. This kit uses 3.4 pixels, which
# leaves the outer bars just inside the bezel (48.5 x 3.4 = 165 px, and the
# glass is visible out to 168).
#
# This kit is not made or endorsed by SBB or Mondaine, and the face has no
# logo. It is an independent drawing of a public design idea for learning.
#
# THE MOTION. The red hand does not tick. It glides once around the dial in
# 58.5 seconds, stops at 12, and WAITS for about a second and a half. While
# it waits, the minute hand hops ahead one minute (and the hour hand creeps
# a half degree), and then the red hand sets off again.
#
# THE DRAWING PROBLEM. This display has no frame buffer, so drawing is
# sending: every pixel costs SPI bytes and every drawing call costs time.
# Redrawing the whole face ten times a second is out of the question, and
# so is the usual trick of erasing a hand and redrawing it, because the red
# hand lies ON TOP of the black hands, and both lie on top of the bars.
# Erase one and you cut a hole in the others.
#
# So Face.show() works on one row of pixels at a time, in three steps:
#
#   1. Work out, for each hand that moved, the left and right edge of the
#      old shape and the new shape on every row they touch. Rows where the
#      edges did not change are skipped.
#   2. For each remaining row, work out what color every pixel in the
#      changed stretch should have by looking at the WHOLE scene from the
#      bottom up: dial, bars, hour hand, minute hand, red stem, red disc.
#      The topmost thing that covers a pixel wins.
#   3. Send those pixels to the glass in small rectangles, a band of up to
#      BAND rows at a time. A drawing command has a fixed cost no matter how
#      small it is (the window has to be set up first), so one rectangle
#      per band beats one command per row, by a wide margin.
#
# Nothing is ever erased and then repaired. Each pixel is written once,
# with the color it should end up with.

import math
import time

import config

WHITE = config.WHITE
BLACK = config.BLACK
RED = config.RAIL_RED

UNIT = 3.4                      # pixels in one design unit "a"
BAND = 16                       # most rows repainted by one drawing command

# All of these are in design units. "Along" is measured from the center
# pin toward the tip; a negative number is the short tail behind the pin.
HOUR_HAND = (-12.0, 3.2, 32.0, 2.6)       # tail, tail half width, tip, tip half width
MINUTE_HAND = (-12.0, 2.6, 46.0, 1.8)
STEM = (-16.5, 0.7, 31.25, 0.7)           # the thin red rod
DISC_CENTER = 31.25                       # the red disc sits here...
DISC_RADIUS = 5.25                        # ...and touches the bars' inner end at 36.5
FIVE_BAR = (36.5, 48.5, 1.75)             # inner end, outer end, half width
MINUTE_BAR = (45.0, 48.5, 0.7)

# The stop-and-go timing, in milliseconds into each minute.
SWEEP_MS = 58500                # the red hand circles in 58.5 s...
HOLD_MS = 60000 - SWEEP_MS      # ...then waits the rest of the minute: 1.5 s
ADVANCE_START_MS = 58650        # the minute hand starts to hop 150 ms into the wait
ADVANCE_MS = 720                # and takes 720 ms to get there
RESYNC_MS = ADVANCE_START_MS + ADVANCE_MS + 30   # all hands at rest: safe to resync

CX = config.CENTER_X
CY = config.CENTER_Y


# ---------------------------------------------------------------------
# Timing
# ---------------------------------------------------------------------
def smootherstep(x):
    """0 -> 1 with a gentle start and a gentle finish. x is clamped to 0..1.

    A plain straight-line move looks mechanical: it starts and stops
    instantly. This curve eases in and out, so the minute hand seems to
    have weight. It is the polynomial 6x^5 - 15x^4 + 10x^3."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    return x * x * x * (x * (x * 6 - 15) + 10)


def advance(ms):
    """How far the minute hand has hopped: 0.0 before the hop, 1.0 after."""
    return smootherstep((ms - ADVANCE_START_MS) / ADVANCE_MS)


def hand_angles(hour, minute, ms):
    """(hour hand, minute hand, second hand) in degrees clockwise from 12,
    for this hour (0-23), minute, and millisecond into the minute."""
    step = advance(ms)
    minute_deg = (minute + step) * 6
    hour_deg = (hour % 12) * 30 + (minute + step) * 0.5
    second_deg = min(ms, SWEEP_MS) * 360 / SWEEP_MS
    return hour_deg, minute_deg, second_deg


class SweepClock:
    """The Pico's real-time clock only counts whole seconds, but a gliding
    hand needs milliseconds. This waits for the RTC's seconds to change,
    notes time.ticks_ms() at that instant, and counts milliseconds from
    there. Call sync() again whenever the RTC might have been set."""

    def __init__(self):
        self.sync()

    def sync(self):
        """Wait (up to one second) for the next RTC tick, and start over
        from it. Afterward the clock agrees with the RTC to about 1 ms."""
        first = time.localtime()[5]
        while time.localtime()[5] == first:
            time.sleep_ms(1)
        self.tick0 = time.ticks_ms()
        t = time.localtime()
        self.hour = t[3]
        self.minute = t[4]
        self.ms0 = t[5] * 1000

    def now(self):
        """(hour 0-23, minute, milliseconds into the minute)."""
        ms = self.ms0 + time.ticks_diff(time.ticks_ms(), self.tick0)
        minute = self.minute + ms // 60000
        hour = (self.hour + minute // 60) % 24
        return hour, minute % 60, ms % 60000


# ---------------------------------------------------------------------
# Shapes: a shape is the left and right edge of a figure on each row
# ---------------------------------------------------------------------
def _scan(points):
    """The rows covered by a convex polygon, as (top row, lows, highs):
    on row top + k the polygon covers columns lows[k] to highs[k]. Uses
    the same rule as shapes.poly(): an edge covers the rows from its upper
    end up to, but not including, its lower end."""
    count = len(points)
    top = min(p[1] for p in points)
    rows = max(p[1] for p in points) - top
    lows = [9999] * rows
    highs = [-9999] * rows
    for i in range(count):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % count]
        if y0 == y1:
            continue
        if y0 > y1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        slope = (x1 - x0) / (y1 - y0)
        for row in range(y0, y1):
            x = int(x0 + (row - y0) * slope + 0.5)
            k = row - top
            if x < lows[k]:
                lows[k] = x
            if x > highs[k]:
                highs[k] = x
    return top, lows, highs


def _quad_span(points, y):
    """Columns (low, high) that a four-point polygon covers on row y, worked
    out on demand. Agrees exactly with _scan(). (low > high: nothing.)"""
    low = 9999
    high = -9999
    for i in range(4):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) & 3]
        if y0 == y1:
            continue
        if y0 > y1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        if y0 <= y < y1:
            slope = (x1 - x0) / (y1 - y0)
            x = int(x0 + (y - y0) * slope + 0.5)
            if x < low:
                low = x
            if x > high:
                high = x
    return low, high


class _Shape:
    """One colored figure, stored as its per-row left and right edges."""

    def __init__(self, key, color, top, lows, highs):
        self.key = key              # what pose this is, to spot "unchanged"
        self.color = color
        self.top = top
        self.lows = lows
        self.highs = highs
        self.rows = len(lows)

    def edges(self, y):
        """(low, high) on row y; low > high means the shape is not there."""
        k = y - self.top
        if 0 <= k < self.rows:
            return self.lows[k], self.highs[k]
        return 9999, -9999


def _disc(cx, cy, r, color):
    lows = []
    highs = []
    for dy in range(-r, r + 1):
        inside = 1.0 - (float(dy) * dy) / (float(r) * r)
        half = int(r * math.sqrt(inside) + 0.5) if inside > 0 else 0
        lows.append(cx - half)
        highs.append(cx + half)
    return _Shape((cx, cy, r), color, cy - r, lows, highs)


# ---------------------------------------------------------------------
# The face
# ---------------------------------------------------------------------
class Face:
    """The dial and its three hands. Angles are degrees clockwise from 12."""

    def __init__(self, display, unit=UNIT):
        self.display = display
        self.unit = unit
        self.layers = None          # [hour, minute, stem, disc] on the glass
        # Where the bars are, worked out once: four corners for each.
        self.bars = []
        for i in range(60):
            inner, outer, half = FIVE_BAR if i % 5 == 0 else MINUTE_BAR
            self.bars.append(self._corners(i * 6, inner * unit, outer * unit,
                                           half * unit, half * unit))
        self.bar_tops = [min(p[1] for p in bar) for bar in self.bars]
        self.bar_bottoms = [max(p[1] for p in bar) for bar in self.bars]
        # Anything painted closer to the center than this cannot touch a bar.
        reach = FIVE_BAR[0] * unit - 3
        self.rim2 = reach * reach
        # Scratch space for one band of pixels, and one full row of each
        # color to copy from. Made once, here, so drawing never has to ask
        # the memory manager for more.
        self.band = bytearray(BAND * config.WIDTH * 2)
        self.fills = {}
        for color in (WHITE, BLACK, RED):
            self.fills[color] = bytes((color >> 8, color & 0xFF)) * config.WIDTH

    def _corners(self, angle, tail, tip, tail_half, tip_half):
        """Four corners (as screen points) of a tapered bar pointing at
        `angle` degrees: tail end first, then the tip end."""
        a = math.radians(angle)
        s = math.sin(a)
        c = math.cos(a)
        points = []
        for along, across in ((tail, -tail_half), (tip, -tip_half),
                              (tip, tip_half), (tail, tail_half)):
            points.append((round(CX + along * s + across * c),
                           round(CY - along * c + across * s)))
        return points

    def _hand(self, angle, shape, color, old):
        tail, tail_half, tip, tip_half = shape
        u = self.unit
        points = self._corners(angle, tail * u, tip * u,
                               tail_half * u, tip_half * u)
        key = tuple(points)
        if old is not None and old.key == key:
            return old
        top, lows, highs = _scan(points)
        return _Shape(key, color, top, lows, highs)

    def _build(self, hour_deg, minute_deg, second_deg, old):
        """The four moving shapes for these angles, reusing any that did
        not change by even one pixel."""
        o = old or (None, None, None, None)
        hour = self._hand(hour_deg, HOUR_HAND, BLACK, o[0])
        minute = self._hand(minute_deg, MINUTE_HAND, BLACK, o[1])
        stem = self._hand(second_deg, STEM, RED, o[2])
        a = math.radians(second_deg)
        x = round(CX + DISC_CENTER * self.unit * math.sin(a))
        y = round(CY - DISC_CENTER * self.unit * math.cos(a))
        if o[3] is not None and o[3].key == (x, y, round(DISC_RADIUS * self.unit)):
            disc = o[3]
        else:
            disc = _disc(x, y, round(DISC_RADIUS * self.unit), RED)
        return [hour, minute, stem, disc]

    def draw_dial(self):
        """Paint the empty dial: white, with the 60 black bars. The hands
        are not on the glass afterward -- the next show() draws them all."""
        display = self.display
        display.fill(WHITE)
        for bar in self.bars:
            top, lows, highs = _scan(bar)
            for k in range(len(lows)):
                display.hline(lows[k], top + k, highs[k] - lows[k] + 1, BLACK)
        self.layers = None

    def forget(self):
        """Something else painted over the face: the next show() redraws
        every hand from scratch. (Call draw_dial() first.)"""
        self.layers = None

    def show(self, hour_deg, minute_deg, second_deg):
        """Move the hands to these angles, repainting only what changed."""
        new = self._build(hour_deg, minute_deg, second_deg, self.layers)

        if self.layers is None:
            # Nothing of ours is on the glass yet: draw bottom to top.
            for shape in new:
                for k in range(shape.rows):
                    if shape.lows[k] <= shape.highs[k]:
                        self.display.hline(shape.lows[k], shape.top + k,
                                           shape.highs[k] - shape.lows[k] + 1,
                                           shape.color)
            self.layers = new
            return

        # Which stretches of which rows differ between old and new?
        dirty = {}
        for before, after in zip(self.layers, new):
            if before is after:
                continue
            first = min(before.top, after.top)
            last = max(before.top + before.rows, after.top + after.rows)
            for y in range(first, last):
                bl, bh = before.edges(y)
                al, ah = after.edges(y)
                if bl == al and bh == ah:
                    continue
                self._mark(dirty, y, min(bl, al), max(bh, ah))

        self.layers = new
        rows = sorted(dirty)
        i = 0
        while i < len(rows):
            # Gather rows into a band, and find the columns it needs.
            top = rows[i]
            low = 9999
            high = -9999
            j = i
            while j < len(rows) and rows[j] - top < BAND:
                for span in dirty[rows[j]]:
                    if span[0] < low:
                        low = span[0]
                    if span[1] > high:
                        high = span[1]
                j += 1
            self._repaint(top, rows[j - 1], low, high)
            i = j

    @staticmethod
    def _mark(dirty, y, low, high):
        """Add columns low..high of row y to the stretches to repaint,
        joining any stretch it touches (or nearly touches: starting a new
        drawing command costs more than a few extra pixels)."""
        spans = dirty.get(y)
        if spans is None:
            dirty[y] = [[low, high]]
            return
        for span in spans:
            if low <= span[1] + 6 and high >= span[0] - 6:
                if low < span[0]:
                    span[0] = low
                if high > span[1]:
                    span[1] = high
                return
        spans.append([low, high])

    def _repaint(self, top, bottom, low, high):
        """Repaint columns low..high of rows top..bottom from the whole
        scene, with ONE drawing command: fill a scratch buffer with the
        right color for every pixel in the rectangle, then send it."""
        width = high - low + 1
        height = bottom - top + 1
        buf = self.band
        fills = self.fills
        for r in range(height):
            start = r * width * 2
            for x, length, color in self._runs(top + r, low, high):
                a = start + (x - low) * 2
                buf[a:a + length * 2] = fills[color][:length * 2]
        self.display.blit_buffer(memoryview(buf)[:width * height * 2],
                                 low, top, width, height)

    def _runs(self, y, low, high):
        """The stretches of one color on row y between columns low and
        high, left to right, as a list of (x, length, color)."""
        parts = []                  # (low, high, color), bottom layer first

        dy = y - CY
        reach = max(abs(low - CX), abs(high - CX))
        if dy * dy + reach * reach >= self.rim2:
            for i in range(60):
                if self.bar_tops[i] <= y < self.bar_bottoms[i]:
                    a, b = _quad_span(self.bars[i], y)
                    if a <= b and a <= high and b >= low:
                        parts.append((a, b, BLACK))

        for shape in self.layers:
            k = y - shape.top
            if 0 <= k < shape.rows:
                a = shape.lows[k]
                b = shape.highs[k]
                if a <= b and a <= high and b >= low:
                    parts.append((a, b, shape.color))

        if not parts:
            return [(low, high + 1 - low, WHITE)]

        if len(parts) == 1:                  # the common case: one thing
            a, b, color = parts[0]
            a = max(a, low)
            b = min(b, high)
            runs = []
            if a > low:
                runs.append((low, a - low, WHITE))
            runs.append((a, b + 1 - a, color))
            if b < high:
                runs.append((b + 1, high - b, WHITE))
            return runs

        # Cut the row wherever any part starts or stops, then give each
        # piece the color of the topmost part that covers it.
        cuts = {low, high + 1}
        for a, b, color in parts:
            cuts.add(max(a, low))
            cuts.add(min(b, high) + 1)
        edges = sorted(cuts)

        runs = []
        for i in range(len(edges) - 1):
            x = edges[i]
            color = WHITE
            for a, b, c in parts:
                if a <= x <= b:
                    color = c
            length = edges[i + 1] - x
            if runs and runs[-1][2] == color:
                runs[-1] = (runs[-1][0], runs[-1][1] + length, color)
            else:
                runs.append((x, length, color))
        return runs
