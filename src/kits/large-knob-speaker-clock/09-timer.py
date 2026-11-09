# Lab 09: Countdown Timer
# Set a time with the knob, start it, and it counts down to zero. In the
# last ten seconds the digits turn red and the speaker ticks once a
# second; at zero, 00:00 flashes and the speaker beeps until you press a
# button or turn the knob. The ticks around the edge of the screen show
# how much time is left: all lit at the start, going out one by one, back
# toward the middle of the top edge.
#
#   K0    (GP11)      start / pause
#   PUSH  (GP10)      set: minutes -> seconds -> go!    (while paused: reset)
#   KNOB  (GP8, GP9)  while setting: change the yellow number
#
# PUSH is the knob itself: press it straight down. A line at the top
# always shows what the controls do right now. The PUSH that finishes
# setting the seconds also starts the timer -- there is no need to press
# K0 as well. (Set it to 00:00 and it waits in READY instead.)
#
# A TIMER IS A STATE MACHINE. What a control does depends on what the
# timer is doing: PUSH means "set the time" when the timer is ready,
# "next" while you set the minutes, "go" while you set the seconds, and
# "reset" while it is paused. The
# program keeps one variable, `state`, that says which of six states it
# is in, and every press and every turn is handled by asking "what state
# are we in?" first.
#
#                  PUSH                 PUSH: go!
#   SET_MINUTES --------> SET_SECONDS -----------+
#        ^                                       |
#        | PUSH                                  v
#      READY ------------- K0 -------------> RUNNING <---K0---> PAUSED
#       ^  ^                                     |                 |
#       |  |                       reaches 00:00 v                 |
#       |  +---- K0, PUSH, or a turn -------- DONE                 |
#       |                                                          |
#       +------------------------- PUSH ---------------------------+
#
# Turning the knob only matters in three states: it changes the number in
# the two SET states, and stops the alarm in DONE.
#
# It never counts down by subtracting a little each loop -- the loop's
# speed changes every time it draws something, and the errors would pile
# up. It works out when the timer will END, and each time around the
# loop asks how far away that moment is.
#
# The speaker makes its sound on the Pico's second core (see sound.py),
# so the beeps stay smooth while this loop is busy drawing.

NAME = "09-timer.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

import config
import sound
from watchparts import Digit, TickFrame, TextLine, Button, Knob, DIGITS, BLANK

BLACK = config.BLACK
DIGIT_COLOR = config.WHITE
SETTING_COLOR = config.YELLOW     # the field being set
WARNING_COLOR = config.RED        # the last WARNING_MS, and the alarm
GHOST = config.color565(24, 24, 30)
ACCENT = config.CYAN
TICK_OFF = config.color565(40, 40, 40)
HINT_COLOR = config.color565(150, 150, 150)
TITLE_COLOR = config.CYAN
SMALL = config.SMALL_FONT
BIG = config.BIG_FONT

START_MINUTES = 5
START_SECONDS = 0
WARNING_MS = 10_000     # the digits turn red for the last 10 seconds
FLASH_MS = 500          # how fast the alarm flashes
TICK_IN_WARNING = True  # a tick from the speaker each of the last seconds

SET_MINUTES, SET_SECONDS, READY, RUNNING, PAUSED, DONE = range(6)
STATE_NAMES = ("SET MINUTES", "SET SECONDS", "READY", "RUNNING", "PAUSED",
               "TIME'S UP!")
STATE_COLORS = (SETTING_COLOR, SETTING_COLOR, HINT_COLOR, config.GREEN,
                config.YELLOW, WARNING_COLOR)
HINTS = ("KNOB +/-   PUSH next", "KNOB +/-   PUSH go",
         "K0 start   PUSH set", "K0 pause", "K0 go   PUSH reset",
         "any control: stop")

# ---------------------------------------------------------------------
# Layout: MM:SS in 56 x 104 digits, centered, with a title, a hint and
# the state above them and a note below. The ticks use the outer 10 pixels of the
# screen, so everything else stays clear of them. A digit's height must
# be 3 x its thickness plus an even number.
# ---------------------------------------------------------------------
DIGIT_W, DIGIT_H, DIGIT_T = 56, 104, 10
PAIR_GAP = 10
COLON_GAP = 12
_row = 4 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T
_x = (config.WIDTH - _row) // 2
DIGIT_X = (_x,
           _x + DIGIT_W + PAIR_GAP,
           _x + 2 * DIGIT_W + PAIR_GAP + 2 * COLON_GAP + DIGIT_T,
           _x + 3 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T)
