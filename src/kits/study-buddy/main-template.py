# Main Template: One Study Buddy, Five Sound Demos
# Step through the interactive sound labs, one at a time, on one program:
#
#   Hear the Range -> Waveforms -> Sound Effects -> Ringtones -> Theremin
#   (labs 04 to 08, then back to the start)
#
# A row of five dots at the bottom of the screen shows which demo you are
# in. Copy this file to the Pico as main.py and the board starts in it.
#
# THE THREE BUTTONS
#
#   HOLD MODE for one second   go to the NEXT demo
#   tap MODE                   the demo's own action: play it again, play
#                              the sound, start the sweep, turn the note on
#   UP / DOWN                  change the demo's parameter: the voice, the
#                              sound, the tune, the pitch
#
# Why a hold, and not a tap, for "next"? Every demo needs MODE for its own
# action (replay, play, start). If a tap also switched demos, a student
# trying to hear a sound again would be flung into the next demo. A hold is
# hard to do by accident. Watch the screen: the demo changes the moment the
# second is up, and you can let go.
#
# HOW THE DEMOS ARE BUILT
# Labs 04 to 08 each run their own loop, so they cannot be called one after
# another. Here each one is a small class with the same four jobs, and the
# loop at the bottom of this file only knows about those four:
#
#   start()       draw the demo's screen and get the sound ready
#   update(now)   called every pass of the loop (about every 10 ms) with
#                 time.ticks_ms(). Read UP and DOWN, redraw only what changed
#   on_mode(now)  MODE was tapped
#   stop()        silence the demo before the next one starts
#
# To add a sixth demo, write one more class like these and add it to MODES.
#
# TWO RULES FOR A DEMO: draw only above the dots (nothing lower than
# y = DOT_Y - 12), and call clear(), never display.fill(), to wipe its
# screen. Each demo explains its sound ideas in its own lab (04 to 08).

NAME = "main-template.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import math
import random
import time

import config
import sfx
import shapes
import sound
from watchparts import Button, LONG, SHORT

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
TRACK = config.color565(70, 70, 70)
GRID = config.color565(50, 50, 60)
RECIPE_RATE = 16000            # sample rate for the beeps, tunes, and effects

# The row of dots at the bottom of the round screen.
DOT_Y = 322
DOT_SPACING = 16
DOT_RADIUS = 4
DOT_ON = config.WHITE
DOT_OFF = config.color565(70, 70, 70)
HINT_Y = 282                   # the demo's own button hint
HOLD_HINT_Y = 300              # "hold MODE: next demo", the same in every demo

display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]


# --- helpers every demo uses ---------------------------------------------------
def put(text, y, font=SMALL, color=config.WHITE, width=34):
    """Draw text centered at row y, padded to `width` characters so it
    covers whatever was there before."""
    config.centered_text(display, font, text.center(width), y, color)


def clear():
    """Blank the demo's part of the screen, and leave the dots alone."""
    display.fill_rect(0, 0, config.WIDTH, DOT_Y - 12, config.BLACK)


def hints(text):
    """The two hint lines at the bottom: this demo's, then the common one."""
    put(text, HINT_Y, SMALL, DIM, 30)
    put("hold MODE: next demo", HOLD_HINT_Y, SMALL, DIM, 24)


def draw_dots(current):
    """One dot per demo across the bottom, centered; the current one is
    bright."""
    x = config.CENTER_X - (len(MODES) - 1) * DOT_SPACING // 2
    for i in range(len(MODES)):
        shapes.circle(display, x + i * DOT_SPACING, DOT_Y, DOT_RADIUS,
                      DOT_ON if i == current else DOT_OFF, config.FILL)


def start_sound(rate=RECIPE_RATE, ibuf=4096):
    """(Re)start the amplifier. Calling sound.init() again with different
    settings restarts the audio, which is how each demo gets its own."""
    sound.init(rate=rate, ibuf=ibuf)
    sound.volume(config.VOLUME)


class Demo:
    """What every demo has. A demo that makes sound overrides start()."""

    def start(self):
        pass

    def update(self, now):
        pass

    def on_mode(self, now):
        pass

    def stop(self):
        sound.stop()
        sound.deinit()


