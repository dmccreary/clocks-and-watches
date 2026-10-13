# Lab 06: Sound Effects Gallery
# Twenty-one sounds, and not one of them is a recording. Each is a short
# list of notes in sfx.py, and the Pico makes them from scratch. Browse
# them, play them, and see the recipe for each on the screen.
#
#   UP     next sound
#   DOWN   previous sound
#   MODE   play it
#
# THE RECIPES
# Every note in sfx.py is six numbers: (start Hz, end Hz, milliseconds,
# wave, loudness, fade-out). The pitch slides from the start frequency to
# the end frequency. Look at the screen while you listen to a few:
#
#   laser      2200 -> 180 Hz, a saw wave        a fast slide DOWN
#   jump       250 -> 750 Hz, a square wave      a short slide UP
#   explosion  noise, with a long fade-out        no pitch at all
#   coin       two square-wave notes, the second one held and fading
#   siren      a triangle wave sliding up and down, three times
#
# Almost every sound you have ever heard in a video game is some of these
# ingredients, mixed differently.

NAME = "06-sound-effects.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import sfx
import sound
from watchparts import Button

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)

NAMES = sfx.NAMES
WAVES = ("sine", "square", "triangle", "saw", "noise")

display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]
sound.init(rate=16000, ibuf=4096)
sound.volume(config.VOLUME)


def put(text, y, font=SMALL, color=config.WHITE, width=34):
    config.centered_text(display, font, text.center(width), y, color)


def recipe(name):
    """Describe a sound's first note in words, and how many there are."""
    steps = sfx.EFFECTS[name]
    f0, f1, ms, wave, level, fade = steps[0]
    if wave == sfx.NOISE:
        first = "noise"
    elif f0 == 0:
        first = "a rest"
    elif f0 == f1:
        first = "{} Hz {}".format(f0, WAVES[wave])
    else:
        first = "{}->{} Hz {}".format(f0, f1, WAVES[wave])
    return first, len(steps), sum(step[2] for step in steps)


def show(index):
    name = NAMES[index]
    first, count, total_ms = recipe(name)
    put("SOUND EFFECTS", 44, SMALL, config.CYAN, 26)
    put(name, 92, BIG, config.YELLOW, 14)
    put("{} of {}".format(index + 1, len(NAMES)), 134, SMALL, DIM, 20)
    put("{} note{}, {} ms".format(count, "" if count == 1 else "s",
                                 total_ms), 166, SMALL, config.WHITE, 30)
    put("first: " + first, 188, SMALL, config.WHITE, 34)
    status(False)
    put("UP/DOWN: browse  MODE: play", 284, SMALL, DIM, 30)


def status(playing):
    if playing:
        put("PLAYING", 226, BIG, config.GREEN, 12)
    else:
        put("MODE: play", 226, BIG, DIM, 12)


display.fill(config.BLACK)
index = 0
show(index)
was_playing = False
try:
    while True:
        now = time.ticks_ms()
        if up_button.pressed(now) or down_button.pressed(now):
            step = 1 if up_button.held else -1
            sound.stop()
            index = (index + step) % len(NAMES)
            show(index)
            was_playing = False
        elif mode_button.pressed(now):
            sound.stop()
            sound.play(NAMES[index])
        playing = sound.busy()
        if playing != was_playing:
            status(playing)
            was_playing = playing
        time.sleep_ms(10)
finally:
    sound.deinit()

# Try This
#   1. Open sfx.py and find "laser". Change 2200 to 3000. Upload it, and
#      play the laser again. What changed?
#   2. Make your own sound: add  "zap": [(1500, 100, 150, SAW, 0.5, 20)],
#      to EFFECTS, and "zap" to NAMES. Then try a square wave (SQUARE)
#      instead of SAW.
#   3. Find the two sounds that use noise. Why can't you hum along to them?
#   4. Which effect has the most notes? Which is the longest?
