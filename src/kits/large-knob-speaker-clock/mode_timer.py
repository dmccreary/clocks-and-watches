# mode_timer.py -- a countdown timer with a speaker alarm, as a mode for
# 16-main-template.py.
#
# The timer is a STATE MACHINE: at any moment it is in exactly one of six
# states -- setting the minutes, setting the seconds, ready, running,
# paused, or done -- and each control does something different in each
# state. update() first decides whether a press moves it to a new state,
# then draws whatever that state looks like.
#
# The controls:
#
#   K0    start / pause
#   PUSH  set: minutes -> seconds -> go!    (while paused: reset)
#   KNOB  while setting: change the yellow number
#
# The PUSH that finishes setting the seconds also starts the timer, as in
# lab 09. (Set it to 00:00 and it waits in READY instead.)
#
# The knob belongs to the clock here: turning it switches modes. But
# while the time is being set, or the alarm is going off, the timer keeps
# the knob for itself (on_knob() returns True), so a turn there changes
# the number or stops the alarm instead of switching modes.
#
# Switching away does not stop a running timer. stop() hands back when it
# will end as "wake_at", and 16-main-template.py switches back to this
# mode the moment that time comes, so the alarm goes off whatever mode
# the clock is showing.
#
# THE ALARM. When the time is up the digits flash 00:00 in red, the
# Pico's own LED flashes with them, and the speaker beeps four times on
# every flash -- until any control is touched. During the last
# WARNING_MS the digits turn red and the speaker ticks once a second.
#
# Every mode has the same four functions, and this one has the optional
# on_knob() too -- see 16-main-template.py. A mode only gets rows 0 to
# 219 of the screen, because the mode dots go below.

import time
from machine import Pin

import config
import sound
from watchparts import Digit, TickFrame, TextLine, DIGITS, BLANK

DIGIT_COLOR = config.WHITE
SETTING_COLOR = config.YELLOW
WARNING_COLOR = config.RED
GHOST = config.color565(24, 24, 30)
ACCENT = config.CYAN
TICK_OFF = config.color565(40, 40, 40)
HINT_COLOR = config.color565(150, 150, 150)
TITLE_COLOR = config.CYAN
SMALL = config.SMALL_FONT

START_MINUTES = 5
START_SECONDS = 0
WARNING_MS = 10_000
FLASH_MS = 500
TICK_IN_WARNING = True   # a tick from the speaker each of the last seconds

SET_MINUTES, SET_SECONDS, READY, RUNNING, PAUSED, DONE = range(6)
STATE_NAMES = ("SET MINUTES", "SET SECONDS", "READY", "RUNNING", "PAUSED",
               "TIME'S UP!")
STATE_COLORS = (SETTING_COLOR, SETTING_COLOR, HINT_COLOR, config.GREEN,
                config.YELLOW, WARNING_COLOR)
HINTS = ("KNOB +/- PUSH next", "KNOB +/- PUSH go",
         "K0 start  PUSH set", "K0 pause", "K0 go  PUSH reset",
         "any control: stop")

# Layout. A digit's height must be 3 x its thickness plus an even number.
MODE_ROWS = 220         # rows 0 to 219
DIGIT_W, DIGIT_H, DIGIT_T = 56, 98, 10
PAIR_GAP = 10
COLON_GAP = 12
TITLE_Y = 13            # "TIMER", so you know which mode this is
HINT_Y = 29
STATE_Y = 46
DIGIT_TOP = 84
NOTE_Y = DIGIT_TOP + DIGIT_H + 4
TICK_DEPTH, TICK_DEPTH_FIVE, TICK_LENGTH = 5, 10, 8


