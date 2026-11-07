# mode_live.py -- mode 3: a live graph of the temperature.
#
# Every new reading adds one column to the graph, moving from left to right.
# When the graph reaches the right edge it starts over on the left, like the
# sweep of a heart monitor. A thin grey line (the cursor) marks where the
# newest reading goes next, and everything behind it is the recent past.
#
# The trace changes color with the temperature, using the mood-ring colors.
#
# Drawing one column takes only two or three drawing calls: erase the old
# column, then draw a short vertical line from the last reading's height to
# this one. (Drawing a slanted line would cost one call for every dot.)
import config
import widgets
from display_ctx import Mode
import vga1_8x16 as SMALL_FONT
import vga1_bold_16x32 as BIG_FONT

CENTER_X = config.CENTER_X

PLOT_W = config.LIVE_WIDTH
PLOT_H = 80
PLOT_X = CENTER_X - PLOT_W // 2
PLOT_Y = 92

VALUE_Y = 50
RANGE_Y = 176
SPAN_Y = 196

VALUE_LINE_WIDTH = 6 * BIG_FONT.WIDTH            # five digits and the unit letter
VALUE_X = CENTER_X - VALUE_LINE_WIDTH // 2 - BIG_FONT.WIDTH // 2

CURSOR = widgets.dim(config.WHITE, 40)


class LiveMode(Mode):
    NAME = "Live"
    TITLE = "LIVE GRAPH"
    TITLE_Y = 32

    def enter(self, ctx):
        d = ctx.display
        ctx.begin(True)
        self.draw_status(ctx, ctx.sensor_ok)
        d.rect(PLOT_X - 1, PLOT_Y - 1, PLOT_W + 2, PLOT_H + 2, config.GREY)

        seconds = PLOT_W * config.DISPLAY_SECONDS
        if seconds >= 120:
            span = "last %d min" % (seconds // 60)
        else:
            span = "last %d sec" % seconds
        widgets.draw_centered(d, SMALL_FONT, widgets.pad_center(span, 12),
                              CENTER_X, SPAN_Y, config.GREY, config.BLACK)

        self.lo = None                 # None means "start the graph from scratch"
        self.hi = None
        self.range_text = None

    # --- turning a temperature into a height on the screen -----------------
    def y_for(self, temp_f):
        fraction = (temp_f - self.lo) / (self.hi - self.lo)
        y = PLOT_Y + PLOT_H - 1 - int(fraction * (PLOT_H - 1))
        if y < PLOT_Y:
            y = PLOT_Y
        if y > PLOT_Y + PLOT_H - 1:
            y = PLOT_Y + PLOT_H - 1
        return y

    def wanted_range(self, ctx):
        """The lowest and highest temperature the graph should show right now."""
        count = min(ctx.sample_count, len(ctx.history))
        recent = ctx.history[:count]
        low = min(recent)
        high = max(recent)
        span = high - low + 2.0                     # one degree of room each side
        if span < config.LIVE_MIN_SPAN_F:
            span = config.LIVE_MIN_SPAN_F
        middle = (low + high) / 2.0
        return middle - span / 2.0, middle + span / 2.0

    # --- drawing the graph --------------------------------------------------
    def draw_sample(self, ctx, n, connect):
        """Draw reading number n as one column of the graph."""
        d = ctx.display
        column = n % PLOT_W
        x = PLOT_X + column
        temp_f = ctx.history[column]
        y = self.y_for(temp_f)
        y_before = y
        if connect and column > 0:
            y_before = self.y_for(ctx.history[column - 1])

        top = min(y, y_before)
        height = abs(y - y_before) + 2
        if top + height > PLOT_Y + PLOT_H:
            height = PLOT_Y + PLOT_H - top
        d.fill_rect(x, PLOT_Y, 1, PLOT_H, config.BLACK)
        d.fill_rect(x, top, 1, height,
                    widgets.mood_color(temp_f, config.MOOD_COLD_F, config.MOOD_HOT_F))

    def draw_cursor(self, ctx, n):
        """The thin line that shows where reading number n will go."""
        x = PLOT_X + n % PLOT_W
        ctx.display.fill_rect(x, PLOT_Y, 1, PLOT_H, CURSOR)

    def replot(self, ctx):
        """Wipe the graph and draw all the recent readings again."""
        d = ctx.display
        d.fill_rect(PLOT_X, PLOT_Y, PLOT_W, PLOT_H, config.BLACK)
        latest = ctx.sample_count - 1
        count = min(ctx.sample_count, len(ctx.history))
        first = latest - count + 1
        for n in range(first, latest + 1):
            self.draw_sample(ctx, n, n > first)
        self.draw_cursor(ctx, latest + 1)

    def draw_range(self, ctx):
        low = ctx.in_unit(self.lo)
        high = ctx.in_unit(self.hi)
        text = "%.1f - %.1f %s" % (low, high, ctx.unit())
        if text != self.range_text:
            self.range_text = text
            widgets.draw_centered(ctx.display, SMALL_FONT, widgets.pad_center(text, 15),
                                  CENTER_X, RANGE_Y, config.WHITE, config.BLACK)

    # --- the Mode jobs ------------------------------------------------------
    def update(self, ctx):
        d = ctx.display
        latest = ctx.sample_count - 1
        temp_f = ctx.temp_f

        low, high = self.wanted_range(ctx)
        outside = self.lo is None or temp_f < self.lo or temp_f > self.hi
        # Also zoom back in after a big spike has scrolled out of the graph.
        too_loose = self.lo is not None and (self.hi - self.lo) > 2.5 * (high - low)
        if outside or too_loose:
            self.lo = low
            self.hi = high
            self.replot(ctx)
        else:
            self.draw_sample(ctx, latest, True)
            self.draw_cursor(ctx, latest + 1)
        self.draw_range(ctx)

        color = ctx.mood()
        digits = "%5.1f" % ctx.in_unit(temp_f)
        d.text(BIG_FONT, digits + ctx.unit(), VALUE_X, VALUE_Y, color, config.BLACK)
        ctx.refresh_rim()
