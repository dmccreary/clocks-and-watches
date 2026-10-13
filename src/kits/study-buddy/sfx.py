# sfx.py -- the Study Buddy's named sounds, as plain data.
#
# sound.play("coin") looks the name up in EFFECTS and queues each step as a
# note. A sound effect is just a list of notes, and every note is six
# numbers:
#
#     (start_hz, end_hz, milliseconds, wave, loudness, fade_out_ms)
#
#   start_hz, end_hz   the pitch glides from the first to the second. Make
#                      them equal for a steady note. 0 and 0 is a rest.
#   wave               0 sine, 1 square, 2 triangle, 3 saw, 4 noise
#   loudness           0.0 to 1.0
#   fade_out_ms        how long the note takes to die away
#
# To make your own, add an entry. Lab 06 plays every one of these in a
# gallery, and its "Try This" suggests inventing a new one.
#
# Why these sounds? Each is a classic recipe:
#   coin, jump, powerup, gameover   the beeps and blips of old video games
#   laser      a saw wave sliding fast from high to low
#   explosion  noise (all frequencies at once) that fades slowly
#   siren      a triangle wave gliding up and down
#   doorbell   two sine notes, each ringing out

SINE, SQUARE, TRIANGLE, SAW, NOISE = range(5)

C5, D5, E5, G5, A4 = 523, 587, 659, 784, 440
C6, E6, G6 = 1047, 1319, 1568


def _rest(ms):
    return (0, 0, ms, SINE, 0, 0)


_CHIME = [
    (C5, C5, 140, SINE, 0.8, 60),
    (E5, E5, 140, SINE, 0.8, 60),
    (G5, G5, 420, SINE, 0.8, 250),
]

EFFECTS = {
    # --- the Study Buddy's own sounds (labs 03 and later use these) -------
    "right": [(C6, C6, 90, SINE, 0.8, 30), (G6, G6, 220, SINE, 0.8, 120)],
    "wrong": [(196, 98, 350, SAW, 0.5, 60)],
    "chime": _CHIME,
    "reminder": _CHIME + [_rest(350)] + _CHIME,
    "done": [(G5, G5, 160, SINE, 0.8, 60), (E5, E5, 160, SINE, 0.8, 60),
             (D5, D5, 160, SINE, 0.8, 60), (C5, C5, 160, SINE, 0.8, 60),
             (A4, A4, 500, SINE, 0.8, 300)],
    "start": [(C5, C5, 90, SQUARE, 0.5, 20), (G5, G5, 160, SQUARE, 0.5, 60)],

    # --- the fun ones (lab 06) -------------------------------------------
    "coin": [(988, 988, 80, SQUARE, 0.5, 10), (E6, E6, 400, SQUARE, 0.5, 300)],
    "jump": [(250, 750, 180, SQUARE, 0.5, 40)],
    "laser": [(2200, 180, 220, SAW, 0.5, 30)],
    "explosion": [(1, 1, 900, NOISE, 1.0, 800)],
    "powerup": [(C5, C5, 70, SQUARE, 0.5, 15), (E5, E5, 70, SQUARE, 0.5, 15),
                (G5, G5, 70, SQUARE, 0.5, 15), (C6, C6, 70, SQUARE, 0.5, 15),
                (E6, E6, 70, SQUARE, 0.5, 15), (G6, G6, 260, SQUARE, 0.5, 200)],
    "gameover": [(392, 392, 220, TRIANGLE, 0.8, 30),
                 (370, 370, 220, TRIANGLE, 0.8, 30),
                 (330, 330, 220, TRIANGLE, 0.8, 30),
                 (294, 147, 800, TRIANGLE, 0.8, 400)],
    "siren": [(600, 1200, 500, TRIANGLE, 0.7, 0),
              (1200, 600, 500, TRIANGLE, 0.7, 0)] * 3,
    "doorbell": [(E5, E5, 450, SINE, 0.9, 350), (C5, C5, 800, SINE, 0.9, 650)],
    "bird": [(2200, 3400, 70, SINE, 0.6, 20), (3400, 2400, 60, SINE, 0.6, 20),
             _rest(50),
             (2400, 3600, 90, SINE, 0.6, 20), (3600, 2600, 70, SINE, 0.6, 20),
             _rest(50),
             (2600, 3800, 110, SINE, 0.6, 40), (3800, 2000, 140, SINE, 0.6, 60)],
    "robot": [(1200, 1800, 70, SINE, 0.7, 10), (1800, 900, 60, SINE, 0.7, 10),
              (1500, 1500, 50, SINE, 0.7, 10), (900, 2200, 90, SINE, 0.7, 10),
              (2200, 1100, 70, SINE, 0.7, 10), (1400, 2000, 60, SINE, 0.7, 10),
              (2000, 700, 160, SINE, 0.7, 60)],
    "ufo": [(400, 800, 220, SINE, 0.7, 0), (800, 400, 220, SINE, 0.7, 0)] * 4,
    "rain": [(1, 1, 2500, NOISE, 0.12, 600)],
    "heartbeat": [(90, 70, 110, SINE, 1.0, 60), _rest(90),
                  (80, 60, 140, SINE, 1.0, 90), _rest(600)] * 2,
    "engine": [(60, 220, 1400, SAW, 0.6, 200)],
    "magic": [(1047, 1047, 60, SINE, 0.7, 40), (1319, 1319, 60, SINE, 0.7, 40),
              (1568, 1568, 60, SINE, 0.7, 40), (2093, 2093, 60, SINE, 0.7, 40),
              (2637, 2637, 60, SINE, 0.7, 40), (3136, 3136, 500, SINE, 0.7, 450)],
}

# The order the gallery in lab 06 shows them.
NAMES = ("coin", "jump", "powerup", "laser", "explosion", "gameover",
         "siren", "doorbell", "bird", "robot", "ufo", "magic", "engine",
         "heartbeat", "rain", "right", "wrong", "chime", "reminder", "done",
         "start")
