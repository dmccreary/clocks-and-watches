# Lab 04: Hear the Range
# A tone that slides from the lowest pitch you could ever hear up to the
# highest, while the screen shows its frequency. You press UP twice:
#
#   1st press   when you first HEAR the tone (the low end)
#   2nd press   when it DISAPPEARS (the high end)
#
# Then the screen tells you the range you heard. Frequency is measured in
# hertz (Hz): how many times a second the speaker cone moves back and
# forth. A piano goes from 27 Hz to 4,186 Hz. Young ears can hear from
# about 20 Hz up to about 20,000 Hz.
#
# TWO LIMITS, AND THEY ARE NOT THE SAME
#   * The speaker. A speaker this small cannot move enough air to make deep
#     bass, so the low end is silent (or just clicks) up to somewhere in the
#     low hundreds of hertz. That tells you about the SPEAKER.
#   * Your ears. The high end is where YOUR hearing stops. Children often
#     hear nearly 20,000 Hz. Most adults stop between about 15,000 and
#     17,000, and it keeps falling with age. Try it on your teacher.
#
# The sweep goes up in quarter-octaves. An octave is a doubling of the
# frequency (220 Hz, 440 Hz, 880 Hz sound like "the same note" higher up),
# so the sweep covers 10 octaves from 20 Hz to 20,480 Hz. Equal steps in
# octaves sound like equal steps in pitch, which is why the bar below the
# number is spaced by octaves, not by hertz.
#
# Turn the volume down before you start. The top of the sweep is piercing.

NAME = "04-hear-the-range.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time

import config
import sound
from watchparts import Button

RATE = 44100                 # 44,100 samples a second can make up to 22,050 Hz
LOW_HZ = 20
STEPS = 4                    # slides per octave
OCTAVES = 10
SEGMENT_MS = 400
TOTAL_SEGMENTS = STEPS * OCTAVES
TOTAL_MS = TOTAL_SEGMENTS * SEGMENT_MS
REACTION_MS = 250            # it takes a moment to press a button
VOLUME = min(config.VOLUME, 30)

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
TRACK = config.color565(70, 70, 70)
BAR_X, BAR_W, BAR_Y = 40, 280, 196

display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]


def put(text, y, font=SMALL, color=config.WHITE, width=34):
    config.centered_text(display, font, text.center(width), y, color)


def freq_at(ms):
    """The frequency being made ms milliseconds into the sweep."""
    ms = max(0, min(ms, TOTAL_MS - 1))
    k = ms // SEGMENT_MS
    f0 = LOW_HZ * 2 ** (k / STEPS)
    f1 = LOW_HZ * 2 ** ((k + 1) / STEPS)
    return f0 + (f1 - f0) * (ms % SEGMENT_MS) / SEGMENT_MS


def bar_x(freq):
    """Where along the bar a frequency goes: evenly by octave."""
    octaves = math.log(max(freq, LOW_HZ) / LOW_HZ) / math.log(2)
    return BAR_X + int(BAR_W * octaves / OCTAVES)


def hz_text(freq):
    return "{:,} Hz".format(int(freq))


def piano_text(freq):
    if freq < 27.5:
        return "below the piano!"
    if freq > 4186:
        return "above the piano!"
    return "nearest note: " + sound.note_name(freq)


def draw_frame():
    """The parts of the screen that never change during a sweep."""
    display.fill(config.BLACK)
    put("HEAR THE RANGE", 44, SMALL, config.CYAN, 26)
    display.fill_rect(BAR_X, BAR_Y + 10, BAR_W, 4, TRACK)
    for octave in range(OCTAVES + 1):          # a tick for every doubling
        x = BAR_X + BAR_W * octave // OCTAVES
        display.fill_rect(x, BAR_Y + 4, 2, 16, TRACK)
    display.text(SMALL, "20 Hz", BAR_X - 8, 222, DIM, config.BLACK)
    display.text(SMALL, "20,000", BAR_X + BAR_W - 40, 222, DIM, config.BLACK)


def intro():
    display.fill(config.BLACK)
    put("HEAR THE RANGE", 44, SMALL, config.CYAN, 26)
    put("A tone will slide from", 100, SMALL)
    put("deep and low to high", 120, SMALL)
    put("and squeaky.", 140, SMALL)
    put("Press UP when you first hear it,", 176, SMALL, config.YELLOW)
    put("and again when it disappears.", 196, SMALL, config.YELLOW)
    put("Turn the volume down first!", 232, SMALL, config.RED)
    put("UP: start", 270, SMALL, DIM)


