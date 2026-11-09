# Lab 20: Mode Main -- Six Programs in One Clock
# Labs 10 to 15 as six modes of one clock. HOLD K0 for one second to go
# to the next mode:
#
#   Stopwatch -> Analog Clock -> Railway Clock -> Forecast -> Calendar
#        ^                                                       |
#        +------------------ Time and Quote <--------------------+
#
# Each mode works just like its lab, with its own controls -- the knob,
# PUSH, and SHORT presses of K0 (under one second) all belong to the
# mode. A card with the mode's name shows while the next one loads. The
# clock starts in Analog Clock. Copy this file to the Pico as main.py
# and it is the whole clock.
#
# ONE BUTTON, TWO JOBS. K0 starts the stopwatch, toggles the analog
# clock's ticking, refreshes the forecast and picks a random quote -- and
# it also changes the mode. watchparts.Button.short_or_long() tells the
# two apart by how long the button is held:
#
#   let go before 1 second   SHORT -- handed to the mode, as a press
#   still held at 1 second   LONG  -- the next mode, right away, without
#                                     waiting for you to let go
#
# The catch: a short press can only be recognised once you LET GO -- until
# then it might still turn into a long one. So K0 in a mode acts on the
# release, not the push. (In the stopwatch that hardly matters: the start
# and the stop are both late by about the same amount, so the time
# between them is still right.)
#
# EACH MODE IS A MODULE, LOADED ONLY WHEN IT IS NEEDED, like lab 16. Six
# programs at once would fill a lot of RAM with code nobody is looking
# at, so only the mode on the screen is in memory. Changing mode:
#
#   1. asks the current mode to stop(), and keeps whatever it hands back
#   2. removes that mode -- and every module it brought in with it -- from
#      memory, and runs the garbage collector to free the space
#   3. imports the next mode fresh, and calls its start()
#
# THE THREE FUNCTIONS EVERY MODE HAS (the files are app_*.py):
#
#   start(display, k0, push, knob, saved)
#       Draw the whole screen. k0 has the same pressed() as a Button, but
#       only reports short presses. push is the knob's push switch, and
#       knob is the knob. saved is whatever stop() returned the last time,
#       or None.
#   update(now)
#       Called on every pass of the loop with time.ticks_ms(). Read the
#       controls, redraw only what changed.
#   stop()
#       Return a dict to keep until next time (or None). The stopwatch
#       keeps running this way, and the forecast keeps its weather.
#
# A mode owns the whole screen. The chime on the hour and the nightly
# time sync belong to this program, so they happen in every mode.

NAME = "20-mode-main.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import sys
import time

import config
import shapes
import sound
import wifi_time
from watchparts import Button, Knob, SHORT, LONG

# (module, name) for each mode, in the order K0 steps through them.
MODES = (
    ("app_stopwatch", "Stopwatch"),       # lab 10
    ("app_analog", "Analog Clock"),       # lab 11
    ("app_railway", "Railway Clock"),     # lab 12
    ("app_forecast", "Forecast"),         # lab 13
    ("app_calendar", "Calendar"),         # lab 14
    ("app_quote", "Time and Quote"),      # lab 15
)
START_MODE = 1           # Analog Clock

SYNC_WITH_WIFI = True    # set the clock over WiFi at power-up...
RESYNC_HOUR = 3          # ...and again at 3:00 AM every night

CHIME_ON_THE_HOUR = True # a chime at the top of every hour, in any mode
QUIET_HOURS = (22, 7)    # ...except from 10 PM until 7 AM
CARD_MS = 400            # show the mode's name at least this long

CARD_COLOR = config.CYAN
DIM = config.color565(120, 120, 120)
DOT_ON = config.WHITE
DOT_OFF = config.color565(70, 70, 70)
DOT_Y = 160
DOT_SPACING = 20
DOT_RADIUS = 5


class ShortPresses:
    """What a mode gets in place of the K0 Button: pressed() is True once
    for each SHORT press the main loop saw, and long presses never reach
    the mode at all."""

    def __init__(self):
        self.waiting = 0

    def add(self):
        self.waiting += 1

    def clear(self):
        self.waiting = 0

    def pressed(self, now=None, repeat=False):
        if self.waiting:
            self.waiting -= 1
            return True
        return False