# --- lab 04: hear the range --------------------------------------------------
class HearTheRange(Demo):
    """A tone slides from 20 Hz up to 20,480 Hz. Press UP when you first hear
    it and again when it disappears. MODE starts it, or cancels it."""

    RATE = 44100               # 44,100 samples a second reach up to 22,050 Hz
    LOW_HZ = 20
    STEPS = 4                  # slides per octave
    OCTAVES = 10
    SEGMENT_MS = 400
    TOTAL_SEGMENTS = STEPS * OCTAVES
    TOTAL_MS = TOTAL_SEGMENTS * SEGMENT_MS
    REACTION_MS = 250          # it takes a moment to press a button
    VOLUME = min(config.VOLUME, 30)
    BAR_X, BAR_W, BAR_Y = 40, 280, 196
    DRAW_EVERY_MS = 30

    INTRO, SWEEP, RESULT = range(3)

    def start(self):
        self.state = self.INTRO
        self.show_intro()

    def freq_at(self, ms):
        """The frequency being made ms milliseconds into the sweep."""
        ms = max(0, min(ms, self.TOTAL_MS - 1))
        k = ms // self.SEGMENT_MS
        f0 = self.LOW_HZ * 2 ** (k / self.STEPS)
        f1 = self.LOW_HZ * 2 ** ((k + 1) / self.STEPS)
        return f0 + (f1 - f0) * (ms % self.SEGMENT_MS) / self.SEGMENT_MS

    def bar_x(self, freq):
        """Where along the bar a frequency goes: evenly by octave."""
        octaves = math.log(max(freq, self.LOW_HZ) / self.LOW_HZ) / math.log(2)
        return self.BAR_X + int(self.BAR_W * octaves / self.OCTAVES)

    @staticmethod
    def hz_text(freq):
        return "{:,} Hz".format(int(freq))

    @staticmethod
    def piano_text(freq):
        if freq < 27.5:
            return "below the piano!"
        if freq > 4186:
            return "above the piano!"
        return "nearest note: " + sound.note_name(freq)

    def show_intro(self):
        clear()
        put("HEAR THE RANGE", 44, SMALL, config.CYAN, 26)
        put("A tone will slide from", 100, SMALL)
        put("deep and low to high", 120, SMALL)
        put("and squeaky.", 140, SMALL)
        put("Press UP when you first hear it,", 176, SMALL, config.YELLOW)
        put("and again when it disappears.", 196, SMALL, config.YELLOW)
        put("Turn the volume down first!", 232, SMALL, config.RED)
        hints("MODE or UP: start")

    def draw_frame(self):
        """The parts of the screen that never change during a sweep."""
        clear()
        put("HEAR THE RANGE", 44, SMALL, config.CYAN, 26)
        display.fill_rect(self.BAR_X, self.BAR_Y + 10, self.BAR_W, 4, TRACK)
        for octave in range(self.OCTAVES + 1):     # a tick for every doubling
            x = self.BAR_X + self.BAR_W * octave // self.OCTAVES
            display.fill_rect(x, self.BAR_Y + 4, 2, 16, TRACK)
        display.text(SMALL, "20 Hz", self.BAR_X - 8, 222, DIM, config.BLACK)
        display.text(SMALL, "20,000", self.BAR_X + self.BAR_W - 40, 222, DIM,
                     config.BLACK)
        hints("MODE: cancel")

    def begin(self):
        """Queue the whole sweep and start the screen to match it."""
        sound.init(rate=self.RATE, ibuf=16384, volume=self.VOLUME)
        queued_at = time.ticks_ms()
        last = self.TOTAL_SEGMENTS - 1
        for k in range(self.TOTAL_SEGMENTS):
            sound.tone(self.LOW_HZ * 2 ** (k / self.STEPS), self.SEGMENT_MS,
                       to=self.LOW_HZ * 2 ** ((k + 1) / self.STEPS),
                       level=0.8, attack=0 if k else 20,
                       release=0 if k < last else 40, link=k > 0)
        self.draw_frame()
        put("Press UP when you hear it", 262, SMALL, config.YELLOW)
        self.marks = [None, None]
        self.marker_x = None
        self.last_text = None
        self.last_draw = queued_at
        # The ears hear the sweep one reserve after it was queued, so the
        # screen waits that long to line up with them.
        self.started = time.ticks_add(queued_at, sound.latency_ms())
        self.state = self.SWEEP

    def update(self, now):
        pressed = up_button.pressed(now)
        if self.state != self.SWEEP:
            if pressed:
                self.begin()
            return
        elapsed = time.ticks_diff(now, self.started)
        if elapsed < 0:
            return                                  # not heard yet
        if elapsed >= self.TOTAL_MS:
            self.finish()
            return
        freq = self.freq_at(elapsed)
        if time.ticks_diff(now, self.last_draw) >= self.DRAW_EVERY_MS:
            self.last_draw = now
            self.draw_freq(freq)
        if pressed:
            heard = self.freq_at(elapsed - self.REACTION_MS)
            if self.marks[0] is None:
                self.marks[0] = heard
                put("Press UP when it disappears", 262, SMALL, config.YELLOW)
            elif self.marks[1] is None:
                self.marks[1] = heard
                put("Marked! Listening on ...", 262, SMALL, config.GREEN)

    def draw_freq(self, freq):
        text = self.hz_text(freq)
        if text == self.last_text:
            return
        self.last_text = text
        put(text, 96, BIG, config.WHITE, 16)
        put(self.piano_text(freq), 138, SMALL, DIM, 26)
        x = self.bar_x(freq)
        if self.marker_x is not None:
            # Erase the old marker, then put back the bar and any octave
            # tick it was covering.
            m = self.marker_x
            display.fill_rect(m - 3, self.BAR_Y, 7, 24, config.BLACK)
            display.fill_rect(m - 3, self.BAR_Y + 10, 7, 4, TRACK)
            for octave in range(self.OCTAVES + 1):
                tx = self.BAR_X + self.BAR_W * octave // self.OCTAVES
                if m - 3 <= tx <= m + 3:
                    display.fill_rect(tx, self.BAR_Y + 4, 2, 16, TRACK)
        display.fill_rect(x - 3, self.BAR_Y, 7, 24, config.YELLOW)
        self.marker_x = x

    def finish(self):
        sound.deinit()
        low, high = self.marks
        self.state = self.RESULT
        clear()
        put("YOUR RANGE", 44, SMALL, config.CYAN, 26)
        if low is None:
            put("You never pressed UP.", 120, SMALL)
            put("Did you hear it?", 140, SMALL)
        else:
            put("first heard at", 88, SMALL, DIM)
            put(self.hz_text(low), 110, BIG, config.GREEN, 16)
            if high is None:
                put("and it was still", 164, SMALL, DIM)
                put("audible at the end!", 184, SMALL, DIM)
            else:
                put("stopped hearing at", 158, SMALL, DIM)
                put(self.hz_text(high), 180, BIG, config.YELLOW, 16)
        put("Down low, small speakers mostly buzz.", 232, SMALL, DIM)
        put("Adults often stop at 10,000-17,000.", 252, SMALL, DIM)
        hints("MODE or UP: again")
        print("heard from {} to {} Hz".format(
            None if low is None else round(low),
            None if high is None else round(high)))

    def on_mode(self, now):
        if self.state == self.SWEEP:
            sound.deinit()                          # cancel
            self.state = self.INTRO
            self.show_intro()
        else:
            self.begin()


