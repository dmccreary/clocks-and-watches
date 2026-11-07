# Audio

The Study Buddy speaks in three levels. Each one works without the next,
so the device is useful with just a speaker and the first level.

## The Sound Module

`sound.py` is a **resident** module: the template imports it once at
power-up, and it stays loaded in every mode (see
[Architecture](01-architecture.md#changes-to-the-main-template)). It owns
the one I2S object, so no mode ever creates its own.

The module is written (`src/kits/study-buddy/sound.py`). What it has today:

| Function | What it does |
|---|---|
| `init(rate=16000, ibuf=8192, volume=None, core=1)` | Starts I2S from `config.py` and the loop that feeds it. `rate` is samples per second (44100 for the full range of hearing). `ibuf` is the reserve in bytes, which is 256 ms at the defaults. `core` is 1 (second core) or 0. |
| `tone(freq, ms, wave, to, level, attack, release)` | Queues a note. `to` makes the pitch glide. `wave` is sine, square, triangle, saw, or noise. Short fades keep it from clicking. |
| `rest(ms)` | Queues silence. |
| `hold(freq, wave)`, `pitch(freq)`, `release()` | A note that keeps playing while the pitch is steered (for the button theremin). |
| `play(name)` | Queues a named sound from `sfx.py`, such as `"right"`, `"wrong"`, `"chime"`, `"reminder"`, `"done"`, `"start"`, `"coin"`, or `"laser"`. |
| `rtttl(text)` | Queues a tune written as an old-phone ringtone string. |
| `note_freq("A4")`, `note_name(440)` | Note names to hertz and back. |
| `stop()` | Empties the queue. Sound already in the reserve still plays, up to 256 ms at the defaults. |
| `busy()`, `wait()` | Is anything still playing, and wait until it is done. |
| `volume(n)` | 0 to 100, applied in software. |
| `stats()`, `reset_stats()` | Underruns, the smallest reserve seen, and the longest wait between chunks. Lab 03 reads these. |
| `deinit()` | Stops the loop and frees the I2S hardware. |

Not written yet: `wav(path)` to stream a 16-bit mono WAV file from flash,
and `say(parts)` to play a list of clips one after another (see level 2).

Every playing function returns immediately. Playback continues on its own,
and a mode only needs to call `busy()` if it wants to wait.

### Level 1: tones

Tones are generated in RAM, so they need **no flash**. The named sounds
are built from short note lists:

| Sound | Idea |
|---|---|
| `right` | Two rising notes, C5 then G5 |
| `wrong` | One low, short note |
| `chime` | A soft three-note arpeggio |
| `reminder` | The chime, then a pause, then the chime again |
| `done` | A falling pentatonic phrase (the timer alarm) |

[`src/dac`](https://github.com/dmccreary/clocks-and-watches/tree/main/src/dac)
already has I2S tone and melody code that was tried on a PCM5102A. Moving
it to the MAX98357A means changing the pins and nothing else, since both
take the same I2S signal.

### Level 2: composed phrases

Short recorded clips, joined together, give spoken reminders without
needing every sentence recorded:

```text
"Your" + "algebra" + "quiz" + "is" + "tomorrow"
```

This needs a vocabulary of about 60 clips: subjects (algebra, history,
science, reading, spelling, math, English, Spanish, art, music), kinds
(quiz, test, exam, homework), times (today, tomorrow, in one hour, on
Monday ... Sunday), and glue words. That is roughly half a minute of audio:
about 1 MB at 16 kHz or 0.5 MB at 8 kHz, so it fits in flash (see the
[Flash Budget](#flash-budget)).

An event's `subject` and `kind` pick the clips. If a clip is missing, the
Study Buddy falls back to the chime, so a missing file never breaks a
reminder.

### Level 3: recorded packs

A pack item can name an `audio` clip to play with its question. The best
use is **vocabulary where the sound matters**: Spanish words, spelling,
and place names. The clips are made on a computer ahead of time and
installed with the deck, using the text-to-speech workflow in the book's
media tools. The Pico never makes speech itself, because the RP2350 cannot
run text-to-speech.

## Flash Budget

Audio is the biggest thing on the Pico's flash. The 2.5 MB filesystem of the
Pico 2 W (after the 1.5 MB of firmware) has to hold the program as well:

| Format | Per second | In 2.0 MB (leaving room for code and packs) |
|---|---|---|
| 16 kHz, 16-bit mono | 32 KB | about 64 seconds |
| 8 kHz, 16-bit mono | 16 KB | about 128 seconds |

!!! note "Why there is no 11.025 kHz row"
    The MAX98357A datasheet says the amplifier accepts a sample rate (its
    LRCLK) of only 8, 16, 32, 44.1, 48, 88.2, or 96 kHz, and that 11.025,
    12, 22.05, and 24 kHz are **not supported**. The usual "small file"
    rates are therefore out. Convert clips to 16 kHz or 8 kHz.

Level 1 uses none of it. Level 2 uses well under a minute. Level 3 is
where the limit shows up: a 50-word Spanish deck with a clip of about one
second each takes 1.6 MB at 16 kHz, or 0.8 MB at 8 kHz.

Three ways to get more room, from cheapest to most expensive:

1. **Record at 8 kHz instead of 16 kHz.** It halves the size. Speech stays
   understandable but sounds like a telephone, so listen to a clip before
   converting a whole deck. 8 kHz also needs the amplifier's SD pin on a
   GPIO (see [the SD pin section](#the-amplifiers-sd-and-gain-pins)).
2. **A 16 MB flash board** such as the Pimoroni Pico Plus 2 W
   **(verify MicroPython support and pin compatibility)**. This is about
   8 times the room.
3. **A micro-SD card**, which holds any amount of audio. The card's module
   needs a second SPI bus and four more wires. The display uses hardware
   SPI0 (GP2 and GP3), and the speaker is on GP18 to GP21, which leaves
   hardware SPI1 free on GP8 to GP12: SCK on GP10, MOSI on GP11, MISO on
   GP12, and chip select on GP9 **(verify on the bench)**.

!!! note "WAV format"
    `sound.wav()` reads uncompressed 16-bit mono PCM only. MicroPython has
    no MP3 or ADPCM decoder in the standard build, so clips are converted
    to WAV on the computer with a converter script (still to be written),
    which writes 16 kHz or 8 kHz files, the small rates the amplifier
    accepts. The player checks the WAV header, so a wrong format or sample
    rate is rejected with a message and never played as noise.

## Playback Must Survive Drawing and Freezing

Updating the display blocks the Pico. A full-screen fill takes 131 ms, the
analog face's redraw takes up to 232 ms, and a WiFi connect took **9.5
seconds** on the real kit. If the audio buffer runs dry during one of
these, the speaker clicks or stutters.

### The sound runs on the second core

The Pico 2 W has two cores that run at the same time. `sound.init()`
starts a small loop on **core 1** that does one job: calculate a chunk of
sound, hand it to the amplifier, repeat. The rest of the program, on
core 0, can freeze for as long as it likes and the sound does not notice.
The note queue is shared between the cores, so a lock guards it.

`init(core=0)` is still there. It has the I2S driver interrupt core 0 each
time it needs a chunk, which is simpler but cannot play through a freeze.

### What was measured

All on the real kit (Pico 2 W, MicroPython 1.29.0, 16 kHz, 256 ms reserve).

**Does core 1 run in parallel?** Yes. The same 150,000-step loop took
1014 ms on core 0 alone and 1024 ms on core 1 alone. With both running at
once, each took 1121 ms, about 10% slower and not twice as slow, so there
is no interpreter lock making the cores take turns. (The 10% is probably
the two cores sharing the memory bus and heap.)

**Does it survive a freeze?** A steady tone played while core 0 sat inside
one long call (`max(range(1_000_000))`, about 1.2 s):

| Audio fed by | Core 0 frozen for | Underruns | Reserve at its lowest | Longest wait between chunks |
|---|---|---|---|---|
| core 0 (interrupts) | 1163 ms | 1 | -878 ms (ran dry) | 1192 ms |
| core 1 (thread) | 1284 ms | 0 | 254 of 256 ms | 64 ms (normal) |

**Does it survive real jobs?** On core 1, with a 9-second tone playing:

| Job on core 0 | Took | Underruns | Reserve at its lowest |
|---|---|---|---|
| 40 KB flash write and delete | 139 ms | 0 | 250 ms |
| 20 forced garbage collections | 133 ms | 0 | 248 ms |
| WiFi connect and NTP time sync | 9451 ms | 0 | 252 ms |

**Reproduced by the lab itself.** Dan ran `03-sound-test.py` on his own
board on 2026-10-06 and sent back what it printed. The numbers match the
test scripts above to within a few milliseconds:

| Part of the lab | Result printed by the lab |
|---|---|
| Part 4, core 0 in charge | core 0 frozen 1164 ms, 1 dropout, reserve fell to -867 of 256 ms, longest wait 1182 ms |
| Part 4, core 1 in charge | core 0 frozen 1284 ms, 0 dropouts, reserve fell to 254 of 256 ms, longest wait 64 ms |
| Part 5, drawing | 17 full-screen fills, 0 dropouts, reserve fell to 252 of 256 ms |

So the result holds on a second run, on the board a student would use, with
the program a student would run.

Two limits on those numbers. They measure whether the audio *supply*
stalled, and cannot see whether the I2S hardware itself ran dry, so they
are backed by listening (a steady tone should stay steady through all of
it). Dan reported that the sounds in lab 03 worked, but has not yet said
whether the one-second gap with core 0 in charge was audible, so that
part is not confirmed by ear. And the flash write was small: a long write,
such as a Library download, still needs listening to before we rely on it.

### Rules for modes

1. **A mode may draw and fetch over WiFi while a sound plays.** The
   full-screen-fill rule from the first draft is no longer needed on core
   1. It still applies if `init(core=0)` is used.
2. **A mode must not write or delete files while a sound plays.** Flash
   erases and writes turn off interrupts and pause core 1, and the I2S
   hardware depends on an interrupt about every 2 ms. A file write causes a
   click or a gap, whichever core feeds the sound: **confirmed by ear** for
   small writes, a 200 KB write, and a mixed load. Wait for `sound.busy()` to
   be false first. This is the one known exception to "core 0 can freeze as
   long as it likes". Whether a write during *silence* is clean is still
   untested (experiment E10). See the
   [multicore guide](06-multicore-guide.md#flash-the-exception).
3. **Do not start any other thread.** The RP2 port has only core 1 to give,
   and the audio loop uses it. (The loop is not idle, either: in blocking
   mode `write()` busy-waits in C while the reserve is full, so core 1 is
   always at full speed. This is harmless, but earlier text on this page said
   it slept, which was wrong.)
4. **Talk to the sound through its functions** (`tone()`, `stop()`, and so
   on), which take the lock. Do not touch its queue directly.

### Still to measure

The [multicore guide](06-multicore-guide.md#experiments-to-run) lists nine
experiments. The script `multicore-stress-test.py` covers the first five.

- A flash write during silence (E10): does it pop? This decides whether the
  rule "do not write while a sound plays" is enough.
- Fixing the flash glitch itself. The options are in the guide's "Ideas
  That Would Offload More".
- The click when I2S starts and stops. If it clicks, the amplifier stays
  running with silence between sounds. The datasheet's advice on clicks is
  in [The Amplifier's SD and GAIN Pins](#the-amplifiers-sd-and-gain-pins).
- Whether full volume on 5 V disturbs the WiFi chip.
- What happens to the core-1 loop when a program stops with Thonny's Stop
  button instead of calling `sound.deinit()`.
- Whether the button theremin still feels quick. The theremin mode and Lab 08
  moved from 22,050 Hz, which the datasheet lists as unsupported, to 16,000 Hz
  (version 1.1 of each file). With the same 4096-byte buffer the reserve grew
  from about 93 ms to 128 ms. This is **not yet tried on the board**. If the
  pitch lags, try a smaller `ibuf` such as 3072 (96 ms).

## The Amplifier's SD and GAIN Pins

Two wires on the MAX98357A set how it behaves, and neither needs code: the
amplifier reads the voltage on each pin. The numbers below come from the
MAX98357A/MAX98357B datasheet (Rev 13, 7/19, document 19-6779) and, for the
breakout board, from Adafruit's
[pinout page](https://learn.adafruit.com/adafruit-max98357-i2s-class-d-mono-amp/pinouts).

### What SD does

The chip's pin is named `SD_MODE`. It does two jobs at once: it can **shut
the amplifier down**, and it **picks which I2S channel is played**. The chip
measures the voltage on the pin:

| Voltage on SD | The amplifier |
|---|---|
| Below about 0.16 V | Is in **shutdown** |
| 0.16 V to 0.77 V | Plays the **mix**, (left + right) / 2 |
| 0.77 V to 1.4 V | Plays the **right** channel |
| Above about 1.4 V | Plays the **left** channel |

Those are the typical trip points. The datasheet lets each one vary from
chip to chip: 0.08 to 0.355 V for the shutdown edge, 0.65 to 0.825 V for the
middle one, and 1.245 to 1.5 V for the top one.

The chip also has a 100 kΩ resistor from SD to ground inside it, so on the
bare chip an SD pin left floating means **shutdown**. To get the right
channel or the mix, pull SD up through a resistor, which makes a voltage
divider with that internal 100 kΩ. For 3.3 V logic the datasheet gives 210 kΩ
(right) and 634 kΩ (mix). For the left channel, drive SD straight to logic
high.

### Why a breakout works with SD unconnected

Adafruit's breakout adds what the bare chip lacks: a 1 MΩ resistor from SD
to VIN. With the chip's internal 100 kΩ, that holds SD at 100 / 1100, about
one eleventh of VIN, which is the mix mode:

| VIN | SD sits at | Against the highest shutdown edge the datasheet allows (0.355 V) |
|---|---|---|
| 5 V | 0.45 V | Above it. Safe on any chip. |
| 3.3 V | 0.30 V | **Below it.** A typical chip (0.16 V) is fine, but a chip at the top of the allowed range would be in shutdown. |

So the margin is thin when the amplifier runs from 3V3. This is arithmetic
from the datasheet and Adafruit's resistor value, not something seen to fail
**(verify on the bench)**, and a copy of the breakout may use a different
resistor. If a board is silent on 3V3, tie SD to 3V3 as described next.

### Three ways to wire SD

| SD is wired to | The amplifier | Good for |
|---|---|---|
| Nothing, on a breakout with the 1 MΩ pull-up | Plays the mix, always on | The simplest wiring, and the kit today. Thin margin on 3V3. |
| 3.3 V (or the amplifier's VIN) | Plays the left channel, always on | Designs that never need to switch the amplifier off |
| A GPIO pin | Left channel when high, shutdown when low | Battery power, muting, and controlling clicks |

**Why many designs wire SD to 3.3 V.** There are three reasons:

1. The voltage is far above the 1.4 V edge on every chip, so no resistor
   tolerance and no breakout resistor matters.
2. Left-only costs nothing here. `sound.py` opens I2S with `I2S.MONO`, and
   MicroPython writes a mono sample to **both** channels, so the left channel
   alone sounds the same as the mix.
3. It saves a GPIO pin.

The price is that the pin can no longer switch the amplifier off. One
caution from the datasheet: SD must not rise above VDD + 0.3 V. That is no
problem when SD and the amplifier's VIN are on the same 3.3 V rail, or when
VIN is 5 V. If VIN can fall below 3.0 V while SD is driven from 3.3 V (a
nearly empty battery), put about 2 kΩ in series with SD.

### What shutdown saves

| State | How it happens | Supply current (typical) |
|---|---|---|
| Running | SD high, I2S clocks running, no speaker connected | 2.75 mA at 5 V, 2.4 mA at 3.7 V |
| Standby | SD high, BCLK stopped (the chip does this by itself) | 340 µA |
| Shutdown | SD low | 0.6 µA |

These are the datasheet's numbers at 25 °C. A speaker playing adds to the
running figure. The standby row matters: an SD pin tied high does **not**
leave the amplifier burning 2.4 mA while idle, as long as `sound.deinit()` has
stopped the clocks. It only runs at full idle current when the clocks keep
running with silence, which is the fallback under "Still to measure" if
starting and stopping I2S clicks.

On USB power none of this is worth a GPIO. On a battery, 340 µA would drain
a 500 mAh cell in about two months by itself, while 0.6 µA would not matter.

### Driving SD from the Pico

The kit does not do this today. GP17 is unused, so a port that wanted it
could add `I2S_SD_PIN = 17` to `config.py` and wire SD to it:

```python
from machine import Pin
import time

sd = Pin(17, Pin.OUT, value=0)   # low: shutdown, 0.6 µA

def amp_on():
    sd.value(1)                  # high: left channel, amplifier on
    time.sleep_ms(10)            # turn-on time is 7.5 ms at most

def amp_off():
    sd.value(0)
```

Two facts from the datasheet help with clicks. The order of SD and the I2S
clocks makes no difference to the click-and-pop level, so there is no
sequence to get right at 16 kHz. But the chip has **no volume ramp-down**
when it enters shutdown: end the sound with a fade (the `release` of
`tone()` does this) and wait for `sound.busy()` to be false before calling
`amp_off()`.

!!! warning "8 kHz audio needs SD under software control"
    At 8 kHz the bit clock runs at 8,000 × 32 = 256 kHz, because it is 32
    times the sample rate (see the [multicore guide](06-multicore-guide.md)).
    That is a special case in the datasheet: the clocks must not run before the
    amplifier is enabled, there must be a 10 µs wait after SD goes high
    before they start, and **if the clocks stop, SD must be set to 0 V
    first**. An SD pin tied high breaks that last rule each time
    `sound.deinit()` stops the clocks, and the datasheet says the chip may
    then not power up properly the next time. The default 16 kHz (a 512 kHz
    bit clock) is not affected. If you use 8 kHz, put SD on a GPIO.

### Why many examples tie GAIN to GND

The GAIN pin (`GAIN_SLOT` on the chip) works the same way: its wiring sets
the gain, with five choices (datasheet Table 8):

| GAIN is wired to | Gain |
|---|---|
| GND through a 100 kΩ resistor (±5%) | 15 dB |
| **GND** | **12 dB** |
| Nothing | 9 dB |
| VIN | 6 dB |
| VIN through a 100 kΩ resistor (±5%) | 3 dB |

Examples overwhelmingly pick **GND, 12 dB**, for four reasons:

1. **It is the datasheet's own setting.** The output-power rating (3.2 W into
   4 Ω at 5 V and 10% distortion) is specified at 12 dB, the typical-performance
   curves are drawn at 12 dB, and the left-channel circuit (Figure 17) and
   the example board layout (Figure 23) use it. The tiny WLP package's pinout
   is even arranged so 12 dB needs no via (Figure 22). People copy the
   reference circuit.
2. **It is the loudest setting that needs no extra part.** A bare wire to
   GND gives 12 dB, and an open pin only 9 dB. Going up to 15 dB takes a
   resistor. The chip's full-scale digital output is just 2.1 dBV (about
   1.3 V rms), so a small speaker needs the gain.
3. **It does not depend on the supply voltage.** The gain edges are
   fractions of VDD, so GND means 12 dB at any VIN. A Pico pin driven high
   only means "VIN" when VIN is 3.3 V: on 5 V, 3.3 V is 0.66 × VDD, which
   sits at the edge of the 3 dB band, not the 6 dB one. This is why the kit
   can only offer 6 dB on a 3.3 V amplifier.
4. **TDM mode fixes the gain at 12 dB**, so it is the setting the chip is
   built around.

More gain is not always more sound. The datasheet gives the output level as
the input level (dBFS) + 2.1 dB + the gain, but the amplifier cannot swing
past its supply. As a rough figure, assuming an ideal bridge that swings the
whole supply, a loud digital signal clips above about -3 dBFS at 12 dB on
5 V and about -7 dBFS at 12 dB on 3.3 V. At 9 dB the limits are about 0 and
-4 dBFS. Real chips clip a little sooner. The kit's default is 9 dB, and its
software volume scales the signal before it reaches the amplifier.

## Volume and Quiet Hours

- `VOLUME` in `config.py` sets the default level.
- A **mute**: holding UP and DOWN together for 1 second toggles it. The
  template handles this chord in every mode, so no mode has to, and a
  small speaker icon with a line through it shows on screen for a moment.
- **Quiet hours** (for example 9 PM to 7 AM) play every sound at one
  third of the volume, and reminders still show on the screen. The
  hours are set in `config.py`.
