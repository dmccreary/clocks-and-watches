#!/usr/bin/env bash
# Upload every SHT40 lesson onto the Pico's flash filesystem.
#
# Every file this kit needs lives in this same folder, next to this
# script: config.py, the numbered lesson programs, and lib/ (the round
# display driver, its fonts, and the helper files the display modes share).
#
# The six-mode display (lab 09) is also copied to the Pico as main.py.
# A Pico runs main.py by itself every time it powers up, so the display works
# with the USB cable plugged into a plain phone charger and no computer at
# all. To make a different lab start by itself, change MAIN_LAB below.
#
# Usage:
#     ./upload-code.sh                  # find the board automatically
#     PORT=/dev/cu.usbmodem14301 ./upload-code.sh   # name the port yourself
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="$SCRIPT_DIR"

# This lab becomes main.py on the Pico.
MAIN_LAB="09-smartwatch-modes.py"

if [ ! -e "$SRC_DIR/config.py" ]; then
    echo "config.py is missing from:"
    echo "    $SRC_DIR"
    echo "Every lesson imports it, so nothing will run without it."
    exit 1
fi

# --- Look at every port on this Mac ---------------------------------
# macOS gives the Pico a different name depending on which USB jack you
# plug it into (/dev/cu.usbmodem101, ...14101, ...14301 and so on).  It
# also lists Bluetooth ports that are not boards at all.  So we print
# every /dev/cu.* port, then work out which one is really a Pico.

echo "Serial ports on this Mac:"
found_any_port=0
for port in /dev/cu.*; do
    [ -e "$port" ] || continue
    found_any_port=1
    echo "    $port"
done

if [ "$found_any_port" = "0" ]; then
    echo "    (none)"
fi
echo

# mpremote devs prints one line per port:
#     <port> <serial number> <vid:pid> <description>
# A real USB board has a true vid:pid such as 2e8a:0005 (Raspberry Pi).
# Bluetooth and other fake ports report 0000:0000, so we skip those.
find_boards() {
    mpremote devs 2>/dev/null | while read -r port serial vidpid rest; do
        case "$port" in
            /dev/cu.Bluetooth*|/dev/cu.BLTH*|/dev/cu.debug*|/dev/cu.wlan*)
                continue
                ;;
        esac
        if [ "$vidpid" = "0000:0000" ] || [ -z "$vidpid" ]; then
            continue
        fi
        echo "$port"
    done
}

if [ -n "$PORT" ]; then
    # The user told us which port to use, so trust them.
    BOARDS="$PORT"
else
    BOARDS="$(find_boards)"
fi

# Count how many boards we found.  grep -c . counts non-empty lines.
BOARD_COUNT="$(printf '%s\n' "$BOARDS" | grep -c . || true)"

if [ "$BOARD_COUNT" -eq 0 ]; then
    echo "No Pico found on any port."
    echo
    echo "Things to check:"
    echo "  1. Is the Pico plugged into USB?"
    echo "  2. Does it have MicroPython installed? A brand new Pico does not."
    echo "  3. Try a different USB cable. Some cheap cables only carry power."
    exit 1
fi

if [ "$BOARD_COUNT" -gt 1 ]; then
    echo "Found more than one board:"
    printf '%s\n' "$BOARDS" | sed 's/^/    /'
    echo
    echo "Pick the one you want and run the script again, like this:"
    echo "    PORT=$(printf '%s\n' "$BOARDS" | head -n 1) ./upload-code.sh"
    exit 1
fi

PORT="$(printf '%s\n' "$BOARDS" | head -n 1)"

if [ ! -e "$PORT" ]; then
    echo "The port $PORT disappeared. Unplug the Pico, plug it back in,"
    echo "then run this script again."
    exit 1
fi

echo "Found a board at $PORT"

# --- Make sure the port is free -------------------------------------
# Thonny, the Arduino IDE and screen all hold the port open while they
# are connected, and only one program can use it at a time.
if ! mpremote connect "$PORT" eval "1" >/dev/null 2>&1; then
    echo
    echo "The board is there, but something else is using the port."
    echo
    echo "Close Thonny (or click its red Stop button), close any other"
    echo "serial monitor, then run this script again."
    exit 1
fi

# --- Copy the lesson files ------------------------------------------
echo "Uploading to $PORT ..."

upload_count=0

# The helper files go into the :lib folder on the Pico. MicroPython looks
# in :lib on its own when a program says "import gc9a01", so the labs need
# no special path. The display labs (06, 07 and 09) fail to import without
# these, so lib goes before the lessons.
if ls "$SRC_DIR"/lib/*.py >/dev/null 2>&1; then
    # mkdir fails if :lib is already there, which is fine.
    mpremote connect "$PORT" fs mkdir :lib >/dev/null 2>&1 || true
    for f in "$SRC_DIR"/lib/*.py; do
        name="$(basename "$f")"
        echo "    lib/$name"
        mpremote connect "$PORT" fs cp "$f" ":lib/$name" >/dev/null
        upload_count=$((upload_count + 1))
    done
fi

# config.py holds every pin number the lessons use, so it goes next.
# Without it the programs that import config will not start.
if [ -e "$SRC_DIR/config.py" ]; then
    echo "    config.py"
    mpremote connect "$PORT" fs cp "$SRC_DIR/config.py" :config.py >/dev/null
    upload_count=$((upload_count + 1))
fi

for f in "$SRC_DIR"/[0-9][0-9]-*.py; do
    [ -e "$f" ] || continue
    name="$(basename "$f")"
    echo "    $name"
    mpremote connect "$PORT" fs cp "$f" ":$name" >/dev/null
    upload_count=$((upload_count + 1))
done

if [ "$upload_count" -eq 0 ]; then
    echo "No lesson files found in $SRC_DIR"
    exit 1
fi

# The six-mode display lab, saved a second time under the name main.py.
if [ -e "$SRC_DIR/$MAIN_LAB" ]; then
    echo "    main.py  (a copy of $MAIN_LAB)"
    mpremote connect "$PORT" fs cp "$SRC_DIR/$MAIN_LAB" :main.py >/dev/null
    upload_count=$((upload_count + 1))
fi

echo
echo "Uploaded $upload_count files. Files now on the Pico:"
mpremote connect "$PORT" fs ls
mpremote connect "$PORT" fs ls :lib

echo
echo "Next step: open Thonny and run 01-i2c-scanner.py"
echo "Unplug the Pico and plug it back in to start the display on its own."