# --- lab 05: five voices ---------------------------------------------------------
class Waveforms(Demo):
    """The same note in five voices, with the wave drawn while you listen.
    UP and DOWN choose the voice; MODE plays it again."""

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
    PLOT_X, PLOT_W = 50, 260
    PLOT_Y, PLOT_H = 190, 100         # center line, and the height of the box
    CYCLES = 2

    def __init__(self):
        self.index = 0

    def start(self):
        start_sound()
        clear()
        self.show()
        self.play()

    @staticmethod
    def height(wave, phase):
        """The wave's height, -1.0 to 1.0, a fraction `phase` (0 to 1) of
        the way through one cycle. The same shapes sound.py calculates."""
        if wave == sound.SINE:
            return math.sin(2 * math.pi * phase)
        if wave == sound.SQUARE:
            return 1.0 if phase < 0.5 else -1.0
        if wave == sound.TRIANGLE:
            return -1 + 4 * phase if phase < 0.5 else 3 - 4 * phase
        if wave == sound.SAW:
            return 2 * phase - 1
        return random.getrandbits(15) / 16384 - 1   # a random height

    def draw_wave(self, wave):
        """Clear the plot box and draw two cycles of the wave."""
        half = self.PLOT_H // 2
        display.fill_rect(self.PLOT_X - 10, self.PLOT_Y - half - 4,
                          self.PLOT_W + 20, self.PLOT_H + 8, config.BLACK)
        display.hline(self.PLOT_X - 10, self.PLOT_Y, self.PLOT_W + 20, GRID)
        previous = None
        # For noise there is no cycle: just draw the jagged line.
        points = self.PLOT_W // 2 if wave == sound.NOISE else self.PLOT_W
        for i in range(points + 1):
            phase = (i / points * self.CYCLES) % 1.0
            h = self.height(wave, phase)
            x = self.PLOT_X + self.PLOT_W * i // points
            y = self.PLOT_Y - int(h * (half - 4))
            if previous is not None:
                display.line(previous[0], previous[1], x, y, config.GREEN)
            previous = (x, y)

    def show(self):
        name, wave, text = self.VOICES[self.index]
        put("FIVE VOICES  {} OF {}".format(self.index + 1, len(self.VOICES)),
            44, SMALL, config.CYAN, 26)
        put(name, 76, BIG, config.YELLOW, 12)
        put(text, 120, SMALL, config.WHITE, 32)
        self.draw_wave(wave)
        if wave == sound.NOISE:
            put("no pitch at all", 258, SMALL, DIM, 26)
        else:
            put("A3 - C4 - E4 - A3", 258, SMALL, DIM, 26)
        hints("UP/DOWN: voice  MODE: again")

    def play(self):
        name, wave, _ = self.VOICES[self.index]
        if wave == sound.NOISE:
            # Noise has no pitch, so play a rhythm instead of a tune.
            for ms in (330, 330, 330, 500):
                sound.tone(1, ms, wave, level=0.7, attack=3, release=60)
        else:
            for note, ms in self.TUNE:
                sound.tone(sound.note_freq(note), ms, wave, level=0.7,
                           attack=5, release=40)

    def update(self, now):
        change = 0
        if up_button.pressed(now):
            change = 1
        elif down_button.pressed(now):
            change = -1
        if change:
            sound.stop()
            self.index = (self.index + change) % len(self.VOICES)
            self.show()
            self.play()

    def on_mode(self, now):
        sound.stop()
        self.play()


