# Lab 16: Countdown Timer
# Set a time with the knob, start it, and it counts down to zero, then
# flashes until you press a button or turn the knob. The ticks around the
# edge of the screen show how much time is left: all lit at the start,
# going out one by one, back toward the middle of the top edge.
#
#   K0    (GP11)      start / pause
#   PUSH  (GP10)      set: minutes -> seconds -> done   (while paused: reset)
#   KNOB  (GP8, GP9)  while setting: change the yellow number
#
# PUSH is the knob itself: press it straight down. A line at the top
# always shows what the controls do right now.
#
# A TIMER IS A STATE MACHINE. What a control does depends on what the
# timer is doing: PUSH means "set the time" when the timer is ready,
# "next" while you set the minutes, and "reset" while it is paused. The
# program keeps one variable, `state`, that says which of six states it
# is in, and every press and every turn is handled by asking "what state
# are we in?" first.
#
#                  PUSH                PUSH
#   SET_MINUTES --------> SET_SECONDS --------> READY <-----------+
#        ^                                      |   |             |
#        +------------------PUSH----------------+   | K0          | PUSH
#                                                   v             |
#               DONE <---reaches 00:00--- RUNNING <---K0---> PAUSED
#                 |
#                 +---K0, PUSH, or a turn of the knob---> READY
#
# Turning the knob only matters in three states: it changes the number in
# the two SET states, and stops the alarm in DONE.
#
# Like the stopwatch, it never counts down by subtracting a little each
# loop. It works out when the timer will END, and each time around the
# loop asks how far away that moment is.

NAME = "16-countdown-timer.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

import config
from watchparts import Digit, TickFrame, TextLine, Button, Knob, DIGITS, BLANK

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
# A line holds 18 characters between the ticks.
HINTS = ("KNOB +/- PUSH next", "KNOB +/- PUSH done",
         "K0 start  PUSH set", "K0 pause", "K0 go  PUSH reset",
         "any control: stop")

# ---------------------------------------------------------------------
# Layout: MM:SS in 57 px digits, centered, with two lines of text above
# them and one below. The ticks use the outer 6 pixels of the screen, so
# everything else stays at least 7 pixels in from every edge.
# ---------------------------------------------------------------------
DIGIT_W, DIGIT_H, DIGIT_T = 28, 57, 5
PAIR_GAP = 5
COLON_GAP = 6
_row = 4 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T
_x = (config.WIDTH - _row) // 2
DIGIT_X = (_x,
           _x + DIGIT_W + PAIR_GAP,
           _x + 2 * DIGIT_W + PAIR_GAP + 2 * COLON_GAP + DIGIT_T,
           _x + 3 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T)
COLON_X = _x + 2 * DIGIT_W + PAIR_GAP + COLON_GAP

HINT_Y = 8
STATE_Y = 24
DIGIT_TOP = 43
NOTE_Y = DIGIT_TOP + DIGIT_H + 3
COLON_Y = (DIGIT_TOP + DIGIT_H // 3 - DIGIT_T // 2,
           DIGIT_TOP + 2 * DIGIT_H // 3 - DIGIT_T // 2)

# ---------------------------------------------------------------------
# Set up the screen, the controls, and the alarm outputs
# ---------------------------------------------------------------------
display = config.init_display()
display.fill(BLACK)

digits = [Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                DIGIT_COLOR, GHOST) for x in DIGIT_X]
hint = TextLine(display, SMALL, config.CENTER_X, HINT_Y, 18, HINT_COLOR)
status = TextLine(display, SMALL, config.CENTER_X, STATE_Y, 11, HINT_COLOR)
note = TextLine(display, SMALL, config.CENTER_X, NOTE_Y, 16, HINT_COLOR)
frame = TickFrame(display, config.WIDTH, config.HEIGHT)

a, b, push, k0 = config.init_controls()
k0_button = Button(k0)
push_button = Button(push)
knob = Knob(a, b, config.ENCODER_STEPS_PER_CLICK)
led = Pin(config.LED_PIN, Pin.OUT)
buzzer = None
if config.BUZZER_PIN is not None:
    from machine import PWM
    buzzer = PWM(Pin(config.BUZZER_PIN))
    buzzer.freq(2000)
    buzzer.duty_u16(0)

for y in COLON_Y:
    display.fill_rect(COLON_X, y, DIGIT_T, DIGIT_T, DIGIT_COLOR)


def alarm_outputs(on):
    led.value(1 if on else 0)
    if buzzer is not None:
        buzzer.duty_u16(32768 if on else 0)


alarm_outputs(False)    # the LED may still be on from another program

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


def show_frame(lit):
    """Light the first `lit` ticks, clockwise from the middle of the top.
    Only ticks whose color changes get repainted -- normally one tick
    every few seconds."""
    for second in range(60):
        frame.paint(second, ACCENT if second < lit else TICK_OFF)


while True:
    now = time.ticks_ms()
    k0_pressed = k0_button.pressed(now)
    push_pressed = push_button.pressed(now)
    # Clicks since the last pass, positive for clockwise. Asking empties
    # the count, so turns made while the timer runs are thrown away.
    clicks = knob.turned()

    # ---- what the controls do, in each state -------------------------
    if state == SET_MINUTES or state == SET_SECONDS:
        if state == SET_MINUTES:
            set_minutes = (set_minutes + clicks) % 100
        else:
            set_seconds = (set_seconds + clicks) % 60
        if push_pressed:
            state = SET_SECONDS if state == SET_MINUTES else READY
            remaining_ms = total_ms()
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
    elif state == PAUSED:
        if k0_pressed:
            end_ticks = time.ticks_add(now, remaining_ms)
            state = RUNNING
        elif push_pressed:
            remaining_ms = total_ms()
            state = READY
    elif state == DONE:
        if k0_pressed or push_pressed or clicks:
            alarm_outputs(False)
            remaining_ms = total_ms()
            state = READY

    # ---- what the screen shows -----------------------------------------
    if state == SET_MINUTES or state == SET_SECONDS:
        show_digits(set_minutes, set_seconds,
                    (SETTING_COLOR if state == SET_MINUTES else DIGIT_COLOR,
                     SETTING_COLOR if state == SET_SECONDS else DIGIT_COLOR))
        show_frame(60 if total_ms() > 0 else 0)
    elif state == DONE:
        # Flash 00:00 in red, on and off, and the alarm with it.
        flash = (time.ticks_diff(now, done_at) // FLASH_MS) % 2 == 0
        if flash != shown_flash:
            for digit in digits:
                digit.show(DIGITS[0] if flash else BLANK, WARNING_COLOR)
            alarm_outputs(flash)
            shown_flash = flash
        show_frame(0)
    else:
        # Round UP to whole seconds, so the display reads 05:00 for the
        # whole first second and reaches 00:00 exactly at zero.
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

    time.sleep_ms(10)
