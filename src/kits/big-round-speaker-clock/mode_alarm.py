# mode_alarm.py -- mode 3: set the alarm, and the screen it rings on.
#
# Showing the alarm:
#   UP          alarm on / off
#   DOWN        play the wake-up tone
#   hold MODE   set the alarm (tap MODE still goes to the next mode)
#
# Setting it -- the part being set is yellow, and MODE belongs to this
# mode until you are done, so a tap cannot switch modes by accident:
#   UP / DOWN   change it (hold to go faster)
#   tap MODE    next part: hour -> minute -> tone -> alarm on/off ->
#               hourly chime on/off -> done
#
# The alarm itself is checked by mode-template.py once a minute, whatever
# mode is showing. When the time comes it sets shared.ringing and switches
# here. Any button stops it; it gives up by itself after RING_MINUTES.
#
# The settings live in shared.py, so they survive switching modes. (They
# do not survive a power cut -- writing flash while the speaker plays makes
# it click; see sound.py.)
#
# Every mode has the same functions -- see mode-template.py.

import time

import config
import shared
from timerow import TimeRow, ampm
from watchparts import TextLine, SHORT, LONG

SET_COLOR = config.YELLOW
ON_COLOR = config.GREEN
OFF_COLOR = config.color565(150, 150, 150)
HINT_COLOR = config.color565(150, 150, 150)
RING_COLOR = config.RED
RING_MINUTES = 5
RING_EVERY_MS = 3000
FLASH_MS = 500

SIZE = (44, 82, 10) if config.TWELVE_HOUR else (40, 74, 10)
TITLE_Y = 52
HINT_Y = 76
DIGIT_TOP = 100
AMPM_Y = DIGIT_TOP + SIZE[1] + 6          # 188
STATE_Y = 212
TONE_Y = 252
CHIME_Y = 272

SHOWING, SET_HOUR, SET_MINUTE, SET_TONE, SET_ON, SET_CHIME = range(6)
HINTS = ("UP on/off  DOWN hear it", "UP+ DOWN-  MODE next",
         "UP+ DOWN-  MODE next", "UP/DOWN tone MODE next",
         "UP/DOWN  MODE next", "UP/DOWN  MODE done")


def start(display, up, down, saved):
    global _up, _down, row, title, hint, ampm_line, state_line, tone_line
    global chime_line, state, shown, last_ring, shown_flash
    _up = up
    _down = down
    display.fill(config.BLACK)
    small = config.SMALL_FONT
    big = config.BIG_FONT
    cx = config.CENTER_X
    title = TextLine(display, small, cx, TITLE_Y, 14, config.CYAN)
    hint = TextLine(display, small, cx, HINT_Y, 24, HINT_COLOR)
    row = TimeRow(display, SIZE, DIGIT_TOP)
    ampm_line = TextLine(display, small, cx, AMPM_Y, 2, config.WHITE)
    state_line = TextLine(display, big, cx, STATE_Y, 12, ON_COLOR)
    tone_line = TextLine(display, small, cx, TONE_Y, 26, config.WHITE)
    chime_line = TextLine(display, small, cx, CHIME_Y, 24, config.WHITE)
    state = SHOWING
    shown = None
    last_ring = None
    shown_flash = None


def ring_stop():
    shared.ringing = False
    shared.speaker.stop()
    global shown
    shown = None                       # back to the normal screen


def on_mode(kind):
    """Tap MODE: next part while setting. Hold MODE: start setting.
    Returns True when this mode used the press."""
    global state, shown
    if shared.ringing:
        ring_stop()
        return True
    if state != SHOWING:
        if kind == SHORT:
            state = state + 1 if state < SET_CHIME else SHOWING
            shown = None
        return True                    # never switch away in the middle
    if kind == LONG:
        state = SET_HOUR
        shown = None
        return True
    return False


def play_tone():
    shared.speaker.stop()
    shared.speaker.play(shared.TONES[shared.alarm_tone])


def update(now):
    global state, shown, last_ring, shown_flash
    up = _up.pressed(now, repeat=True)
    down = _down.pressed(now, repeat=True)

    if shared.ringing:
        if up or down or time.ticks_diff(
                now, shared.ring_started) > RING_MINUTES * 60000:
            ring_stop()
        else:
            show_ringing(now)
            return
    step = 1 if up else -1 if down else 0

    if state == SHOWING:
        if up:
            shared.alarm_on = not shared.alarm_on
            shared.speaker.beep(1320 if shared.alarm_on else 660)
            shown = None
        elif down:
            play_tone()
    elif step:
        if state == SET_HOUR:
            shared.alarm_hour = (shared.alarm_hour + step) % 24
        elif state == SET_MINUTE:
            shared.alarm_minute = (shared.alarm_minute + step) % 60
        elif state == SET_TONE:
            shared.alarm_tone = (shared.alarm_tone + step) % len(shared.TONES)
            play_tone()
        elif state == SET_ON:
            shared.alarm_on = not shared.alarm_on
        elif state == SET_CHIME:
            shared.chime_on = not shared.chime_on
        shown = None

    if shown is None:
        show_settings()
        shown = True


def show_settings():
    title.show("ALARM" if state == SHOWING else "SET ALARM",
               config.CYAN if state == SHOWING else SET_COLOR)
    hint.show(HINTS[state])
    hour_color = SET_COLOR if state == SET_HOUR else config.WHITE
    minute_color = SET_COLOR if state == SET_MINUTE else config.WHITE
    row.show(shared.alarm_hour, shared.alarm_minute,
             colors=(hour_color, minute_color))
    if config.TWELVE_HOUR:
        ampm_line.show(ampm(shared.alarm_hour), hour_color)
    color = SET_COLOR if state == SET_ON else (
        ON_COLOR if shared.alarm_on else OFF_COLOR)
    state_line.show("ALARM ON" if shared.alarm_on else "ALARM OFF", color)
    tone_line.show("tone: " + shared.TONES[shared.alarm_tone],
                   SET_COLOR if state == SET_TONE else config.WHITE)
    chime_line.show("hourly chime: " + ("on" if shared.chime_on else "off"),
                    SET_COLOR if state == SET_CHIME else HINT_COLOR)


def show_ringing(now):
    """Flash WAKE UP and the time, and play the tone every few seconds."""
    global last_ring, shown_flash, shown
    if last_ring is None or time.ticks_diff(now, last_ring) >= RING_EVERY_MS:
        last_ring = now
        play_tone()
    flash = time.ticks_diff(now, shared.ring_started) // FLASH_MS % 2 == 0
    if flash == shown_flash and shown == "ringing":
        return
    shown_flash = flash
    shown = "ringing"
    t = time.localtime()
    title.show("WAKE UP!", RING_COLOR)
    hint.show("any button: stop")
    color = RING_COLOR if flash else config.WHITE
    row.show(t[3], t[4], colors=(color, color))
    if config.TWELVE_HOUR:
        ampm_line.show(ampm(t[3]), color)
    state_line.show("WAKE UP!" if flash else "", RING_COLOR)
    tone_line.show("")
    chime_line.show("")


def stop():
    """Leave setting, and stop ringing, if the user switches away."""
    global state
    state = SHOWING
    if shared.ringing:
        ring_stop()
    return None
