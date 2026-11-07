# main-template.py: The Big Clock
# The largest clock the round screen can hold: four seven-segment digits
# built from plain rectangles, a ring of 60 second ticks around the rim,
# AM/PM above and the date below. The speaker chimes on the hour.
#
# Copy it to the Pico as main.py and the board starts as a clock:
#
#     mpremote cp main-template.py :main.py
#
# THE BUTTONS
#
#   UP / DOWN      volume up / down (hold to keep going). A beep plays at
#                  the new volume.
#   tap MODE       hourly chime on / off
#   hold MODE      set the clock from the internet again, right now
#
# HOW BIG CAN THE DIGITS BE?
# A round screen is widest at the middle and narrower above and below, so
# the row of digits is a rectangle that must fit INSIDE a circle. Its
# corners are the tightest spot. With the tick ring using the outer 16
# pixels, the corners have to stay within radius 150 of the center:
#
#     (row width / 2) ** 2 + (digit height / 2) ** 2  <  150 ** 2
#
# The 12-hour face's first digit is only ever 1 or blank, so it is drawn as
# a half digit (one column), and the other digits get the room it saves:
# 134 ** 2 + 65 ** 2 is about 149 ** 2. Just fits.
#
# THE TIME
# At power-up the clock joins WiFi (secrets.py), asks an NTP server for the
# time, then switches WiFi off. It does that again every night at 3:00 AM,
# because the Pico's own clock drifts a second or two a day.
#
# THE SOUND
# sound.py feeds the amplifier from the Pico's second core. It is started
# ONCE, before the face is built, and left running. The Pico W has about
# 190 KB of RAM for Python, and building the tick ring leaves it in lots of
# small pieces -- start the sound afterwards and the I2S driver cannot find
# one free 4 KB block (a MemoryError, found on the kit 2026-11-06). The
# sound only stops while WiFi syncs the clock, with a gc.collect() before
# it starts again.

NAME = "main-template.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import time

import config
import sfx          # sound.play() imports it -- compile it now, while RAM is tidy
import sound
import wifi_time
from watchparts import Button, Digit, TickRing, TextLine, DIGITS, BLANK
from watchparts import LONG, SHORT

# --- settings you can change ------------------------------------------------
TWELVE_HOUR = True
BLINK_COLON = True
CHIME_ON = True              # chime at the top of every hour
QUIET_START = 22             # no chime from 10 PM ...
QUIET_END = 7                # ... until 7 AM
RESYNC_HOUR = 3              # set the clock from the internet at 3:00 AM
VOLUME_STEP = 10

DIGIT_COLOR = config.WHITE
GHOST = config.color565(22, 22, 28)       # the faint unlit segments
ACCENT = config.CYAN
TICK_OFF = config.color565(40, 40, 40)
DATE_COLOR = config.YELLOW
NOTE_COLOR = config.GREEN

# (digit width, digit height, segment thickness). The height must be
# 3 * thickness plus an even number. The 24-hour face has a full first
# digit, so its digits are smaller to fit the same circle.
SIZE_12 = (64, 130, 16)
SIZE_24 = (56, 98, 14)
PAIR_GAP = 10                # between the two digits of a pair
COLON_GAP = 12               # either side of the colon

NOTE_MS = 2000               # how long a "volume 50" note replaces the date

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


# --- the speaker ---------------------------------------------------------------
class Speaker:
    """sound.py, started once and kept running. off() and start() are only
    for the few seconds WiFi is in use."""

    def __init__(self):
        self.running = False
        sound.volume(config.VOLUME)

    def start(self):
        if not self.running:
            gc.collect()                # one unbroken block for the I2S buffer
            sound.init(rate=16000, ibuf=4096)
            self.running = True

    def play(self, name):
        """A named effect from sfx.py, such as "chime"."""
        if self.running:
            sound.play(name)

    def beep(self, freq=880, ms=120):
        if self.running:
            sound.stop()
            sound.tone(freq, ms, release=40)

    def off(self):
        if self.running:
            sound.deinit()
            self.running = False


