# 06-test-wifi.py: WiFi Test
# Checks the two files the clock needs before it can set itself from the
# internet, then joins your WiFi network:
#
#   1. secrets.py   exists, and has wifi_ssid and wifi_pass filled in
#                   (not the "your-network-name" placeholders)
#   2. config.py    has CITY, TIMEZONE_HOURS and USE_US_DST
#   3. WiFi         is your network in range, and does the password work?
#
# Everything is printed to the Thonny shell. Nothing is drawn, so this
# works even before the display is wired.
#
# The Pico W only connects to 2.4 GHz networks. If your router has one
# name for both bands, that is fine; if it has a separate 5 GHz name, use
# the 2.4 GHz one.

NAME = "06-test-wifi.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import time
import network

problems = []


def problem(message):
    problems.append(message)
    print("  PROBLEM:", message)


# ---------------------------------------------------------------------
print()
print("1. secrets.py")
# ---------------------------------------------------------------------
secrets = None
try:
    import secrets
except ImportError:
    problem("there is no secrets.py on the Pico. On your computer run "
            "'cp secrets-template.py secrets.py', edit it, and upload it.")

if secrets is not None:
    ssid = getattr(secrets, "wifi_ssid", None)
    password = getattr(secrets, "wifi_pass", None)
    if not ssid:
        problem("secrets.py has no wifi_ssid")
    elif ssid == "your-network-name":
        problem("wifi_ssid is still the template's placeholder")
    else:
        print("  ok  wifi_ssid = '{}'".format(ssid))
    if not password:
        problem("secrets.py has no wifi_pass")
    elif password == "your-network-password":
        problem("wifi_pass is still the template's placeholder")
    elif len(password) < 8:
        problem("wifi_pass is {} characters; WPA2 passwords are at least 8"
                .format(len(password)))
    else:
        # Never print the password itself.
        print("  ok  wifi_pass is set ({} characters)".format(len(password)))

# ---------------------------------------------------------------------
print()
print("2. config.py")
# ---------------------------------------------------------------------
config = None
try:
    import config
except ImportError as error:
    problem("config.py could not be imported: {}".format(error))

if config is not None:
    city = getattr(config, "CITY", None)
    if city:
        print("  ok  CITY = '{}'".format(city))
    else:
        problem("config.py has no CITY")

    zone = getattr(config, "TIMEZONE_HOURS", None)
    if isinstance(zone, (int, float)) and -12 <= zone <= 14:
        print("  ok  TIMEZONE_HOURS = {}".format(zone))
    else:
        problem("TIMEZONE_HOURS should be a number from -12 to 14, not {}"
                .format(zone))

    dst = getattr(config, "USE_US_DST", None)
    if dst in (True, False):
        print("  ok  USE_US_DST = {}".format(dst))
    else:
        problem("USE_US_DST should be True or False, not {}".format(dst))

    for name in ("LATITUDE", "LONGITUDE"):
        if not hasattr(config, name):
            problem("config.py has no {} (needed for the weather clock)"
                    .format(name))

# ---------------------------------------------------------------------
print()
print("3. WiFi")
# ---------------------------------------------------------------------
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
print("  MAC address:", ":".join("{:02x}".format(b)
                                 for b in wlan.config("mac")))

STATUS = {
    network.STAT_IDLE: "idle",
    network.STAT_CONNECTING: "connecting",
    network.STAT_WRONG_PASSWORD: "wrong password",
    network.STAT_NO_AP_FOUND: "network not found",
    network.STAT_CONNECT_FAIL: "connection failed",
    network.STAT_GOT_IP: "connected",
}

secrets_ok = secrets is not None and not any(
    "secrets.py" in p or "wifi_" in p for p in problems)
if not secrets_ok:
    print("  skipped until secrets.py is fixed")
else:
    found = wlan.scan()
    mine = [n for n in found if n[0].decode() == secrets.wifi_ssid]
    if mine:
        print("  ok  '{}' is in range at {} dBm (-50 strong, -80 weak)"
              .format(secrets.wifi_ssid, mine[0][3]))
    else:
        print("  '{}' was not in the scan ({} networks seen) -- trying "
              "anyway, scans sometimes miss weak networks".format(
                  secrets.wifi_ssid, len(found)))

    print("  joining ...")
    started = time.ticks_ms()
    wlan.connect(secrets.wifi_ssid, secrets.wifi_pass)
    while not wlan.isconnected():
        if wlan.status() < 0:
            break
        if time.ticks_diff(time.ticks_ms(), started) > 15000:
            break
        time.sleep_ms(250)
    took = time.ticks_diff(time.ticks_ms(), started)

    if wlan.isconnected():
        ip, mask, gateway, dns = wlan.ifconfig()
        print("  ok  connected in {} ms".format(took))
        print("      IP {}  gateway {}  DNS {}".format(ip, gateway, dns))
        try:
            import socket
            address = socket.getaddrinfo("pool.ntp.org", 123)[0][-1]
            print("  ok  pool.ntp.org is at {}".format(address[0]))
        except OSError as error:
            problem("connected, but could not look up pool.ntp.org ({})"
                    .format(error))
    else:
        status = wlan.status()
        problem("could not join '{}': {} (status {})".format(
            secrets.wifi_ssid, STATUS.get(status, "unknown"), status))
    wlan.disconnect()
wlan.active(False)

# ---------------------------------------------------------------------
print()
if problems:
    print("{} problem(s) to fix:".format(len(problems)))
    for message in problems:
        print("  -", message)
else:
    print("All good. Run 07-get-time.py next.")