def start(display, k0, push, saved):
    global _k0, _push, digits, hint, status, note, frame, led
    global state, set_minutes, set_seconds, remaining_ms, end_ticks, done_at
    global shown_state, shown_flash, ticked_second
    _k0 = k0
    _push = push
    # Forget any press made while another mode was on the screen.
    k0.pressed()
    push.pressed()
    display.fill_rect(0, 0, config.WIDTH, MODE_ROWS, config.BLACK)
    config.centered_text(display, SMALL, "TIMER", TITLE_Y, TITLE_COLOR)

    row = 4 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T
    x = (config.WIDTH - row) // 2
    digit_x = (x, x + DIGIT_W + PAIR_GAP,
               x + 2 * DIGIT_W + PAIR_GAP + 2 * COLON_GAP + DIGIT_T,
               x + 3 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T)
    colon_x = x + 2 * DIGIT_W + PAIR_GAP + COLON_GAP
    digits = [Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                    DIGIT_COLOR, GHOST) for x in digit_x]
    for y in (DIGIT_TOP + DIGIT_H // 3 - DIGIT_T // 2,
              DIGIT_TOP + 2 * DIGIT_H // 3 - DIGIT_T // 2):
        display.fill_rect(colon_x, y, DIGIT_T, DIGIT_T, DIGIT_COLOR)

    hint = TextLine(display, SMALL, config.CENTER_X, HINT_Y, 18, HINT_COLOR)
    status = TextLine(display, config.BIG_FONT, config.CENTER_X, STATE_Y, 11,
                      HINT_COLOR)
    note = TextLine(display, SMALL, config.CENTER_X, NOTE_Y, 16, HINT_COLOR)
    frame = TickFrame(display, config.WIDTH, MODE_ROWS, TICK_DEPTH,
                      TICK_DEPTH_FIVE, TICK_LENGTH)

    led = Pin(config.LED_PIN, Pin.OUT)
    led.value(0)            # the LED may still be on from another program

    if saved is None:
        state = READY
        set_minutes, set_seconds = START_MINUTES, START_SECONDS
        remaining_ms = total_ms()
        end_ticks = 0
    else:
        state = saved["state"]
        set_minutes = saved["set_minutes"]
        set_seconds = saved["set_seconds"]
        remaining_ms = saved["remaining_ms"]
        end_ticks = saved["end_ticks"]
    done_at = 0
    shown_state = None
    shown_flash = None
    ticked_second = None


def total_ms():
    return (set_minutes * 60 + set_seconds) * 1000


def alarm_outputs(on):
    """The LED follows the flashing digits. Each time they light up, four
    quick beeps start -- they last about as long as one flash."""
    led.value(1 if on else 0)
    if on:
        for _ in range(4):
            sound.tone(2093, 60, wave=sound.SQUARE, level=0.6, attack=2,
                       release=5)
            sound.rest(40)


def start_beep():
    """A short rising pair of notes: the timer has started."""
    sound.tone(1320, 40, wave=sound.SQUARE, level=0.3, attack=2, release=8)
    sound.tone(1760, 60, wave=sound.SQUARE, level=0.3, attack=2, release=8)


def silence():
    """Stop the alarm: LED off, and drop any beeps still queued."""
    led.value(0)
    sound.stop()


def on_knob(clicks):
    """The knob was turned: clicks is how far, positive for clockwise.
    Return True if the timer used the turn; False lets it switch modes."""
    global state, set_minutes, set_seconds, remaining_ms
    if state == SET_MINUTES:
        set_minutes = (set_minutes + clicks) % 100
        return True
    if state == SET_SECONDS:
        set_seconds = (set_seconds + clicks) % 60
        return True
    if state == DONE:                          # any control stops the alarm
        silence()
        remaining_ms = total_ms()
        state = READY
        return True
    return False


def show_digits(minutes, seconds, colors):
    values = (minutes // 10, minutes % 10, seconds // 10, seconds % 10)
    for i in range(4):
        digits[i].show(DIGITS[values[i]], colors[i // 2])


def show_frame(lit):
    for second in range(60):
        frame.paint(second, ACCENT if second < lit else TICK_OFF)


def update(now):
    global state, remaining_ms, end_ticks, done_at
    global shown_state, shown_flash, ticked_second
    k0_pressed = _k0.pressed(now)
    push_pressed = _push.pressed(now)

    if state == SET_MINUTES or state == SET_SECONDS:
        if push_pressed:
            remaining_ms = total_ms()
            if state == SET_MINUTES:
                state = SET_SECONDS
            elif remaining_ms > 0:               # done setting: go!
                end_ticks = time.ticks_add(now, remaining_ms)
                state = RUNNING
                start_beep()
            else:                                # 00:00: nothing to run
                state = READY
    elif state == READY:
        if k0_pressed and total_ms() > 0:
            end_ticks = time.ticks_add(now, remaining_ms)
            state = RUNNING
        elif push_pressed:
            state = SET_MINUTES
    elif state == RUNNING:
        remaining_ms = max(0, time.ticks_diff(end_ticks, now))
        if k0_pressed:
            state = PAUSED
        elif remaining_ms == 0:
            state = DONE
            done_at = now
        elif TICK_IN_WARNING and remaining_ms <= WARNING_MS:
            second = (remaining_ms + 999) // 1000
            if second != ticked_second:
                sound.tone(1000, 15, wave=sound.SQUARE, level=0.3,
                           attack=1, release=5)
                ticked_second = second
    elif state == PAUSED:
        if k0_pressed:
            end_ticks = time.ticks_add(now, remaining_ms)
            state = RUNNING
        elif push_pressed:
            remaining_ms = total_ms()
            state = READY
    elif state == DONE:
        if k0_pressed or push_pressed:
            silence()
            remaining_ms = total_ms()
            state = READY

    if state == SET_MINUTES or state == SET_SECONDS:
        show_digits(set_minutes, set_seconds,
                    (SETTING_COLOR if state == SET_MINUTES else DIGIT_COLOR,
                     SETTING_COLOR if state == SET_SECONDS else DIGIT_COLOR))
        show_frame(60 if total_ms() > 0 else 0)
    elif state == DONE:
        flash = (time.ticks_diff(now, done_at) // FLASH_MS) % 2 == 0
        if flash != shown_flash:
            for digit in digits:
                digit.show(DIGITS[0] if flash else BLANK, WARNING_COLOR)
            alarm_outputs(flash)
            shown_flash = flash
        show_frame(0)
    else:
        seconds_left = (remaining_ms + 999) // 1000
        warn = state == RUNNING and remaining_ms <= WARNING_MS
        color = WARNING_COLOR if warn else DIGIT_COLOR
        show_digits(seconds_left // 60, seconds_left % 60, (color, color))
        total = total_ms()
        show_frame((remaining_ms * 60 + total - 1) // total if total else 0)

    if state != shown_state:
        status.show(STATE_NAMES[state], STATE_COLORS[state])
        hint.show(HINTS[state])
        if state == DONE:
            note.show("K0, PUSH or knob")
        elif state == SET_MINUTES:
            note.show("0 to 99 minutes")
        elif state == SET_SECONDS:
            note.show("0 to 59 seconds")
        else:
            note.show("Set to %02d:%02d" % (set_minutes, set_seconds))
        if state != DONE:
            shown_flash = None
        shown_state = state


def stop():
    """Keep the timer's state. A running timer also says when it will
    reach zero, so the clock can come back here for the alarm."""
    if state == DONE:
        silence()
    led.value(0)
    saved = {"state": state, "set_minutes": set_minutes,
             "set_seconds": set_seconds, "remaining_ms": remaining_ms,
             "end_ticks": end_ticks}
    if state == RUNNING:
        saved["wake_at"] = end_ticks
    return saved
