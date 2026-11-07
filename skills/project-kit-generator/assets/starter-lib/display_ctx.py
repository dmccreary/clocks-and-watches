# display_ctx.py -- what every display mode shares. (Copy this to lib/ in the new kit.)
#
# "ctx" is short for context. It holds the display, the latest reading, the
# unit (F or C) and the recent history. Each mode gets the same ctx, so a mode
# never has to ask for the display or the sensor by itself.
#
# This file also holds Mode, the pattern every mode follows. A mode has three
# jobs:
#
#   enter(ctx)        Wipe the screen and draw the parts that never change.
#   update(ctx)       Draw the numbers. Called after every new reading.
#   tick(ctx, now)    Optional. Called all the time, for small animations.
import math
import config
import widgets
import vga1_8x16 as SMALL_FONT


def _rim_points():
    """Sixty dots around the edge of the screen, like the marks on a watch bezel."""
    points = []
    for k in range(60):
        angle = math.radians(k * 6)
        size = 3
        if k % 5 == 0:
            size = 5                        # a bigger dot at every "hour"
        x = int(config.CENTER_X + 110 * math.sin(angle) + 0.5) - size // 2
        y = int(config.CENTER_Y - 110 * math.cos(angle) + 0.5) - size // 2
        points.append((x, y, size))
    return points


RIM_POINTS = _rim_points()


class Context:
    def __init__(self, display, records, mode_count):
        self.display = display
        self.records = records
        self.mode_count = mode_count
        self.mode_index = 0
        self.use_fahrenheit = True
        self.sensor_ok = True
        self.temp_c = None
        self.temp_f = None
        self.humidity = None
        self.rim_color = None
        # One temperature (in F) for every reading, oldest overwritten first.
        # The Live graph draws from this, so it can show the past.
        self.history = [0.0] * config.LIVE_WIDTH
        self.sample_count = 0

    # --- readings -------------------------------------------------------
    def add_reading(self, temp_c, humidity):
        self.temp_c = temp_c
        self.temp_f = temp_c * 9.0 / 5.0 + 32.0
        self.humidity = humidity
        self.history[self.sample_count % len(self.history)] = self.temp_f
        self.sample_count += 1

    def have_reading(self):
        return self.temp_f is not None

    # --- units ----------------------------------------------------------
    def unit(self):
        if self.use_fahrenheit:
            return "F"
        return "C"

    def other_unit(self):
        if self.use_fahrenheit:
            return "C"
        return "F"

    def in_unit(self, temp_f):
        """A temperature in F, changed to whichever unit is showing."""
        if self.use_fahrenheit:
            return temp_f
        return (temp_f - 32.0) * 5.0 / 9.0

    def in_other_unit(self, temp_f):
        if self.use_fahrenheit:
            return (temp_f - 32.0) * 5.0 / 9.0
        return temp_f

    # --- colors ---------------------------------------------------------
    def mood(self, temp_f=None):
        """The mood-ring color. It is rounded to whole degrees, so the color
        only changes when the temperature moves a full degree."""
        if temp_f is None:
            temp_f = self.temp_f
        if temp_f is None:
            return config.GREY
        return widgets.mood_color(int(temp_f + 0.5), config.MOOD_COLD_F, config.MOOD_HOT_F)

    # --- shared screen parts ---------------------------------------------
    def begin(self, rim):
        """Start a new screen: wipe it, and draw the page dots and the rim."""
        self.display.fill(config.BLACK)
        self.draw_page_dots()
        self.rim_color = None
        if rim:
            self.draw_rim(self.mood())

    def draw_page_dots(self):
        """One dot for each mode. The bright one is the mode you are in."""
        start = config.CENTER_X - (self.mode_count - 1) * 6
        for i in range(self.mode_count):
            color = config.GREY
            if i == self.mode_index:
                color = config.WHITE
            self.display.fill_rect(start + i * 12 - 2, 216, 5, 5, color)

    def draw_rim(self, color):
        for x, y, size in RIM_POINTS:
            self.display.fill_rect(x, y, size, size, color)
        self.rim_color = color

    def refresh_rim(self):
        """Repaint the rim, but only if the mood color has changed."""
        color = self.mood()
        if color != self.rim_color:
            self.draw_rim(color)


class Mode:
    """The pattern every display mode follows."""
    NAME = "Mode"
    READ_MS = config.DISPLAY_SECONDS * 1000   # how often this mode wants a reading

    # The line of small text near the top. When the sensor stops answering it
    # turns into a red SENSOR FAIL, and it goes back when the sensor returns.
    TITLE = ""
    TITLE_Y = 36
    TITLE_COLOR = config.WHITE

    def enter(self, ctx):
        pass

    def update(self, ctx):
        pass

    def tick(self, ctx, now):
        pass

    def title_background(self, ctx):
        return config.BLACK

    def draw_status(self, ctx, ok):
        if ok:
            text = self.TITLE
            color = self.TITLE_COLOR
            background = self.title_background(ctx)
        else:
            text = "SENSOR FAIL"
            color = config.RED
            background = config.BLACK
        widgets.draw_centered(ctx.display, SMALL_FONT, widgets.pad_center(text, 11),
                              config.CENTER_X, self.TITLE_Y, color, background)
