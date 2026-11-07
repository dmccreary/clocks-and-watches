# mode_hilo.py -- mode 6: the highest and lowest readings.
#
# The display remembers the hottest and coldest temperature it has felt, and
# the wettest and driest air too. It keeps track in EVERY mode, not just this
# one, and it saves the records in a file, so they survive unplugging.
#
# Try to set a new record! Touch the sensor to break the high, or hold it near
# a cold drink to break the low. To start over, hold the button for three
# seconds while you are in this mode.
import time
import config
import widgets
from display_ctx import Mode
import vga1_8x16 as SMALL_FONT
import vga1_bold_16x32 as BIG_FONT

CENTER_X = config.CENTER_X

HI_Y = 54
LO_Y = 94
DIVIDER_Y = 136
HUMIDITY_Y = 148
UPTIME_Y = 174
HINT_Y = 192

VALUE_X = 88
UNIT_X = VALUE_X + 5 * BIG_FONT.WIDTH + 4

HINT = "hold %ds: clear" % (config.CLEAR_PRESS_MS // 1000)


def value_text(temp_f, ctx):
    if temp_f is None:
        return " --.-"
    return "%5.1f" % ctx.in_unit(temp_f)


class HiLoMode(Mode):
    NAME = "Hi/Lo"
    TITLE = "RECORDS"
    TITLE_Y = 32

    def __init__(self):
        self.hi_icon = widgets.Thermometer(56, HI_Y, 18, 7, 5, 2)
        self.lo_icon = widgets.Thermometer(56, LO_Y, 18, 7, 5, 2)
        self.message_until = 0

    def enter(self, ctx):
        d = ctx.display
        ctx.begin(True)
        self.draw_status(ctx, ctx.sensor_ok)
        self.hi_icon.draw_outline(d, config.WHITE)
        self.lo_icon.draw_outline(d, config.WHITE)
        d.text(SMALL_FONT, "HI", 70, HI_Y + 8, config.WHITE, config.BLACK)
        d.text(SMALL_FONT, "LO", 70, LO_Y + 8, config.WHITE, config.BLACK)
        d.hline(CENTER_X - 70, DIVIDER_Y, 140, config.GREY)
        self.message_until = 0
        self.draw_hint(ctx, HINT, config.GREY)

    def draw_hint(self, ctx, text, color):
        widgets.draw_centered(ctx.display, SMALL_FONT, widgets.pad_center(text, 16),
                              CENTER_X, HINT_Y, color, config.BLACK)

    def cleared(self, ctx, now):
        """The app calls this right after the records are cleared."""
        self.message_until = time.ticks_add(now, 2000)
        self.draw_hint(ctx, "RECORDS CLEARED", config.YELLOW)

    def update(self, ctx):
        d = ctx.display
        records = ctx.records

        # Highest temperature
        hi_color = config.GREY
        if records.hi_f is not None:
            hi_color = widgets.mood_color(records.hi_f, config.MOOD_COLD_F, config.MOOD_HOT_F)
        self.hi_icon.set_level(d, 1.0, hi_color, config.GREY)
        d.text(BIG_FONT, value_text(records.hi_f, ctx), VALUE_X, HI_Y, hi_color, config.BLACK)
        d.text(SMALL_FONT, ctx.unit(), UNIT_X, HI_Y + 16, hi_color, config.BLACK)

        # Lowest temperature
        lo_color = config.GREY
        if records.lo_f is not None:
            lo_color = widgets.mood_color(records.lo_f, config.MOOD_COLD_F, config.MOOD_HOT_F)
        self.lo_icon.set_level(d, 0.2, lo_color, config.GREY)
        d.text(BIG_FONT, value_text(records.lo_f, ctx), VALUE_X, LO_Y, lo_color, config.BLACK)
        d.text(SMALL_FONT, ctx.unit(), UNIT_X, LO_Y + 16, lo_color, config.BLACK)

        # Humidity records, with the water drop icon
        widgets.draw_droplet(d, 62, HUMIDITY_Y + 14, 6, widgets.humidity_color(60))
        if records.hi_h is None:
            humidity = "HI --% LO --%"
        else:
            humidity = "HI%3d%% LO%3d%%" % (int(records.hi_h + 0.5), int(records.lo_h + 0.5))
        d.text(SMALL_FONT, widgets.pad_center(humidity, 14), 80, HUMIDITY_Y + 4,
               config.WHITE, config.BLACK)

        # How long the display has been running
        seconds = time.ticks_ms() // 1000
        uptime = "up %d:%02d:%02d" % (seconds // 3600, (seconds // 60) % 60, seconds % 60)
        widgets.draw_centered(d, SMALL_FONT, widgets.pad_center(uptime, 14),
                              CENTER_X, UPTIME_Y, config.GREY, config.BLACK)
        ctx.refresh_rim()

    def tick(self, ctx, now):
        if self.message_until and time.ticks_diff(now, self.message_until) >= 0:
            self.message_until = 0
            self.draw_hint(ctx, HINT, config.GREY)
