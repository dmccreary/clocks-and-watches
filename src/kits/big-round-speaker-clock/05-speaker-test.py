# 05-speaker-test.py: Speaker Test
# Plays a steady 400 Hz tone for two seconds to check the MAX98357A
# amplifier and the speaker.
#
# This test talks to the I2S hardware directly instead of using sound.py,
# so the only things that can stop it working are the wires and the amp:
#
#   Amp pin   Pico pin
#   -------   --------
#   BCLK      GP9
#   LRC       GP10      (must be the pin right AFTER BCLK)
#   DIN       GP11
#   GAIN      GP12
#   VIN, GND  VBUS (5 V) or 3V3, and GND
#   SD        not connected
#
# If you hear nothing:
#   - check the amp's VIN and GND first -- with no power it is silent
#   - check that DIN goes to GP11 (the audio itself travels on this wire)
#   - check the speaker's two wires in the amp's + and - terminals
# If I2S() raises an error, BCLK and LRC are probably swapped.

NAME = "05-speaker-test.py"
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
print("Playing {} Hz for {} seconds at volume {} -- listen now".format(
    FREQ, SECONDS, config.VOLUME))

try:
    started = time.ticks_ms()
    audio.write(fade_in)
    for _ in range(chunks - 2):
        audio.write(steady)
    audio.write(fade_out)
    # write() returns as soon as the last chunk is in the I2S buffer, so
    # push some silence through to let it finish playing.
    for _ in range(4):
        audio.write(silence)
    print("Done after {} ms.".format(time.ticks_diff(time.ticks_ms(),
                                                     started)))
finally:
    audio.deinit()

print("Heard it? The amp and speaker work. Heard nothing? See the list at")
print("the top of this file.")

# Try This
#   1. Change FREQ to 800. The pitch goes up an octave. (Keep FREQ a number
#      that divides 16000 exactly, such as 200, 500, 800 or 1000.)
#   2. Change VOLUME in config.py to 10, then 80. Which is comfortable?
#   3. Change GAIN_DB in config.py to 12. How much louder is it?
