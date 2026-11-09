# Large Knob Clock Kit

## Description

This Raspberry Pi Pico 2W clock kit uses a larger 2.4 inch TFT RGB display with a resolution of 320 pixels horizontal and 240 vertical.  It is based on the ST7789 driver IC.
It uses a 4-wire SPI and also has a push button rotary knob with an additional push button below it.

Unlike the other knob clock it, this version also has a MAX98357A I2S Audio Amplifier and speaker for generating high quality sound.

This kit is very similar to the [Knob Clock Kit](../rect-tft-display/) but
it uses a larger display and has a amplifier and speaker.

## Part List

1. Raspberry Pi Pico 2W (wifi)
2. 2.4 in rectangular TFT with Press Knob and button
3. MAX98357A I2S Audio Amplifier and speaker
4. 400 tie Solderless breadboard
5. Colorful 10cm ribbon cable from display to breadboard

## Pin Assignements

### Display

Here are the pin assignments starting on row 4 of the breadboard and going to row 15

1. SCL - GPIO 2 - Orange - breadboard row 4
2. SDA - GPIO 3 - Yellow - breadboard row 5
3. RST - GPIO 4 - Green - breadboard row 6
4. DC - GPIO 5 - Blue - breadboard row 7
5. GND is the brown wire - breadboard row 8
6. CS is the purple on row 9
7. BLK (backlight) is gray - breadboard row 10
8. A white - breadboard row 11
8. B Push 2nd blue - breadboard row 12
9. Row 13 is GND (no connection)
10. Push - 2nd green wire - breadboard row 14
11. K0 2nd purple - breadboard row 15 (bottom left pin on the Pico)

### Amplifier

1. BCLK - Yellow wire - breadboard row 16
2. LRC - green wire - breadboard row 17
3. GND - black wire - breadboard row 18
3. DIN - orange wire - breadboard row 19
4. GAIN - brown wire - breadboard row 20
5. SD (no connection)

## Programs

Upload everything with `./upload-code.sh` (quit Thonny first), then run
the labs in order from Thonny. All pin numbers and settings live in
`config.py`.

| Program | What it does |
|---|---|
| `01-blink-onboard-led.py` | Blinks the Pico's own LED. Checks the board and the firmware before any wiring matters. |
| `02-probe.py` | Prints a full hardware report: chip, RAM, flash, kit files, WiFi, clock, knob and button pins, SPI speed, the I2S pin rule with three test beeps, and a summary on the screen. |
| `03-test-display.py` | "Hello World!", a white border, a corner arrow and red/green/blue bars. Tells you which of `ROTATION`, `BGR`, `INVERT` and the offsets to change if the picture is wrong. |
| `04-test-knob.py` | Tests the knob turning (click count, direction, a sliding marker, and the raw A/B levels), the knob press (PUSH) and the K0 button, on the screen and in the shell. |
| `05-test-sound.py` | Plays a 400 Hz tone for two seconds and then a C-major scale straight through I2S, with the note shown on the screen. |
| `06-wifi-sync-time.py` | Sets the Pico's clock from an internet time server and plays a chime when it works. Needs `secrets.py`. |
| `07-digital-clock.py` | Big seven-segment clock with day and date, and a chime at the top of every hour. |
| `08-alarm.py` | An alarm clock: set the alarm time and a wake-up tone with the knob, K0 turns it on and off. It rings until you press K0, or PUSH to snooze for five minutes. |
| `09-timer.py` | Countdown timer: set it with the knob, and the PUSH that finishes setting starts it. K0 pauses and goes on. Ticks for the last ten seconds, then beeps and flashes until you touch a control. |
| `10-stopwatch.py` | Stopwatch with hundredths and laps: K0 start/stop, PUSH lap (or reset when stopped), a different beep for each. |
| `11-analog.py` | A round clock face as tall as the screen, with the day, date and AM/PM in the corners. K0 turns a tick-tock sound on and off; chimes on the hour. |
| `12-mondaine.py` | A Swiss-railway-style station clock whose red hand glides round in 58.5 s, waits at 12, and lets the minute hand hop. Uses `lib/mondaine.py`. |
| `13-forecast.py` | The time, the weather now, and today's and tomorrow's high, low and sky from Open-Meteo, refreshed every 30 minutes (K0 or PUSH: now). Needs `secrets.py`. |
| `14-calendar.py` | A month calendar with today and the US holidays marked, and the next three holidays listed. Turn the knob to page through the months; PUSH for this month. |
| `15-time-and-quote.py` | A clock with a quote of the day under it. K0 for a random new quote, turn the knob to step through them, PUSH for today's. |
| `16-main-template.py` | The whole clock: turn the knob to switch between five modes. Copy it to the Pico as `main.py`. |
| `20-mode-main.py` | Labs 10 to 15 as six modes of one clock. Hold K0 for one second for the next mode; short K0 presses, the knob and PUSH belong to the mode. Copy it to the Pico as `main.py`. |

