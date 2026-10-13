# Lab 08: Backlight Test
# Checks the wiring of BLK, the pin that switches the screen's backlight.
#
# An LCD makes no light of its own. The picture is a layer of tiny
# shutters, and the backlight is a white light behind them. Switch the
# backlight off and the picture is still there -- it is just too dark to
# see.
#
# This lab fills the screen with white, then switches the backlight off
# and on five times, one second each. The Thonny shell says which it is:
#
#   backlight OFF
#   backlight ON
#
# The screen should go dark every time the shell says OFF. The lab ends
# with the backlight on.
#
# BLK is on GP7. If the screen stays lit the whole time, BLK is not on
# GP7 -- fix BL_PIN in config.py. Many display boards light the backlight
# by themselves when nothing is driving BLK, so a wrong pin looks like
# "always on", not "always off".

NAME = "08-backlight-test.py"
VERSION = "1.1"
print("{} v{}".format(NAME, VERSION))

import time
import config

display = config.init_display()

display.fill(config.WHITE)
config.centered_text(display, config.SMALL_FONT, "Backlight Test", 44,
                     config.BLACK, config.WHITE)
config.centered_text(display, config.SMALL_FONT,
                     "BLK on GP{}".format(config.BL_PIN), 66,
                     config.BLACK, config.WHITE)

for i in range(5):
    print("backlight OFF")
    config.set_backlight(False)
    time.sleep(1)
    print("backlight ON")
    config.set_backlight(True)
    time.sleep(1)

print("Done. The backlight is on.")
