# Lab 07: Ringtones
# Play tunes written the way old phones stored their ringtones: as a line
# of text. The format is called RTTTL (Ring Tone Text Transfer Language),
# and it is wonderfully small. This is a whole song:
#
#   Twinkle:d=4,o=5,b=100:c,c,g,g,a,a,2g,f,f,e,e,d,d,2c
#
#   Twinkle     the name
#   d=4         a note with no number is a QUARTER note
#   o=5         the notes are in the 5th octave
#   b=100       100 beats per minute
#   c,c,g,g...  the notes. "2g" is a HALF note. "8c" would be an eighth.
#               "c." is dotted: half again as long. "p" is a pause.
#
# The screen shows the note being played, so you can follow along.
#
#   UP / DOWN   choose a tune
#   MODE        play it (press again to stop)
#
# Each tune uses a different wave, so you hear how the SAME melody changes
# character: a music box (sine), an old video game (square), a flute
# (triangle), and a trumpet-ish buzz (saw). Lab 05 shows why.
#
# These tunes are all traditional songs, free for anyone to play.

NAME = "07-ringtones.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import sound
from watchparts import Button

BIG = config.BIG_FONT
SMALL = config.SMALL_FONT
DIM = config.color565(150, 150, 150)
TRACK = config.color565(60, 60, 60)

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
WAVE_NAMES = sound.WAVE_NAMES

BAR_X, BAR_W, BAR_Y = 60, 240, 214

display = config.init_display()
mode_button, up_button, down_button = [
    Button(pin) for pin in config.init_buttons()]
sound.init(rate=16000, ibuf=4096)
sound.volume(config.VOLUME)


def put(text, y, font=SMALL, color=config.WHITE, width=34):
    config.centered_text(display, font, text.center(width), y, color)


def load(index):
    """Read tune `index`. Returns its notes and each note's end time."""
    _, notes = sound.rtttl_notes(TUNES[index][2])
    ends = []
    total = 0
    for _, ms in notes:
        total += ms
        ends.append(total)
    return notes, ends


def show(index, notes):
    title, wave, _ = TUNES[index]
    put("RINGTONES  {} OF {}".format(index + 1, len(TUNES)), 44, SMALL,
        config.CYAN, 26)
    put(title, 80, BIG, config.YELLOW, 16)
    put("{} wave, {} notes".format(WAVE_NAMES[wave], len(notes)), 122, SMALL,
        DIM, 30)
    display.fill_rect(BAR_X, BAR_Y, BAR_W, 8, TRACK)
    put("..", 160, BIG, DIM, 6)
    put("MODE: play", 258, SMALL, DIM, 30)
    put("UP/DOWN: choose a tune", 284, SMALL, DIM, 30)


index = 0
notes, ends = load(index)
display.fill(config.BLACK)
show(index, notes)
started = None              # when the tune began (as the ears hear it)
last_note = None
try:
    while True:
        now = time.ticks_ms()
        if up_button.pressed(now) or down_button.pressed(now):
            step = 1 if up_button.held else -1
            sound.stop()
            started = None
            last_note = None
            index = (index + step) % len(TUNES)
            notes, ends = load(index)
            show(index, notes)
        elif mode_button.pressed(now):
            sound.stop()
            if started is not None:
                started = None                      # MODE again: stop
                last_note = None
                show(index, notes)
            else:
                sound.rtttl(TUNES[index][2], TUNES[index][1])
                started = time.ticks_add(now, sound.latency_ms())
                put("MODE: stop", 258, SMALL, DIM, 30)

        if started is not None:
            elapsed = time.ticks_diff(now, started)
            if elapsed >= 0:
                if elapsed >= ends[-1]:
                    started = None
                    last_note = None
                    show(index, notes)
                    put("done!", 160, BIG, config.GREEN, 6)
                else:
                    i = 0
                    while ends[i] <= elapsed:
                        i += 1
                    if i != last_note:
                        last_note = i
                        freq = notes[i][0]
                        put(sound.note_name(freq) if freq else "rest", 160,
                            BIG, config.GREEN if freq else DIM, 6)
                    filled = BAR_W * elapsed // ends[-1]
                    display.fill_rect(BAR_X, BAR_Y, filled, 8, config.CYAN)
        time.sleep_ms(10)
finally:
    sound.deinit()

# Try This
#   1. Change b=100 in "Twinkle" to b=160. Is it a different song, or the
#      same song played faster?
#   2. Write your own: "Mine:d=4,o=5,b=120:c,e,g,2c6". The 6 after the c is
#      the octave, so c6 is the C one octave higher.
#   3. Give "Ode to Joy" a different wave: change sound.SQUARE in TUNES to
#      sound.SINE. Does it still sound like a video game?
#   4. Find a song you know that uses only about eight different notes and
#      write it out in RTTTL. Public-domain folk songs work well.
