# mode-template.py: One Clock, Ten Modes
# Tap MODE to step through ten modes; a row of ten dots along the bottom
# shows which one you are in. It starts in the Big Clock.
#
#   0 Big Clock       the largest digits the round screen can hold
#   1 Temperature     the time, and the temperature outside right now
#   2 Forecast        the time, the temperature, today's and tomorrow's
#                     highs and lows
#   3 Alarm           set the alarm (it rings in any mode)
#   4 Timer           a countdown timer (it beeps in any mode)
#   5 Stopwatch       with laps
#   6 Analog          an analog watch face (from the sw-gc9b72 kit)
#   7 Railway         the Swiss station clock (from the mondaine kit)
#   8 Phrase          a medium clock with a phrase of the day
#   9 Holidays        a calendar of US holidays; UP/DOWN change the month
#
# Copy it to the Pico as main.py to make it the program that runs at
# power-up:
#
#     mpremote cp mode-template.py :main.py
#
# THE BUTTONS
#   tap MODE     next mode
#   hold MODE    the mode's own job if it has one (set the alarm, set the
#                timer); otherwise set the clock from the internet now
#   UP / DOWN    belong to the mode -- see the top of each mode_*.py file
#
# EACH MODE IS A MODULE, LOADED ONLY WHILE IT IS SHOWING. Ten faces at
# once would not fit in a Pico W's memory. So when you tap MODE this
# program:
#
#   1. asks the current mode to stop(), and keeps what it hands back
#   2. removes that mode -- and every module it brought with it -- from
#      memory, and runs the garbage collector to free the space
#   3. imports the next mode fresh, and calls its start()
#
# Anything that must outlive a mode (the alarm time, the volume, the last
# weather download) lives in shared.py, which stays loaded.
#
# THE FUNCTIONS EVERY MODE HAS. That is all this program knows about a
# mode, so an eleventh one is one more module like these:
#
#   start(display, up, down, saved)
#       Draw the whole screen. up and down are the UP and DOWN Buttons.
#       saved is whatever stop() returned last time, or None.
#   update(now)
#       Called every pass of the loop with time.ticks_ms(). Read UP and
#       DOWN, redraw only what changed. Return True to have the mode dots
#       drawn again (if the mode painted over them).
#   on_mode(kind)                                       (optional)
#       MODE was pressed: kind is SHORT or LONG. Return True if the mode
#       used the press itself.
#   stop()
#       Turn off anything that is on, and return a dict to keep (or
#       None). A dict with "wake_at" -- a time.ticks_ms() value -- asks
#       for the mode to be shown again at that moment: that is how the
#       timer's alarm interrupts whatever mode is showing.
#
#   DOT_ON, DOT_OFF                                     (optional)
#       Colors for the dots, for a mode whose background is not black.
#
# THE ONE RULE: a mode must not draw in the strip where the dots go
# (y = 310 to 322, x = 120 to 240), except in start() before the dots are
# drawn.
#
# The main loop also does the jobs no single mode owns: it rings the
# alarm, chimes on the hour, and sets the clock from the internet at
# 3:00 AM.

NAME = "mode-template.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import gc
import sys
import time

import config
import sfx          # sound.play() imports it -- compile it now, while RAM is tidy
import shapes
import sound
import wifi_time
import shared
import watchparts
from watchparts import Button, SHORT, LONG

# (module, name) for each mode, in the order MODE steps through them.
MODES = (
    ("mode_big", "Big Clock"),
    ("mode_temp", "Temperature"),
    ("mode_forecast", "Forecast"),
    ("mode_alarm", "Alarm"),
    ("mode_timer", "Timer"),
    ("mode_stopwatch", "Stopwatch"),
    ("mode_analog", "Analog"),
    ("mode_mondaine", "Railway"),
    ("mode_phrase", "Phrase"),
    ("mode_calendar", "Holidays"),
)
START_MODE = 0           # the Big Clock
ALARM_MODE = 3           # where the alarm rings

# Set to a number of seconds to step through the modes by themselves, like
# a display in a shop window. 0 waits for the MODE button.
DEMO_SECONDS = 0

SYNC_WITH_WIFI = True    # set the clock over WiFi at power-up...
RESYNC_HOUR = 3          # ...and again at 3:00 AM every night

# Ten dots, 12 px apart, centered at the bottom. Their outer edge is 150 px
# from the center, just inside the second-tick rings, which start at 152.
DOT_Y = 316
DOT_SPACING = 12
DOT_RADIUS = 4
DOT_ON = config.WHITE
DOT_OFF = config.color565(70, 70, 70)