# --- lab 06: sound effects gallery --------------------------------------------------
class SoundEffects(Demo):
    """Twenty-one sounds from sfx.py. UP and DOWN browse; MODE plays."""

    WAVES = ("sine", "square", "triangle", "saw", "noise")

    def __init__(self):
        self.index = 0

    def start(self):
        start_sound()
        clear()
        self.show()
        self.was_playing = False

    def recipe(self, name):
        """Describe a sound's first note in words, and how many there are."""
        steps = sfx.EFFECTS[name]
        f0, f1, ms, wave, level, fade = steps[0]
        if wave == sfx.NOISE:
            first = "noise"
        elif f0 == 0:
            first = "a rest"
        elif f0 == f1:
            first = "{} Hz {}".format(f0, self.WAVES[wave])
        else:
            first = "{}->{} Hz {}".format(f0, f1, self.WAVES[wave])
        return first, len(steps), sum(step[2] for step in steps)

    def show(self):
        name = sfx.NAMES[self.index]
        first, count, total_ms = self.recipe(name)
        put("SOUND EFFECTS", 44, SMALL, config.CYAN, 26)
        put(name, 92, BIG, config.YELLOW, 14)
        put("{} of {}".format(self.index + 1, len(sfx.NAMES)), 134, SMALL,
            DIM, 20)
        put("{} note{}, {} ms".format(count, "" if count == 1 else "s",
                                      total_ms), 166, SMALL, config.WHITE, 30)
        put("first: " + first, 188, SMALL, config.WHITE, 34)
        self.status(False)
        hints("UP/DOWN: browse  MODE: play")

    @staticmethod
    def status(playing):
        if playing:
            put("PLAYING", 226, BIG, config.GREEN, 12)
        else:
            put("MODE: play", 226, BIG, DIM, 12)

    def update(self, now):
        step = 0
        if up_button.pressed(now):
            step = 1
        elif down_button.pressed(now):
            step = -1
        if step:
            sound.stop()
            self.index = (self.index + step) % len(sfx.NAMES)
            self.show()
            self.was_playing = False
        playing = sound.busy()
        if playing != self.was_playing:
            self.status(playing)
            self.was_playing = playing

    def on_mode(self, now):
        sound.stop()
        sound.play(sfx.NAMES[self.index])


