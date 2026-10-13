# wifi_time.py -- set the Pico 2 W's clock from the internet.
#
# The Pico has no battery-backed clock. Every time it powers up, its
# real-time clock (RTC) starts over at midnight, January 1st -- unless
# something sets it. Thonny sets it for you when it connects, which is
# why the time looks right while you are developing and wrong the first
# time you run on a battery. This module fixes that:
#
#   1. connect to WiFi using the network in secrets.py
#   2. ask an NTP (Network Time Protocol) server for the time
#   3. shift it from UTC to your time zone (config.TIMEZONE_HOURS),
#      including US daylight saving time if config.USE_US_DST is True
#   4. write the result into the RTC, then turn WiFi back off
#
# After sync_time() returns True, time.localtime() gives local time.
#
#     import wifi_time
#     if wifi_time.sync_time():
#         print("clock set")

import time
import network
import ntptime
from machine import RTC

import config


def _status(display, message):
    """Print a progress message, and show it on the display if we have one."""
    print(message)
    if display is not None:
        display.fill_rect(0, 200, config.WIDTH, 16, config.BLACK)
        config.centered_text(display, config.SMALL_FONT, message, 200)


def connect(display=None, timeout_s=15):
    """Join the WiFi network in secrets.py. Returns the WLAN object, or
    None if secrets.py is missing or the network never answers."""
    try:
        import secrets
    except ImportError:
        _status(display, "No secrets.py on the Pico")
        return None

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        return wlan

    _status(display, "Joining " + secrets.wifi_ssid)
    wlan.connect(secrets.wifi_ssid, secrets.wifi_pass)

    start = time.ticks_ms()
    while not wlan.isconnected():
        # status() below 0 means the connection failed outright (wrong
        # password, no such network) -- no point waiting out the timeout.
        if wlan.status() < 0:
            break
        if time.ticks_diff(time.ticks_ms(), start) > timeout_s * 1000:
            break
        time.sleep_ms(250)

    if not wlan.isconnected():
        _status(display, "WiFi failed, status " + str(wlan.status()))
        wlan.active(False)
        return None

    _status(display, "IP " + wlan.ifconfig()[0])
    return wlan


def _sunday_on_or_after(year, month, day):
    """Day of the month of the first Sunday on or after year-month-day.
    localtime()[6] is the weekday: Monday is 0, Sunday is 6."""
    weekday = time.localtime(time.mktime((year, month, day, 0, 0, 0, 0, 0)))[6]
    return day + (6 - weekday) % 7


def is_us_dst(utc_seconds, timezone_hours):
    """True if US daylight saving time is in effect at this UTC moment.

    DST starts at 2:00 AM standard time on the second Sunday in March
    (the first Sunday on or after March 8) and ends at 2:00 AM daylight
    time on the first Sunday in November. Both edges are converted to
    UTC so they can be compared against the NTP time directly."""
    year = time.gmtime(utc_seconds)[0]
    start_day = _sunday_on_or_after(year, 3, 8)
    end_day = _sunday_on_or_after(year, 11, 1)
    start = time.mktime((year, 3, start_day, 2, 0, 0, 0, 0)) - timezone_hours * 3600
    end = time.mktime((year, 11, end_day, 2, 0, 0, 0, 0)) - (timezone_hours + 1) * 3600
    return start <= utc_seconds < end


def utc_offset_hours(utc_seconds):
    """Hours to add to UTC to get local time, right now."""
    offset = config.TIMEZONE_HOURS
    if config.USE_US_DST and is_us_dst(utc_seconds, config.TIMEZONE_HOURS):
        offset += 1
    return offset


def sync_time(display=None, tries=3):
    """Set the RTC to local time from an NTP server. Returns True on success.

    Pass the display to see progress messages on the screen as well as
    in the Thonny shell."""
    wlan = connect(display)
    if wlan is None:
        return False

    ok = False
    for attempt in range(1, tries + 1):
        try:
            _status(display, "Asking " + ntptime.host)
            ntptime.settime()          # sets the RTC to UTC
            ok = True
            break
        except OSError as error:
            _status(display, "NTP try %d failed: %s" % (attempt, error))
            time.sleep(2)

    # A watch does not need WiFi between syncs, and the radio is the
    # biggest power draw on the board.
    wlan.disconnect()
    wlan.active(False)

    if not ok:
        return False

    utc = time.time()
    local = time.localtime(utc + utc_offset_hours(utc) * 3600)
    # RTC().datetime() wants (year, month, day, weekday, hour, minute,
    # second, subseconds) -- a DIFFERENT order from localtime(), which
    # puts weekday after the seconds.
    RTC().datetime((local[0], local[1], local[2], local[6],
                    local[3], local[4], local[5], 0))
    _status(display, "Time set %02d:%02d:%02d" % (local[3], local[4], local[5]))
    return True
