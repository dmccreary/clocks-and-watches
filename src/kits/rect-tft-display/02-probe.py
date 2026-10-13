# Lab 02: Hardware Probe
# Checks everything about this kit that software can check, and prints a
# report to the Thonny shell. Run it first on a new board, and again any
# time something stops working -- it tells you whether the problem is
# the board, the files, the wiring, or your code.
#
#   1. Processor and firmware   which chip, which cores, which
#                               MicroPython build, CPU speed
#   2. RAM                      how much there is, and whether a
#                               full-screen frame buffer would fit in it
#   3. Flash                    chip size, filesystem space, every file
#   4. Kit files                is the driver, font, and config on the board?
#   5. Power and sensors        USB power, chip temperature, BOOTSEL button
#   6. WiFi                     MAC address, nearby networks, is yours there?
#   7. Real-time clock          has anything set the time yet?
#   8. Knob and button          are PUSH and K0 both reading "not pressed"?
#   9. SPI bus                  the clock rate you asked for vs. what you got
#  10. Display                  start it, time a full-screen fill, draw a
#                               summary you can check by eye
#
# Nothing here writes to flash or changes a setting, so it is always safe
# to run. The display check is the only part that needs your eyes: this
# board has no read-back pin, so the Pico cannot ask the display whether
# it is working. If the screen shows four color bars and "Probe OK", it
# is.

NAME = "02-probe.py"
VERSION = "1.1"
print("{} v{}".format(NAME, VERSION))

import gc
import os
import sys
import time
import binascii
import machine
from machine import Pin

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


# ---------------------------------------------------------------------
heading("1. Processor and firmware")
# ---------------------------------------------------------------------
u = os.uname()
board = sys.implementation._machine
print("board     :", board)

# The RP2350 carries two kinds of processor core on the same chip -- two
# ARM cores and two RISC-V cores -- and only one pair runs at a time. The
# MicroPython firmware you flashed decides which, and says so in its
# board name.
PROCESSORS = (
    ("RISCV", "RP2350, running its two Hazard3 RISC-V cores"),
    ("RP2350", "RP2350, running its two ARM Cortex-M33 cores"),
    ("RP2040", "RP2040, two ARM Cortex-M0+ cores"),
)
for marker, description in PROCESSORS:
    if marker in board:
        print("processor :", description)
        break

# MicroPython can compile Python down to the processor's own machine
# instructions, and records which instruction set it was built for.
INSTRUCTION_SETS = (
    "none", "x86", "x64", "armv6", "armv6m", "armv7m", "armv7em",
    "armv7emsp", "armv7emdp", "xtensa", "xtensawin", "rv32imc", "rv64imc")
code = (getattr(sys.implementation, "_mpy", 0) >> 10) & 0x3F
if 0 < code < len(INSTRUCTION_SETS):
    print("instr. set:", INSTRUCTION_SETS[code])

