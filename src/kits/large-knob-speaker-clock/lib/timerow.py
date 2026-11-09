# timerow.py -- a row of four seven-segment digits and a colon: HH:MM.
#
# Copied from the big-round-speaker-clock kit. Labs 13 and 15 show the
# time as big segment digits at different sizes. This class lays the row
# out from a digit size and draws it, repainting only the segments that
# change (lib/watchparts.py's Digit does the remembering).
#
#     row = TimeRow(display, (52, 100, 14), top=92)
#     row.show(hour, minute)               # hour is 0-23
#     row.show(hour, minute, colon=False)  # the colon "off" half of a blink
#
# size is (digit width, digit height, segment thickness), and the height
# must be 3 * thickness plus an even number.
#
# On a 12-hour clock the first digit is only ever 1 or blank, so it is a
# HALF digit -- just its right-hand column -- and the row is narrower.

import config
from watchparts import Digit, DIGITS, BLANK

GHOST = config.color565(22, 22, 28)      # the faint unlit segments

DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def date_text(t):
    """'Fri, Nov 6, 2026' from a time.localtime() tuple."""
    return "{}, {} {}, {}".format(DAYS[t[6]], MONTHS[t[1] - 1], t[2], t[0])


def ampm(hour):
    return "AM" if hour < 12 else "PM"


class TimeRow:
    def __init__(self, display, size, top, color=config.WHITE, ghost=GHOST,
                 twelve_hour=None):
        self.display = display
        self.twelve = config.TWELVE_HOUR if twelve_hour is None else twelve_hour
        width, height, thick = size
        pair_gap = max(4, width // 6)
        colon_gap = max(5, width * 3 // 16)
        first = thick if self.twelve else width
        row = first + 3 * width + 2 * pair_gap + 2 * colon_gap + thick
        x = (config.WIDTH - row) // 2
        self.left = x
        self.right = x + row
        self.top = top
        self.bottom = top + height
        self.thick = thick
        self.color = color
        self.ghost = ghost

        self.digits = [Digit(display, x, top, width, height, thick, color,
                             ghost, half=self.twelve)]
        x += first + pair_gap
        self.digits.append(Digit(display, x, top, width, height, thick, color,
                                 ghost))
        x += width + colon_gap
        self.colon_x = x
        x += thick + colon_gap
        for _ in range(2):
            self.digits.append(Digit(display, x, top, width, height, thick,
                                     color, ghost))
            x += width + pair_gap
        self.colon_y = (top + height // 3 - thick // 2,
                        top + 2 * height // 3 - thick // 2)
        self.forget()

    def forget(self):
        """After something paints over the row: repaint all of it next."""
        for digit in self.digits:
            digit.forget()
        self.shown_colon = None

    def show(self, hour, minute, colon=True, colors=None):
        """Show hour (0-23) and minute. colors is (hours color, minutes
        color), for picking out the part being set."""
        hour_color, minute_color = colors or (self.color, self.color)
        shown = (hour % 12 or 12) if self.twelve else hour
        tens = shown // 10
        first = DIGITS[tens] if (tens or not self.twelve) else BLANK
        self.digits[0].show(first, hour_color)
        self.digits[1].show(DIGITS[shown % 10], hour_color)
        self.digits[2].show(DIGITS[minute // 10], minute_color)
        self.digits[3].show(DIGITS[minute % 10], minute_color)
        key = (colon, hour_color)
        if key != self.shown_colon:
            for y in self.colon_y:
                self.display.fill_rect(self.colon_x, y, self.thick,
                                       self.thick,
                                       hour_color if colon else self.ghost)
            self.shown_colon = key