### The five modes of `16-main-template.py`

| Mode | Controls |
|---|---|
| `mode_weather.py` -- time, date, and today's and tomorrow's forecast from Open-Meteo | none |
| `mode_analog.py` -- a round dial with hour, minute and second hands | none |
| `mode_digital.py` -- big digits with a frame of 60 second ticks | none |
| `mode_stopwatch.py` -- minutes, seconds and hundredths, with laps, best and average | K0 start/stop, PUSH lap or reset, with beeps |
| `mode_timer.py` -- countdown timer with a speaker alarm | PUSH to set, knob to change; the last PUSH starts it, K0 pause/go |

The speaker ticks when the mode changes and chimes on the hour (not
between 10 PM and 7 AM). A running timer keeps going in other modes and
jumps back to the timer, with its alarm, when it reaches zero.

### The six modes of `20-mode-main.py`

Hold K0 for one second to go to the next mode; a card with the mode's
name shows while it loads. A K0 press shorter than that goes to the mode,
and acts when you let go. The clock starts in Analog Clock.

| Mode | Lab | Controls |
|---|---|---|
| `app_stopwatch.py` -- Stopwatch | 10 | K0 start/stop, PUSH lap or reset. Keeps running in other modes. |
| `app_analog.py` -- Analog Clock | 11 | K0 tick-tock sound on/off |
| `app_railway.py` -- Railway Clock | 12 | none |
| `app_forecast.py` -- Forecast | 13 | K0 or PUSH: get the weather now. Keeps the weather between visits. |
| `app_calendar.py` -- Calendar | 14 | knob: next/previous month, PUSH: this month |
| `app_quote.py` -- Time and Quote | 15 | K0 random quote, knob: next/previous, PUSH: today's |

The chime on the hour (not between 10 PM and 7 AM) and the nightly time
sync happen in every mode.

### Support files

| File | What it is |
|---|---|
| `config.py` | Pins, display settings, speaker gain and volume, time zone, location |
| `lib/st7789.py` | The display driver: same methods as the rect-tft-display kit's `st7735s.py` |
| `lib/shapes.py`, `lib/watchparts.py` | Circles and polygons; digits, tick frames, text lines, buttons and the knob |
| `lib/timerow.py` | A row of segment digits, HH:MM, at any size (labs 13 and 15) |
| `lib/mondaine.py` | The railway clock face and its stop-and-go timing (lab 12), changed to a white dial on the black rectangle |
| `lib/holidays.py` | US holidays for any year, worked out from rules (lab 14) |
| `lib/vga1_*.py` | The three fonts |
| `quotes.py` | The quotes for lab 15 and the Time and Quote mode -- add your own here |
| `sound.py`, `sfx.py` | Background sound on the Pico's second core, and the named sound effects |
| `wifi_time.py`, `forecast.py` | WiFi time sync and the weather forecast (`fetch_now()` adds the weather right now, for lab 13) |
| `secrets-template.py` | Copy to `secrets.py` and add your WiFi name and password |
| `upload-code.sh` | Copies the whole kit to the Pico with mpremote |

## Board Settings

These settings in `config.py` are confirmed on the real board with lab 03
(the display) and lab 04 (the knob). If a different batch of boards
behaves differently, those two labs tell you what to change.

- `ROTATION = 1` -- landscape with the knob on the right
- `INVERT = False` and `BGR = True` -- the usual ST7789 settings
  (`INVERT = True`, `BGR = False`) made red, green and blue show as
  yellow, purple and cyan
- `BAUDRATE = 24_000_000` -- a clean picture at 24 MHz
- `ENCODER_STEPS_PER_CLICK = 4` -- one click of this knob is 4 steps; with 2,
  every click counted as two
