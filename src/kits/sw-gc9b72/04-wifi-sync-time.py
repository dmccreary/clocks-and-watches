# Lab 04: Set the Clock from the Internet
# Connects the Pico 2 W to WiFi, asks a time server for the current time,
# converts it to your time zone, and stores it in the Pico's real-time
# clock (RTC).
#
# Before you run this:
#   1. Copy secrets-template.py to secrets.py and put your WiFi name and
#      password in it. secrets.py is in .gitignore, so it never gets
#      committed.
#   2. Set TIMEZONE_HOURS in config.py (Central is -6).
#   3. Upload secrets.py to the Pico (upload-code.sh does this for you).
#
# The RTC keeps counting through a soft reset, so after this lab runs you
# can start lab 03 or lab 05 and they will show the right time -- until
# the Pico loses power. Lab 05 can run this same sync on its own at
# power-up; see SYNC_WITH_WIFI at the top of that file.

NAME = "04-wifi-sync-time.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import config
import wifi_time

display = config.init_display()
display.fill(config.BLACK)
config.centered_text(display, config.BIG_FONT, "Setting clock", 130)

# sync_time() prints each step to the Thonny shell and also shows it on
# the display at row 200, so you can watch it work without a computer.
if wifi_time.sync_time(display):
    t = time.localtime()
    config.centered_text(display, config.BIG_FONT,
                         "%02d:%02d:%02d" % (t[3], t[4], t[5]),
                         240, config.GREEN)
    config.centered_text(display, config.SMALL_FONT,
                         "%d-%02d-%02d" % (t[0], t[1], t[2]), 280)
else:
    config.centered_text(display, config.BIG_FONT, "Not set", 240,
                         config.RED)
    config.centered_text(display, config.SMALL_FONT,
                         "Check secrets.py", 280)
