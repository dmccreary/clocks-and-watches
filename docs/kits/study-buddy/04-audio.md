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
Monday ... Sunday), and glue words. At 11 kHz speech quality that is roughly
half a minute of audio, so it fits comfortably in flash.

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
| 11.025 kHz, 16-bit mono | 22 KB | about 93 seconds |
| 8 kHz, 16-bit mono | 16 KB | about 128 seconds |

Level 1 uses none of it. Level 2 uses well under a minute. Level 3 is
where the limit shows up: a 50-word Spanish deck with a clip of about one
second each takes 1.1 MB at 11 kHz.

Three ways to get more room, from cheapest to most expensive:

1. **Record at 11 kHz or 8 kHz.** Speech stays clear, and it nearly halves
   the size.
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
    to WAV on the computer with a converter script (still to be written).
    The player checks the WAV header, so a wrong format is rejected with
    a message and never played as noise.

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
  running with silence between sounds.
- Whether full volume on 5 V disturbs the WiFi chip.
- What happens to the core-1 loop when a program stops with Thonny's Stop
  button instead of calling `sound.deinit()`.

## Volume and Quiet Hours

- `VOLUME` in `config.py` sets the default level.
- A **mute**: holding UP and DOWN together for 1 second toggles it. The
  template handles this chord in every mode, so no mode has to, and a
  small speaker icon with a line through it shows on screen for a moment.
- **Quiet hours** (for example 9 PM to 7 AM) play every sound at one
  third of the volume, and reminders still show on the screen. The
  hours are set in `config.py`.
