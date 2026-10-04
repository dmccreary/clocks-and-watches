# sound.py -- the Study Buddy's sound module (lab 03).
#
# Makes sound with the MAX98357A amplifier. There are no sound files: every
# beep, melody, and effect is calculated on the Pico, a few thousand
# numbers ("samples") per second, and sent to the amplifier over I2S.
#
# THE WHOLE IDEA IN FIVE LINES
#
#     import sound
#     sound.init()                      # start the amplifier
#     sound.tone(440, 500)              # play A4 for half a second ...
#     sound.tone(660, 500)              # ... then E5. Notes queue up.
#     sound.play("coin")                # or play a named effect
#
# Every function that makes sound returns AT ONCE. The notes play in the
# background while your program keeps drawing, reading buttons, and so on.
# Use sound.busy() to ask "is anything still playing?", or sound.wait()
# to stand still until it is finished.
#
# HOW IT KEEPS PLAYING WHILE YOU DRAW
#
# The amplifier needs a steady stream of samples. If the stream ever runs
# dry you hear a click. Drawing on the screen can freeze the Pico's loop
# for 130 ms or more, so this module keeps a reserve: an I2S "ring buffer"
# (ibuf bytes) that holds the next few hundred milliseconds of sound.
# The I2S driver calls _irq() each time it has used up a chunk, and _irq()
# calculates the next chunk and tops the reserve up. As long as no single
# freeze is longer than the reserve, you never hear it.
#
#     reserve (ms) = ibuf / (2 * rate) * 1000      e.g. 8192 / 32000 = 256 ms
#
# A bigger reserve survives longer freezes, but a change you ask for (a
# new note, stop()) is heard one reserve later. Lab 08 uses a small reserve
# so the pitch follows your fingers; lab 03 measures how big it must be.
#
# THE SYNTHESIZER
#
# _render() is a "viper" function: MicroPython compiles it to real machine
# code, about 30 times faster than ordinary Python. A chunk of 1024
# samples takes well under a millisecond. Every sample, it:
#
#   1. moves a PHASE along (a number that counts 0 to 2**32 around one
#      wave cycle, then wraps back to 0). Bigger steps mean a higher pitch.
#   2. turns the phase into a wave height: sine, square, triangle, saw,
#      or noise
#   3. multiplies by the loudness (the volume and the note's fade in/out)
#
# Lab 05 shows what each of those five waves looks like and sounds like.

import array
import math
import time

import micropython
from machine import Pin, I2S

import config

SINE, SQUARE, TRIANGLE, SAW, NOISE = range(5)
WAVE_NAMES = ("sine", "square", "triangle", "saw", "noise")

CHUNK = 1024                     # samples calculated per call of _irq()
MAX_QUEUE = 200                  # notes waiting; extras are dropped
_ONE = 1 << 22                   # loudness 1.0, as a fixed-point number
_PHASE_ONE = 1 << 32             # a full cycle of the phase counter

# One cycle of a sine wave, in 1024 steps. Stored as 0..65535 (the real
# height plus 32768) because the compiled code reads unsigned numbers.
_TABLE = array.array("H", (
    32768 + int(32767 * math.sin(2 * math.pi * i / 1024))
    for i in range(1024)))


@micropython.viper
def _render(out: ptr16, off: int, count: int, table: ptr16, wave: int,
            phase: int, step: int, dstep: int, gain: int, dgain: int) -> int:
    """Fill out[off : off + count] with samples. Returns the new phase.

    step is how far the phase moves each sample, and dstep is how much the
    step itself changes each sample (a glide). gain is the loudness as a
    number where 1 << 22 means full, and dgain is how much it changes each
    sample (a fade). All of it is whole-number math, because that is what
    runs fast."""
    i = 0
    while i < count:
        if wave == 0:                                  # sine
            idx = (phase >> 22) & 1023
            frac = (phase >> 10) & 4095
            s0 = int(table[idx]) - 32768
            s1 = int(table[(idx + 1) & 1023]) - 32768
            v = s0 + (((s1 - s0) * frac) >> 12)        # blend two neighbors
        elif wave == 1:                                # square
            v = 32767
            if phase < 0:
                v = -32767
        elif wave == 2:                                # triangle
            p = phase >> 16
            t = p ^ (p >> 31)
            v = (t << 1) - 32767
        elif wave == 3:                                # saw
            v = phase >> 16
        else:                                          # noise
            phase = phase * 1664525 + 1013904223
            v = phase >> 16
        g = gain
        if g < 0:
            g = 0
        out[off + i] = (v * (g >> 7)) >> 15
        if wave != 4:
            phase += step
            step += dstep
        gain += dgain
        i += 1
    return phase


