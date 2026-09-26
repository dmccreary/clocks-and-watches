# Lab 11: Countdown Timer
# Set a time with the buttons, start it, and it counts down to zero, then
# flashes until you press a button. The ring around the rim shows how
# much time is left: full at the start, emptying back toward 12 o'clock.
#
#   MODE  (GP13)  set: minutes -> seconds -> done
#   UP    (GP14)  start / pause   (while setting: add one)
#   DOWN  (GP15)  reset, only while paused   (while setting: take one away)
#
# Hold UP or DOWN while setting and the number keeps changing. A line
# near the top always shows what the buttons do right now.
#
# A TIMER IS A STATE MACHINE. What a button does depends on what the
# timer is doing: UP means "add one" while you set the minutes, "start"
# when the timer is ready, and "pause" while it runs. The program keeps
# one variable, `state`, that says which of six states it is in, and
# every button press is handled by asking "what state are we in?" first.
#
#                  MODE                MODE
#   SET_MINUTES --------> SET_SECONDS --------> READY <-----------+
#        ^                                      |   |             |
#        +------------------MODE----------------+   | UP          | DOWN
#                                                   v             |
#               DONE <---reaches 00:00--- RUNNING <---UP---> PAUSED
#                 |
#                 +---any button---> READY
#
# Like the stopwatch, it never counts down by subtracting a little each
# loop. It works out when the timer will END, and each time around the
# loop asks how far away that moment is.

NAME = "11-countdown-timer.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

import config
from watchparts import Digit, TickRing, TextLine, Button, DIGITS, BLANK

BLACK = config.BLACK
DIGIT_COLOR = config.WHITE
SETTING_COLOR = config.YELLOW     # the field being set
WARNING_COLOR = config.RED        # the last WARNING_MS, and the alarm
GHOST = config.color565(24, 24, 30)
ACCENT = config.CYAN
TICK_OFF = config.color565(40, 40, 40)
HINT_COLOR = config.color565(150, 150, 150)
SMALL = config.SMALL_FONT

START_MINUTES = 5
START_SECONDS = 0
WARNING_MS = 10_000     # the digits turn red for the last 10 seconds
FLASH_MS = 500          # how fast the alarm flashes

SET_MINUTES, SET_SECONDS, READY, RUNNING, PAUSED, DONE = range(6)
STATE_NAMES = ("SET MINUTES", "SET SECONDS", "READY", "RUNNING", "PAUSED",
               "TIME'S UP!")
STATE_COLORS = (SETTING_COLOR, SETTING_COLOR, HINT_COLOR, config.GREEN,
                config.YELLOW, WARNING_COLOR)
HINTS = ("UP+  DOWN-  MODE next", "UP+  DOWN-  MODE done",
         "UP start  MODE set", "UP pause", "UP go  DOWN reset",
         "any button: stop")

# ---------------------------------------------------------------------
# Layout: the full-size digits of lab 08, MM:SS, centered
# ---------------------------------------------------------------------
DIGIT_W, DIGIT_H, DIGIT_T = 58, 114, 12
PAIR_GAP = 10
COLON_GAP = 12
_row = 4 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T
_x = (config.WIDTH - _row) // 2
DIGIT_X = (_x,
           _x + DIGIT_W + PAIR_GAP,
           _x + 2 * DIGIT_W + PAIR_GAP + 2 * COLON_GAP + DIGIT_T,
           _x + 3 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T)
COLON_X = _x + 2 * DIGIT_W + PAIR_GAP + COLON_GAP
DIGIT_TOP = config.CENTER_Y - DIGIT_H // 2
COLON_Y = (DIGIT_TOP + DIGIT_H // 3 - DIGIT_T // 2,
           DIGIT_TOP + 2 * DIGIT_H // 3 - DIGIT_T // 2)

TITLE_Y = 50
HINT_Y = 76
STATE_Y = 100
NOTE_Y = DIGIT_TOP + DIGIT_H + 16

# ---------------------------------------------------------------------
# Set up the screen and the alarm outputs
# ---------------------------------------------------------------------
display = config.init_display()
display.fill(BLACK)

digits = [Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                DIGIT_COLOR, GHOST) for x in DIGIT_X]
title = TextLine(display, SMALL, config.CENTER_X, TITLE_Y, 5, HINT_COLOR)
hint = TextLine(display, SMALL, config.CENTER_X, HINT_Y, 22, HINT_COLOR)
status = TextLine(display, SMALL, config.CENTER_X, STATE_Y, 11, HINT_COLOR)
note = TextLine(display, SMALL, config.CENTER_X, NOTE_Y, 18, HINT_COLOR)
ring = TickRing(display, config.CENTER_X, config.CENTER_Y,
                config.SAFE_RADIUS - 2, config.SAFE_RADIUS - 10,
                config.SAFE_RADIUS - 16)

mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]
led = Pin(config.LED_PIN, Pin.OUT)
buzzer = None
if config.BUZZER_PIN is not None:
    from machine import PWM
    buzzer = PWM(Pin(config.BUZZER_PIN))
    buzzer.freq(2000)
    buzzer.duty_u16(0)

title.show("TIMER")
for y in COLON_Y:
    display.fill_rect(COLON_X, y, DIGIT_T, DIGIT_T, DIGIT_COLOR)


def alarm_outputs(on):
    led.value(1 if on else 0)
    if buzzer is not None:
        buzzer.duty_u16(32768 if on else 0)


# ---------------------------------------------------------------------
# The timer
# ---------------------------------------------------------------------
state = READY
set_minutes = START_MINUTES
set_seconds = START_SECONDS
remaining_ms = 0        # time left, whenever the timer is not running
end_ticks = 0           # ticks_ms() at which a running timer reaches zero
done_at = 0             # ticks_ms() when the timer reached zero

shown_state = None
shown_flash = None


def total_ms():
    return (set_minutes * 60 + set_seconds) * 1000


remaining_ms = total_ms()


def show_digits(minutes, seconds, colors):
    """colors is (minutes color, seconds color)."""
    values = (minutes // 10, minutes % 10, seconds // 10, seconds % 10)
    for i in range(4):
        digits[i].show(DIGITS[values[i]], colors[i // 2])


def show_ring(lit):
    """Light the first `lit` ticks, clockwise from 12. Only ticks whose
    color changes get repainted -- normally one tick every few seconds."""
    for second in range(60):
        ring.paint(second, ACCENT if second < lit else TICK_OFF)


while True:
    now = time.ticks_ms()
    up = up_button.pressed(now, repeat=True)
    down = down_button.pressed(now, repeat=True)
    mode = mode_button.pressed(now)

    # ---- what the buttons do, in each state --------------------------
    if state == SET_MINUTES or state == SET_SECONDS:
        step = 1 if up else -1 if down else 0
        if state == SET_MINUTES:
            set_minutes = (set_minutes + step) % 100
        else:
            set_seconds = (set_seconds + step) % 60
        if mode:
            state = SET_SECONDS if state == SET_MINUTES else READY
            remaining_ms = total_ms()
    elif state == READY:
        if up and total_ms() > 0:
            end_ticks = time.ticks_add(now, remaining_ms)
            state = RUNNING
        elif mode:
            state = SET_MINUTES
    elif state == RUNNING:
        remaining_ms = max(0, time.ticks_diff(end_ticks, now))
        if up:
            state = PAUSED
        elif remaining_ms == 0:
            state = DONE
            done_at = now
    elif state == PAUSED:
        if up:
            end_ticks = time.ticks_add(now, remaining_ms)
            state = RUNNING
        elif down:
            remaining_ms = total_ms()
            state = READY
    elif state == DONE:
        if up or down or mode:
            alarm_outputs(False)
            remaining_ms = total_ms()
            state = READY

    # ---- what the screen shows -----------------------------------------
    if state == SET_MINUTES or state == SET_SECONDS:
        show_digits(set_minutes, set_seconds,
                    (SETTING_COLOR if state == SET_MINUTES else DIGIT_COLOR,
                     SETTING_COLOR if state == SET_SECONDS else DIGIT_COLOR))
        show_ring(60 if total_ms() > 0 else 0)
    elif state == DONE:
        # Flash 00:00 in red, on and off, and the alarm with it.
        flash = (time.ticks_diff(now, done_at) // FLASH_MS) % 2 == 0
        if flash != shown_flash:
            for digit in digits:
                digit.show(DIGITS[0] if flash else BLANK, WARNING_COLOR)
            alarm_outputs(flash)
            shown_flash = flash
        show_ring(0)
    else:
        # Round UP to whole seconds, so the display reads 05:00 for the
        # whole first second and reaches 00:00 exactly at zero.
        seconds_left = (remaining_ms + 999) // 1000
        warn = state == RUNNING and remaining_ms <= WARNING_MS
        color = WARNING_COLOR if warn else DIGIT_COLOR
        show_digits(seconds_left // 60, seconds_left % 60, (color, color))
        total = total_ms()
        show_ring((remaining_ms * 60 + total - 1) // total if total else 0)

    if state != shown_state:
        status.show(STATE_NAMES[state], STATE_COLORS[state])
        hint.show(HINTS[state])
        if state == DONE:
            note.show("Press any button")
        elif state == SET_MINUTES or state == SET_SECONDS:
            note.show("Hold to go faster")
        else:
            note.show("Set to %02d:%02d" % (set_minutes, set_seconds))
        if state != DONE:
            shown_flash = None
        shown_state = state

    time.sleep_ms(10)
