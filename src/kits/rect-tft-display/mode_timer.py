# mode_timer.py -- the countdown timer of lab 16, as a mode for
# 17-main-template.py. Lab 16 explains the state machine behind it.
#
# The controls do what they do in lab 16:
#
#   K0    start / pause
#   PUSH  set: minutes -> seconds -> done   (while paused: reset)
#   KNOB  while setting: change the yellow number
#
# The knob belongs to the clock here: turning it switches modes. But
# while the time is being set, or the alarm is going off, the timer keeps
# the knob for itself (on_knob() returns True), so a turn there changes
# the number or stops the alarm instead of switching modes.
#
# Switching away does not stop a running timer. stop() hands back when it
# will end as "wake_at", and 17-main-template.py switches back to this
# mode the moment that time comes, so the alarm goes off whatever mode
# the clock is showing.
#
# Every mode has the same four functions, and this one has the optional
# on_knob() too -- see 17-main-template.py. A mode only gets rows 0 to
# 119 of the screen, because the mode dots go below, so the digits are
# 4 rows shorter than lab 16's and the lines of text sit closer to them.

import time
from machine import Pin

import config
from watchparts import Digit, TickFrame, TextLine, DIGITS, BLANK

DIGIT_COLOR = config.WHITE
SETTING_COLOR = config.YELLOW
WARNING_COLOR = config.RED
GHOST = config.color565(24, 24, 30)
ACCENT = config.CYAN
TICK_OFF = config.color565(40, 40, 40)
HINT_COLOR = config.color565(150, 150, 150)
SMALL = config.SMALL_FONT

START_MINUTES = 5
START_SECONDS = 0
WARNING_MS = 10_000
FLASH_MS = 500

SET_MINUTES, SET_SECONDS, READY, RUNNING, PAUSED, DONE = range(6)
STATE_NAMES = ("SET MINUTES", "SET SECONDS", "READY", "RUNNING", "PAUSED",
               "TIME'S UP!")
STATE_COLORS = (SETTING_COLOR, SETTING_COLOR, HINT_COLOR, config.GREEN,
                config.YELLOW, WARNING_COLOR)
HINTS = ("KNOB +/- PUSH next", "KNOB +/- PUSH done",
         "K0 start  PUSH set", "K0 pause", "K0 go  PUSH reset",
         "any control: stop")

# Layout, the same as lab 16 but fitted into 120 rows.
MODE_ROWS = 120         # rows 0 to 119
DIGIT_W, DIGIT_H, DIGIT_T = 28, 53, 5
PAIR_GAP = 5
COLON_GAP = 6
HINT_Y = 7
STATE_Y = 23
DIGIT_TOP = 41
NOTE_Y = DIGIT_TOP + DIGIT_H + 2


def start(display, k0, push, saved):
    global _k0, _push, digits, hint, status, note, frame, led, buzzer
    global state, set_minutes, set_seconds, remaining_ms, end_ticks, done_at
    global shown_state, shown_flash
    _k0 = k0
    _push = push
    # Forget any press made while another mode was on the screen.
    k0.pressed()
    push.pressed()
    display.fill_rect(0, 0, config.WIDTH, MODE_ROWS, config.BLACK)

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
    status = TextLine(display, SMALL, config.CENTER_X, STATE_Y, 11, HINT_COLOR)
    note = TextLine(display, SMALL, config.CENTER_X, NOTE_Y, 16, HINT_COLOR)
    frame = TickFrame(display, config.WIDTH, MODE_ROWS)

    led = Pin(config.LED_PIN, Pin.OUT)
    buzzer = None
    if config.BUZZER_PIN is not None:
        from machine import PWM
        buzzer = PWM(Pin(config.BUZZER_PIN))
        buzzer.freq(2000)
        buzzer.duty_u16(0)
    alarm_outputs(False)    # the LED may still be on from another program

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


def total_ms():
    return (set_minutes * 60 + set_seconds) * 1000


def alarm_outputs(on):
    led.value(1 if on else 0)
    if buzzer is not None:
        buzzer.duty_u16(32768 if on else 0)


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
        alarm_outputs(False)
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
    global shown_state, shown_flash
    k0_pressed = _k0.pressed(now)
    push_pressed = _push.pressed(now)

    if state == SET_MINUTES or state == SET_SECONDS:
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
        if k0_pressed or push_pressed:
            alarm_outputs(False)
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
    alarm_outputs(False)
    saved = {"state": state, "set_minutes": set_minutes,
             "set_seconds": set_seconds, "remaining_ms": remaining_ms,
             "end_ticks": end_ticks}
    if state == RUNNING:
        saved["wake_at"] = end_ticks
    return saved
