# mode_timer.py -- the countdown timer of lab 11, as a mode for
# 12-main-template.py. Lab 11 explains the state machine behind it.
#
# The MODE button belongs to the watch here -- a short press switches
# modes -- so the timer is set with a LONG press instead:
#
#   hold MODE (1 s)   set the time: minutes, then seconds
#   MODE, while setting   next field / done
#   UP    start / pause   (while setting: add one)
#   DOWN  reset, only while paused   (while setting: take one away)
#
# While the time is being set, or the alarm is going off, the timer keeps
# the MODE button for itself (on_mode() returns True), so a press there
# cannot accidentally switch modes.
#
# Switching away does not stop a running timer. stop() hands back when it
# will end as "wake_at", and 12-main-template.py switches back to this
# mode the moment that time comes, so the alarm goes off whatever mode
# the watch is showing.
#
# Every mode has the same four functions -- see 12-main-template.py.

import time
from machine import Pin

import config
from watchparts import Digit, TickRing, TextLine, DIGITS, BLANK, SHORT, LONG

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
HINTS = ("UP+  DOWN-  MODE next", "UP+  DOWN-  MODE done",
         "UP start  hold MODE set", "UP pause", "UP go  DOWN reset",
         "any button: stop")

# Layout, the same as lab 11.
DIGIT_W, DIGIT_H, DIGIT_T = 58, 114, 12
PAIR_GAP = 10
COLON_GAP = 12
DIGIT_TOP = config.CENTER_Y - DIGIT_H // 2
TITLE_Y = 50
HINT_Y = 76
STATE_Y = 100
NOTE_Y = DIGIT_TOP + DIGIT_H + 16


def start(display, up, down, saved):
    global _up, _down, digits, hint, status, note, ring, led, buzzer
    global state, set_minutes, set_seconds, remaining_ms, end_ticks, done_at
    global shown_state, shown_flash
    _up = up
    _down = down
    display.fill(config.BLACK)

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

    TextLine(display, SMALL, config.CENTER_X, TITLE_Y, 5,
             HINT_COLOR).show("TIMER")
    hint = TextLine(display, SMALL, config.CENTER_X, HINT_Y, 23, HINT_COLOR)
    status = TextLine(display, SMALL, config.CENTER_X, STATE_Y, 11, HINT_COLOR)
    note = TextLine(display, SMALL, config.CENTER_X, NOTE_Y, 18, HINT_COLOR)
    ring = TickRing(display, config.CENTER_X, config.CENTER_Y,
                    config.SAFE_RADIUS - 2, config.SAFE_RADIUS - 10,
                    config.SAFE_RADIUS - 16)

    led = Pin(config.LED_PIN, Pin.OUT)
    buzzer = None
    if config.BUZZER_PIN is not None:
        from machine import PWM
        buzzer = PWM(Pin(config.BUZZER_PIN))
        buzzer.freq(2000)
        buzzer.duty_u16(0)

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


def on_mode(kind):
    """MODE was pressed (SHORT or LONG). Return True if the timer used it;
    False lets a short press switch modes."""
    global state, remaining_ms
    if state == DONE:                          # any button stops the alarm
        alarm_outputs(False)
        remaining_ms = total_ms()
        state = READY
        return True
    if state == SET_MINUTES or state == SET_SECONDS:
        if kind == SHORT:
            if state == SET_MINUTES:
                state = SET_SECONDS
            else:
                state = READY
                remaining_ms = total_ms()
        return True                            # never leave in the middle
    if kind == LONG and (state == READY or state == PAUSED):
        state = SET_MINUTES
        return True
    return kind == LONG                        # a long press never switches


def show_digits(minutes, seconds, colors):
    values = (minutes // 10, minutes % 10, seconds // 10, seconds % 10)
    for i in range(4):
        digits[i].show(DIGITS[values[i]], colors[i // 2])


def show_ring(lit):
    for second in range(60):
        ring.paint(second, ACCENT if second < lit else TICK_OFF)


def update(now):
    global state, set_minutes, set_seconds, remaining_ms, end_ticks, done_at
    global shown_state, shown_flash
    up = _up.pressed(now, repeat=True)
    down = _down.pressed(now, repeat=True)

    if state == SET_MINUTES or state == SET_SECONDS:
        step = 1 if up else -1 if down else 0
        if state == SET_MINUTES:
            set_minutes = (set_minutes + step) % 100
        else:
            set_seconds = (set_seconds + step) % 60
    elif state == READY:
        if up and total_ms() > 0:
            end_ticks = time.ticks_add(now, remaining_ms)
            state = RUNNING
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
        if up or down:
            alarm_outputs(False)
            remaining_ms = total_ms()
            state = READY

    if state == SET_MINUTES or state == SET_SECONDS:
        show_digits(set_minutes, set_seconds,
                    (SETTING_COLOR if state == SET_MINUTES else DIGIT_COLOR,
                     SETTING_COLOR if state == SET_SECONDS else DIGIT_COLOR))
        show_ring(60 if total_ms() > 0 else 0)
    elif state == DONE:
        flash = (time.ticks_diff(now, done_at) // FLASH_MS) % 2 == 0
        if flash != shown_flash:
            for digit in digits:
                digit.show(DIGITS[0] if flash else BLANK, WARNING_COLOR)
            alarm_outputs(flash)
            shown_flash = flash
        show_ring(0)
    else:
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


def stop():
    """Keep the timer's state. A running timer also says when it will
    reach zero, so the watch can come back here for the alarm."""
    alarm_outputs(False)
    saved = {"state": state, "set_minutes": set_minutes,
             "set_seconds": set_seconds, "remaining_ms": remaining_ms,
             "end_ticks": end_ticks}
    if state == RUNNING:
        saved["wake_at"] = end_ticks
    return saved
