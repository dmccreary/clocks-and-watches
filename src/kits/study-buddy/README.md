# Study Buddy kit

A Raspberry Pi Pico 2 W with a 2.1" round GC9B72 display, three buttons, and a
MAX98357A amplifier driving a speaker. It is the
[GC9B72 smartwatch kit](../sw-gc9b72) plus sound, with modes aimed at studying.
The design is in [docs/kits/study-buddy](../../../docs/kits/study-buddy/index.md).

## Wiring

The display and buttons are wired exactly as in the smartwatch kit.

| Part | Pico pins |
|---|---|
| Display (SCL, SDA, RST, DC, CS, BL) | GP2, GP3, GP4, GP5, GP6, GP7 (SPI0), plus 3V3 and GND |
| Buttons MODE, UP, DOWN | GP13, GP14, GP15, each with its other leg to GND |
| Amplifier LRC | GP21 |
| Amplifier BCLK | GP20 |
| Amplifier DIN | GP19 |
| Amplifier GAIN | GP18 |
| Amplifier VIN, GND | 5 V (VBUS) or 3V3, and GND |

**The I2S pin rule:** MicroPython's I2S on the Pico needs LRC on the pin right
after BCLK. Here BCLK is GP20 and LRC is GP21. Swap those two wires and
`I2S()` raises an error. Lab 02 checks the rule.

All the pin numbers are in `config.py`.

## Setup

1. Put MicroPython `RPI_PICO2_W` (or `RPI_PICO_W`) on the Pico.
2. `cp secrets-template.py secrets.py`, then put in your WiFi name and password.
   (`secrets.py` is gitignored.)
3. Set `TIMEZONE_HOURS` in `config.py`.
4. Quit Thonny, then upload everything:

   ```bash
   ./upload-code.sh
   ```

   If it finds the wrong serial port, name it:
   `PORT=/dev/cu.usbmodem14301 ./upload-code.sh`.

## Labs

| Lab | File | What it does |
|---|---|---|
| 01 | `01-blink-onboard-led.py` | Blinks the LED on the Pico. Checks the board and firmware. |
| 02 | `02-probe.py` | Checks the board, files, WiFi, buttons, SPI, speaker, and display. Plays three beeps (set `PLAY_BEEPS = False` for silence). |

More labs are planned in the
[roadmap](../../../docs/kits/study-buddy/05-roadmap.md).

## Files

| File | What it is |
|---|---|
| `config.py` | Every pin number and setting. The labs import it. |
| `lib/` | The GC9B72 driver, two fonts, shapes, and `watchparts.py`. Copied from `sw-gc9b72`. |
| `wifi_time.py` | Sets the clock over WiFi. Copied from `sw-gc9b72`. |
| `secrets-template.py` | A template for your WiFi settings. |
| `upload-code.sh` | Copies the kit to the Pico with `mpremote`. |

`lib/` and `wifi_time.py` are copies, so a fix in one kit has to be made in the
other by hand.
