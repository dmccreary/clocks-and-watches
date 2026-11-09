# Lab 06: Set the Clock from the Internet
# Connects the Pico 2 W to WiFi, asks a time server for the current time,
# converts it to your time zone, and stores it in the Pico's real-time
# clock (RTC). When it works, the speaker plays a happy chime.
#
# Before you run this:
#   1. Copy secrets-template.py to secrets.py and put your WiFi name and
#      password in it. secrets.py is in .gitignore, so it never gets
#      committed.
#   2. Set TIMEZONE_HOURS in config.py (Central is -6).
#   3. Upload secrets.py to the Pico (upload-code.sh does this for you).
#
# The RTC keeps counting through a soft reset, so after this lab runs you
# can start lab 07 and it will show the right time -- until the Pico
# loses power. The clock in lab 16 runs this same sync by itself at
# power-up; see SYNC_WITH_WIFI at the top of that file.
#
# This is the first lab that uses sound.py instead of talking to the
# amplifier directly. sound.play("chime") returns at once and the notes
# play in the background, so the screen can change while you listen.

NAME = "06-wifi-sync-time.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import config
import sound
import wifi_time

display = config.init_display()
display.fill(config.BLACK)
config.centered_text(display, config.BIG_FONT, "Set the clock", 24,
                     config.CYAN)
config.centered_text(display, config.SMALL_FONT, "from the internet", 64,
                     config.GRAY)

sound.init()

# sync_time() prints each step to the Thonny shell and also shows it on
# the display (on row wifi_time.STATUS_Y), so you can watch it work
# without a computer.
if wifi_time.sync_time(display):
    sound.play("chime")
    t = time.localtime()
    config.centered_text(display, config.BIG_FONT,
                         "%2d:%02d %s" % (t[3] % 12 or 12, t[4],
                                          "AM" if t[3] < 12 else "PM"),
                         150, config.GREEN)
    config.centered_text(display, config.SMALL_FONT,
                         "%d-%02d-%02d" % (t[0], t[1], t[2]), 196)
else:
    sound.play("wrong")
    config.centered_text(display, config.BIG_FONT, "Not set", 150,
                         config.RED)
    config.centered_text(display, config.SMALL_FONT,
                         "Check secrets.py and TIMEZONE_HOURS", 196)

sound.wait()        # let the last note finish before the program ends
sound.deinit()
