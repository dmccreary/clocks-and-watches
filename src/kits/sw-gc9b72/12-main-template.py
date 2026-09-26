# Lab 12: Main Template -- One Watch, Five Modes
# Press MODE to step through five modes, one at a time:
#
#   Weather -> Analog -> Digital -> Stopwatch -> Timer -> (back to Weather)
#
# A row of five dots at the bottom of the screen shows which mode you are
# in. The watch starts in Weather. Copy this file to the Pico as main.py
# and it is the whole watch.
#
# EACH MODE IS A MODULE, LOADED ONLY WHEN IT IS NEEDED. Five watch faces
# at once would fill a lot of RAM with code and drawings nobody is looking
# at. So only the mode on the screen is in memory. Pressing MODE:
#
#   1. asks the current mode to stop(), and keeps whatever it hands back
#   2. removes that mode -- and every module it brought in with it -- from
#      memory, and runs the garbage collector to free the space
#   3. imports the next mode fresh, and calls its start()
#
# THE FOUR FUNCTIONS EVERY MODE HAS. That is all this program knows about
# a mode, so adding a sixth one means writing one more module like these:
#
#   start(display, up, down, saved)
#       Draw the whole screen. up and down are the UP and DOWN buttons.
#       saved is whatever stop() returned the last time, or None.
#   update(now)
#       Called on every pass of the loop, about every 10 ms, with
#       time.ticks_ms(). Read the buttons, redraw only what changed.
#   on_mode(kind)                                          (optional)
#       MODE was pressed: kind is SHORT or LONG. Return True if the mode
#       used the press itself; a short press it does not use switches to
#       the next mode.
#   stop()
#       Turn off anything that is on, and return a dict to keep until
#       next time (or None). A dict with a "wake_at" time -- a
#       time.ticks_ms() value -- asks for this mode to be shown again at
#       that moment, which is how a timer's alarm interrupts the weather.
#
# And two rules: a mode must not draw in the strip where the dots go
# (y = DOT_Y - 6 to DOT_Y + 6, the middle of the bottom edge), and must
# not clear the whole screen except in start().
#
# The MODE button belongs to this program, not to the modes: it reports
# a short press when MODE is let go, and a long press as soon as it has
# been held for a second. The stopwatch and timer in lab 10 and lab 11
# use MODE for laps and setting, so their mode versions use UP and DOWN
# for those, and the timer is set with a long press.

NAME = "12-main-template.py"
VERSION = "1.1"
print("{} v{}".format(NAME, VERSION))

import gc
import sys
import time

import config
import shapes
import wifi_time
from watchparts import Button, SHORT

# (module, name) for each mode, in the order MODE steps through them.
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

DOT_Y = 322
DOT_SPACING = 16
DOT_RADIUS = 4
DOT_ON = config.WHITE
DOT_OFF = config.color565(70, 70, 70)


def draw_dots(current):
    """One dot per mode across the bottom, centered; the current mode's
    is bright."""
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
    mode.start(display, up_button, down_button, saved.get(name))
    draw_dots(index)
    gc.collect()
    print("Mode:", MODES[index][1], "--", gc.mem_free() // 1024, "KB free")


display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]

if SYNC_WITH_WIFI:
    display.fill(config.BLACK)
    config.centered_text(display, config.BIG_FONT, "Setting clock", 130)
    if not wifi_time.sync_time(display):
        time.sleep(3)    # keep going on whatever time the RTC has

saved = {}               # module name -> what its stop() returned
mode = None
mode_index = 0
loaded_before = set()
gc.collect()
switch_to(START_MODE)
synced_day = time.localtime()[2]

while True:
    now = time.ticks_ms()

    press = mode_button.short_or_long(now)
    if press is not None:
        on_mode = getattr(mode, "on_mode", None)
        used = on_mode is not None and on_mode(press)
        if not used and press == SHORT:
            switch_to((mode_index + 1) % len(MODES))

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
