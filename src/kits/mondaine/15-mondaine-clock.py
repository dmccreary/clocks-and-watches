# Lab 15: The Railway Clock
# Everything from labs 01 to 14, in one program. Copy this file to the Pico
# as main.py and it is the whole clock: it sets itself from the internet
# at power-up, glides the red hand around the dial, parks it at 12 while
# the minute hand hops, and sets itself again every night at 3 AM.
#
#   MODE  (GP13)  short press: run -> set hour -> set minute -> run
#                 hold for a second (while running): set the clock from
#                 the internet right now
#   UP    (GP14)  adds one to the hour or minute being set
#   DOWN  (GP15)  subtracts one
#
# NEW IDEAS: putting a program together from parts you tested one at a
# time, and housekeeping that runs while the clock is at rest.
#
# THE PARTS. lib/mondaine.py draws the face and times the motion (labs 02
# to 12). lib/buttons.py reads the buttons (labs 13 and 14). wifi_time.py
# talks to the internet (lab 08). This file only decides what happens
# when.
#
# THE REST. Once a minute, for about a second, nothing moves: the minute
# hand has landed and the red hand is waiting at 12. The program uses that
# moment for housekeeping, when nobody can see a hiccup:
#
#   - clock.sync() lines the millisecond counter up with the RTC again
#   - at 3 AM, once a day, it asks the internet for the right time
#
# Both finish before the red hand sets off.
#
# HOW FAST IS IT? It tries for 20 frames a second. A frame repaints only
# the rows the moving hand touched, and a hand pointing straight up or
# down touches the most. Run lab 10 and read its frames-a-second line to
# see what your board manages; a slower board just takes smaller, more
# frequent-looking steps, and the hand is never behind the clock.

NAME = "15-mondaine-clock.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import RTC

import config
import mondaine
import wifi_time
from buttons import Button, SHORT, LONG

SYNC_WITH_WIFI = True    # set the clock over WiFi at power-up...
RESYNC_HOUR = 3          # ...and again at 3:00 AM every night

RUN_FRAME_MS = 50        # up to 20 frames a second while the clock runs
SET_FRAME_MS = 20        # look at the buttons more often while setting

RUN, SET_HOUR, SET_MINUTE = 0, 1, 2
LABELS = ("", " SET HOUR ", "SET MINUTE")     # the same width, 10 characters
LABEL_Y = 240


def set_rtc(hour, minute, second):
    """Change the time of day, keeping the date the RTC already has."""
    year, month, day, weekday = rtc.datetime()[:4]
    rtc.datetime((year, month, day, weekday, hour, minute, second, 0))


def set_clock_from_internet():
    """Show what is happening, ask the internet for the time, and put the
    dial back. The caller must run clock.sync() afterward."""
    display.fill(config.BLACK)
    config.centered_text(display, config.BIG_FONT, "Setting clock", 130)
    if not wifi_time.sync_time(display):
        time.sleep(3)        # keep going on whatever time the RTC has
    face.draw_dial()


rtc = RTC()
display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]
face = mondaine.Face(display)

if SYNC_WITH_WIFI:
    set_clock_from_internet()
else:
    face.draw_dial()

clock = mondaine.SweepClock()
mode = RUN
at_rest = False              # did this minute's rest-time chores run yet?
synced_day = time.localtime()[2]
last_drawn = None

while True:
    frame_start = time.ticks_ms()

    press = mode_button.short_or_long(frame_start)
    if press == SHORT:
        mode = (mode + 1) % 3
        if mode == RUN:
            face.draw_dial()           # wipes the label off the dial
            clock.sync()               # the RTC may have just changed
        last_drawn = None
    elif press == LONG and mode == RUN and SYNC_WITH_WIFI:
        set_clock_from_internet()
        clock.sync()

    if mode == RUN:
        hour, minute, ms = clock.now()
        face.show(*mondaine.hand_angles(hour, minute, ms))

        if ms >= mondaine.RESYNC_MS:
            if not at_rest:
                at_rest = True
                today = time.localtime()[2]
                if (SYNC_WITH_WIFI and hour == RESYNC_HOUR
                        and today != synced_day):
                    set_clock_from_internet()
                    synced_day = today
                clock.sync()           # waits for the top of the minute
        else:
            at_rest = False
        frame_ms = RUN_FRAME_MS

    else:
        t = time.localtime()
        hour, minute, second = t[3], t[4], t[5]

        step = 0
        if up_button.pressed(frame_start, repeat=True):
            step = 1
        elif down_button.pressed(frame_start, repeat=True):
            step = -1
        if step and mode == SET_HOUR:
            hour = (hour + step) % 24
            set_rtc(hour, minute, second)
        elif step and mode == SET_MINUTE:
            minute = (minute + step) % 60
            set_rtc(hour, minute, 0)

        if (hour, minute, mode) != last_drawn:
            face.show((hour % 12) * 30 + minute * 0.5, minute * 6, 0)
            config.centered_text(display, config.SMALL_FONT, LABELS[mode],
                                 LABEL_Y, config.YELLOW, config.BLACK)
            last_drawn = (hour, minute, mode)
        frame_ms = SET_FRAME_MS

    spent = time.ticks_diff(time.ticks_ms(), frame_start)
    time.sleep_ms(max(1, frame_ms - spent))
