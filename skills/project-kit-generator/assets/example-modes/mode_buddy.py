# mode_buddy.py -- mode 2: Buddy, a face that feels the air.
#
# Buddy's whole face is the mood-ring color for the temperature: blue when
# it is cold, green when it is comfy, red when it is hot. Buddy's mouth and
# sweat drops change too, and Buddy blinks every few seconds.
#
# The face is only drawn from scratch when the mood changes. The rest of the
# time we just write the numbers and the words, so the screen stays calm.
import time
import config
import shapes
import widgets
from display_ctx import Mode
import vga1_8x16 as SMALL_FONT

CENTER_X = config.CENTER_X
CENTER_Y = config.CENTER_Y

FACE_R = 94
EYE_Y = 108
EYE_XS = (CENTER_X - 34, CENTER_X + 34)
LENS_R = 28          # the black rim of Buddy's glasses
WHITE_R = 23         # the white of the eye
PUPIL_R = 8
NUMBERS_Y = 38
CAPTION_Y = 178

SWEAT = widgets.color565(140, 210, 255)

FREEZING, COOL, COMFY, WARM, HOT = 0, 1, 2, 3, 4


def band_for(temp_f):
    if temp_f < config.BUDDY_COLD_F:
        return FREEZING
    if temp_f < config.TEMP_COOL_F:
        return COOL
    if temp_f < config.TEMP_WARM_F:
        return COMFY
    if temp_f < config.TEMP_HOT_F:
        return WARM
    return HOT


def caption_for(band, humidity):
    if band == FREEZING:
        return "Brrr, cold!"
    if band == HOT:
        return "Whew, hot!"
    if humidity < 30:
        return "Thirsty!"
    if humidity > 70:
        return "Sticky!"
    if band == COOL:
        return "A bit cool"
    if band == COMFY:
        return "Ahh, nice!"
    return "Getting warm"


class BuddyMode(Mode):
    NAME = "Buddy"
    TITLE = ""
    TITLE_Y = NUMBERS_Y

    def enter(self, ctx):
        ctx.begin(True)
        self.band = None            # None means "the face is not drawn yet"
        self.face_color = None
        self.caption = None
        self.eyes_open = True
        self.reopen_at = 0
        self.next_blink = time.ticks_add(time.ticks_ms(), config.BUDDY_BLINK_MS)
        self.draw_status(ctx, ctx.sensor_ok)

    def title_background(self, ctx):
        if self.face_color is None:
            return config.BLACK
        return self.face_color

    # --- drawing pieces ---------------------------------------------------
    def draw_eyes_open(self, d):
        for i in range(2):
            cx = EYE_XS[i]
            shapes.circle(d, cx, EYE_Y, WHITE_R, config.WHITE, 1)
            # The pupils look a little toward each other.
            look = 3
            if i == 1:
                look = -3
            shapes.circle(d, cx + look, EYE_Y + 2, PUPIL_R, config.BLACK, 1)

    def draw_eyes_closed(self, d):
        for cx in EYE_XS:
            shapes.circle(d, cx, EYE_Y, WHITE_R, self.face_color, 1)
            d.fill_rect(cx - WHITE_R + 2, EYE_Y - 1, WHITE_R * 2 - 3, 3, config.BLACK)

    def draw_mouth(self, d, band):
        black = config.BLACK
        if band == FREEZING:
            # A shivering mouth: little blocks going up and down.
            for k in range(8):
                y = 152
                if k % 2:
                    y = 157
                d.fill_rect(CENTER_X - 32 + k * 8, y, 8, 4, black)
        elif band == COOL:
            for k in range(3):
                shapes.ellipse(d, CENTER_X, 150, 24, 9 - k, black, 0, shapes.BOTTOM_HALF)
        elif band == COMFY:
            for k in range(4):
                shapes.ellipse(d, CENTER_X, 138, 36, 27 - k, black, 0, shapes.BOTTOM_HALF)
        elif band == WARM:
            d.fill_rect(CENTER_X - 32, 156, 64, 5, black)
        else:
            shapes.ellipse(d, CENTER_X, 152, 28, 17, black, 1)
            shapes.ellipse(d, CENTER_X, 158, 14, 10, config.RED, 1, shapes.BOTTOM_HALF)

    def draw_face(self, ctx, color, band):
        d = ctx.display
        self.face_color = color
        shapes.circle(d, CENTER_X, CENTER_Y, FACE_R, color, 1)
        for cx in EYE_XS:
            shapes.circle(d, cx, EYE_Y, LENS_R, config.BLACK, 1)          # glasses
        d.fill_rect(CENTER_X - 8, EYE_Y - 2, 16, 4, config.BLACK)          # bridge
        self.draw_eyes_open(d)
        self.eyes_open = True
        self.draw_mouth(d, band)
        # Sweat drops at Buddy's temples, made with the same water drop that
        # marks humidity in the other modes.
        if band >= WARM:
            widgets.draw_droplet(d, 46, 98, 6, SWEAT)
        if band == HOT:
            widgets.draw_droplet(d, 194, 98, 6, SWEAT)

    def draw_words(self, ctx, band):
        d = ctx.display
        color = widgets.text_color_on(self.face_color, config.BLACK, config.WHITE)
        numbers = "%.1f%s %d%%" % (ctx.in_unit(ctx.temp_f), ctx.unit(),
                                   int(ctx.humidity + 0.5))
        d.text(SMALL_FONT, widgets.pad_center(numbers, 11),
               CENTER_X - (11 * SMALL_FONT.WIDTH) // 2, NUMBERS_Y,
               color, self.face_color)
        caption = caption_for(band, ctx.humidity)
        d.text(SMALL_FONT, widgets.pad_center(caption, 12),
               CENTER_X - (12 * SMALL_FONT.WIDTH) // 2, CAPTION_Y,
               color, self.face_color)

    # --- the Mode jobs ----------------------------------------------------
    def update(self, ctx):
        band = band_for(ctx.temp_f)
        color = ctx.mood()
        if band != self.band or color != self.face_color:
            self.draw_face(ctx, color, band)
            self.band = band
            ctx.refresh_rim()
        self.draw_words(ctx, band)

    def tick(self, ctx, now):
        if self.face_color is None:
            return                                   # the face is not drawn yet
        d = ctx.display
        if self.eyes_open:
            if time.ticks_diff(now, self.next_blink) >= 0:
                self.draw_eyes_closed(d)
                self.eyes_open = False
                self.reopen_at = time.ticks_add(now, 150)
        elif time.ticks_diff(now, self.reopen_at) >= 0:
            self.draw_eyes_open(d)
            self.eyes_open = True
            self.next_blink = time.ticks_add(now, config.BUDDY_BLINK_MS)