# --- the face ----------------------------------------------------------------
class BigFace:
    def __init__(self, display):
        self.display = display
        width, height, thick = SIZE_12 if TWELVE_HOUR else SIZE_24
        self.thick = thick
        first = thick if TWELVE_HOUR else width
        row = first + 3 * width + 2 * PAIR_GAP + 2 * COLON_GAP + thick
        x = (config.WIDTH - row) // 2
        top = config.CENTER_Y - height // 2

        # Digit 0 is the hours' tens. As a half digit, x is its left edge.
        self.digits = [Digit(display, x, top, width, height, thick,
                             DIGIT_COLOR, GHOST, half=TWELVE_HOUR)]
        x += first + PAIR_GAP
        self.digits.append(Digit(display, x, top, width, height, thick,
                                 DIGIT_COLOR, GHOST))
        x += width + COLON_GAP
        self.colon_x = x
        x += thick + COLON_GAP
        for _ in range(2):
            self.digits.append(Digit(display, x, top, width, height, thick,
                                     DIGIT_COLOR, GHOST))
            x += width + PAIR_GAP
        self.colon_y = (top + height // 3 - thick // 2,
                        top + 2 * height // 3 - thick // 2)

        gc.collect()
        self.ring = TickRing(display, config.CENTER_X, config.CENTER_Y,
                             config.SAFE_RADIUS - 2, config.SAFE_RADIUS - 10,
                             config.SAFE_RADIUS - 16)
        small = config.SMALL_FONT
        self.ampm = TextLine(display, small, config.CENTER_X, top - 34, 2,
                             ACCENT)
        self.date = TextLine(display, small, config.CENTER_X,
                             top + height + 18, 22, DATE_COLOR)
        self.note_until = None
        self.forget()

    def forget(self):
        """After display.fill(): repaint everything on the next show()."""
        for digit in self.digits:
            digit.forget()
        self.ring.forget()
        self.ampm.forget()
        self.date.forget()
        self.shown_colon = None

    def note(self, text, now):
        """Show a short message where the date goes, for NOTE_MS."""
        self.date.show(text, NOTE_COLOR)
        self.note_until = time.ticks_add(now, NOTE_MS)

    def show(self, t, now, synced):
        year, month, day, hour, minute, second, weekday = t[:7]

        shown_hour = (hour % 12 or 12) if TWELVE_HOUR else hour
        tens = shown_hour // 10
        first = DIGITS[tens] if (tens or not TWELVE_HOUR) else BLANK
        for digit, pattern in zip(self.digits,
                                  (first, DIGITS[shown_hour % 10],
                                   DIGITS[minute // 10],
                                   DIGITS[minute % 10])):
            digit.show(pattern)

        colon = (second % 2 == 0) if BLINK_COLON else True
        if colon != self.shown_colon:
            for y in self.colon_y:
                self.display.fill_rect(self.colon_x, y, self.thick,
                                       self.thick,
                                       DIGIT_COLOR if colon else GHOST)
            self.shown_colon = colon

        # Ticks 0 to `second` are lit. paint() skips ticks that already
        # have the right color, so normally only one is sent.
        for i in range(60):
            self.ring.paint(i, ACCENT if i <= second else TICK_OFF)

        if TWELVE_HOUR:
            self.ampm.show("AM" if hour < 12 else "PM")

        if self.note_until is not None:
            if time.ticks_diff(now, self.note_until) < 0:
                return
            self.note_until = None
        if synced:
            self.date.show("{}, {} {}, {}".format(
                DAYS[weekday], MONTHS[month - 1], day, year), DATE_COLOR)
        else:
            self.date.show("time not set", config.RED)


# --- start up ----------------------------------------------------------------
display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]
speaker = Speaker()


def sync(show_progress):
    """Set the clock over WiFi. Progress goes to the screen only at
    start-up; later syncs would scribble over the digits."""
    speaker.off()                       # WiFi first, sound after
    if show_progress:
        display.fill(config.BLACK)
        config.centered_text(display, config.BIG_FONT, "Big Clock", 130,
                             config.CYAN)
    ok = wifi_time.sync_time(display if show_progress else None)
    speaker.start()
    return ok


synced = sync(show_progress=True)       # also starts the speaker
if not synced and time.localtime()[0] >= 2025:
    synced = True                       # Thonny or mpremote set the clock
display.fill(config.BLACK)
face = BigFace(display)                 # AFTER the speaker -- see THE SOUND
gc.collect()
print("free RAM:", gc.mem_free())
speaker.play("start")

chime_on = CHIME_ON
last_second = None
last_hour = time.localtime()[3]
last_sync_day = time.localtime()[2]

try:
    while True:
        now = time.ticks_ms()

        press = mode_button.short_or_long(now)
        if press == SHORT:
            chime_on = not chime_on
            face.note("chime " + ("on" if chime_on else "off"), now)
            if chime_on:
                speaker.play("right")
        elif press == LONG:
            face.note("syncing ...", now)
            synced = sync(show_progress=False) or synced
            now = time.ticks_ms()
            face.note("synced" if synced else "sync failed", now)
            last_second = None

        change = 0
        if up_button.pressed(now, repeat=True):
            change = VOLUME_STEP
        elif down_button.pressed(now, repeat=True):
            change = -VOLUME_STEP
        if change:
            level = sound.volume(sound.volume() + change)
            face.note("volume {}".format(level), now)
            speaker.beep()
            last_second = None          # redraw so the note appears now

        t = time.localtime()
        if t[5] != last_second or face.note_until is not None:
            last_second = t[5]
            face.show(t, now, synced)

        hour, minute = t[3], t[4]
        if hour != last_hour:
            last_hour = hour
            quiet = (hour >= QUIET_START or hour < QUIET_END)
            if chime_on and minute == 0 and not quiet:
                speaker.play("chime")

        if (hour == RESYNC_HOUR and minute == 0 and t[2] != last_sync_day):
            last_sync_day = t[2]
            synced = sync(show_progress=False) or synced
            last_second = None

        time.sleep_ms(20)
finally:
    speaker.off()

# Try This
#   1. Set TWELVE_HOUR = False for a 24-hour clock. The digits shrink --
#      why? (Look at "HOW BIG CAN THE DIGITS BE?" at the top.)
#   2. Change GHOST to config.BLACK to hide the unlit segments.
#   3. Change "chime" to "doorbell" or "bird" (sfx.py has 21 sounds).
#   4. Make it chime the hour: play "chime", then one sound.tone(523, 300)
#      plus sound.rest(300) for every hour (hour % 12 or 12 of them).