def wait_for_up():
    while not up_button.pressed(time.ticks_ms()):
        time.sleep_ms(10)


def sweep():
    """Play the sweep and run the screen. Returns the two frequencies the
    student marked (None for one they did not mark)."""
    sound.init(rate=RATE, ibuf=16384, volume=VOLUME)
    for k in range(TOTAL_SEGMENTS):
        sound.tone(LOW_HZ * 2 ** (k / STEPS), SEGMENT_MS,
                   to=LOW_HZ * 2 ** ((k + 1) / STEPS), level=0.8,
                   attack=0 if k else 20, release=0 if k < TOTAL_SEGMENTS - 1
                   else 40, link=k > 0)
    draw_frame()
    put("Press UP when you hear it", 262, SMALL, config.YELLOW)
    time.sleep_ms(sound.latency_ms())          # line the screen up with the ears

    marks = [None, None]
    marker_x = None
    started = time.ticks_ms()
    last_text = None
    while True:
        now = time.ticks_ms()
        elapsed = time.ticks_diff(now, started)
        if elapsed >= TOTAL_MS:
            break
        freq = freq_at(elapsed)
        text = hz_text(freq)
        if text != last_text:
            put(text, 96, BIG, config.WHITE, 16)
            put(piano_text(freq), 138, SMALL, DIM, 26)
            x = bar_x(freq)
            if marker_x is not None:
                # Erase the old marker, then put back the bar and any
                # octave tick it was covering.
                display.fill_rect(marker_x - 3, BAR_Y, 7, 24, config.BLACK)
                display.fill_rect(marker_x - 3, BAR_Y + 10, 7, 4, TRACK)
                for octave in range(OCTAVES + 1):
                    tx = BAR_X + BAR_W * octave // OCTAVES
                    if marker_x - 3 <= tx <= marker_x + 3:
                        display.fill_rect(tx, BAR_Y + 4, 2, 16, TRACK)
            display.fill_rect(x - 3, BAR_Y, 7, 24, config.YELLOW)
            marker_x = x
            last_text = text
        if up_button.pressed(now):
            heard = freq_at(elapsed - REACTION_MS)
            if marks[0] is None:
                marks[0] = heard
                put("Press UP when it disappears", 262, SMALL, config.YELLOW)
            elif marks[1] is None:
                marks[1] = heard
                put("Marked! Listening on ...", 262, SMALL, config.GREEN)
        time.sleep_ms(30)
    sound.wait()
    sound.deinit()
    return marks


def result(low, high):
    display.fill(config.BLACK)
    put("YOUR RANGE", 44, SMALL, config.CYAN, 26)
    if low is None:
        put("You never pressed UP.", 120, SMALL)
        put("Did you hear it?", 140, SMALL)
    else:
        put("first heard at", 88, SMALL, DIM)
        put(hz_text(low), 110, BIG, config.GREEN, 16)
        if high is None:
            put("and it was still", 164, SMALL, DIM)
            put("audible at the end!", 184, SMALL, DIM)
        else:
            put("stopped hearing at", 158, SMALL, DIM)
            put(hz_text(high), 180, BIG, config.YELLOW, 16)
    put("A small speaker can't make deep bass.", 232, SMALL, DIM)
    put("Most adults stop near 15,000-17,000.", 252, SMALL, DIM)
    put("UP: again", 284, SMALL, DIM)
    print("heard from {} to {} Hz".format(
        None if low is None else round(low),
        None if high is None else round(high)))


try:
    while True:
        intro()
        wait_for_up()
        low, high = sweep()
        result(low, high)
        wait_for_up()
finally:
    sound.deinit()

# Try This
#   1. Find the lowest frequency where YOUR speaker makes a clear tone, not
#      just clicking. Is it above 100 Hz? 300? Why can't a speaker this
#      small go lower?
#   2. Ask a parent and a friend to do the same. Who hears the highest?
#   3. Change STEPS to 12. Now the sweep moves in single notes of the
#      piano (12 notes to an octave) and the pitch rises more smoothly.
#   4. Change OCTAVES to 5 and LOW_HZ to 500. This zooms in on the range
#      where speech and most music live.
