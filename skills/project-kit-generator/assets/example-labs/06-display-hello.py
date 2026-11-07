# Say Hello on the Round Display
#
# Before we draw a temperature on the round screen, we need to prove the
# Pico can talk to it. This program writes one line of big text in the
# middle of the display. It does not use the SHT40 at all, so you can run
# it before the sensor is even plugged in.
#
# If the screen stays dark, check the wiring table in config.py, then check
# that lib/ made it onto the Pico (upload-code.sh copies it for you).
#
# This display has no frame buffer. Every text() and fill() call sends its
# pixels straight down the wire to the glass, so there is no show() to call
# afterwards. What you draw is on the screen right away.
#
# Wiring is in config.py. Change pin numbers there, not here.

import config
import vga1_bold_16x32 as BIG_FONT   # 16 pixels wide, 32 tall, easy to read

try:
    display = config.init_display()
    display.fill(config.BLACK)

    # "Hello World!" is 12 letters, and each letter is 16 pixels wide, so
    # the whole line is 192 pixels. Half of that is 96. Start 96 pixels to
    # the left of the middle and the line lands exactly in the center.
    # The font is 32 pixels tall, so start 16 above the middle for the same
    # reason.
    text = "Hello World!"
    x = config.CENTER_X - (len(text) * BIG_FONT.WIDTH) // 2
    y = config.CENTER_Y - BIG_FONT.HEIGHT // 2
    display.text(BIG_FONT, text, x, y, config.WHITE, config.BLACK)

    print("Drew '{}' at x={}, y={}".format(text, x, y))
    print("Look at the display. Do you see Hello World?")
    print("TEST PASS")

except ImportError as error:
    print("Could not load a display file:", error)
    print("Run ./upload-code.sh again. It copies gc9a01.py and the fonts")
    print("into the :lib folder on the Pico.")
    print("TEST FAIL")
except OSError as error:
    print("Could not talk to the display:", error)
    print("Check the wiring table at the top of config.py.")
    print("TEST FAIL")
