# Lab 05: Five Voices
# The same note, played five ways. The speaker cone moves in and out, and
# the SHAPE of that movement decides what the sound is like. The screen
# draws the shape while you listen:
#
#   sine       a smooth curve. The purest sound there is: one frequency.
#   triangle   straight lines up and down. Soft and hollow, like a flute.
#   square     jumps between high and low. Buzzy, like an old video game.
#   saw        climbs slowly, drops suddenly. Bright and sharp, like a buzzer.
#   noise      random numbers. Every pitch at once: a hiss, like rain.
#
# The first four voices play the same pitch (A3, 220 Hz) at the same
# loudness, and you can still tell them apart instantly. That difference has
# a name: TIMBRE (say "TAM-ber"). A trumpet and a violin playing the same
# note differ in timbre. The sharper the corners of the wave, the more
# high-pitched extras (harmonics) ride along with the note, and the brighter
# it sounds. A sine has none. A square has lots.
#
#   UP    next voice
#   DOWN  previous voice
#   MODE  hear it again

NAME = "05-waveforms.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import random
import time

import config
import sound
from watchparts import Button

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
GRID = config.color565(50, 50, 60)
WAVE_COLOR = config.GREEN

# (name, sound.py wave, what it sounds like)
VOICES = (
    ("sine", sound.SINE, "Smooth and pure, like a whistle"),
    ("triangle", sound.TRIANGLE, "Soft and hollow, like a flute"),
    ("square", sound.SQUARE, "Buzzy, like an old video game"),
    ("saw", sound.SAW, "Bright and sharp, like a buzzer"),
    ("noise", sound.NOISE, "Every pitch at once: a hiss"),
)

# The notes of the little tune that shows off each voice.
TUNE = (("A3", 330), ("C4", 330), ("E4", 330), ("A3", 500))

# Where the picture of the wave goes.
PLOT_X, PLOT_W = 50, 260
PLOT_Y, PLOT_H = 190, 100          # center line, and the height of the box
CYCLES = 2

display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]
sound.init(rate=16000, ibuf=4096)
sound.volume(config.VOLUME)


def put(text, y, font=SMALL, color=config.WHITE, width=34):
    config.centered_text(display, font, text.center(width), y, color)


def height(wave, phase):
    """The wave's height, -1.0 to 1.0, a fraction `phase` (0 to 1) of the
    way through one cycle. The same shapes sound.py calculates."""
    if wave == sound.SINE:
        return math.sin(2 * math.pi * phase)
    if wave == sound.SQUARE:
        return 1.0 if phase < 0.5 else -1.0
    if wave == sound.TRIANGLE:
        return -1 + 4 * phase if phase < 0.5 else 3 - 4 * phase
    if wave == sound.SAW:
        return 2 * phase - 1
    return random.getrandbits(15) / 16384 - 1      # a random height, -1 to 1


def draw_wave(wave):
    """Clear the plot box and draw two cycles of the wave."""
    half = PLOT_H // 2
    display.fill_rect(PLOT_X - 10, PLOT_Y - half - 4, PLOT_W + 20,
                      PLOT_H + 8, config.BLACK)
    display.hline(PLOT_X - 10, PLOT_Y, PLOT_W + 20, GRID)
    previous = None
    # For noise there is no cycle: just draw the jagged line.
    points = PLOT_W // 2 if wave == sound.NOISE else PLOT_W
    for i in range(points + 1):
        phase = (i / points * CYCLES) % 1.0
        h = height(wave, phase)
        x = PLOT_X + PLOT_W * i // points
        y = PLOT_Y - int(h * (half - 4))
        if previous is not None:
            display.line(previous[0], previous[1], x, y, WAVE_COLOR)
        previous = (x, y)


def show(index):
    name, wave, text = VOICES[index]
    put("FIVE VOICES  {} OF {}".format(index + 1, len(VOICES)), 44, SMALL,
        config.CYAN, 26)
    put(name, 76, BIG, config.YELLOW, 12)
    put(text, 120, SMALL, config.WHITE, 32)
    draw_wave(wave)
    if wave == sound.NOISE:
        put("no pitch at all", 266, SMALL, DIM, 26)
    else:
        put("A3 - C4 - E4 - A3", 266, SMALL, DIM, 26)
    put("UP/DOWN: voice  MODE: again", 292, SMALL, DIM, 30)


def play(index):
    name, wave, _ = VOICES[index]
    if wave == sound.NOISE:
        # Noise has no pitch, so play a rhythm instead of a tune.
        for ms in (330, 330, 330, 500):
            sound.tone(1, ms, wave, level=0.7, attack=3, release=60)
    else:
        for note, ms in TUNE:
            sound.tone(sound.note_freq(note), ms, wave, level=0.7,
                       attack=5, release=40)


display.fill(config.BLACK)
index = 0
show(index)
play(index)
try:
    while True:
        now = time.ticks_ms()
        change = 0
        if up_button.pressed(now):
            change = 1
        elif down_button.pressed(now):
            change = -1
        if change:
            sound.stop()
            index = (index + change) % len(VOICES)
            show(index)
            play(index)
        elif mode_button.pressed(now):
            sound.stop()
            play(index)
        time.sleep_ms(10)
finally:
    sound.deinit()

# Try This
#   1. Listen to the saw, then the square. Which sounds brighter? Look at
#      the pictures: which has the sharper corners?
#   2. sound.py can also glide. Add  to=440  to the sound.tone() call in
#      play() and listen to each voice slide up an octave.
#   3. Change TUNE to your own four notes. Note names go from C0 up. A4 is
#      the A an orchestra tunes to (440 Hz).
#   4. Make the noise sound like a drum: in play(), change release=60 to
#      release=200 for a swishy cymbal, or release=15 for a snappy snare.