# --- lab 07: ringtones ------------------------------------------------------------
class Ringtones(Demo):
    """Four traditional tunes, each stored as one line of text. UP and DOWN
    choose a tune; MODE plays it, and stops it."""

    TUNES = (
        ("Twinkle Twinkle", sound.SINE,
         "Twinkle:d=4,o=5,b=100:c,c,g,g,a,a,2g,f,f,e,e,d,d,2c,"
         "g,g,f,f,e,e,2d,g,g,f,f,e,e,2d,"
         "c,c,g,g,a,a,2g,f,f,e,e,d,d,2c"),
        ("Ode to Joy", sound.SQUARE,
         "Ode:d=4,o=5,b=114:e,e,f,g,g,f,e,d,c,c,d,e,e.,8d,2d,"
         "e,e,f,g,g,f,e,d,c,c,d,e,d.,8c,2c"),
        ("Frere Jacques", sound.TRIANGLE,
         "Jacques:d=4,o=5,b=100:c,d,e,c,c,d,e,c,e,f,2g,e,f,2g,"
         "8g,8a,8g,8f,e,c,8g,8a,8g,8f,e,c,c,g4,2c,c,g4,2c"),
        ("Mary Had a Lamb", sound.SAW,
         "Mary:d=4,o=5,b=120:e,d,c,d,e,e,2e,d,d,2d,e,g,2g,"
         "e,d,c,d,e,e,e,e,d,d,e,d,2c"),
    )
    BAR_X, BAR_W, BAR_Y = 60, 240, 214

    def __init__(self):
        self.index = 0

    def start(self):
        start_sound()
        clear()
        self.load()
        self.show()
        self.started = None        # when the tune began (as the ears hear it)
        self.last_note = None

    def load(self):
        """Read the chosen tune. Works out each note's end time."""
        _, self.notes = sound.rtttl_notes(self.TUNES[self.index][2])
        self.ends = []
        total = 0
        for _, ms in self.notes:
            total += ms
            self.ends.append(total)

    def show(self):
        title, wave, _ = self.TUNES[self.index]
        put("RINGTONES  {} OF {}".format(self.index + 1, len(self.TUNES)), 44,
            SMALL, config.CYAN, 26)
        put(title, 80, BIG, config.YELLOW, 16)
        put("{} wave, {} notes".format(sound.WAVE_NAMES[wave],
                                       len(self.notes)), 122, SMALL, DIM, 30)
        display.fill_rect(self.BAR_X, self.BAR_Y, self.BAR_W, 8, TRACK)
        put("..", 160, BIG, DIM, 6)
        put("MODE: play", 258, SMALL, DIM, 30)
        hints("UP/DOWN: choose a tune")

    def halt(self):
        """Stop the tune and put the screen back to 'ready'."""
        sound.stop()
        self.started = None
        self.last_note = None
        self.show()

    def update(self, now):
        step = 0
        if up_button.pressed(now):
            step = 1
        elif down_button.pressed(now):
            step = -1
        if step:
            sound.stop()
            self.started = None
            self.last_note = None
            self.index = (self.index + step) % len(self.TUNES)
            self.load()
            self.show()

        if self.started is None:
            return
        elapsed = time.ticks_diff(now, self.started)
        if elapsed < 0:
            return
        if elapsed >= self.ends[-1]:
            self.halt()
            put("done!", 160, BIG, config.GREEN, 6)
            return
        i = 0
        while self.ends[i] <= elapsed:
            i += 1
        if i != self.last_note:
            self.last_note = i
            freq = self.notes[i][0]
            put(sound.note_name(freq) if freq else "rest", 160, BIG,
                config.GREEN if freq else DIM, 6)
        display.fill_rect(self.BAR_X, self.BAR_Y,
                          self.BAR_W * elapsed // self.ends[-1], 8,
                          config.CYAN)

    def on_mode(self, now):
        if self.started is not None:
            self.halt()                                 # MODE again: stop
        else:
            sound.stop()
            sound.rtttl(self.TUNES[self.index][2], self.TUNES[self.index][1])
            self.started = time.ticks_add(now, sound.latency_ms())
            put("MODE: stop", 258, SMALL, DIM, 30)