def draw_dots():
    on = getattr(mode, "DOT_ON", DOT_ON)
    off = getattr(mode, "DOT_OFF", DOT_OFF)
    x = config.CENTER_X - (len(MODES) - 1) * DOT_SPACING // 2
    for i in range(len(MODES)):
        shapes.circle(display, x + i * DOT_SPACING, DOT_Y, DOT_RADIUS,
                      on if i == mode_index else off, config.FILL)


def switch_to(index):
    """Stop and unload the current mode, then load and start mode `index`."""
    global mode, mode_index, loaded_before, shown_since
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
        # watchparts stays loaded (this file uses its Button), and it keeps
        # every tick ring it has built, ready for next time. On a Pico W
        # that cache -- thousands of small pieces -- leaves no room to load
        # the next mode, so throw it away too. (A mode with a ring takes
        # half a second longer to start.)
        watchparts._ring_cache.clear()
        gc.collect()

    mode_index = index
    name = MODES[index][0]
    loaded_before = set(sys.modules)
    mode = __import__(name)
    mode.start(display, up_button, down_button, saved.get(name))
    draw_dots()
    shown_since = time.ticks_ms()
    gc.collect()
    print("Mode {}: {} -- {} KB free".format(index, MODES[index][1],
                                             gc.mem_free() // 1024))


# --- start up -------------------------------------------------------------------
display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]

if SYNC_WITH_WIFI:
    display.fill(config.BLACK)
    config.centered_text(display, config.BIG_FONT, "Setting clock", 130,
                         config.CYAN)
    if wifi_time.sync_time(display):
        shared.synced = True
    else:
        time.sleep(2)    # keep going on whatever time the RTC has
# The speaker starts BEFORE the first mode draws -- see shared.py.
shared.start_speaker(config.VOLUME)

saved = {}               # module name -> what its stop() returned
mode = None
mode_index = 0
loaded_before = set()
gc.collect()
switch_to(START_MODE)
shared.speaker.play("start")

t = time.localtime()
last_minute = (t[3], t[4])
synced_day = t[2]

# --- the main loop -----------------------------------------------------------------
try:
    while True:
        now = time.ticks_ms()

        press = mode_button.short_or_long(now)
        if press is not None:
            on_mode = getattr(mode, "on_mode", None)
            used = on_mode is not None and on_mode(press)
            if not used:
                if press == SHORT:
                    switch_to((mode_index + 1) % len(MODES))
                elif SYNC_WITH_WIFI:          # an unused long press
                    ok = shared.sync_time()
                    shared.speaker.play("right" if ok else "wrong")

        if mode.update(now):
            draw_dots()

        if DEMO_SECONDS and time.ticks_diff(now, shown_since) >= \
                DEMO_SECONDS * 1000:
            switch_to((mode_index + 1) % len(MODES))

        # A mode that is not showing can ask to be shown at a set time.
        for i in range(len(MODES)):
            kept = saved.get(MODES[i][0])
            if (i != mode_index and kept is not None and "wake_at" in kept
                    and time.ticks_diff(now, kept["wake_at"]) >= 0):
                switch_to(i)
                break

        # Once a minute: the alarm, the hourly chime, the nightly sync.
        t = time.localtime()
        minute_now = (t[3], t[4])
        if minute_now != last_minute:
            last_minute = minute_now
            hour, minute = minute_now
            if (shared.alarm_on and not shared.ringing
                    and minute_now == (shared.alarm_hour,
                                       shared.alarm_minute)):
                shared.ringing = True
                shared.ring_started = now
                print("Alarm!")
                if mode_index != ALARM_MODE:
                    switch_to(ALARM_MODE)
            elif (minute == 0 and shared.chime_on and not shared.ringing
                  and not shared.quiet_hour(hour)
                  and not shared.speaker.busy()):
                shared.speaker.play("chime")
            if (SYNC_WITH_WIFI and hour == RESYNC_HOUR and minute == 0
                    and t[2] != synced_day):
                synced_day = t[2]
                shared.sync_time()

        time.sleep_ms(5)
finally:
    if shared.speaker is not None:
        shared.speaker.off()

# Try This
#   1. Change START_MODE to 7, so the clock wakes up as the railway clock.
#   2. Reorder MODES to put your favorites first. The dots follow. (If you
#      move the alarm, change ALARM_MODE to its new place.)
#   3. Make an eleventh mode: copy mode_big.py to mode_mine.py, change its
#      colors, and add ("mode_mine", "Mine") to MODES. Is there room for
#      eleven dots? (Each one moves the row 6 px wider.)
