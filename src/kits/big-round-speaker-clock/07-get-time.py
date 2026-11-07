# 07-get-time.py: Get the Time
# Sets the Pico's clock from an NTP (Network Time Protocol) server over
# WiFi, then shows the time in a simple digital format -- in the Thonny
# shell and on the screen -- once a second.
#
# The Pico W has no battery-backed clock. Each time it powers up its
# real-time clock (RTC) starts over in the past, unless something sets it.
# wifi_time.sync_time() does that:
#
#   1. joins the network in secrets.py
#   2. asks pool.ntp.org for the time, which always comes back in UTC
#   3. adds config.TIMEZONE_HOURS, plus an hour in summer if
#      config.USE_US_DST is True
#   4. writes it into the RTC and switches WiFi off again
#
# After that, time.localtime() gives local time with no network at all.
# Run 06-test-wifi.py first if the sync fails.

NAME = "07-get-time.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time

import config
import wifi_time

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

display = config.init_display()
display.fill(config.BLACK)
config.centered_text(display, config.BIG_FONT, "Getting time", 120,
                     config.CYAN)

# sync_time() prints each step, and shows it on the screen at y = 200.
ok = wifi_time.sync_time(display)
display.fill(config.BLACK)
if ok:
    print("Clock set from", wifi_time.ntptime.host)
    config.centered_text(display, config.SMALL_FONT, "set by NTP", 250,
                         config.GREEN)
else:
    print("Could not reach an NTP server -- showing the Pico's own clock,")
    print("which is wrong unless Thonny set it. Run 06-test-wifi.py.")
    config.centered_text(display, config.SMALL_FONT, "NOT synced", 250,
                         config.RED)

shown = None
while True:
    year, month, day, hour, minute, second, weekday = time.localtime()[:7]
    if second != shown:
        shown = second
        clock = "{:02d}:{:02d}:{:02d}".format(hour, minute, second)
        date = "{} {} {}, {}".format(DAYS[weekday], MONTHS[month - 1], day,
                                     year)
        print(date, clock)
        # Fixed-width strings, so each new one covers the last exactly.
        config.centered_text(display, config.BIG_FONT, clock, 150)
        config.centered_text(display, config.SMALL_FONT, date.center(20),
                             200, config.YELLOW)
    time.sleep_ms(50)

# Try This
#   1. Change TIMEZONE_HOURS in config.py to 0. Now the clock shows UTC,
#      the time the NTP server really sent.
#   2. Show a 12-hour clock: use (hour % 12 or 12) instead of hour, and
#      add "AM" if hour < 12 else "PM".