COLON_X = _x + 2 * DIGIT_W + PAIR_GAP + COLON_GAP

TITLE_Y = 14            # "TIMER", so you know what this is
HINT_Y = 30
STATE_Y = 48
DIGIT_TOP = 86
NOTE_Y = DIGIT_TOP + DIGIT_H + 6         # 196
COLON_Y = (DIGIT_TOP + DIGIT_H // 3 - DIGIT_T // 2,
           DIGIT_TOP + 2 * DIGIT_H // 3 - DIGIT_T // 2)

# The frame of ticks: short ticks 5 px deep, every fifth one 10 px.
TICK_DEPTH, TICK_DEPTH_FIVE, TICK_LENGTH = 5, 10, 8

# ---------------------------------------------------------------------
# Set up the screen, the controls, and the alarm outputs
# ---------------------------------------------------------------------
display = config.init_display()
display.fill(BLACK)
config.centered_text(display, SMALL, "TIMER", TITLE_Y, TITLE_COLOR)

digits = [Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                DIGIT_COLOR, GHOST) for x in DIGIT_X]
hint = TextLine(display, SMALL, config.CENTER_X, HINT_Y, 20, HINT_COLOR)
status = TextLine(display, BIG, config.CENTER_X, STATE_Y, 11, HINT_COLOR)
note = TextLine(display, SMALL, config.CENTER_X, NOTE_Y, 16, HINT_COLOR)
frame = TickFrame(display, config.WIDTH, config.HEIGHT, TICK_DEPTH,
                  TICK_DEPTH_FIVE, TICK_LENGTH)

a, b, push, k0 = config.init_controls()
k0_button = Button(k0)
push_button = Button(push)
knob = Knob(a, b, config.ENCODER_STEPS_PER_CLICK)
led = Pin(config.LED_PIN, Pin.OUT)
led.value(0)            # the LED may still be on from another program
sound.init()

for y in COLON_Y:
    display.fill_rect(COLON_X, y, DIGIT_T, DIGIT_T, DIGIT_COLOR)


def alarm_outputs(on):
    """The LED follows the flashing digits. Each time they light up, four
    quick beeps start -- they last about as long as one flash."""
    led.value(1 if on else 0)
    if on:
        for _ in range(4):
            sound.tone(2093, 60, wave=sound.SQUARE, level=0.6, attack=2,
                       release=5)
            sound.rest(40)


def silence():
    """Stop the alarm: LED off, and drop any beeps still queued."""
    led.value(0)
    sound.stop()


def tick():
    """One short tick, for each of the last WARNING_MS seconds."""
    sound.tone(1000, 15, wave=sound.SQUARE, level=0.3, attack=1, release=5)


def start_beep():
    """A short rising pair of notes: the timer has started."""
    sound.tone(1320, 40, wave=sound.SQUARE, level=0.3, attack=2, release=8)
    sound.tone(1760, 60, wave=sound.SQUARE, level=0.3, attack=2, release=8)


def click():
    """A tiny tick for each click of the knob while setting."""
    sound.tone(1800, 12, wave=sound.SQUARE, level=0.25, attack=1, release=4)


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
ticked_second = None    # the last warning second that got its tick


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
        if clicks:
            if state == SET_MINUTES:
                set_minutes = (set_minutes + clicks) % 100
            else:
                set_seconds = (set_seconds + clicks) % 60
            click()
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
                tick()
                ticked_second = second
    elif state == PAUSED:
        if k0_pressed:
            end_ticks = time.ticks_add(now, remaining_ms)
            state = RUNNING
        elif push_pressed:
            remaining_ms = total_ms()
            state = READY
    elif state == DONE:
        if k0_pressed or push_pressed or clicks:
            silence()
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
        if state != RUNNING:
            ticked_second = None
        shown_state = state

    time.sleep_ms(10)
