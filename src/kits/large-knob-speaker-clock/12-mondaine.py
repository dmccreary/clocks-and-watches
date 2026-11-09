# Lab 12: Railway Clock
# A Swiss-railway-style station clock: a white dial with no numbers,
# heavy black bars, tapered black hands, and a red second hand that ends
# in a disc, like a railway signal paddle. The day and date sit in the
# top corners.
#
# Watch the red hand. It does not tick: it GLIDES once around the dial in
# 58.5 seconds, stops at 12, and waits. While it waits, the minute hand
# hops ahead one minute, and then the red hand sets off again. Real
# station clocks work this way so that every clock in every station
# starts each minute together, on a signal from the master clock.
#
# There are no controls. At the top of every hour the speaker chimes.
#
# THE PROBLEM. Gliding means the red hand moves 20 times a second, and
# there is no frame buffer -- every pixel has to be sent over SPI. The
# usual "draw the old hand in the background color" trick does not work
# here either: the red hand lies ON TOP of the black hands, and they lie
# on top of the bars, so erasing one would cut a hole in the others.
#
# THE ANSWER is in lib/mondaine.py. For each row of pixels a hand touches
# it works out the color every changed pixel should END UP -- dial, bars,
# hour hand, minute hand, red rod, red disc, topmost wins -- and sends
# only those pixels, a band of up to 16 rows in one go. Nothing is erased
# and then repaired, so nothing flickers. Read the top of lib/mondaine.py
# for the whole story.
#
# MILLISECONDS FROM A CLOCK THAT COUNTS SECONDS. time.localtime() only
# counts whole seconds, which is fine for a ticking hand but not for a
# gliding one. mondaine.SweepClock waits for the seconds to change, notes
# time.ticks_ms() at that instant, and counts milliseconds from there.
#
# This design is not made or endorsed by SBB or Mondaine, and the face
# has no logo. It is an independent drawing of a public design idea.

NAME = "12-mondaine.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import mondaine
import sound

CHIME_ON_THE_HOUR = True
FRAME_MS = 50            # up to 20 frames a second

BLACK = config.BLACK
CORNER_COLOR = config.WHITE
DIM = config.color565(150, 150, 150)
SMALL = config.SMALL_FONT
BIG = config.BIG_FONT
MARGIN = 4

DAYS = ("MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN")
MONTHS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN",
          "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")

display = config.init_display()
sound.init()

if time.localtime()[0] < 2025:
    print("The Pico's clock has not been set. Connect with Thonny, which")
    print("sets it from your computer, or run lab 06 to set it over WiFi.")

face = mondaine.Face(display)
face.draw_dial()
clock = mondaine.SweepClock()    # waits up to a second for the seconds to tick


def draw_corners():
    """Day top left, date top right, in the black corners the round dial
    leaves on a rectangular screen."""
    t = time.localtime()
    right = config.WIDTH - MARGIN
    display.text(BIG, DAYS[t[6]], MARGIN, MARGIN, CORNER_COLOR, BLACK)
    display.text(BIG, "%2d" % t[2], right - 2 * BIG.WIDTH, MARGIN,
                 CORNER_COLOR, BLACK)
    display.text(SMALL, MONTHS[t[1] - 1], right - 3 * SMALL.WIDTH,
                 MARGIN + BIG.HEIGHT + 2, DIM, BLACK)
    return t[2]


shown_day = draw_corners()
last_frame = time.ticks_ms()
at_rest = False
chimed_hour = clock.now()[0]

while True:
    now = time.ticks_ms()
    hour, minute, ms = clock.now()
    face.show(*mondaine.hand_angles(hour, minute, ms))

    if ms >= mondaine.RESYNC_MS:
        if not at_rest:
            # Every hand is standing still: a safe moment to line the
            # milliseconds up with the Pico's clock again, and to check
            # the date and the hour.
            at_rest = True
            clock.sync()
            if time.localtime()[2] != shown_day:
                shown_day = draw_corners()
    else:
        at_rest = False

    if minute == 0 and hour != chimed_hour:
        chimed_hour = hour
        if CHIME_ON_THE_HOUR:
            sound.play("chime")

    # Wait out the rest of this frame.
    spent = time.ticks_diff(time.ticks_ms(), now)
    if spent < FRAME_MS:
        time.sleep_ms(FRAME_MS - spent)
