# Lab 02: Hardware Probe
# Checks everything about this kit that software can check, and prints a
# report to the Thonny shell. Run it first on a new board, and again any
# time something stops working -- it tells you whether the problem is
# the board, the files, the wiring, or your code.
#
#   1. Board and firmware   which chip, which MicroPython build, CPU speed
#   2. RAM                  how much there is, and whether a full-screen
#                           frame buffer would fit in it
#   3. Flash                chip size, filesystem space, every file on it
#   4. Kit files            is the driver, font, and config on the board?
#   5. Power and sensors    USB power, chip temperature, BOOTSEL button
#   6. WiFi                 MAC address, nearby networks, is yours there?
#   7. Real-time clock      has anything set the time yet?
#   8. Buttons              are MODE / UP / DOWN all reading "not pressed"?
#   9. SPI bus              the clock rate you asked for vs. what you got
#  10. Speaker              the I2S pin rule, the amplifier's gain pin, and
#                           three short beeps you can check by ear
#  11. Display              start it, time a full-screen fill, draw a
#                           summary you can check by eye
#
# Nothing here writes to flash or changes a setting, so it is always safe
# to run. The display and speaker checks are the parts that need your
# senses: neither the GC9B72 (its read-back pin, SDO, is not wired) nor
# the MAX98357A can report back to the Pico. If the screen shows four
# color bars and "Probe OK", the display works. If you hear three rising
# beeps, the speaker does. Set PLAY_BEEPS to False for a silent probe.

import gc
import os
import sys
import time
import binascii
import machine
from machine import Pin

NAME = "02-probe.py"
VERSION = "1.0"

PLAY_BEEPS = True    # False to skip the sound in section 11

warnings = []


def warn(message):
    """Record a problem for the summary at the end, and print it now."""
    warnings.append(message)
    print("  WARNING:", message)


def heading(title):
    print()
    print("=" * 56)
    print(title)
    print("=" * 56)


def kb(n):
    return "{:,} bytes ({:.1f} KB)".format(n, n / 1024)


def mb(n):
    return "{:.2f} MB".format(n / (1024 * 1024))


def exists(path):
    try:
        os.stat(path)
        return True
    except OSError:
        return False


print("{} v{}".format(NAME, VERSION))

