# mode_finger.py -- mode 5: the finger test.
#
# Press a fingertip on the sensor. Your finger is warmer than the room, so the
# sensor warms up and the thermometer on the screen fills up. When the
# sensor reaches FINGER_TARGET_F (in config.py) the thermometer is full and the
# screen cheers!
#
# When you switch to this mode it takes a few readings first, to find out
# how warm the room is. That is the "baseline". Keep your finger off the sensor
# until the screen says "Touch the sensor!".
#
# This mode reads the sensor faster than the others so the thermometer feels
# quick. Watch the blinking LED: it blinks faster in this mode, too.
import time
import config
import widgets
from display_ctx import Mode
import vga1_8x16 as SMALL_FONT
import vga1_bold_16x32 as BIG_FONT

CENTER_X = config.CENTER_X

COLUMN_X = 116
NOW_LABEL_Y = 56
NOW_VALUE_Y = 72
GOAL_LABEL_Y = 110
GOAL_VALUE_Y = 126
MESSAGE_Y = 156

MEASURING, READY, WARMING, ALMOST, DONE, COOLING = 0, 1, 2, 3, 4, 5

MESSAGES = (
    ("Reading", "the room"),
    ("Touch the", "sensor!"),
    ("Getting", "warmer..."),
    ("Almost", "there!"),
    ("HOT", "HANDS!"),
    ("Cooling", "off..."),
)


class FingerMode(Mode):
    NAME = "Finger"
    READ_MS = config.FINGER_READ_MS
    TITLE = "FINGER TEST"
    TITLE_Y = 30

    def __init__(self):
        self.thermometer = widgets.Thermometer(76, 50, 104, 27, 24, 3)

    def enter(self, ctx):
        d = ctx.display
        ctx.begin(True)
        self.draw_status(ctx, ctx.sensor_ok)

        self.thermometer.draw_outline(d, config.WHITE)
        self.thermometer.set_level(d, 0.0, config.GREY, config.GREY)
        self.thermometer.mark(d, 1.0, 12, config.WHITE)

        d.text(SMALL_FONT, "NOW", COLUMN_X, NOW_LABEL_Y, config.GREY, config.BLACK)
        d.text(SMALL_FONT, "GOAL", COLUMN_X, GOAL_LABEL_Y, config.GREY, config.BLACK)
        goal = "%.1f %s" % (ctx.in_unit(config.FINGER_TARGET_F), ctx.unit())
        d.text(SMALL_FONT, goal, COLUMN_X, GOAL_VALUE_Y, config.WHITE, config.BLACK)

        # Start over: find the room temperature again.
        self.samples = []
        self.baseline = None
        self.span = config.FINGER_MIN_SPAN_F
        self.level = 0.0
        self.state = None
        self.first_reading = ctx.sample_count      # ignore the reading we already had
        self.flash_on = False
        self.next_flash = 0
        self.show_state(ctx, MEASURING)

    # --- the words on the screen ----------------------------------------------
    def show_state(self, ctx, state):
        if state == self.state:
            return
        self.state = state
        self.draw_message(ctx, config.WHITE)

    def draw_message(self, ctx, color):
        first, second = MESSAGES[self.state]
        d = ctx.display
        d.text(SMALL_FONT, widgets.pad_center(first, 10), COLUMN_X, MESSAGE_Y,
               color, config.BLACK)
        d.text(SMALL_FONT, widgets.pad_center(second, 10), COLUMN_X, MESSAGE_Y + 18,
               color, config.BLACK)

    # --- the Mode jobs ---------------------------------------------------------
    def update(self, ctx):
        if ctx.sample_count == self.first_reading:
            return                       # nothing new since we came into this mode
        d = ctx.display
        temp_f = ctx.temp_f

        if self.baseline is None:
            # Still measuring the room. Add up the first few readings.
            self.samples.append(temp_f)
            if len(self.samples) >= config.FINGER_BASELINE_SAMPLES:
                self.baseline = sum(self.samples) / len(self.samples)
                self.show_state(ctx, READY)
            climb = 0.0
        else:
            # If the sensor reads colder than the baseline, the room is cooler
            # than we thought, so ease the baseline down. It never goes UP,
            # because a warm finger must not be mistaken for a warmer room.
            if temp_f < self.baseline:
                self.baseline = self.baseline + (temp_f - self.baseline) * config.FINGER_BASELINE_DECAY

            span = config.FINGER_TARGET_F - self.baseline
            if span < config.FINGER_MIN_SPAN_F:
                span = config.FINGER_MIN_SPAN_F
            climb = (temp_f - self.baseline) / span
            if climb < 0.0:
                climb = 0.0
            if climb > 1.0:
                climb = 1.0

            # Ease toward the target instead of jumping to it.
            before = self.level
            self.level = self.level + (climb - self.level) * config.FINGER_SMOOTHING
            falling = self.level < before - 0.004

            if self.level >= 0.97:
                self.show_state(ctx, DONE)
            elif self.level < 0.12:
                self.show_state(ctx, READY)
            elif falling:
                self.show_state(ctx, COOLING)
            elif self.level >= 0.8:
                self.show_state(ctx, ALMOST)
            else:
                self.show_state(ctx, WARMING)

        mood = ctx.mood()
        self.thermometer.set_level(d, self.level, mood, config.GREY)
        digits = "%4s" % ("%.1f" % ctx.in_unit(temp_f))
        d.text(BIG_FONT, digits, COLUMN_X, NOW_VALUE_Y, mood, config.BLACK)
        d.text(SMALL_FONT, ctx.unit(), COLUMN_X + 4 * BIG_FONT.WIDTH + 4,
               NOW_VALUE_Y + 16, mood, config.BLACK)
        ctx.refresh_rim()

    def tick(self, ctx, now):
        # While the goal is reached, the message flashes yellow and white.
        if self.state == DONE and time.ticks_diff(now, self.next_flash) >= 0:
            self.flash_on = not self.flash_on
            color = config.WHITE
            if self.flash_on:
                color = config.YELLOW
            self.draw_message(ctx, color)
            self.next_flash = time.ticks_add(now, 350)
