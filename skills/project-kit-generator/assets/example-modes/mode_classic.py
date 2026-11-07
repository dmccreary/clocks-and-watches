# mode_classic.py -- mode 1: the classic face from lab 07. (SHT40 example: adapt the values, keep the pattern.)
#
# The temperature in big letters, the other unit underneath, the humidity
# with a bar, and a white ring around the edge. The big number changes color
# in four steps as the air gets warmer (the steps are in config.py).
import config
import shapes
import widgets
from display_ctx import Mode
import vga1_8x16 as SMALL_FONT
import vga1_bold_16x32 as BIG_FONT

CENTER_X = config.CENTER_X
CENTER_Y = config.CENTER_Y

TEMP_VALUE_Y = 56
TEMP_C_Y = 92
DIVIDER_Y = 118
HUMIDITY_LABEL_Y = 128
HUMIDITY_VALUE_Y = 148
BAR_Y = 194
BAR_WIDTH = 120
BAR_HEIGHT = 10
BAR_X = CENTER_X - BAR_WIDTH // 2

# Same layout tricks as lab 07: every number has a fixed width, and the whole
# line slides half a slot left so the part you can SEE is centered.
TEMP_DIGITS = 5
TEMP_LINE_WIDTH = (TEMP_DIGITS + 2) * BIG_FONT.WIDTH
TEMP_X = CENTER_X - TEMP_LINE_WIDTH // 2 - BIG_FONT.WIDTH // 2
HUMIDITY_LINE_WIDTH = 6 * BIG_FONT.WIDTH
HUMIDITY_X = CENTER_X - HUMIDITY_LINE_WIDTH // 2 - BIG_FONT.WIDTH // 2
OTHER_UNIT_X = CENTER_X - (7 * SMALL_FONT.WIDTH) // 2 - SMALL_FONT.WIDTH // 2


def temperature_color(temperature_f):
    """Cyan, green, orange or red, depending on how warm it is."""
    if temperature_f < config.TEMP_COOL_F:
        return config.CYAN
    if temperature_f < config.TEMP_WARM_F:
        return config.GREEN
    if temperature_f < config.TEMP_HOT_F:
        return config.ORANGE
    return config.RED


class ClassicMode(Mode):
    NAME = "Classic"
    TITLE = "TEMPERATURE"
    TITLE_Y = 36

    def enter(self, ctx):
        d = ctx.display
        ctx.begin(False)
        shapes.ring(d, CENTER_X, CENTER_Y, config.SAFE_RADIUS, config.WHITE, 2)
        self.draw_status(ctx, ctx.sensor_ok)
        d.hline(CENTER_X - 70, DIVIDER_Y, 140, config.GREY)
        label = "HUMIDITY"
        d.text(SMALL_FONT, label, CENTER_X - (len(label) * SMALL_FONT.WIDTH) // 2,
               HUMIDITY_LABEL_Y, config.WHITE, config.BLACK)
        d.rect(BAR_X - 2, BAR_Y - 2, BAR_WIDTH + 4, BAR_HEIGHT + 4, config.WHITE)

    def update(self, ctx):
        d = ctx.display
        color = temperature_color(ctx.temp_f)

        digits = "%5.1f" % ctx.in_unit(ctx.temp_f)
        d.text(BIG_FONT, digits, TEMP_X, TEMP_VALUE_Y, color, config.BLACK)
        degree_x = TEMP_X + TEMP_DIGITS * BIG_FONT.WIDTH + BIG_FONT.WIDTH // 2
        shapes.ring(d, degree_x, TEMP_VALUE_Y + 7, 4, color, 2)
        d.text(BIG_FONT, ctx.unit(),
               TEMP_X + (TEMP_DIGITS + 1) * BIG_FONT.WIDTH, TEMP_VALUE_Y,
               color, config.BLACK)

        other = "%5.1f %s" % (ctx.in_other_unit(ctx.temp_f), ctx.other_unit())
        d.text(SMALL_FONT, other, OTHER_UNIT_X, TEMP_C_Y, config.WHITE, config.BLACK)

        text = "%5.1f%%" % ctx.humidity
        d.text(BIG_FONT, text, HUMIDITY_X, HUMIDITY_VALUE_Y, config.CYAN, config.BLACK)

        filled = int(BAR_WIDTH * ctx.humidity / 100.0)
        if filled > 0:
            d.fill_rect(BAR_X, BAR_Y, filled, BAR_HEIGHT, config.CYAN)
        if filled < BAR_WIDTH:
            d.fill_rect(BAR_X + filled, BAR_Y, BAR_WIDTH - filled, BAR_HEIGHT,
                        config.GREY)
