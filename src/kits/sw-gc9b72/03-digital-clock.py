# Lab 03: Digital Clock
# Shows the time, the day of the week, and the date, read from the Pico's
# real-time clock with time.localtime().
#
# Where does the time come from? The Pico 2 W has no battery-backed clock.
# Thonny sets the RTC from your computer every time it connects, so this
# lab shows the right time while you run it from Thonny. On battery power
# the clock starts from a default date instead -- run lab 04 to set it from
# the internet, or use lab 05, which can do that itself at power-up.
#
# There is no show() on this display, and no frame buffer to hide the
# drawing in. So this lab never clears the screen. It redraws only the
# text that changed, right on top of the old text: text() paints each
# character's background as well as its foreground, which erases the old
# digit underneath. That only works because "%2d:%02d:%02d" is always
# exactly 8 characters wide.

NAME = "03-digital-clock.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import config
import shapes

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

TIME_Y = 150     # 32 px tall big font, so rows 150-181 straddle the center
AMPM_Y = 190
DAY_Y = 108
DATE_Y = 228

# Width of the box cleared behind the day and date lines. Wide enough for
# the longest date ("September 30, 2026" is 18 x 8 = 144 px) but narrow
# enough to stay inside the blue ring, which a full-width clear would cut.
CLEAR_WIDTH = 200
CLEAR_X = (config.WIDTH - CLEAR_WIDTH) // 2

display = config.init_display()
display.fill(config.BLACK)
shapes.ring(display, config.CENTER_X, config.CENTER_Y,
            config.SAFE_RADIUS, config.BLUE, 3)

last_second = -1
last_day = -1

while True:
    # localtime() -> (year, month, day, hour, minute, second, weekday, yearday)
    year, month, day, hour, minute, second, weekday, _ = time.localtime()

    if second != last_second:
        last_second = second
        hour12 = hour % 12 or 12          # 0 -> 12, 13 -> 1, ...
        config.centered_text(display, config.BIG_FONT,
                             "%2d:%02d:%02d" % (hour12, minute, second),
                             TIME_Y)
        config.centered_text(display, config.SMALL_FONT,
                             "AM" if hour < 12 else "PM", AMPM_Y, config.CYAN)

    if day != last_day:
        last_day = day
        # Day and month names change length ("Friday" -> "Saturday"), so
        # the old text can stick out past the new text. Clear the row
        # first.
        display.fill_rect(CLEAR_X, DAY_Y, CLEAR_WIDTH, 16, config.BLACK)
        config.centered_text(display, config.SMALL_FONT, DAYS[weekday],
                             DAY_Y, config.YELLOW)
        display.fill_rect(CLEAR_X, DATE_Y, CLEAR_WIDTH, 16, config.BLACK)
        config.centered_text(display, config.SMALL_FONT,
                             "%s %d, %d" % (MONTHS[month - 1], day, year),
                             DATE_Y, config.YELLOW)

    time.sleep_ms(50)
