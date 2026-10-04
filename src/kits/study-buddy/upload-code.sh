#!/usr/bin/env bash
# Upload the whole Study Buddy kit to a Raspberry Pi Pico 2 W wired to a
# 2.1" 360x360 GC9B72 round display and a MAX98357A speaker amplifier,
# using mpremote. Run from within this directory or from anywhere -- the
# script resolves its own location.
#
# Upload order matters, because later files import earlier ones:
#   1. lib/        -> :lib/   the GC9B72 driver, both font modules, shapes.py
#   2. config.py              every lab imports it
#   3. secrets.py             your WiFi name and password, if you made one
#   4. everything else        wifi_time.py, the modes, and the numbered labs
#
# The fonts are not optional. This driver has no built-in font, so
# config.py fails to import if lib/vga1_8x16.py and
# lib/vga1_bold_16x32.py are not on the board.
#
# secrets.py is in .gitignore, so it only exists if you created it from
# secrets-template.py. The template itself is never uploaded.
#
# IMPORTANT: Quit (or "Stop/Disconnect" from) Thonny before running this.
# Only one program can use the Pico's serial port at a time. If Thonny is
# connected, mpremote fails with:
#   "failed to access /dev/cu.usbmodem... (it may be in use by another program)"

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v mpremote >/dev/null 2>&1; then
    echo "Error: mpremote is not installed. Install with: pip install mpremote" >&2
    exit 1
fi

echo "NOTE: Quit or disconnect Thonny first -- only one program can use the"
echo "      Pico's serial port at a time."
echo

echo "Checking for connected Pico..."
# We pass the exact serial port to mpremote rather than using "connect auto",
# which only matches a fixed list of vendor/product IDs and silently reports
# "no device found" for boards it does not recognize.
#
# macOS renames the port every time you plug into a different USB jack, so
# find it instead of hard-coding it. Force one with:
#   PORT=/dev/cu.usbmodem14301 ./upload-code.sh
if [[ -n "${PORT:-}" ]]; then
    echo "Using device from PORT environment variable: $PORT"
else
    # macOS uses /dev/cu.usbmodem*; Linux uses /dev/ttyACM* or /dev/ttyUSB*.
    # (macOS also lists every Pico a second time as /dev/tty.usbmodem*.
    # That is the same board, so it is left out of the search.)
    shopt -s nullglob
    serial_devs=(
        /dev/cu.usbmodem*
        /dev/ttyACM*
        /dev/ttyUSB*
    )
    shopt -u nullglob
    if (( ${#serial_devs[@]} == 0 )); then
        echo "Error: No Pico detected (no usbmodem/ttyACM/ttyUSB device). Plug it in and try again." >&2
        exit 1
    fi
    PORT="${serial_devs[0]}"
    if (( ${#serial_devs[@]} > 1 )); then
        echo "Multiple serial devices found; using the first:"
        printf '  %s\n' "${serial_devs[@]}"
        echo "Override with: PORT=/dev/your-device ./upload-code.sh"
    fi
    echo "Using device: $PORT"
fi

upload() {
    local src="$1" dest="$2"
    echo "  -> ${dest#:}"
    if ! mpremote connect "$PORT" fs cp "$src" "$dest"; then
        echo >&2
        echo "Error: could not write to the Pico." >&2
        echo "If the port is 'in use by another program', QUIT or DISCONNECT" >&2
        echo "Thonny (or any other serial monitor) and run this script again." >&2
        exit 1
    fi
}

# Interrupt any running program (a main.py watch face, say) before copying.
mpremote connect "$PORT" soft-reset >/dev/null 2>&1 || true

shopt -s nullglob
lib_files=( lib/*.py )
all_files=( *.py )
shopt -u nullglob

echo "Uploading ${#lib_files[@]} file(s) to Pico :lib/ ..."
mpremote connect "$PORT" fs mkdir :lib >/dev/null 2>&1 || true
for f in "${lib_files[@]}"; do
    upload "$f" ":lib/$(basename "$f")"
done

echo "Uploading config.py ..."
upload config.py :config.py

if [[ -f secrets.py ]]; then
    echo "Uploading secrets.py ..."
    upload secrets.py :secrets.py
else
    echo "No secrets.py here -- skipping it. WiFi time sync needs one:"
    echo "cp secrets-template.py secrets.py, then edit it."
fi

echo "Uploading labs ..."
for f in "${all_files[@]}"; do
    case "$f" in
        config.py|secrets.py|secrets-template.py) continue ;;
    esac
    upload "$f" ":$f"
done

echo
echo "Done. Files on Pico:"
mpremote connect "$PORT" fs ls
mpremote connect "$PORT" fs ls :lib 2>/dev/null || true
