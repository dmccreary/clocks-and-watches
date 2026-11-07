# mode_ring.py -- mode 4: ring gauges, like the rings on a smartwatch.
#
# The outer ring is the temperature. It fills from blue (cold) toward red
# (hot), and each block along the ring keeps its own color, so a full ring is
# a whole rainbow. The inner ring is the humidity: orange when the air is dry,
# green when it is comfy, and blue when it is damp.
#
# In the middle, a tiny thermometer and a water drop show the same two
# numbers. Both icons are drawn from circles, rectangles and triangles.
import config
import widgets
from display_ctx import Mode
import vga1_8x16 as SMALL_FONT
import vga1_bold_16x32 as BIG_FONT

CENTER_X = config.CENTER_X
CENTER_Y = config.CENTER_Y

SEGMENTS = 30
START_DEGREES = -150       # 7 o'clock, measured clockwise from 12 o'clock
SWEEP_DEGREES = 300        # the last 60 degrees at the bottom are left open

TEMP_ROW_Y = 72
HUMIDITY_ROW_Y = 124
NUMBER_X = 90


def fit4(value):
    """A number in exactly four letters, like ' 9.9' or '72.5' or ' 100'."""
    text = "%.1f" % value
    if len(text) > 4:
        text = "%.0f" % value
    return "%4s" % text


class RingMode(Mode):
    NAME = "Ring"
    TITLE = ""
    TITLE_Y = 106

    def __init__(self):
        # Two gauges, one inside the other, with a small gap between them.
        self.temp_gauge = widgets.ArcGauge(
            CENTER_X, CENTER_Y, 90, 102, SEGMENTS, START_DEGREES, SWEEP_DEGREES,
            1.6, widgets.MOOD_STOPS)
        self.humidity_gauge = widgets.ArcGauge(
            CENTER_X, CENTER_Y, 75, 87, SEGMENTS, START_DEGREES, SWEEP_DEGREES,
            1.6, widgets.HUMIDITY_STOPS)
        self.thermometer = widgets.Thermometer(79, 74, 18, 7, 5, 2)

    def enter(self, ctx):
        d = ctx.display
        ctx.begin(True)
        self.temp_gauge.forget()
        self.humidity_gauge.forget()
        self.thermometer.draw_outline(d, config.WHITE)
        self.draw_status(ctx, ctx.sensor_ok)

    def update(self, ctx):
        d = ctx.display
        temp_f = ctx.temp_f
        humidity = ctx.humidity

        # How full is each ring? A number from 0.0 to 1.0.
        temp_fraction = (temp_f - config.MOOD_COLD_F) / (config.MOOD_HOT_F - config.MOOD_COLD_F)
        if temp_fraction < 0.0:
            temp_fraction = 0.0
        if temp_fraction > 1.0:
            temp_fraction = 1.0

        self.temp_gauge.set_level(d, int(temp_fraction * SEGMENTS + 0.5))
        self.humidity_gauge.set_level(d, int(humidity / 100.0 * SEGMENTS + 0.5))

        # The temperature row: thermometer, number, unit.
        mood = ctx.mood()
        self.thermometer.set_level(d, temp_fraction, mood, config.GREY)
        d.text(BIG_FONT, fit4(ctx.in_unit(temp_f)), NUMBER_X, TEMP_ROW_Y, mood, config.BLACK)
        d.text(SMALL_FONT, ctx.unit(), NUMBER_X + 4 * BIG_FONT.WIDTH + 4,
               TEMP_ROW_Y + 16, mood, config.BLACK)

        # The humidity row: water drop and number.
        wet = widgets.humidity_color(humidity)
        widgets.draw_droplet(d, 82, HUMIDITY_ROW_Y + 22, 6, wet)
        d.text(BIG_FONT, "%3d%%" % int(humidity + 0.5), NUMBER_X + 2, HUMIDITY_ROW_Y,
               wet, config.BLACK)

        ctx.refresh_rim()
