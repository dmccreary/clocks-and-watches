# widgets.py -- colors, icons and gauges shared by the display modes.
#
# Everything here is built from the drawing tools in shapes.py and the
# display driver: filled rectangles, filled circles and filled polygons.
# There are no picture files. The water drop, for example, is just a circle
# with a triangle on top.
import math
from array import array
import shapes

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------
# The screen wants RGB565 colors: 5 bits of red, 6 of green, 5 of blue, packed
# into one number. We do our color math with normal (red, green, blue) numbers
# from 0 to 255, and pack them at the very end.


def color565(red, green, blue):
    return ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)


def split565(color):
    """Undo color565: give back (red, green, blue), each 0 to 255."""
    red = ((color >> 11) & 0x1F) * 255 // 31
    green = ((color >> 5) & 0x3F) * 255 // 63
    blue = (color & 0x1F) * 255 // 31
    return red, green, blue


def dim(color, amount_percent):
    """Make a color darker. 100 keeps it, 50 is half as bright, 0 is black."""
    red, green, blue = split565(color)
    return color565(red * amount_percent // 100,
                    green * amount_percent // 100,
                    blue * amount_percent // 100)


def gradient(stops, position):
    """Slide along a list of (red, green, blue) colors.

    position 0.0 gives the first color and 1.0 gives the last. Anything in
    between is a smooth mix of the two colors on either side. This is how a
    handful of colors becomes a whole rainbow."""
    if position <= 0.0:
        stop = stops[0]
        return color565(stop[0], stop[1], stop[2])
    if position >= 1.0:
        stop = stops[-1]
        return color565(stop[0], stop[1], stop[2])

    gaps = len(stops) - 1
    scaled = position * gaps
    index = int(scaled)
    if index >= gaps:
        index = gaps - 1
    blend = scaled - index

    start = stops[index]
    end = stops[index + 1]
    return color565(int(start[0] + (end[0] - start[0]) * blend),
                    int(start[1] + (end[1] - start[1]) * blend),
                    int(start[2] + (end[2] - start[2]) * blend))


# Blue when cold, then cyan, green, orange, and red when hot.
MOOD_STOPS = ((30, 70, 255), (0, 200, 255), (0, 230, 90), (255, 170, 0), (255, 30, 30))

# Dry air is orange. Comfy air is green. Damp air is blue.
HUMIDITY_STOPS = ((255, 140, 0), (230, 230, 60), (0, 220, 120), (0, 170, 255), (60, 60, 255))


def mood_color(temp_f, cold_f, hot_f):
    """The mood-ring color for a temperature."""
    return gradient(MOOD_STOPS, (temp_f - cold_f) / (hot_f - cold_f))


def humidity_color(percent):
    return gradient(HUMIDITY_STOPS, percent / 100.0)


def text_color_on(background, dark, light):
    """Pick black-ish or white-ish text, whichever is easier to read on a color."""
    red, green, blue = split565(background)
    brightness = (red * 30 + green * 59 + blue * 11) // 100
    if brightness > 120:
        return dark
    return light


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------
def pad_center(text, width):
    """Pad text with spaces on both sides so it is exactly `width` letters."""
    extra = width - len(text)
    if extra <= 0:
        return text
    left = extra // 2
    return " " * left + text + " " * (extra - left)


def draw_centered(display, font, text, center_x, y, color, background):
    x = center_x - (len(text) * font.WIDTH) // 2
    display.text(font, text, x, y, color, background)


# ---------------------------------------------------------------------------
# Icons
# ---------------------------------------------------------------------------
def draw_droplet(display, center_x, center_y, radius, color):
    """A water drop: a circle for the round bottom and a triangle for the tip.

    (center_x, center_y) is the middle of the round part. The tip is two
    radii above it. The triangle's base sits half a radius above the center,
    where its sides just touch the circle."""
    shapes.circle(display, center_x, center_y, radius, color, 1)
    tip_y = center_y - radius * 2
    side = radius * 87 // 100
    base_y = center_y - radius // 2
    shapes.triangle(display, center_x, tip_y,
                    center_x - side, base_y, center_x + side, base_y, color, 1)


class Thermometer:
    """A thermometer drawn from a rectangle and two circles.

    The tube is a rectangle with a round top. The bulb at the bottom is a
    circle. We draw it in two steps: draw_outline() paints the glass once,
    and set_level() paints what is inside, as often as we like.

    tube_w must be an odd number so the round top matches the tube."""

    def __init__(self, center_x, top, tube_h, tube_w, bulb_r, wall):
        self.cx = center_x
        self.top = top
        self.tube_h = tube_h
        self.tube_w = tube_w
        self.bulb_r = bulb_r
        self.wall = wall
        self.half = tube_w // 2                       # also the radius of the round top
        self.cap_y = top + self.half                  # center of the round top
        self.bulb_y = top + tube_h + bulb_r - 2       # center of the bulb
        self.inner_half = self.half - wall
        self.stem_top = self.cap_y                    # where the straight part starts
        self.stem_bottom = top + tube_h + 3           # a few dots into the bulb

    def draw_outline(self, display, color):
        display.fill_rect(self.cx - self.half, self.cap_y,
                          self.tube_w, self.top + self.tube_h - self.cap_y, color)
        shapes.circle(display, self.cx, self.cap_y, self.half, color, 1)
        shapes.circle(display, self.cx, self.bulb_y, self.bulb_r, color, 1)

    def set_level(self, display, fraction, liquid_color, empty_color):
        """Fill the thermometer. fraction is 0.0 (empty) to 1.0 (full)."""
        if fraction < 0.0:
            fraction = 0.0
        if fraction > 1.0:
            fraction = 1.0
        x = self.cx - self.inner_half
        width = self.inner_half * 2 + 1

        top_color = empty_color
        if fraction >= 1.0:
            top_color = liquid_color
        shapes.circle(display, self.cx, self.cap_y, self.inner_half, top_color, 1)

        total = self.stem_bottom - self.stem_top
        liquid = int(total * fraction)
        empty = total - liquid
        if empty > 0:
            display.fill_rect(x, self.stem_top, width, empty, empty_color)
        if liquid > 0:
            display.fill_rect(x, self.stem_top + empty, width, liquid, liquid_color)

        shapes.circle(display, self.cx, self.bulb_y, self.bulb_r - self.wall,
                      liquid_color, 1)

    def mark(self, display, fraction, length, color):
        """Draw a little tick mark beside the tube at a level (for a goal line)."""
        total = self.stem_bottom - self.stem_top
        y = self.stem_top + total - int(total * fraction)
        display.hline(self.cx + self.half + 2, y, length, color)


# ---------------------------------------------------------------------------
# Segmented arc gauge
# ---------------------------------------------------------------------------
class ArcGauge:
    """A curved gauge made of little blocks, like the rings on a smartwatch.

    Each block is a four-sided polygon. Angles are measured clockwise from
    12 o'clock. A lit block glows in its own color from the gradient; an
    unlit block is a dim version of the same color. When the value changes we
    only repaint the blocks that changed, which keeps the screen quick."""

    def __init__(self, center_x, center_y, r_in, r_out, segments,
                 start_deg, sweep_deg, gap_deg, stops):
        self.segments = segments
        self.polygons = []
        self.lit_colors = []
        self.dim_colors = []
        self.state = [None] * segments      # None = never drawn
        step = sweep_deg / segments
        for i in range(segments):
            a0 = math.radians(start_deg + i * step + gap_deg / 2)
            a1 = math.radians(start_deg + (i + 1) * step - gap_deg / 2)
            self.polygons.append(array('h', [
                self._x(center_x, r_in, a0), self._y(center_y, r_in, a0),
                self._x(center_x, r_out, a0), self._y(center_y, r_out, a0),
                self._x(center_x, r_out, a1), self._y(center_y, r_out, a1),
                self._x(center_x, r_in, a1), self._y(center_y, r_in, a1)]))
            color = gradient(stops, i / (segments - 1))
            self.lit_colors.append(color)
            self.dim_colors.append(dim(color, 18))

    @staticmethod
    def _x(center, radius, angle):
        return int(center + radius * math.sin(angle) + 0.5)

    @staticmethod
    def _y(center, radius, angle):
        return int(center - radius * math.cos(angle) + 0.5)

    def forget(self):
        """Call this after the screen has been wiped, so every block is redrawn."""
        self.state = [None] * self.segments

    def set_level(self, display, lit_count):
        """Light the first lit_count blocks. Only blocks that changed are drawn."""
        if lit_count < 0:
            lit_count = 0
        if lit_count > self.segments:
            lit_count = self.segments
        for i in range(self.segments):
            lit = i < lit_count
            if self.state[i] is not lit:
                self.state[i] = lit
                if lit:
                    color = self.lit_colors[i]
                else:
                    color = self.dim_colors[i]
                shapes.poly(display, 0, 0, self.polygons[i], color, 1)
