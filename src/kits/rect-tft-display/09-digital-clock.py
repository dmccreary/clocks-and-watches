# Lab 09: Digital Clock
# Shows the time in big digits, the way a bedside clock does: hours and
# minutes on a 12-hour clock, a colon that blinks once a second, and AM
# or PM underneath. The day of the week goes above the time and the date
# below it. All of it is read from the Pico's real-time clock with
# time.localtime().
#
# Where does the time come from? The Pico 2 W has no battery-backed
# clock. Thonny sets the Pico's clock from your computer every time it
# connects, so this lab shows the right local time while you run it from
# Thonny. Unplug the Pico and the time is lost -- run lab 10 to set it
# from the internet instead.
#
# Even the big font is small for a clock you read from across the room,
# so the digits are built the way a calculator builds them: out of seven
# bars, called segments. Each bar is one filled rectangle.
#
#      aaaa
#     f    b
#     f    b
#      gggg
#     e    c
#     e    c
#      dddd
#
# A "1" lights b and c. An "8" lights all seven.
#
# There is no show() on this display, and no frame buffer to hide the
# drawing in. So this lab never clears the screen. It redraws a digit
# only when it changes, and the day and the date only at midnight -- most
# seconds, nothing moves but the colon. Lab 13 takes the idea further and
# repaints only the bars that change.

NAME = "09-digital-clock.py"
VERSION = "1.1"
print("{} v{}".format(NAME, VERSION))

import time
import config

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday",
        "Friday", "Saturday", "Sunday")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")

DIGIT_COLOR = config.WHITE
AMPM_COLOR = config.CYAN
TEXT_COLOR = config.YELLOW

DIGIT_WIDTH = 28
DIGIT_HEIGHT = 60
THICKNESS = 6           # how thick each bar is
GAP = 6                 # space between digits

SMALL = config.SMALL_FONT

DAY_Y = 4
TOP = 24                # the row the digits start on
AMPM_Y = TOP + DIGIT_HEIGHT + 4
DATE_Y = 108

# Left to right: hour tens, hour ones, the colon, minute tens, minute
# ones. Work out where each one starts so the whole row is centered.
ROW_WIDTH = 4 * DIGIT_WIDTH + THICKNESS + 4 * GAP
LEFT = (config.WIDTH - ROW_WIDTH) // 2
STEP = DIGIT_WIDTH + GAP
COLON_X = LEFT + 2 * STEP
DIGIT_X = (LEFT, LEFT + STEP,
           COLON_X + THICKNESS + GAP, COLON_X + THICKNESS + GAP + STEP)

# Where each bar sits inside a digit: (x, y, width, height).
HALF = DIGIT_HEIGHT // 2
SEGMENTS = {
    "a": (0, 0, DIGIT_WIDTH, THICKNESS),
    "b": (DIGIT_WIDTH - THICKNESS, 0, THICKNESS, HALF),
    "c": (DIGIT_WIDTH - THICKNESS, HALF, THICKNESS, HALF),
    "d": (0, DIGIT_HEIGHT - THICKNESS, DIGIT_WIDTH, THICKNESS),
    "e": (0, HALF, THICKNESS, HALF),
    "f": (0, 0, THICKNESS, HALF),
    "g": (0, HALF - THICKNESS // 2, DIGIT_WIDTH, THICKNESS),
}

# Which bars are lit for each digit, 0 to 9.
DIGITS = ("abcdef", "bc", "abdeg", "abcdg", "bcfg",
          "acdfg", "acdefg", "abc", "abcdefg", "abcdfg")

display = config.init_display()
display.fill(config.BLACK)


def draw_digit(position, digit):
    """Draw a digit, 0 to 9, in one of the four positions. None is a blank."""
    x = DIGIT_X[position]
    display.fill_rect(x, TOP, DIGIT_WIDTH, DIGIT_HEIGHT, config.BLACK)
    if digit is None:
        return
    for name in DIGITS[digit]:
        dx, dy, width, height = SEGMENTS[name]
        display.fill_rect(x + dx, TOP + dy, width, height, DIGIT_COLOR)


def draw_colon(visible):
    """Draw the two dots of the colon, or paint them out."""
    color = DIGIT_COLOR if visible else config.BLACK
    display.fill_rect(COLON_X, TOP + 17, THICKNESS, THICKNESS, color)
    display.fill_rect(COLON_X, TOP + 37, THICKNESS, THICKNESS, color)


if time.localtime()[0] < 2025:
    print("The Pico's clock has not been set. Connect with Thonny, which")
    print("sets it from your computer, or run lab 10 to set it over WiFi.")

shown = [-1, -1, -1, -1]        # the digit in each position; -1 is "not drawn yet"
last_second = -1
last_ampm = ""
last_day = -1

while True:
    # localtime() -> (year, month, day, hour, minute, second, weekday, yearday)
    year, month, day, hour, minute, second, weekday, _ = time.localtime()

    if second != last_second:
        last_second = second

        hour12 = hour % 12 or 12            # 0 -> 12, 13 -> 1, ...
        digits = (hour12 // 10 or None,     # no leading zero: " 9:05"
                  hour12 % 10,
                  minute // 10,
                  minute % 10)
        for position in range(4):
            if digits[position] != shown[position]:
                shown[position] = digits[position]
                draw_digit(position, digits[position])

        draw_colon(second % 2 == 0)

        ampm = "AM" if hour < 12 else "PM"
        if ampm != last_ampm:
            last_ampm = ampm
            config.centered_text(display, SMALL, ampm, AMPM_Y, AMPM_COLOR)

    if day != last_day:
        last_day = day
        # Day and month names change length ("Friday" -> "Saturday"), so
        # the old text can stick out past the new text. Clear the row
        # first.
        display.fill_rect(0, DAY_Y, config.WIDTH, SMALL.HEIGHT, config.BLACK)
        config.centered_text(display, SMALL, DAYS[weekday], DAY_Y, TEXT_COLOR)
        display.fill_rect(0, DATE_Y, config.WIDTH, SMALL.HEIGHT, config.BLACK)
        config.centered_text(display, SMALL,
                             "%s %d, %d" % (MONTHS[month - 1], day, year),
                             DATE_Y, TEXT_COLOR)

    time.sleep_ms(100)
