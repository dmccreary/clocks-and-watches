# Lab 08: Alarm Clock
# Set an alarm time with the knob, turn the alarm on, and when that time
# comes the speaker plays a wake-up tone, over and over, until you stop
# it -- or press snooze for five more minutes.
#
#   K0    (GP11)      alarm on / off        (ringing: stop)
#   PUSH  (GP10)      set: hour -> minute -> tone -> done
#                                           (ringing: snooze)
#   KNOB  (GP8, GP9)  while setting: change the yellow part
#
# Changing the hour or the minute turns the alarm ON by itself -- if you
# took the trouble to set a time, you want to be woken at it. K0 still
# turns it off afterwards. Only changing the tone leaves it as it was.
#
# PUSH is the knob itself: press it straight down. The top line is the
# time now, the big digits are the ALARM time, and the line under the
# digits says what the alarm is doing.
#
# AN ALARM CLOCK IS A STATE MACHINE, like the timer in lab 09. The
# program keeps one variable, `state`, and every press and turn is
# handled by asking "what state are we in?" first:
#
#              PUSH             PUSH               PUSH
#   SHOWING -------> SET_HOUR -------> SET_MINUTE -------> SET_TONE
#    ^  |  ^                                                  |
#    |  |  +-------------------- PUSH (done) -----------------+
#    |  |
#    |  |   the alarm time comes, if the alarm is on
#    |  +------------------------------------------> RINGING
#    |                                                |  |  ^
#    +---- K0, a turn, or RING_MINUTES unanswered ----+  |  |
#    |                                                   |  | SNOOZE_MINUTES
#    |                                              PUSH |  | later
#    |                                                   v  |
#    +------------ K0: cancel the snooze ------------- SNOOZING
#
# WHEN DOES IT RING? Once a minute, the moment the minute changes, the
# program asks: is the alarm on, and is it now exactly the alarm time? So
# set the alarm at least one minute ahead -- an alarm set for the minute
# that is already here rings tomorrow.
#
# The alarm time is forgotten when the Pico loses power. Edit ALARM_HOUR
# and ALARM_MINUTE below to change where it starts.
#
# Where does the time come from? From the Pico's own clock: Thonny sets
# it every time it connects, and lab 06 sets it over WiFi.

NAME = "08-alarm.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
from machine import Pin

import config
import sound
from watchparts import Digit, TextLine, Button, Knob, DIGITS, BLANK

TWELVE_HOUR = True
ALARM_HOUR = 7          # the alarm time at power-up, on a 24-hour clock
ALARM_MINUTE = 0
ALARM_ON = False
SNOOZE_MINUTES = 5
RING_MINUTES = 5        # stop by itself if nobody comes
RING_GAP_MS = 700       # the pause between one wake-up tone and the next
FLASH_MS = 500

# Wake-up tones, from sfx.py. Turning the knob in SET_TONE plays each one.
TONES = ("reminder", "doorbell", "bird", "chime", "magic", "powerup",
         "siren")

BLACK = config.BLACK
DIGIT_COLOR = config.WHITE
OFF_COLOR = config.color565(110, 110, 110)   # the digits while the alarm is off
SETTING_COLOR = config.YELLOW
RING_COLOR = config.RED
ON_COLOR = config.GREEN
GHOST = config.color565(24, 24, 30)
HINT_COLOR = config.color565(150, 150, 150)
NOW_COLOR = config.CYAN
SMALL = config.SMALL_FONT
BIG = config.BIG_FONT

SHOWING, SET_HOUR, SET_MINUTE, SET_TONE, RINGING, SNOOZING = range(6)
# A line of the small font holds 40 characters.
HINTS = ("K0 alarm on/off   PUSH set",
         "KNOB hour +/-   PUSH next",
         "KNOB minute +/-   PUSH next",
         "KNOB pick a tone   PUSH done",
         "K0 stop   PUSH snooze",
         "K0 cancel the snooze")

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

# ---------------------------------------------------------------------
# Layout: the time now in the big font, a hint, the alarm time in 60 x
# 100 segment digits, AM/PM, the alarm's state in the big font, and the
# tone at the bottom. A digit's height must be 3 x its thickness plus an
# even number.
# ---------------------------------------------------------------------
DIGIT_W, DIGIT_H, DIGIT_T = 60, 100, 10
PAIR_GAP = 10
COLON_GAP = 12

NOW_Y = 4
HINT_Y = 42
DIGIT_TOP = 64
AMPM_Y = DIGIT_TOP + DIGIT_H + 2         # 166
STATUS_Y = AMPM_Y + SMALL.HEIGHT + 4     # 186
TONE_Y = STATUS_Y + BIG.HEIGHT + 4       # 222