def show_card(index):
    """The mode's name, which mode of how many, and a row of dots."""
    display.fill(config.BLACK)
    config.centered_text(display, config.BIG_FONT, MODES[index][1], 92,
                         CARD_COLOR)
    config.centered_text(display, config.SMALL_FONT,
                         "mode {} of {}".format(index + 1, len(MODES)),
                         130, DIM)
    x = config.CENTER_X - (len(MODES) - 1) * DOT_SPACING // 2
    for i in range(len(MODES)):
        shapes.circle(display, x + i * DOT_SPACING, DOT_Y, DOT_RADIUS,
                      DOT_ON if i == index else DOT_OFF, config.FILL)
    config.centered_text(display, config.SMALL_FONT,
                         "hold K0 for the next mode", 212, DIM)


def switch_to(index):
    """Stop and unload the current mode, then load and start mode `index`."""
    global mode, mode_index, loaded_before
    card_at = time.ticks_ms()
    if mode is not None:
        name = MODES[mode_index][0]
        kept = mode.stop()
        if kept is None:
            saved.pop(name, None)
        else:
            saved[name] = kept
        mode = None
        # Remove the mode, and every module it imported that was not here
        # before it, so their memory can be reused.
        for module_name in list(sys.modules):
            if module_name not in loaded_before:
                del sys.modules[module_name]
        gc.collect()

    show_card(index)
    mode_index = index
    name = MODES[index][0]
    loaded_before = set(sys.modules)
    mode = __import__(name)
    gc.collect()
    # Leave the card up long enough to read.
    wait = CARD_MS - time.ticks_diff(time.ticks_ms(), card_at)
    if wait > 0:
        time.sleep_ms(wait)
    # Throw away anything pressed or turned while the mode was loading.
    knob.turned()
    push_button.pressed()
    k0_short.clear()
    mode.start(display, k0_short, push_button, knob, saved.get(name))
    print("Mode:", MODES[index][1], "--", gc.mem_free() // 1024, "KB free")


def quiet(hour):
    """True during QUIET_HOURS, which may run past midnight."""
    start, end = QUIET_HOURS
    if start <= end:
        return start <= hour < end
    return hour >= start or hour < end


display = config.init_display()
a, b, push, k0 = config.init_controls()
k0_button = Button(k0)
k0_short = ShortPresses()
push_button = Button(push)
knob = Knob(a, b, config.ENCODER_STEPS_PER_CLICK)
sound.init()

display.fill(config.BLACK)
if SYNC_WITH_WIFI:
    config.centered_text(display, config.BIG_FONT, "Setting clock", 48,
                         config.CYAN)
    if wifi_time.sync_time(display):
        sound.play("start")
    else:
        time.sleep(3)    # keep going on whatever time the clock has

saved = {}               # module name -> what its stop() returned
mode = None
mode_index = 0
loaded_before = set()
gc.collect()
switch_to(START_MODE)
synced_day = time.localtime()[2]
chimed_hour = time.localtime()[3]

while True:
    now = time.ticks_ms()

    kind = k0_button.short_or_long(now)
    if kind == LONG:
        # Two rising notes: you held it long enough, let go.
        sound.tone(880, 40, wave=sound.SQUARE, level=0.25, attack=2,
                   release=8)
        sound.tone(1320, 60, wave=sound.SQUARE, level=0.25, attack=2,
                   release=8)
        switch_to((mode_index + 1) % len(MODES))
        continue
    if kind == SHORT:
        k0_short.add()

    mode.update(now)

    t = time.localtime()

    # The hourly chime.
    if t[3] != chimed_hour and t[4] == 0:
        chimed_hour = t[3]
        if CHIME_ON_THE_HOUR and not quiet(t[3]) and not sound.busy():
            sound.play("chime")

    # Once a day, set the clock again. (The clock stands still while it
    # connects, then catches up.)
    if SYNC_WITH_WIFI and t[3] == RESYNC_HOUR and t[2] != synced_day:
        wifi_time.sync_time()
        synced_day = t[2]

    time.sleep_ms(5)