# ---------------------------------------------------------------------
heading("1. Board and firmware")
# ---------------------------------------------------------------------
u = os.uname()
board = sys.implementation._machine
print("board     :", board)
print("build     :", getattr(sys.implementation, "_build", "unknown"))
print("MicroPython", u.release, "--", u.version)
print("CPU clock : {} MHz".format(machine.freq() // 1_000_000))
print("unique ID :", binascii.hexlify(machine.unique_id()).decode())

RESET_CAUSES = {}
for cause in ("PWRON_RESET", "WDT_RESET", "HARD_RESET", "SOFT_RESET",
              "DEEPSLEEP_RESET"):
    if hasattr(machine, cause):
        RESET_CAUSES[getattr(machine, cause)] = cause
cause = machine.reset_cause()
print("last reset:", RESET_CAUSES.get(cause, cause))

if "Pico W" not in board and "Pico 2 W" not in board:
    warn("this kit needs a Pico W or Pico 2 W, but this board is: " + board)
if cause == getattr(machine, "WDT_RESET", None):
    warn("the last reset was the watchdog -- a program hung or crashed")

# ---------------------------------------------------------------------
heading("2. RAM")
# ---------------------------------------------------------------------
# The chip has more RAM than MicroPython reports. Some of it holds the
# firmware's own variables, the stack, and the WiFi driver's buffers; the
# rest is the "heap", where every Python object lives.
if "RP2350" in board:
    print("chip SRAM : 520 KB (RP2350 datasheet)")
elif "RP2040" in board:
    print("chip SRAM : 264 KB (RP2040 datasheet)")

gc.collect()
free = gc.mem_free()
used = gc.mem_alloc()
print("heap total:", kb(free + used))
print("heap used :", kb(used))
print("heap free :", kb(free))

# The GC9B72 driver draws straight to the glass because a 360 x 360
# RGB565 frame buffer takes 259,200 bytes -- far more than a plain Pico
# has. Would one fit here? The only honest test is to try. It must be one
# unbroken block, so this also checks that memory is not fragmented.
FRAME_BYTES = 360 * 360 * 2
try:
    frame = bytearray(FRAME_BYTES)
    print("frame buf : fits -- a full 360x360 RGB565 screen needs",
          kb(FRAME_BYTES))
    del frame
except MemoryError:
    print("frame buf : does NOT fit -- a full 360x360 RGB565 screen needs",
          kb(FRAME_BYTES))
gc.collect()

if free < 100 * 1024:
    warn("less than 100 KB of heap free -- is a big program still loaded?")

# ---------------------------------------------------------------------
heading("3. Flash")
# ---------------------------------------------------------------------
# MicroPython only reports the filesystem part of the flash chip. The
# rest holds the firmware. To find the size of the whole chip, use a
# trick: the flash chip ignores address bits it does not have, so on a
# 4 MB chip, reading 4 MB past the start "wraps around" and returns the
# same bytes as the start. The smallest offset that wraps is the size.
# The flash is mapped into memory at 0x10000000, so this only reads.
XIP_BASE = 0x10000000


def flash_bytes(offset, count=64):
    return bytes(machine.mem8[XIP_BASE + offset + i] for i in range(count))


chip_size = None
start = flash_bytes(0)
for size_mb in (1, 2, 4, 8, 16):
    if size_mb == 16 or flash_bytes(size_mb * 1024 * 1024) == start:
        chip_size = size_mb * 1024 * 1024
        break
# (16 MB is the most the XIP window can address, so stop there.)

block_size, _, total_blocks, free_blocks = os.statvfs("/")[:4]
fs_total = block_size * total_blocks
fs_free = block_size * free_blocks
print("flash chip:", mb(chip_size), "(found by address wrap-around)")
print("firmware  :", mb(chip_size - fs_total),
      "reserved for MicroPython itself")
print("filesystem:", kb(fs_total))
print("  used    :", kb(fs_total - fs_free))
print("  free    :", kb(fs_free))

if fs_free < 64 * 1024:
    warn("less than 64 KB of flash free")

print()
print("Files on flash:")


def list_files(path="/", indent=1):
    for entry in sorted(os.ilistdir(path)):
        name, kind = entry[0], entry[1]
        full = path.rstrip("/") + "/" + name
        if kind == 0x4000:                     # a directory
            print("  " * indent + name + "/")
            list_files(full, indent + 1)
        else:
            size = entry[3] if len(entry) > 3 else os.stat(full)[6]
            print("  " * indent + "{:<28} {:>7,} bytes".format(name, size))


list_files()

# ---------------------------------------------------------------------
heading("4. Kit files")
# ---------------------------------------------------------------------
# Checked before importing config.py, because config.py imports the
# driver and both fonts -- if any of them is missing, the import itself
# would crash and this probe would never get to tell you which one.
REQUIRED = (
    ("lib/gc9b72.py", "the display driver"),
    ("lib/vga1_8x16.py", "the small font"),
    ("lib/vga1_bold_16x32.py", "the big font"),
    ("lib/shapes.py", "circles, polygons, and rings"),
    ("config.py", "pin numbers and settings"),
    ("wifi_time.py", "sets the clock over WiFi"),
    ("lib/watchparts.py", "digits, rings, text, buttons"),
)
for path, purpose in REQUIRED:
    if exists(path):
        print("  ok      {:<24} {}".format(path, purpose))
    else:
        print("  MISSING {:<24} {}".format(path, purpose))
        warn(path + " is not on the board -- run upload-code.sh")

has_secrets = exists("secrets.py")
if has_secrets:
    print("  ok      {:<24} {}".format("secrets.py", "your WiFi name and password"))
else:
    print("  none    {:<24} {}".format(
        "secrets.py", "optional -- only needed for WiFi time sync"))

# Sections 8-11 need the driver, both fonts, shapes, and config.py --
# the first five files above.
config = None
if all(exists(path) for path, _ in REQUIRED[:5]):
    import config
else:
    print()
    print("Skipping sections 8-11 (buttons, SPI, speaker, display) until the")
    print("missing files are uploaded.")

# ---------------------------------------------------------------------
heading("5. Power and sensors")
# ---------------------------------------------------------------------
# On a Pico 2 W the "is USB plugged in?" signal is wired to the WiFi
# chip, not to a normal GPIO. MicroPython calls that pin WL_GPIO2.
try:
    usb = Pin("WL_GPIO2", Pin.IN).value()
    print("USB power :", "yes" if usb else "no -- running on battery / VSYS")
except (ValueError, TypeError):
    print("USB power : cannot tell on this board")

# The battery voltage (VSYS) is NOT read here. On the Pico 2 W its ADC
# pin, GP29, is shared with the WiFi chip's clock line, and reading it
# while WiFi is in use can crash the radio.

# The chip's built-in temperature sensor is ADC channel 4. It measures
# the silicon, which runs a few degrees warmer than the room.
reading = machine.ADC(4).read_u16() * 3.3 / 65535
temp_c = 27 - (reading - 0.706) / 0.001721
print("chip temp : {:.1f} C ({:.1f} F)".format(temp_c, temp_c * 9 / 5 + 32))

try:
    import rp2
    print("BOOTSEL   :", "HELD" if rp2.bootsel_button() else "not pressed")
except (ImportError, AttributeError):
    pass

# ---------------------------------------------------------------------
heading("6. WiFi")
# ---------------------------------------------------------------------
try:
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    mac = binascii.hexlify(wlan.config("mac"), ":").decode()
    print("MAC       :", mac)
    print("scanning  : ...")
    found = wlan.scan()
    # scan() gives (ssid, bssid, channel, RSSI, security, hidden).
    # RSSI is signal strength in dBm: -50 is strong, -80 is weak.
    found = sorted(found, key=lambda net: net[3], reverse=True)
    print("networks  : {} found; strongest five:".format(len(found)))
    for net in found[:5]:
        name = net[0].decode() or "(hidden)"
        print("    {:>4} dBm  ch {:>2}  {}".format(net[3], net[2], name))

    if has_secrets:
        import secrets
        mine = [n for n in found if n[0].decode() == secrets.wifi_ssid]
        # A scan is a quick listen on each channel, so a weak network
        # (around -70 dBm or lower) is sometimes missed. Listen twice more
        # before calling it missing.
        for _ in range(2):
            if mine:
                break
            time.sleep(1)
            mine = [n for n in wlan.scan()
                    if n[0].decode() == secrets.wifi_ssid]
        if mine:
            print("your net  : '{}' is visible at {} dBm".format(
                secrets.wifi_ssid, mine[0][3]))
        else:
            warn("the network in secrets.py ('{}') was not found -- "
                 "check the spelling, and that it is 2.4 GHz".format(
                     secrets.wifi_ssid))
    wlan.active(False)
except Exception as error:
    warn("WiFi check failed: {}".format(error))

# ---------------------------------------------------------------------
heading("7. Real-time clock")
# ---------------------------------------------------------------------
t = time.localtime()
print("RTC time  : {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(*t[:6]))
if t[0] < 2025:
    # Thonny sets the RTC when it connects; mpremote does not. At
    # power-up the RTC starts from a fixed date in the past.
    warn("the RTC has not been set -- connect with Thonny, or sync over WiFi")

# ---------------------------------------------------------------------
if config is not None:
    heading("8. Buttons")
    # -----------------------------------------------------------------
    # Pull-ups hold every button at 1. A 0 here, with nobody touching
    # anything, means a button is being held, is wired to the wrong pin,
    # or its pin is shorted to GND.
    buttons = config.init_buttons()
    for label, pin_number, pin in zip(
            ("MODE", "UP", "DOWN"),
            (config.BUTTON_MODE_PIN, config.BUTTON_INCREMENT_PIN,
             config.BUTTON_DECREMENT_PIN),
            buttons):
        value = pin.value()
        state = "1 (not pressed)" if value else "0 (PRESSED or shorted)"
        print("  {:<5} GP{:<3} {}".format(label, pin_number, state))
        if not value:
            warn("{} button (GP{}) reads pressed".format(label, pin_number))
    print("  (an unconnected button also reads 1, so this cannot see a missing wire)")

    # -----------------------------------------------------------------
    heading("9. SPI bus")
    # -----------------------------------------------------------------
    spi = machine.SPI(config.SPI_ID, baudrate=config.BAUDRATE,
                      sck=Pin(config.SCK_PIN), mosi=Pin(config.MOSI_PIN))
    # The SPI object's text form includes the rate it really runs at.
    actual = int(str(spi).split("baudrate=")[1].split(",")[0])
    print("asked for : {:.1f} MHz".format(config.BAUDRATE / 1e6))
    print("got       : {:.1f} MHz".format(actual / 1e6))
    if actual != config.BAUDRATE:
        warn("SPI runs at {:.1f} MHz, not the {:.1f} MHz in config.py".format(
            actual / 1e6, config.BAUDRATE / 1e6))
    print("pins      : SCK GP{}  MOSI GP{}  RST GP{}  DC GP{}  CS GP{}  BL GP{}"
          .format(config.SCK_PIN, config.MOSI_PIN, config.RST_PIN,
                  config.DC_PIN, config.CS_PIN, config.BL_PIN))

    # -----------------------------------------------------------------
    heading("10. Speaker")
    # -----------------------------------------------------------------
    # What the Pico CAN check: the pin rule, that the I2S hardware starts,
    # and that it takes audio at the right speed. What it cannot check is
    # whether the amplifier and speaker are wired up, so it plays three
    # short rising beeps for you to listen for.
    lrc, bclk = config.I2S_LRC_PIN, config.I2S_BCLK_PIN
    print("pins      : LRC GP{}  BCLK GP{}  DIN GP{}  GAIN GP{}".format(
        lrc, bclk, config.I2S_DIN_PIN, config.I2S_GAIN_PIN))

    # MicroPython's I2S on the Pico needs LRC (it calls it "ws") on the pin
    # right after BCLK (it calls that "sck"). Break the rule and I2S()
    # raises an error, so test it first and say why.
    pin_rule_ok = lrc == bclk + 1
    if pin_rule_ok:
        print("pin rule  : ok -- LRC (GP{}) is one more than BCLK (GP{})"
              .format(lrc, bclk))
    else:
        warn("I2S needs LRC on the pin right after BCLK, but LRC is GP{} "
             "and BCLK is GP{}".format(lrc, bclk))

    gain_pin = config.set_gain()
    print("gain      : {} dB (GAIN pin GP{} set as {})".format(
        config.GAIN_DB, config.I2S_GAIN_PIN,
        "floating" if config.GAIN_DB == 9 else
        "high" if config.GAIN_DB == 6 else "low"))

    if not pin_rule_ok:
        print("beeps     : skipped until the pin rule is fixed")
    elif not PLAY_BEEPS:
        print("beeps     : skipped (PLAY_BEEPS is False)")
    else:
        import math
        import struct
        from machine import I2S

        RATE = 16000
        IBUF = 4096                       # bytes the I2S driver holds
        FADE = RATE // 100                # 10 ms fades so beeps don't click
        # Half of VOLUME keeps the probe from being startling.
        amplitude = int(32767 * config.VOLUME / 100 * 0.5)

        def beep(freq, ms):
            """16-bit mono samples of one sine-wave beep, then 40 ms quiet."""
            count = RATE * ms // 1000
            out = bytearray((count + RATE * 40 // 1000) * 2)
            for i in range(count):
                fade = min(1.0, i / FADE, (count - i) / FADE)
                value = int(amplitude * fade
                            * math.sin(2 * math.pi * freq * i / RATE))
                struct.pack_into("<h", out, i * 2, value)
            return out

        # C5, E5, G5 -- a rising major chord. 100 ms of silence at the end
        # lets the last beep finish before I2S is switched off.
        clip = b"".join(beep(f, 180) for f in (523, 659, 784))
        clip += bytes(RATE * 100 // 1000 * 2)
        audio_seconds = len(clip) / (RATE * 2)

        audio = None
        try:
            audio = I2S(0, sck=Pin(bclk), ws=Pin(lrc),
                        sd=Pin(config.I2S_DIN_PIN), mode=I2S.TX, bits=16,
                        format=I2S.MONO, rate=RATE, ibuf=IBUF)
            print("I2S       : started at {} Hz, 16-bit mono".format(RATE))
            print("beeps     : playing three rising beeps -- listen now")
            start_us = time.ticks_us()
            audio.write(clip)             # waits until the data is accepted
            took = time.ticks_diff(time.ticks_us(), start_us) / 1e6
            time.sleep_ms(IBUF * 1000 // (RATE * 2) + 50)  # drain the buffer

            # write() returns once the last bytes are in the buffer, which
            # is about one buffer-length (128 ms) before they finish playing.
            expected = audio_seconds - IBUF / (RATE * 2)
            print("timing    : {:.2f} s of audio accepted in {:.2f} s "
                  "(expected about {:.2f} s)".format(
                      audio_seconds, took, expected))
            if took < 0.8 * expected or took > 1.25 * audio_seconds:
                warn("I2S ran at the wrong speed -- the data is being taken "
                     "{:.2f} s instead of about {:.2f} s".format(took, expected))
        except Exception as error:
            warn("I2S failed: {}".format(error))
        finally:
            if audio is not None:
                audio.deinit()
        print("            (the Pico cannot hear -- no sound means check the "
              "amp's VIN and GND wires and the speaker)")

    # -----------------------------------------------------------------
    heading("11. Display")
    # -----------------------------------------------------------------
    start_us = time.ticks_us()
    display = config.init_display()
    init_ms = time.ticks_diff(time.ticks_us(), start_us) / 1000
    print("init      : {:.0f} ms (most of it is the controller's own"
          " required delays)".format(init_ms))

    start_us = time.ticks_us()
    display.fill(config.BLACK)
    fill_us = time.ticks_diff(time.ticks_us(), start_us)
    mbits = FRAME_BYTES * 8 / fill_us
    print("full fill : {:.1f} ms = {:.1f} Mbit/s delivered ({:.0f}% of the"
          " wire rate)".format(fill_us / 1000, mbits,
                               100 * mbits * 1e6 / actual))
    print("            so at most {:.0f} full-screen redraws per second".format(
        1e6 / fill_us))

    # Four color bars across the middle. If they come out in a different
    # order, or with red and blue swapped, the color order (MADCTL) is
    # wrong for this panel.
    bar_width = 60
    x = config.CENTER_X - 2 * bar_width
    for color in (config.RED, config.GREEN, config.BLUE, config.WHITE):
        display.fill_rect(x, 150, bar_width, 60, color)
        x += bar_width

    font = config.SMALL_FONT
    y = 225
    if warnings:
        config.centered_text(display, config.BIG_FONT, "Probe: {} warn".format(
            len(warnings)), 95, config.YELLOW)
        # 28 characters of the small font is 224 px -- about as wide as
        # the circle gets this far below the center.
        for message in warnings[:4]:
            config.centered_text(display, font, message[:28], y, config.YELLOW)
            y += 18
    else:
        config.centered_text(display, config.BIG_FONT, "Probe OK", 95,
                             config.GREEN)
        config.centered_text(display, font, "RAM {} KB free".format(
            free // 1024), y)
        config.centered_text(display, font, "Flash {} MB, {} KB free".format(
            chip_size // (1024 * 1024), fs_free // 1024), y + 18)
        config.centered_text(display, font, "SPI {:.0f} MHz, {:.0f} ms fill".format(
            actual / 1e6, fill_us / 1000), y + 36)
    print("check the screen: red, green, blue, and white bars, left to right")

# ---------------------------------------------------------------------
heading("Summary")
# ---------------------------------------------------------------------
if warnings:
    print("{} warning(s):".format(len(warnings)))
    for message in warnings:
        print("  -", message)
else:
    print("Everything software can check looks good.")
