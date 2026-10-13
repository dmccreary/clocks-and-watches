# Lab 17: Main Template -- One Clock, Five Modes
# Turn the knob to step through five modes, one click at a time:
#
#   Weather <-> Analog <-> Digital <-> Stopwatch <-> Timer <-> (Weather)
#
# Clockwise goes forward through the list, counter-clockwise goes back. A
# row of five dots at the bottom of the screen shows which mode you are
# in. The clock starts in Weather. Copy this file to the Pico as main.py
# and it is the whole clock.
#
# EACH MODE IS A MODULE, LOADED ONLY WHEN IT IS NEEDED. Five clock faces
# at once would fill a lot of RAM with code and drawings nobody is looking
# at. So only the mode on the screen is in memory. Turning the knob:
#
#   1. asks the current mode to stop(), and keeps whatever it hands back
#   2. removes that mode -- and every module it brought in with it -- from
#      memory, and runs the garbage collector to free the space
#   3. imports the next mode fresh, and calls its start()
#
# THE FOUR FUNCTIONS EVERY MODE HAS. That is all this program knows about
# a mode, so adding a sixth one means writing one more module like these:
#
#   start(display, k0, push, saved)
#       Draw the whole screen. k0 and push are the K0 button and the
#       knob's push switch. saved is whatever stop() returned the last
#       time, or None.
#   update(now)
#       Called on every pass of the loop, about every 10 ms, with
#       time.ticks_ms(). Read the buttons, redraw only what changed.
#   on_knob(clicks)                                        (optional)
#       The knob was turned: clicks is how far, positive for clockwise.
#       Return True if the mode used the turn itself; a turn it does not
#       use switches to the next or the previous mode.
#   stop()
#       Turn off anything that is on, and return a dict to keep until
#       next time (or None). A dict with a "wake_at" time -- a
#       time.ticks_ms() value -- asks for this mode to be shown again at
#       that moment, which is how a timer's alarm interrupts the weather.
#
# And two rules: a mode must stay out of the strip where the dots go --
# the bottom 8 rows of the screen, so a mode has rows 0 to 119 -- and it
# must not clear the screen except in start().
#
# The knob belongs to this program, not to the modes: a turn changes the
# mode unless the mode on the screen says it used the turn itself. The
# timer does that while you are setting it, so turning the knob changes
# the minutes instead of throwing you into another mode. K0 and the
# knob's push switch always belong to the mode.

NAME = "17-main-template.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import sys
import time

import config
import shapes
import wifi_time
from watchparts import Button, Knob

# (module, name) for each mode, in the order the knob steps through them.
MODES = (
    ("mode_weather", "Weather"),
    ("mode_analog", "Analog"),
    ("mode_digital", "Digital"),
    ("mode_stopwatch", "Stopwatch"),
    ("mode_timer", "Timer"),
)
START_MODE = 0           # Weather

SYNC_WITH_WIFI = True    # set the clock over WiFi at power-up...
RESYNC_HOUR = 3          # ...and again at 3:00 AM every night

MODE_ROWS = 120          # a mode draws in rows 0 to 119; the dots go below
DOT_Y = 124
DOT_SPACING = 10
DOT_RADIUS = 2
DOT_ON = config.WHITE
DOT_OFF = config.color565(70, 70, 70)


def draw_dots(current):
    """One dot per mode across the bottom, centered; the current mode's
    is bright."""
    display.fill_rect(0, MODE_ROWS, config.WIDTH, config.HEIGHT - MODE_ROWS,
                      config.BLACK)
    x = config.CENTER_X - (len(MODES) - 1) * DOT_SPACING // 2
    for i in range(len(MODES)):
        shapes.circle(display, x + i * DOT_SPACING, DOT_Y, DOT_RADIUS,
                      DOT_ON if i == current else DOT_OFF, config.FILL)


def switch_to(index):
    """Stop and unload the current mode, then load and start mode `index`."""
    global mode, mode_index, loaded_before
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

    mode_index = index
    name = MODES[index][0]
    loaded_before = set(sys.modules)
    mode = __import__(name)
    mode.start(display, k0_button, push_button, saved.get(name))
    draw_dots(index)
    gc.collect()
    # Loading a mode takes a moment. Throw away any clicks that came in
    # while it did, so one flick of the knob moves one mode. Do the same
    # for the buttons: a press made in the last mode, which may never
    # have looked at them, must not start this one's stopwatch.
    knob.turned()
    k0_button.pressed()
    push_button.pressed()
    print("Mode:", MODES[index][1], "--", gc.mem_free() // 1024, "KB free")


display = config.init_display()
a, b, push, k0 = config.init_controls()
k0_button = Button(k0)
push_button = Button(push)
knob = Knob(a, b, config.ENCODER_STEPS_PER_CLICK)

display.fill(config.BLACK)
if SYNC_WITH_WIFI:
    config.centered_text(display, config.SMALL_FONT, "Setting clock", 24)
    if not wifi_time.sync_time(display):
        time.sleep(3)    # keep going on whatever time the RTC has
    display.fill(config.BLACK)

saved = {}               # module name -> what its stop() returned
mode = None
mode_index = 0
loaded_before = set()
gc.collect()
switch_to(START_MODE)
synced_day = time.localtime()[2]

while True:
    now = time.ticks_ms()

    clicks = knob.turned()
    if clicks:
        on_knob = getattr(mode, "on_knob", None)
        used = on_knob is not None and on_knob(clicks)
        if not used:
            step = 1 if clicks > 0 else -1
            switch_to((mode_index + step) % len(MODES))

    mode.update(now)

    # A mode that is not showing can ask to be shown at a set time.
    for i in range(len(MODES)):
        kept = saved.get(MODES[i][0])
        if (i != mode_index and kept is not None and "wake_at" in kept
                and time.ticks_diff(now, kept["wake_at"]) >= 0):
            switch_to(i)
            break

    # Once a day, set the clock again. (The clock stands still while it
    # connects, then catches up.)
    if SYNC_WITH_WIFI:
        t = time.localtime()
        if t[3] == RESYNC_HOUR and t[2] != synced_day:
            wifi_time.sync_time()
            synced_day = t[2]

    time.sleep_ms(5)
