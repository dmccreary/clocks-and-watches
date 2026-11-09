# holidays.py -- US holidays for any year, worked out from rules.
# Copied from the big-round-speaker-clock kit; lab 14 uses it.
#
# Most holidays are not on a fixed date. Thanksgiving is "the fourth
# Thursday in November"; Memorial Day is "the last Monday in May"; Easter
# is the first Sunday after the first full moon of spring. So instead of a
# list of dates that runs out, this module keeps the RULES and works the
# dates out for whatever year you ask about:
#
#     import holidays
#     holidays.for_month(2026, 11)
#     # [(11, "Veterans Day", True), (26, "Thanksgiving", True)]
#     #   (day, name, is it a federal holiday?)
#     holidays.upcoming(2026, 11, 6, 3)
#     # [(2026, 11, 11, "Veterans Day", True), ...]   the next three
#
# It uses only arithmetic, no time module, so it runs the same on the Pico
# and on a computer -- handy for testing.

# (month, rule, name, federal). A rule is one of:
#   ("date", day)              the same day every year
#   ("nth", weekday, n)        the n-th weekday of the month (n = -1: last)
#   ("easter", offset)         days after Easter Sunday
# Weekdays are numbered like time.localtime(): Monday 0 ... Sunday 6.
MON, TUE, WED, THU, FRI, SAT, SUN = range(7)
RULES = (
    (1, ("date", 1), "New Year's Day", True),
    (1, ("nth", MON, 3), "MLK Jr. Day", True),
    (2, ("date", 14), "Valentine's Day", False),
    (2, ("nth", MON, 3), "Presidents' Day", True),
    (3, ("date", 17), "St. Patrick's", False),
    (0, ("easter", 0), "Easter", False),          # month worked out
    (5, ("nth", SUN, 2), "Mother's Day", False),
    (5, ("nth", MON, -1), "Memorial Day", True),
    (6, ("nth", SUN, 3), "Father's Day", False),
    (6, ("date", 19), "Juneteenth", True),
    (7, ("date", 4), "Independence Day", True),
    (9, ("nth", MON, 1), "Labor Day", True),
    (10, ("nth", MON, 2), "Columbus Day", True),
    (10, ("date", 31), "Halloween", False),
    (11, ("date", 11), "Veterans Day", True),
    (11, ("nth", THU, 4), "Thanksgiving", True),
    (12, ("date", 24), "Christmas Eve", False),
    (12, ("date", 25), "Christmas", True),
    (12, ("date", 31), "New Year's Eve", False),
)

MONTH_NAMES = ("January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November",
               "December")


def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def days_in_month(year, month):
    if month == 2:
        return 29 if is_leap(year) else 28
    return 30 if month in (4, 6, 9, 11) else 31


def weekday(year, month, day):
    """Monday 0 ... Sunday 6, by Sakamoto's method (which counts from
    Sunday, hence the shift at the end)."""
    offsets = (0, 3, 2, 5, 0, 3, 5, 1, 4, 6, 2, 4)
    y = year - 1 if month < 3 else year
    sunday_first = (y + y // 4 - y // 100 + y // 400
                    + offsets[month - 1] + day) % 7
    return (sunday_first + 6) % 7


def nth_weekday(year, month, wday, n):
    """Day of the month of the n-th `wday` (n = -1 for the last one)."""
    if n > 0:
        first = weekday(year, month, 1)
        return 1 + (wday - first) % 7 + 7 * (n - 1)
    last = days_in_month(year, month)
    return last - (weekday(year, month, last) - wday) % 7


def easter(year):
    """(month, day) of Easter Sunday: the "anonymous Gregorian" method,
    published in 1876. It works the moon's cycle out with whole numbers."""
    a = year % 19
    b, c = divmod(year, 100)
    d, e = divmod(b, 4)
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = (h + l - 7 * m + 114) % 31 + 1
    return month, day


def for_month(year, month):
    """[(day, name, federal), ...] for one month, in date order."""
    found = []
    for rule_month, rule, name, federal in RULES:
        kind = rule[0]
        if kind == "easter":
            m, d = easter(year)
            if m == month:
                found.append((d + rule[1], name, federal))
        elif rule_month == month:
            if kind == "date":
                found.append((rule[1], name, federal))
            else:
                found.append((nth_weekday(year, month, rule[1], rule[2]),
                              name, federal))
    found.sort()
    return found


def upcoming(year, month, day, count):
    """The next `count` holidays on or after this date, as
    (year, month, day, name, federal)."""
    result = []
    while len(result) < count:
        for d, name, federal in for_month(year, month):
            if d >= day:
                result.append((year, month, d, name, federal))
                if len(result) == count:
                    break
        month += 1
        if month > 12:
            month = 1
            year += 1
        day = 1
    return result