print("CPU clock : {} MHz".format(machine.freq() // 1_000_000))

# Every RP2 chip keeps an ID in the first register of its SYSINFO block.
# The top four bits are the silicon revision: how many times the chip's
# design has been revised since the first one.
chip_id = machine.mem32[0x40000000]
print("chip ID   : 0x{:08x} (silicon revision {})".format(
    chip_id, (chip_id >> 28) & 0xF))
print("unique ID :", binascii.hexlify(machine.unique_id()).decode())

print("build     :", getattr(sys.implementation, "_build", "unknown"))
print("MicroPython", u.release, "--", u.version)

RESET_CAUSES = {}
for cause in ("PWRON_RESET", "WDT_RESET", "HARD_RESET", "SOFT_RESET",
              "DEEPSLEEP_RESET"):
    if hasattr(machine, cause):
        RESET_CAUSES[getattr(machine, cause)] = cause
cause = machine.reset_cause()
print("last reset:", RESET_CAUSES.get(cause, cause))

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

# A frame buffer is a copy of the whole picture kept in RAM: draw into
# it, then send it to the glass in one go, and the screen never shows a
# half-drawn frame. This kit's driver draws straight to the glass
# instead, but a 160 x 128 RGB565 picture is only 40,960 bytes, so a
# frame buffer is an option here. Would one fit? The only honest test is
# to try. It must be one unbroken block, so this also checks that memory
# is not fragmented.
FRAME_BYTES = 160 * 128 * 2
try:
    frame = bytearray(FRAME_BYTES)
    print("frame buf : fits -- a full 160x128 RGB565 screen needs",
          kb(FRAME_BYTES))
    del frame
except MemoryError:
    print("frame buf : does NOT fit -- a full 160x128 RGB565 screen needs",
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
# driver and all three fonts -- if any of them is missing, the import
# itself would crash and this probe would never get to tell you which
# one.
REQUIRED = (
    ("lib/st7735s.py", "the display driver"),
    ("lib/vga1_8x8.py", "the tiny font"),
    ("lib/vga1_8x16.py", "the small font"),
    ("lib/vga1_bold_16x32.py", "the big font"),
    ("config.py", "pin numbers and settings"),
    ("lib/shapes.py", "circles, polygons, and rings"),
    ("lib/watchparts.py", "digits, ticks, text, buttons, knob"),
    ("wifi_time.py", "sets the clock over WiFi"),
    ("forecast.py", "gets the weather forecast"),
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

# Sections 8-10 need the driver, the three fonts, and config.py -- the
# first five files above.
config = None
if all(exists(path) for path, _ in REQUIRED[:5]):
    import config
else:
    print()
    print("Skipping sections 8-10 (knob and button, SPI, display) until")
    print("the missing files are uploaded.")

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
        if mine:
            print("your net  : '{}' is visible at {} dBm".format(
                secrets.wifi_ssid, mine[0][3]))
        else:
            warn("the network in secrets.py ('{}') was not found -- "
                 "check the spelling, and that it is 2.4 GHz".format(
                     secrets.wifi_ssid))
    wlan.active(False)
except ImportError:
    print("no WiFi   : this firmware has no network module")
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
    warn("the RTC has not been set -- run lab 10, or connect with Thonny")

# ---------------------------------------------------------------------
if config is not None:
    heading("8. Knob and button")
    # -----------------------------------------------------------------
    # Pull-ups hold PUSH and K0 at 1. A 0 here, with nobody touching
    # anything, means the switch is being held, is wired to the wrong
    # pin, or its pin is shorted to GND.
    a, b, push, k0 = config.init_controls()
    for label, pin_number, pin in (
            ("PUSH", config.ENCODER_PUSH_PIN, push),
            ("K0", config.BUTTON_K0_PIN, k0)):
        value = pin.value()
        state = "1 (not pressed)" if value else "0 (PRESSED or shorted)"
        print("  {:<5} GP{:<3} {}".format(label, pin_number, state))
        if not value:
            warn("{} (GP{}) reads pressed".format(label, pin_number))

    # A and B are only reported, not checked: they show where the knob
    # happened to stop, and depending on the knob that can be 1 or 0.
    for label, pin_number, pin in (
            ("A", config.ENCODER_A_PIN, a),
            ("B", config.ENCODER_B_PIN, b)):
        print("  {:<5} GP{:<3} {}".format(label, pin_number, pin.value()))
    print("  (an unconnected pin also reads 1 -- use labs 04, 05 and 06 to")
    print("   test the button and the knob properly)")

    # -----------------------------------------------------------------
    heading("9. SPI bus")
    # -----------------------------------------------------------------
    spi = config.init_spi()
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
    heading("10. Display")
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

    # Four color bars across the screen. If they come out in a different
    # order, or with red and blue swapped, the color order (BGR in
    # config.py) is wrong for this panel.
    bar_width = 30
    x = config.CENTER_X - 2 * bar_width
    for color in (config.RED, config.GREEN, config.BLUE, config.WHITE):
        display.fill_rect(x, 38, bar_width, 20, color)
        x += bar_width

    # The tiny font holds 20 characters on a line.
    font = config.TINY_FONT
    y = 66
    if warnings:
        config.centered_text(display, config.BIG_FONT,
                             "Warn: {}".format(len(warnings)), 2,
                             config.YELLOW)
        for message in warnings[:5]:
            config.centered_text(display, font, message[:20], y, config.YELLOW)
            y += 12
    else:
        config.centered_text(display, config.BIG_FONT, "Probe OK", 2,
                             config.GREEN)
        for line in (
                board.replace("Raspberry Pi ", "")[:20],
                "CPU {} MHz, {:.0f} C".format(
                    machine.freq() // 1_000_000, temp_c),
                "RAM {} KB free".format(free // 1024),
                "Flash {}MB {}K free".format(
                    chip_size // (1024 * 1024), fs_free // 1024),
                "SPI {:.0f}MHz, {:.0f}ms fill".format(
                    actual / 1e6, fill_us / 1000)):
            config.centered_text(display, font, line[:20], y)
            y += 12
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
