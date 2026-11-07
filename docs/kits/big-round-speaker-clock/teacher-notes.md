# Notes for Teachers

These notes are for teachers, parents, and anyone who wants the technical
details behind the [Big Round Speaker Clock Kit](index.md). The code is in
[`src/kits/big-round-speaker-clock`](https://github.com/dmccreary/clocks-and-watches/tree/main/src/kits/big-round-speaker-clock),
and its `README.md` has the full file list.

## Where This Kit Comes From

The kit is the round GC9B72 display from the
[Chrono Smart Clock Kit](../sw-gc9b72/index.md) plus a MAX98357A I2S
amplifier and a small speaker. The display driver, fonts, sound engine,
and WiFi time code were copied from the Study Buddy kit. The timer,
stopwatch, and analog face are adapted from the Chrono Smart Clock Kit,
and the railway face is the [Railway Clock Kit](../mondaine/index.md)'s.
A fix in one kit has to be copied to the others by hand.

The display and buttons are on the same pins as the Chrono Smart Clock
Kit, so its [sourcing notes](../sw-gc9b72/teacher-notes.md#sourcing-parts)
for the Pico, display, cable, and buttons apply here too.

## Suggested Timing

| Session | Labs | Notes |
|---|---|---|
| 1 | 01–04 | Board, checkup, buttons, screen. Most wiring problems show up here. |
| 2 | 05–07 | Speaker, WiFi, time. Have the WiFi name and password ready, and check that the network is 2.4 GHz. |
| 3 | 08 | The Big Clock. Copy it to `main.py` so students take home a working clock. |
| 4+ | 09 | The ten modes. Good for open-ended projects: a new phrase list, new colors, an eleventh mode. |

## The Pico W, Not the Pico 2 W

The kit is set up for the original **Pico W** (RP2040). It has about
190 KB of RAM for Python, much less than the Pico 2 W, and that shapes
the code:

- `mode-template.py` loads one mode at a time and unloads it on the way
  out. All ten together would not fit.
- The clock was tested on the board with about 80–105 KB free in every
  mode. Two things keep RAM from breaking into pieces too small to use:
  `mode-template.py` clears the tick-ring cache in `watchparts` on every
  mode change, and `shared.py` sets aside the railway clock's 11.5 KB
  drawing buffer at power-up.
- The I2S driver needs one unbroken 4 KB block. `main-template.py` starts
  the sound **before** it builds the clock face for this reason: started
  after, it raised a `MemoryError` on the kit.

## The Amplifier

The MAX98357A is an I2S amplifier only. It has **no microphone**.

**The I2S pin rule.** MicroPython's I2S on the Pico needs LRC on the GPIO
right after BCLK. This kit uses BCLK GP9 and LRC GP10. Swapped, `I2S()`
raises an error. `02-probe.py` checks the rule.

**GAIN.** The GAIN pin is wired to GP12 so software can choose the gain
(`GAIN_DB` in `config.py`, applied by `config.set_gain()`):

| `GAIN_DB` | GAIN pin is | GP12 is set to |
|---|---|---|
| 6 | tied to VIN | output, high |
| 9 | floating | input |
| 12 | tied to GND | output, low |

The 6 dB setting only makes sense with the amplifier's VIN on 3.3 V. With
VIN on 5 V (VBUS), use 9 or 12.

**SD** is not connected, so the amplifier is always on.

**Sample rates.** The MAX98357A datasheet supports only 8000, 16000,
32000, 44100, 48000, 88200, and 96000 samples per second. The kit uses
16000. Rates such as 11025 and 22050 are not supported.

**Volume.** `VOLUME` in `config.py` (0–100, default 40) is the starting
loudness. A speaker close to a student's ear is louder than you expect,
so keep it low for testing.

## How the Sound Works

`sound.py` is a small synthesizer. Programs queue notes and named effects
(`sfx.py`), and `sound.py` computes the samples a chunk at a time and
feeds the amplifier from the Pico's **second core**, so the first core is
free to draw. On a board where the second core can't be started, it falls
back to an I2S interrupt on core 0. The comments at the top of `sound.py`
and the Study Buddy kit's
[Multicore Guide](../study-buddy/06-multicore-guide.md) explain the
details.

## Weather and Time

- **Time** comes from `pool.ntp.org` at power-up and again at 3:00 AM
  every night. WiFi is switched off between syncs, and the sound is
  paused while WiFi is on.
- **Weather** comes from [Open-Meteo](https://open-meteo.com), which needs
  no API key. Modes 1 and 2 share one download (in `shared.py`), fetched
  every 30 minutes, using `LATITUDE` and `LONGITUDE` from `config.py`.
- **WiFi** must be 2.4 GHz. Many school networks need a web sign-in page,
  which the Pico W can't complete; a phone hotspot is a common workaround.

## What Has Been Checked, and How

The screen pictures in these pages were made by running each program's
real code in the [GC9B72 display simulator](https://github.com/dmccreary/clocks-and-watches/tree/main/src/display-simulators/gc9b72)
(`render_big_round_speaker_clock_docs.py`), with fake WiFi and weather.
The simulator shows exactly the pixels a program sends to the display,
but it has no speaker and only one core:

| Item | Simulator | Reported from the real kit |
|---|---|---|
| Every screen in these pages | yes | — |
| All ten modes start and draw | yes | yes |
| Sound: chimes, alarm, timer beeps | no (silent) | yes |
| Memory on a Pico W | no | yes (80–105 KB free in every mode) |
| Lab 02's probe report | no (needs the kit's files on a board) | not recorded |

The shell output shown in labs 03, 05, 06, and 07 is from the simulator,
so the network name and addresses are made up.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Onboard LED doesn't blink | Wrong firmware | Flash `RPI_PICO_W`, not `RPI_PICO` |
| Screen stays black | SCL/SDA swapped, or no 3V3 | SCL → GP2, SDA → GP3, VCC → 3V3 |
| Snow or stripes on the screen | Loose RST/DC/CS, or long wires | Check GP4–GP6; set `BAUDRATE = 12_000_000` |
| `I2S()` raises an error | BCLK and LRC swapped | BCLK → GP9, LRC → GP10 |
| No sound, no error | Amplifier unpowered, or DIN loose | Check VIN and GND, then DIN → GP11 |
| Sound too quiet or too loud | Gain or volume | `GAIN_DB` and `VOLUME` in `config.py` |
| A button reads pressed at rest | Button turned 90° in the breadboard | Rotate it a quarter turn |
| One press counts twice in lab 03 | Contact bounce | Expected in lab 03; the clock debounces |
| "network not found" | 5 GHz network | Use the 2.4 GHz network name |
| Time off by one hour | Daylight saving setting | `USE_US_DST` in `config.py` |
| `MemoryError` | Fragmented RAM | Unplug and replug; keep the sound starting before the face |