class _Note:
    """One note waiting to play, or playing now."""

    def __init__(self, f0, f1, ms, wave, level, attack, release, hold):
        rate = _rate
        self.wave = wave
        self.level = level
        self.hold = hold                    # True: plays until release()
        total = rate * ms // 1000 if not hold else 1 << 30
        self.attack = min(rate * attack // 1000, total // 2)
        self.release = min(rate * release // 1000, total - self.attack)
        self.body = total - self.attack - self.release
        self.release_total = max(1, self.release)
        self.attack_total = max(1, self.attack)
        self.step = _step_for(f0)
        self.target = _step_for(f1)
        # A glide changes the step a little every sample. Notes that hold
        # steer toward self.target a chunk at a time instead.
        self.dstep = 0 if hold else (self.target - self.step) // max(1, total)
        self.phase = 0x1234567 if wave == NOISE else 0
        self.gain = 0 if self.attack else int(level * _vgain() * _ONE)
        self.silent = f0 <= 0 and f1 <= 0   # a rest


# --- state -----------------------------------------------------------------
_audio = None
_rate = 16000
_ibuf = 8192
_volume = config.VOLUME
_queue = []
_cur = None
_buf = bytearray(CHUNK * 2)
_buf_mv = memoryview(_buf)
_zeros = memoryview(bytes(CHUNK * 2))
_audible_until = 0
_playing = False                 # True from the first note until the last
_stats = {}


def _vgain():
    """Loudness for the current volume. Squaring makes the volume knob feel
    even: the ear hears each doubling of power as one step."""
    v = _volume / 100
    return v * v


def _step_for(freq):
    """How far the phase moves per sample to make freq Hz."""
    if freq <= 0:
        return 0
    freq = min(freq, _rate * 0.49)          # stay below the Nyquist limit
    return int(freq * _PHASE_ONE / _rate)


def _reset_stats():
    _stats["chunks"] = 0
    _stats["underruns"] = 0
    _stats["min_headroom_ms"] = 10 ** 6
    _stats["max_gap_ms"] = 0
    _stats["t0"] = time.ticks_us()
    _stats["last"] = _stats["t0"]
    _stats["accepted"] = 0                  # samples handed to the ring


def _fill():
    """Calculate one chunk of samples into _buf."""
    global _cur, _audible_until, _playing
    off = 0
    while off < CHUNK:
        note = _cur
        if note is None:
            if _queue:
                note = _cur = _queue.pop(0)
                _playing = True
            else:
                # Nothing to play: fill the rest with silence.
                _buf_mv[off * 2:CHUNK * 2] = _zeros[:(CHUNK - off) * 2]
                if _playing:
                    # The last note was just calculated. It is still in the
                    # reserve, so it keeps coming out of the speaker for
                    # one reserve's worth of time. (Only note this once --
                    # silence chunks keep arriving after it.)
                    _playing = False
                    _audible_until = time.ticks_add(
                        time.ticks_ms(), _ibuf * 1000 // (_rate * 2) + 20)
                return
        target = 0 if note.silent else int(note.level * _vgain() * _ONE)

        if note.attack > 0:
            n = min(note.attack, CHUNK - off)
            dg = (target - 0) // note.attack_total
            note.phase = _render(_buf, off, n, _TABLE, note.wave, note.phase,
                                 note.step, note.dstep, note.gain, dg)
            note.gain += dg * n
            note.attack -= n
        elif note.body > 0:
            n = min(note.body, CHUNK - off)
            dstep = note.dstep
            if note.hold:
                # Steer smoothly toward the pitch the program last asked for.
                dstep = (note.target - note.step) // n
            note.phase = _render(_buf, off, n, _TABLE, note.wave, note.phase,
                                 note.step, dstep, target, 0)
            note.step += dstep * n
            note.gain = target
            if not note.hold:
                note.body -= n
        elif note.release > 0:
            n = min(note.release, CHUNK - off)
            start = note.gain if note.gain > 0 else target
            dg = -(start // note.release_total)
            note.phase = _render(_buf, off, n, _TABLE, note.wave, note.phase,
                                 note.step, note.dstep, note.gain, dg)
            note.gain += dg * n
            note.step += note.dstep * n
            note.release -= n
        else:
            _cur = None
            continue
        off += n
        if note.attack <= 0 and note.body <= 0 and note.release <= 0:
            _cur = None


def _feed():
    """Calculate a chunk and give it to the I2S driver."""
    now = time.ticks_us()
    st = _stats
    # How much sound is waiting in the ring buffer right now? The driver
    # has been playing since t0, and we have given it `accepted` samples,
    # so the difference is the reserve. Below zero means it ran dry.
    played = time.ticks_diff(now, st["t0"]) * _rate // 1_000_000
    headroom = st["accepted"] - played
    if time.ticks_diff(now, st["t0"]) > 30_000_000:
        # ticks_us() wraps after about 17 minutes, so every 30 seconds
        # start counting from now, keeping the same reserve.
        st["t0"] = now
        st["accepted"] = headroom
    if st["chunks"] > 1:
        ms = headroom * 1000 // _rate
        if ms < st["min_headroom_ms"]:
            st["min_headroom_ms"] = ms
        gap = time.ticks_diff(now, st["last"]) // 1000
        if gap > st["max_gap_ms"]:
            st["max_gap_ms"] = gap
        if headroom < 0:
            st["underruns"] += 1
            st["t0"] = now                  # start counting again
            st["accepted"] = 0
    st["last"] = now
    _fill()
    _audio.write(_buf)
    st["accepted"] += CHUNK
    st["chunks"] += 1


def _irq(_):
    _feed()


# --- the public functions ---------------------------------------------------
def init(rate=16000, ibuf=8192, volume=None):
    """Start the amplifier. rate is samples per second (16000 is plenty for
    beeps and tunes, 44100 for the full range of hearing), and ibuf is the
    reserve described at the top of this file, in bytes.

    Calling it again with different settings restarts the audio."""
    global _audio, _rate, _ibuf, _volume, _cur
    deinit()
    _rate = rate
    _ibuf = ibuf
    if volume is not None:
        _volume = volume
    config.set_gain()
    _audio = I2S(0, sck=Pin(config.I2S_BCLK_PIN), ws=Pin(config.I2S_LRC_PIN),
                 sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
                 format=I2S.MONO, rate=rate, ibuf=ibuf)
    _reset_stats()
    _audio.irq(_irq)
    _feed()                         # the first chunk starts the chain


def deinit():
    """Stop the amplifier and free the I2S hardware."""
    global _audio, _cur
    if _audio is not None:
        _audio.deinit()
        _audio = None
    _queue.clear()
    _cur = None


def volume(level=None):
    """Get or set the volume, 0 (silent) to 100 (as loud as it goes)."""
    global _volume
    if level is not None:
        _volume = max(0, min(100, level))
    return _volume


def tone(freq, ms, wave=SINE, to=None, level=1.0, attack=5, release=10):
    """Queue one note: freq Hz for ms milliseconds.

    to      a second frequency. The pitch glides from freq to it.
    level   0.0 to 1.0, how loud this note is next to the volume setting.
    attack  milliseconds to fade in (stops a click at the start).
    release milliseconds to fade out (stops a click at the end, and gives
            notes a little space between them).
    A freq of 0 is a rest."""
    if len(_queue) < MAX_QUEUE:
        _queue.append(_Note(freq, freq if to is None else to, ms, wave,
                            level, attack, release, False))


def rest(ms):
    """Queue silence for ms milliseconds."""
    tone(0, ms, level=0, attack=0, release=0)


def hold(freq, wave=SINE, level=1.0):
    """Start a note that keeps playing until release(). Change its pitch
    with pitch(). It plays after anything already queued, and jumps the
    queue if there is none."""
    global _cur
    release()
    _queue.append(_Note(freq, freq, 0, wave, level, 15, 40, True))


def pitch(freq):
    """Steer a held note toward freq Hz. The change is smooth."""
    if _cur is not None and _cur.hold:
        _cur.target = _step_for(freq)
    elif _queue and _queue[-1].hold:
        _queue[-1].target = _step_for(freq)
        _queue[-1].step = _queue[-1].target


def release():
    """Let a held note fade out."""
    n = _cur
    if n is not None and n.hold:
        n.hold = False
        n.body = 0
        n.release = n.release_total
    for q in _queue:
        if q.hold:
            q.hold = False
            q.body = 0
            q.release = 0


def stop():
    """Stop everything, now. Sound already in the reserve still plays, up
    to one reserve's worth (see the top of this file)."""
    global _cur
    _queue.clear()
    _cur = None


def busy():
    """True while any sound is queued or still coming out of the speaker."""
    if _cur is not None or _queue:
        return True
    return time.ticks_diff(_audible_until, time.ticks_ms()) > 0


def wait():
    """Stand still until all sound has finished."""
    while busy():
        time.sleep_ms(10)


def stats():
    """What the audio has been doing since init() (or reset_stats()):
    chunks calculated, underruns (times the reserve ran dry and the speaker
    got silence or a click), the smallest reserve seen in milliseconds, and
    the longest wait between chunks. Lab 03 reads these."""
    return {"chunks": _stats["chunks"], "underruns": _stats["underruns"],
            "min_headroom_ms": _stats["min_headroom_ms"],
            "max_gap_ms": _stats["max_gap_ms"],
            "reserve_ms": _ibuf * 1000 // (_rate * 2),
            "rate": _rate}


def reset_stats():
    """Start the numbers in stats() from zero."""
    st = _stats
    st["underruns"] = 0
    st["min_headroom_ms"] = 10 ** 6
    st["max_gap_ms"] = 0


# --- notes, tunes, and named sounds -----------------------------------------
_SEMITONES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note_freq(name):
    """Frequency in Hz of a note name like "A4", "C#5", or "Bb3".
    A4 is 440 Hz, the pitch an orchestra tunes to."""
    semitone = _SEMITONES[name[0].upper()]
    i = 1
    if name[i] == "#":
        semitone += 1
        i += 1
    elif name[i] == "b":
        semitone -= 1
        i += 1
    octave = int(name[i:])
    midi = 12 * (octave + 1) + semitone
    return 440 * 2 ** ((midi - 69) / 12)


def note_name(freq):
    """The nearest note name for a frequency, such as "A4". Used by labs
    that show the pitch on screen."""
    if freq <= 0:
        return "--"
    midi = round(69 + 12 * math.log(freq / 440) / math.log(2))
    names = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    return "{}{}".format(names[midi % 12], midi // 12 - 1)


def rtttl(text, wave=SQUARE, level=0.8):
    """Queue a tune written as an RTTTL ringtone, the text format old
    phones used:

        "name:d=4,o=5,b=100:8c,8d,e,p,g.6"

    d, o, and b are the default note length, octave, and beats per
    minute. Each note is [length] letter [#] [.] [octave], and p is a
    pause. A length of 4 is a quarter note, 8 an eighth, and so on."""
    name, defaults, notes = text.split(":")
    d, o, b = 4, 5, 63
    for item in defaults.split(","):
        key, value = item.split("=")
        if key == "d":
            d = int(value)
        elif key == "o":
            o = int(value)
        elif key == "b":
            b = int(value)
    whole_ms = 240000 // b
    for item in notes.split(","):
        item = item.strip().lower()
        if not item:
            continue
        i = 0
        while i < len(item) and item[i].isdigit():
            i += 1
        length = int(item[:i]) if i else d
        item = item[i:]
        dotted = "." in item
        item = item.replace(".", "")
        letter = item[0]
        sharp = "#" in item
        digits = "".join(c for c in item[1:] if c.isdigit())
        octave = int(digits) if digits else o
        ms = whole_ms // length
        if dotted:
            ms = ms * 3 // 2
        if letter == "p":
            rest(ms)
        else:
            tone(note_freq("{}{}{}".format(
                letter.upper(), "#" if sharp else "", octave)),
                ms, wave, level=level, attack=3, release=min(25, ms // 3))
    return name


def play(name):
    """Queue a named sound from sfx.py, such as "coin" or "right"."""
    import sfx
    for f0, f1, ms, wave, level, rel in sfx.EFFECTS[name]:
        tone(f0, ms, wave, to=f1, level=level, attack=3, release=rel)
