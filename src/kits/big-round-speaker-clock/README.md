# Big Round Speaker Clock kit

A Raspberry Pi Pico W (the RP2040 board, not the Pico 2 W) with a 2.1" round
360x360 GC9B72 display, a MAX98357A amplifier driving a small speaker, and
three buttons. The design notes are in
[docs/kits/big-round-speaker-clock](../../../docs/kits/big-round-speaker-clock/README.md).

This kit started as a copy of the [Study Buddy kit](../study-buddy). It uses the
same display driver, fonts, and sound engine, but the amplifier is on different pins.

## Wiring

| Part | Pin | Pico pin |
|---|---|---|
| GC9B72 display | SCL / CLK | GP2 (SPI0 SCK) |
| | SDA / DIN | GP3 (SPI0 MOSI) |
| | RST | GP4 |
| | DC | GP5 |
| | CS | GP6 |
| | BL | GP7 |
| | VCC, GND | 3V3, GND |
| MAX98357A amp | BCLK | GP9 |
| | LRC | GP10 |
| | DIN | GP11 |
| | GAIN | GP12 |
| | SD | not connected |
| | VIN, GND | VBUS (5 V) or 3V3, GND |
| Buttons | MODE, UP, DOWN | GP13, GP14, GP15, each with its other leg to GND |

**The I2S pin rule:** MicroPython's I2S on the Pico needs LRC on the pin right
after BCLK. Here BCLK is GP9 and LRC is GP10. If you swap those two wires,
`I2S()` raises an error. `02-probe.py` checks this rule.

All the pin numbers are in `config.py`.

## Setup

1. Flash MicroPython `RPI_PICO_W` onto the Pico.
2. `cp secrets-template.py secrets.py`, then add your WiFi name and password.
   (`secrets.py` is gitignored.)
3. Set `TIMEZONE_HOURS`, `USE_US_DST` and `CITY` in `config.py`.
4. Quit Thonny, then upload everything:

   ```bash
   ./upload-code.sh
   ```

   If it finds the wrong serial port, give it the port yourself:
   `PORT=/dev/cu.usbmodem14301 ./upload-code.sh`.

## Test programs

Run these in order on a new kit. Each one checks one more part.

| File | What it does |
|---|---|
| `01-blink-onboard-led.py` | Blinks the onboard LED every 0.5 s. Checks the board and firmware. |
| `02-probe.py` | Checks the board, RAM, flash, files, WiFi, buttons, SPI, speaker and display. |
| `03-button-tests.py` | Prints MODE, UP or DOWN each time a button is pressed and released. The LED stays lit while any button is held. |
| `04-display-test.py` | Shows "Hello World" inside a ring at the edge of the visible circle. |
| `05-speaker-test.py` | Plays a 400 Hz tone for 2 s directly through I2S, without `sound.py`. |
| `06-test-wifi.py` | Checks `secrets.py` and the location and time settings in `config.py`, then joins WiFi. |
| `07-get-time.py` | Sets the clock from NTP and shows the time on the console and the screen. |

## The Big Clock

`main-template.py` is the clock. It shows the largest seven-segment digits
that fit inside the round screen, with a ring of second ticks around the
edge, AM/PM above the digits and the date below. It chimes on the hour,
except between 10 PM and 7 AM. It sets itself over WiFi at power-up and
again every night at 3:00 AM.

| Button | Does |
|---|---|
| UP / DOWN | Volume up or down. Hold to keep changing. |
| tap MODE | Turns the hourly chime on or off. |
| hold MODE | Sets the clock from the internet now. |

To make it start at power-up:

```bash
mpremote cp main-template.py :main.py
```

## All ten modes

`mode-template.py` puts ten modes in one program. Tap MODE to go to the next
one. The ten dots along the bottom show which mode you're in. It starts in
the Big Clock.

| Dot | Mode | File | UP / DOWN | Hold MODE |
|---|---|---|---|---|
| 0 | Big Clock | `mode_big.py` | volume | set clock from internet |
| 1 | Time + temperature now | `mode_temp.py` | UP: get weather now | set clock from internet |
| 2 | Time + temperature + forecast | `mode_forecast.py` | UP: get weather now | set clock from internet |
| 3 | Alarm | `mode_alarm.py` | UP: alarm on/off, DOWN: hear tone | set the alarm (tap MODE for next part) |
| 4 | Timer | `mode_timer.py` | UP: start/pause, DOWN: reset | set the time |
| 5 | Stopwatch | `mode_stopwatch.py` | UP: start/stop, DOWN: lap/reset | set clock from internet |
| 6 | Analog watch | `mode_analog.py` | -- | set clock from internet |
| 7 | Railway clock | `mode_mondaine.py` | -- | set clock from internet |
| 8 | Clock + phrase of the day | `mode_phrase.py` | other phrases | set clock from internet |
| 9 | US holiday calendar | `mode_calendar.py` | next / previous month | set clock from internet |

The alarm rings and the timer beeps whatever mode is showing. When the alarm
time comes, the clock switches to the alarm screen, and any button stops it.
The hourly chime is turned on and off from the alarm settings.

Only the mode on the screen is loaded. A Pico W can't hold all ten faces at
once, so `mode-template.py` unloads each mode when you leave it. The alarm,
volume and weather that every mode shares live in `shared.py`. The top of
`mode-template.py` explains how to add an eleventh mode.

To make it start at power-up:

```bash
mpremote cp mode-template.py :main.py
```

Set `DEMO_SECONDS = 8` in `mode-template.py` to make it step through the
modes by itself, like a display in a shop window.

**Memory on the Pico W.** This kit was tested on the board with about 80 to
105 KB free in every mode. Two things keep RAM from breaking into pieces too
small to use:

- `mode-template.py` throws away the tick-ring cache in `watchparts`
  every time it changes mode.
- `shared.py` sets aside the railway clock's 11.5 KB drawing buffer at
  power-up, before anything else breaks the memory up.

The weather comes from [Open-Meteo](https://open-meteo.com). It needs no API
key and uses `LATITUDE` and `LONGITUDE` from `config.py`.

## Files

| File | What it is |
|---|---|
| `config.py` | Every pin number and setting. All the programs import it. |
| `lib/` | GC9B72 driver, two fonts, `shapes.py`, `watchparts.py` (digits, tick ring, text lines, buttons). Copied from `study-buddy`. |
| `sound.py`, `sfx.py` | The synthesizer that feeds the amp from core 1, and the named sound effects. Copied from `study-buddy`. |
| `wifi_time.py` | Sets the clock over WiFi with NTP. Copied from `study-buddy`. |
| `secrets-template.py` | A template for your WiFi settings. |
| `upload-code.sh` | Copies the kit to the Pico with `mpremote`. |
| `mode-template.py`, `mode_*.py` | The ten-mode clock and its modes. |
| `shared.py` | What the modes share: the speaker, alarm, chime and weather. |
| `timerow.py` | A row of HH:MM seven-segment digits at any size. |
| `forecast.py` | Current weather and a two-day forecast from Open-Meteo. |
| `holidays.py` | US holiday dates for any year, worked out from rules. |
| `lib/mondaine.py` | The railway clock face. Copied from the `mondaine` kit, with one addition: `Face(band=...)` accepts a drawing buffer made at power-up. |

`lib/`, `sound.py`, `sfx.py` and `wifi_time.py` are copies, and
`mode_timer.py`, `mode_stopwatch.py` and `mode_analog.py` are adapted from
`sw-gc9b72`. A fix in one kit
has to be copied to the others by hand.