# One row, centered: on a 12-hour clock the first digit is only ever 1
# or blank, so it is a half digit -- just its right-hand column.
_first = DIGIT_T if TWELVE_HOUR else DIGIT_W
_row = _first + 3 * DIGIT_W + 2 * PAIR_GAP + 2 * COLON_GAP + DIGIT_T
_x = (config.WIDTH - _row) // 2
DIGIT_X = (_x,
           _x + _first + PAIR_GAP,
           _x + _first + PAIR_GAP + DIGIT_W + 2 * COLON_GAP + DIGIT_T,
           _x + _first + 2 * PAIR_GAP + 2 * DIGIT_W + 2 * COLON_GAP
           + DIGIT_T)
COLON_X = _x + _first + PAIR_GAP + DIGIT_W + COLON_GAP
COLON_Y = (DIGIT_TOP + DIGIT_H // 3 - DIGIT_T // 2,
           DIGIT_TOP + 2 * DIGIT_H // 3 - DIGIT_T // 2)

# ---------------------------------------------------------------------
# Set up the screen, the controls, the LED and the speaker
# ---------------------------------------------------------------------
display = config.init_display()
display.fill(BLACK)

digits = [Digit(display, x, DIGIT_TOP, DIGIT_W, DIGIT_H, DIGIT_T,
                DIGIT_COLOR, GHOST, half=(TWELVE_HOUR and i == 0))
          for i, x in enumerate(DIGIT_X)]
now_line = TextLine(display, BIG, config.CENTER_X, NOW_Y, 15, NOW_COLOR)
hint = TextLine(display, SMALL, config.CENTER_X, HINT_Y, 34, HINT_COLOR)
ampm_line = TextLine(display, SMALL, config.CENTER_X, AMPM_Y, 2, DIGIT_COLOR)
status = TextLine(display, BIG, config.CENTER_X, STATUS_Y, 14, ON_COLOR)
tone_line = TextLine(display, SMALL, config.CENTER_X, TONE_Y, 20, HINT_COLOR)

a, b, push, k0 = config.init_controls()
k0_button = Button(k0)
push_button = Button(push)
knob = Knob(a, b, config.ENCODER_STEPS_PER_CLICK)
led = Pin(config.LED_PIN, Pin.OUT)
led.value(0)            # the LED may still be on from another program
sound.init()

if time.localtime()[0] < 2025:
    print("The Pico's clock has not been set. Connect with Thonny, which")
    print("sets it from your computer, or run lab 06 to set it over WiFi.")

# ---------------------------------------------------------------------
# The alarm
# ---------------------------------------------------------------------
state = SHOWING
alarm_hour = ALARM_HOUR
alarm_minute = ALARM_MINUTE
alarm_on = ALARM_ON
tone_index = 0
ring_started = 0        # ticks_ms() when the ringing began
last_sound = 0          # ticks_ms() when the last wake-up tone finished
snooze_until = 0        # ticks_ms() when a snooze is over

# Start with this minute already checked, so an alarm set for right now
# does not go off the moment the program starts.
_t = time.localtime()
checked_minute = (_t[3], _t[4])
shown_colon = None


def twelve(hour):
    """13 -> 1, 0 -> 12: the hour on a 12-hour clock."""
    return (hour % 12 or 12) if TWELVE_HOUR else hour


def ampm(hour):
    return "AM" if hour < 12 else "PM"


def beep(freq, ms):
    sound.tone(freq, ms, wave=sound.SQUARE, level=0.3, attack=2, release=8)


def click():
    """A tiny tick for each click of the knob while setting."""
    sound.tone(1800, 12, wave=sound.SQUARE, level=0.25, attack=1, release=4)


def play_tone():
    """Play the chosen wake-up tone, cutting off whatever is playing."""
    sound.stop()
    sound.play(TONES[tone_index])


def start_ringing(now):
    global state, ring_started, last_sound
    state = RINGING
    ring_started = now
    last_sound = time.ticks_add(now, -RING_GAP_MS)   # ring straight away
    print("Alarm! {}:{:02d}".format(twelve(alarm_hour), alarm_minute))


def keep_ringing(now):
    """Play the tone again whenever the last one has finished and the
    pause after it is over. The LED flashes with the digits."""
    global last_sound
    if sound.busy():
        last_sound = now
    elif time.ticks_diff(now, last_sound) >= RING_GAP_MS:
        play_tone()
        last_sound = now
    flash = time.ticks_diff(now, ring_started) // FLASH_MS % 2 == 0
    led.value(1 if flash else 0)
    return flash


def stop_ringing():
    led.value(0)
    sound.stop()


def show_alarm_time(colors):
    """The alarm time in the big digits. colors is (hour color, minute
    color)."""
    global shown_colon
    hour_color, minute_color = colors
    hour = twelve(alarm_hour)
    tens = hour // 10
    first = DIGITS[tens] if (tens or not TWELVE_HOUR) else BLANK
    digits[0].show(first, hour_color)
    digits[1].show(DIGITS[hour % 10], hour_color)
    digits[2].show(DIGITS[alarm_minute // 10], minute_color)
    digits[3].show(DIGITS[alarm_minute % 10], minute_color)
    if hour_color != shown_colon:
        for y in COLON_Y:
            display.fill_rect(COLON_X, y, DIGIT_T, DIGIT_T, hour_color)
        shown_colon = hour_color
    if TWELVE_HOUR:
        ampm_line.show(ampm(alarm_hour), hour_color)


while True:
    now = time.ticks_ms()
    k0_pressed = k0_button.pressed(now)
    push_pressed = push_button.pressed(now)
    # Clicks since the last pass, positive for clockwise. Asking empties
    # the count, so a turn while the alarm is just showing is ignored.
    clicks = knob.turned()
    year, month, day, hour, minute, second, weekday, _ = time.localtime()

    # ---- is it time? ---------------------------------------------------
    if (hour, minute) != checked_minute:
        checked_minute = (hour, minute)
        if (alarm_on and state == SHOWING
                and (hour, minute) == (alarm_hour, alarm_minute)):
            start_ringing(now)
    if state == SNOOZING and time.ticks_diff(now, snooze_until) >= 0:
        start_ringing(now)

    # ---- what the controls do, in each state ---------------------------
    if state == SHOWING:
        if k0_pressed:
            alarm_on = not alarm_on
            if alarm_on:
                beep(1320, 60)
            else:
                beep(660, 80)
        elif push_pressed:
            state = SET_HOUR
    elif state == SET_HOUR or state == SET_MINUTE or state == SET_TONE:
        if clicks:
            if state == SET_HOUR:
                alarm_hour = (alarm_hour + clicks) % 24
                alarm_on = True          # a new alarm time turns it on
                click()
            elif state == SET_MINUTE:
                alarm_minute = (alarm_minute + clicks) % 60
                alarm_on = True
                click()
            else:
                tone_index = (tone_index + clicks) % len(TONES)
                play_tone()
        if push_pressed:
            if state == SET_TONE:
                state = SHOWING
                sound.stop()
                beep(1320, 60)
            else:
                state += 1
    elif state == RINGING:
        if k0_pressed or clicks:
            stop_ringing()
            state = SHOWING
        elif push_pressed:
            stop_ringing()
            snooze_until = time.ticks_add(now, SNOOZE_MINUTES * 60_000)
            state = SNOOZING
        elif time.ticks_diff(now, ring_started) >= RING_MINUTES * 60_000:
            stop_ringing()
            state = SHOWING
    elif state == SNOOZING:
        if k0_pressed:
            beep(660, 80)
            state = SHOWING

    # ---- what the screen shows -----------------------------------------
    # Every show() below repaints only what changed since last time, so
    # it is fine to call them all on every pass.
    if year < 2025:
        now_line.show("clock not set", RING_COLOR)
    else:
        now_line.show("{} {:2d}:{:02d}:{:02d}{}".format(
            DAYS[weekday], twelve(hour), minute, second,
            " " + ampm(hour) if TWELVE_HOUR else ""))
    hint.show(HINTS[state])

    if state == RINGING:
        flash = keep_ringing(now)
        color = RING_COLOR if flash else DIGIT_COLOR
        show_alarm_time((color, color))
        status.show("WAKE UP!" if flash else "", RING_COLOR)
    elif state == SNOOZING:
        left = max(0, time.ticks_diff(snooze_until, now) + 999) // 1000
        show_alarm_time((DIGIT_COLOR, DIGIT_COLOR))
        status.show("SNOOZE {}:{:02d}".format(left // 60, left % 60),
                    SETTING_COLOR)
    elif state == SHOWING:
        color = DIGIT_COLOR if alarm_on else OFF_COLOR
        show_alarm_time((color, color))
        status.show("ALARM ON" if alarm_on else "ALARM OFF",
                    ON_COLOR if alarm_on else OFF_COLOR)
    else:
        show_alarm_time((SETTING_COLOR if state == SET_HOUR else DIGIT_COLOR,
                         SETTING_COLOR if state == SET_MINUTE
                         else DIGIT_COLOR))
        # While setting, the line still says ON or OFF, so you can see
        # it switch on as soon as you change the time.
        status.show("ALARM ON" if alarm_on else "ALARM OFF",
                    ON_COLOR if alarm_on else OFF_COLOR)

    tone_line.show("tone: " + TONES[tone_index],
                   SETTING_COLOR if state == SET_TONE else HINT_COLOR)

    time.sleep_ms(10)