# --- lab 08: button theremin --------------------------------------------------------
class Theremin(Demo):
    """Hold UP or DOWN to slide the pitch, and it lands BETWEEN the notes.
    MODE steps through: sine, triangle, square, saw, then off.

    (Lab 08 puts on/off on MODE and the voice on a long MODE. Here a long
    MODE moves to the next demo, so one button does both jobs.)"""

    LOW_HZ, HIGH_HZ = 110, 1760       # A2 to A6, four octaves
    SLIDE_PER_MS = 1.0004             # 1.0004 ** 1000 is about 1.5x per second
    VOICES = (sound.SINE, sound.TRIANGLE, sound.SQUARE, sound.SAW)
    BAR_X, BAR_W, BAR_Y = 40, 280, 196
    PITCH_EVERY_MS = 20

    def __init__(self):
        self.freq = 440.0
        self.voice = 0
        self.playing = False

    def start(self):
        # A SMALL reserve (about 93 ms at this rate) so the pitch follows
        # your fingers quickly. Lab 03 explains the trade.
        start_sound(rate=22050, ibuf=4096)
        self.playing = False                 # a new visit starts silent
        self.shown = None
        self.marker_x = None
        self.last_pitch_ms = 0
        self.last_tick = time.ticks_ms()
        clear()
        self.draw_frame()
        self.redraw()

    @staticmethod
    def cents_off(freq):
        """How far freq is from the nearest piano note, in cents (hundredths
        of a semitone). 0 is perfectly in tune."""
        semitones = 12 * math.log(freq / 440) / math.log(2)
        return round((semitones - round(semitones)) * 100)

    def bar_x(self, freq):
        octaves = math.log(freq / self.LOW_HZ) / math.log(2)
        return self.BAR_X + int(self.BAR_W * octaves / 4)

    def draw_frame(self):
        put("BUTTON THEREMIN", 44, SMALL, config.CYAN, 26)
        display.fill_rect(self.BAR_X, self.BAR_Y + 10, self.BAR_W, 4, TRACK)
        for octave in range(5):
            x = self.BAR_X + self.BAR_W * octave // 4
            display.fill_rect(x, self.BAR_Y + 4, 2, 16, TRACK)
        display.text(SMALL, "110", self.BAR_X - 4, self.BAR_Y + 26, DIM,
                     config.BLACK)
        display.text(SMALL, "1760", self.BAR_X + self.BAR_W - 28,
                     self.BAR_Y + 26, DIM, config.BLACK)
        hints("UP/DOWN: slide  MODE: voice")

    def redraw(self):
        """Update only what changed since the last call."""
        state = (round(self.freq), self.voice, self.playing)
        if state == self.shown:
            return
        self.shown = state
        freq = self.freq
        cents = self.cents_off(freq)
        in_tune = abs(cents) <= 8
        put(sound.note_name(freq), 84, BIG,
            config.GREEN if in_tune else config.YELLOW, 8)
        put("{} Hz".format(round(freq)), 126, SMALL, config.WHITE, 14)
        put("in tune" if in_tune else "{:+d} cents".format(cents), 148, SMALL,
            config.GREEN if in_tune else DIM, 14)
        put("voice: " + sound.WAVE_NAMES[self.VOICES[self.voice]], 170, SMALL,
            DIM, 20)
        x = self.bar_x(freq)
        if self.marker_x is not None and self.marker_x != x:
            m = self.marker_x
            display.fill_rect(m - 3, self.BAR_Y, 7, 24, config.BLACK)
            display.fill_rect(m - 3, self.BAR_Y + 10, 7, 4, TRACK)
            for octave in range(5):
                tx = self.BAR_X + self.BAR_W * octave // 4
                if m - 3 <= tx <= m + 3:
                    display.fill_rect(tx, self.BAR_Y + 4, 2, 16, TRACK)
        display.fill_rect(x - 3, self.BAR_Y, 7, 24,
                          config.GREEN if self.playing else config.GRAY)
        self.marker_x = x
        put("ON" if self.playing else "off", 240, BIG,
            config.GREEN if self.playing else DIM, 6)

    def on_mode(self, now):
        if not self.playing:
            self.playing = True
        elif self.voice < len(self.VOICES) - 1:
            self.voice += 1
        else:
            self.playing = False
            self.voice = 0
        if self.playing:
            sound.hold(self.freq, self.VOICES[self.voice], level=0.8)
        else:
            sound.release()

    def update(self, now):
        dt = time.ticks_diff(now, self.last_tick)
        self.last_tick = now
        up_button.pressed(now)               # keeps up_button.held current
        down_button.pressed(now)
        if up_button.held != down_button.held:    # exactly one is down
            factor = self.SLIDE_PER_MS ** dt
            freq = self.freq * factor if up_button.held else self.freq / factor
            self.freq = max(self.LOW_HZ, min(self.HIGH_HZ, freq))
            if (self.playing and time.ticks_diff(now, self.last_pitch_ms)
                    >= self.PITCH_EVERY_MS):
                sound.pitch(self.freq)
                self.last_pitch_ms = now
        self.redraw()

    def stop(self):
        self.playing = False
        Demo.stop(self)


