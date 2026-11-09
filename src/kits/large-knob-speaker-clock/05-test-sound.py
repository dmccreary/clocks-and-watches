# Lab 05: Test the Sound
# Plays a steady 400 Hz tone for two seconds, then a rising scale of
# eight notes, to check the MAX98357A amplifier and the speaker.
#
# This test talks to the I2S hardware directly instead of using sound.py,
# so the only things that can stop it working are the wires and the amp:
#
#   Amp pin   Pico pin   Breadboard row   Wire
#   -------   --------   --------------   ------
#   BCLK      GP12       16               yellow
#   LRC       GP13       17               green   (must be the pin right
#                                                   AFTER BCLK)
#   GND       GND        18               black
#   DIN       GP14       19               orange
#   GAIN      GP15       20               brown
#   SD        not connected
#   VIN       VBUS (5 V) or 3V3
#
# If you hear nothing:
#   - check the amp's VIN and GND first -- with no power it is silent
#   - check that DIN goes to GP14 (the audio itself travels on this wire)
#   - check the speaker's two wires in the amp's + and - terminals
# If I2S() raises an error, BCLK and LRC are probably swapped.
#
# HOW A SPEAKER MAKES A NOTE. Sound is air pushed back and forth. The
# Pico sends the amplifier a list of numbers ("samples"), 16,000 every
# second, and each one says where the speaker cone should be at that
# instant. Numbers that rise and fall smoothly 400 times a second -- a
# sine wave -- push the air 400 times a second, and you hear a note
# just above G4 (392 Hz). Twice as many times a second sounds one octave
# higher.

NAME = "05-test-sound.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import struct
import time
from machine import Pin, I2S

import config

RATE = 16000            # samples per second
FREQ = 400              # 16000 / 400 = exactly 40 samples per wave
SECONDS = 2
CHUNK_WAVES = 25        # 25 waves = 1000 samples = 62.5 ms per chunk

# A C-major scale: do, re, mi, fa, sol, la, ti, do.
SCALE = (("C", 262), ("D", 294), ("E", 330), ("F", 349),
         ("G", 392), ("A", 440), ("B", 494), ("C", 523))
NOTE_MS = 300

amplitude = int(32767 * config.VOLUME / 100)
samples_per_wave = RATE // FREQ
chunk_samples = samples_per_wave * CHUNK_WAVES


def make_chunk(fade=None):
    """One chunk of the sine wave as 16-bit samples. fade is "in", "out"
    or None; a fade stops the click a sudden start or stop makes."""
    out = bytearray(chunk_samples * 2)
    for i in range(chunk_samples):
        level = 1.0
        if fade == "in":
            level = i / chunk_samples
        elif fade == "out":
            level = 1 - i / chunk_samples
        value = int(amplitude * level
                    * math.sin(2 * math.pi * i / samples_per_wave))
        struct.pack_into("<h", out, i * 2, value)
    return out


def make_note(freq, ms):
    """A whole note, any frequency, with 10 ms fades at each end."""
    count = RATE * ms // 1000
    fade = RATE // 100
    out = bytearray(count * 2)
    for i in range(count):
        level = min(1.0, i / fade, (count - i) / fade)
        value = int(amplitude * 0.8 * level
                    * math.sin(2 * math.pi * freq * i / RATE))
        struct.pack_into("<h", out, i * 2, value)
    return out


def show(line1, line2=""):
    """Two lines in the middle of the screen."""
    display.fill_rect(0, 90, config.WIDTH, 80, config.BLACK)
    config.centered_text(display, config.BIG_FONT, line1, 96, config.YELLOW)
    config.centered_text(display, config.SMALL_FONT, line2, 140)


display = config.init_display()
display.fill(config.BLACK)
config.centered_text(display, config.BIG_FONT, "Sound Test", 16, config.CYAN)
config.centered_text(display, config.SMALL_FONT,
                     "volume {}  gain {} dB".format(config.VOLUME,
                                                    config.GAIN_DB),
                     56, config.GRAY)
config.centered_text(display, config.SMALL_FONT,
                     "BCLK GP{} LRC GP{} DIN GP{} GAIN GP{}".format(
                         config.I2S_BCLK_PIN, config.I2S_LRC_PIN,
                         config.I2S_DIN_PIN, config.I2S_GAIN_PIN),
                     210, config.GRAY)

steady = make_chunk()
fade_in = make_chunk("in")
fade_out = make_chunk("out")
silence = bytes(chunk_samples * 2)
chunks = RATE * SECONDS // chunk_samples        # 32 chunks = 2 seconds

if config.I2S_LRC_PIN != config.I2S_BCLK_PIN + 1:
    print("WARNING: LRC (GP{}) must be the pin right after BCLK (GP{})".format(
        config.I2S_LRC_PIN, config.I2S_BCLK_PIN))

config.set_gain()
audio = I2S(0, sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
            sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
            format=I2S.MONO, rate=RATE, ibuf=4096)
print("I2S started: BCLK GP{}, LRC GP{}, DIN GP{}, gain {} dB".format(
    config.I2S_BCLK_PIN, config.I2S_LRC_PIN, config.I2S_DIN_PIN,
    config.GAIN_DB))

try:
    # Part 1: one steady tone.
    print("Playing {} Hz for {} seconds at volume {} -- listen now".format(
        FREQ, SECONDS, config.VOLUME))
    show("{} Hz".format(FREQ), "a steady tone for {} seconds".format(SECONDS))
    started = time.ticks_ms()
    audio.write(fade_in)
    for _ in range(chunks - 2):
        audio.write(steady)
    audio.write(fade_out)
    for _ in range(4):
        audio.write(silence)
    print("Done after {} ms.".format(time.ticks_diff(time.ticks_ms(),
                                                     started)))

    # Part 2: a scale. Each note is calculated first, then shown, then
    # played -- write() waits while the I2S buffer is full, so the
    # screen changes at about the time you hear the note.
    print("Playing a C-major scale")
    for name, freq in SCALE:
        note = make_note(freq, NOTE_MS)
        show(name, "{} Hz".format(freq))
        print("  {}  {} Hz".format(name, freq))
        audio.write(note)
    # write() returns as soon as the last note is in the I2S buffer, so
    # push some silence through to let it finish playing.
    for _ in range(4):
        audio.write(silence)
finally:
    audio.deinit()

show("Done", "heard both? the speaker works")
print("Heard it? The amp and speaker work. Heard nothing? See the list at")
print("the top of this file.")

# Try This
#   1. Change FREQ to 800. The pitch goes up an octave. (Keep FREQ a number
#      that divides 16000 exactly, such as 200, 500, 800 or 1000.)
#   2. Change VOLUME in config.py to 10, then 80. Which is comfortable?
#   3. Change GAIN_DB in config.py to 12. How much louder is it?
#   4. Play the scale backwards: change `for name, freq in SCALE` to
#      `for name, freq in reversed(SCALE)`.
