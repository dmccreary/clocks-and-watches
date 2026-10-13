# Lab 08: Button Theremin
# A theremin is an instrument you play without touching it: you wave your
# hands near two antennas and the pitch slides up and down. This one has
# buttons instead of antennas, but the pitch slides the same smooth way.
#
#   UP          hold to slide the pitch UP
#   DOWN        hold to slide the pitch DOWN
#   MODE        sound on / off
#   hold MODE   change the voice (sine, triangle, square, saw)
#
# A piano jumps from note to note. A violin, a trombone, and a theremin can
# land BETWEEN the notes. The screen shows the nearest note and how far off
# it you are: in tune is when the bar sits at the middle.
#
# TWO CORES AGAIN
# While core 0 reads your buttons and draws the screen, core 1 keeps the
# speaker fed. sound.hold() starts a note that keeps playing, and
# sound.pitch() steers it. Steering is smooth, so the pitch glides instead
# of jumping, even when your finger is slow.
#
# This lab uses a SMALL reserve (4096 bytes, about 93 ms at 22,050 samples
# a second) so the pitch follows your fingers quickly. Lab 03 explains why
# a bigger reserve is safer but slower.

NAME = "08-button-theremin.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import time

import config
import sound
from watchparts import Button, SHORT, LONG

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
TRACK = config.color565(70, 70, 70)

LOW_HZ, HIGH_HZ = 110, 1760          # A2 to A6, four octaves
SLIDE_PER_MS = 1.0004                # 1.0004 ** 1000 is about 1.5x per second
VOICES = (sound.SINE, sound.TRIANGLE, sound.SQUARE, sound.SAW)
BAR_X, BAR_W, BAR_Y = 40, 280, 206

display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]
sound.init(rate=22050, ibuf=4096)
sound.volume(config.VOLUME)


def put(text, y, font=SMALL, color=config.WHITE, width=34):
    config.centered_text(display, font, text.center(width), y, color)


def cents_off(freq):
    """How far freq is from the nearest piano note, in cents (hundredths of
    a semitone). 0 is perfectly in tune; +50 and -50 are as far off as it
    gets."""
    semitones = 12 * math.log(freq / 440) / math.log(2)
    return round((semitones - round(semitones)) * 100)


def bar_x(freq):
    octaves = math.log(freq / LOW_HZ) / math.log(2)
    return BAR_X + int(BAR_W * octaves / 4)


def draw_frame():
    display.fill(config.BLACK)
    put("BUTTON THEREMIN", 44, SMALL, config.CYAN, 26)
    display.fill_rect(BAR_X, BAR_Y + 10, BAR_W, 4, TRACK)
    for octave in range(5):
        x = BAR_X + BAR_W * octave // 4
        display.fill_rect(x, BAR_Y + 4, 2, 16, TRACK)
    display.text(SMALL, "110", BAR_X - 4, BAR_Y + 26, DIM, config.BLACK)
    display.text(SMALL, "1760", BAR_X + BAR_W - 28, BAR_Y + 26, DIM,
                 config.BLACK)


freq = 440.0
voice = 0
playing = False
shown = None
marker_x = None
last_pitch_ms = 0
last_tick = time.ticks_ms()
draw_frame()


def redraw():
    """Update only what changed since the last call."""
    global shown, marker_x
    state = (round(freq), voice, playing)
    if state == shown:
        return
    shown = state
    cents = cents_off(freq)
    in_tune = abs(cents) <= 8
    put(sound.note_name(freq), 84, BIG, config.GREEN if in_tune
        else config.YELLOW, 8)
    put("{} Hz".format(round(freq)), 126, SMALL, config.WHITE, 14)
    put("{:+d} cents".format(cents) if not in_tune else "in tune", 148, SMALL,
        config.GREEN if in_tune else DIM, 14)
    put("voice: " + sound.WAVE_NAMES[VOICES[voice]], 176, SMALL, DIM, 20)
    x = bar_x(freq)
    if marker_x is not None and marker_x != x:
        display.fill_rect(marker_x - 3, BAR_Y, 7, 24, config.BLACK)
        display.fill_rect(marker_x - 3, BAR_Y + 10, 7, 4, TRACK)
        for octave in range(5):
            tx = BAR_X + BAR_W * octave // 4
            if marker_x - 3 <= tx <= marker_x + 3:
                display.fill_rect(tx, BAR_Y + 4, 2, 16, TRACK)
    display.fill_rect(x - 3, BAR_Y, 7, 24,
                      config.GREEN if playing else config.GRAY)
    marker_x = x
    put("ON" if playing else "off", 262, BIG, config.GREEN if playing
        else DIM, 6)
    put("UP/DOWN: slide  MODE: on/off", 300, SMALL, DIM, 28)


try:
    redraw()
    while True:
        now = time.ticks_ms()
        dt = time.ticks_diff(now, last_tick)
        last_tick = now

        press = mode_button.short_or_long(now)
        up_button.pressed(now)               # keeps up_button.held current
        down_button.pressed(now)

        if press == SHORT:
            playing = not playing
            if playing:
                sound.hold(freq, VOICES[voice], level=0.8)
            else:
                sound.release()
        elif press == LONG:
            voice = (voice + 1) % len(VOICES)
            if playing:
                sound.hold(freq, VOICES[voice], level=0.8)

        if up_button.held != down_button.held:    # exactly one is down
            factor = SLIDE_PER_MS ** dt
            freq = freq * factor if up_button.held else freq / factor
            freq = max(LOW_HZ, min(HIGH_HZ, freq))
            if playing and time.ticks_diff(now, last_pitch_ms) >= 20:
                sound.pitch(freq)
                last_pitch_ms = now

        redraw()
        time.sleep_ms(10)
finally:
    sound.deinit()

# Try This
#   1. Hold UP until the sound disappears into a squeak at the top. Hold
#      DOWN until it rumbles. Where does your speaker stop making deep sound?
#   2. Try to land exactly on A4 (440 Hz) by tapping. Can you hit "in tune"?
#   3. Play "Twinkle Twinkle" by sliding to each note. It is hard! Real
#      theremin players practice for years.
#   4. Change SLIDE_PER_MS to 1.0010 for a faster slide. Is it easier or
#      harder to be accurate?