# --- the main loop --------------------------------------------------------------
# The demos, in the order a long MODE press steps through them.
MODES = (HearTheRange(), Waveforms(), SoundEffects(), Ringtones(),
         Theremin())
START_MODE = 0           # Hear the Range


def switch_to(index):
    """Silence the demo on the screen, then start demo `index`."""
    global mode, mode_index
    if mode is not None:
        mode.stop()
    mode_index = index
    mode = MODES[index]
    display.fill(config.BLACK)
    mode.start()
    draw_dots(index)
    print("Demo:", type(mode).__name__)


mode = None
mode_index = 0
try:
    switch_to(START_MODE)
    while True:
        now = time.ticks_ms()

        # MODE belongs to this loop: a short press is reported when the
        # button is let go, a long press the moment it has been held for
        # watchparts.LONG_PRESS_MS (one second).
        press = mode_button.short_or_long(now)
        if press == LONG:
            switch_to((mode_index + 1) % len(MODES))
        elif press == SHORT:
            mode.on_mode(now)

        mode.update(now)
        time.sleep_ms(10)
finally:
    sound.deinit()

# Try This
#   1. Hold MODE and count "one-one-thousand". Does the demo change when you
#      reach one second? Change LONG_PRESS_MS in lib/watchparts.py to 2000.
#      Is two seconds too slow? (Other programs that use it change too.)
#   2. Change START_MODE to 4 so the board wakes up as a theremin.
#   3. Reorder MODES so your favorite demo comes first. The dots follow.
#   4. Make a sixth demo: copy Waveforms, keep its four functions, and have
#      it play a scale with sound.note_freq("C4") up to "C5". Add it to MODES.
