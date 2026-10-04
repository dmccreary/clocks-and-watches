# Audio

The Study Buddy speaks in three levels. Each one works without the next,
so the device is useful with just a speaker and the first level.

## The Sound Module

`sound.py` is a **resident** module: the template imports it once at
power-up, and it stays loaded in every mode (see
[Architecture](01-architecture.md#changes-to-the-main-template)). It owns
the one I2S object, so no mode ever creates its own.

| Function | What it does |
|---|---|
| `init()` | Sets up I2S from `config.py` and a 16 KB ring buffer. |
| `tone(freq, ms)` | Plays a tone, with a short fade-in and fade-out so it doesn't click. |
| `play(name)` | Plays a named sound: `"right"`, `"wrong"`, `"chime"`, `"reminder"`, `"done"`, `"start"`. |
| `melody(notes)` | Plays a list of `(note, ms)` pairs. |
| `wav(path)` | Streams a 16-bit mono WAV file from flash. |
| `say(parts)` | Plays a list of WAV clips one after the other (see level 2). |
| `stop()` | Stops everything at once. |
| `busy()` | `True` while anything is playing. |
| `volume(n)` | 0 to 100. Applied in software by scaling samples. |

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

## Playback Must Survive Drawing

Updating the display blocks the Pico. A full-screen fill takes 131 ms, the
analog face's redraw takes up to 232 ms, and a WiFi fetch takes a second
or two. If the audio buffer runs dry during one of these, the speaker
makes a click or a stutter.

The design handles this with three rules:

1. **Use I2S in non-blocking mode** with a callback that refills the ring
   buffer from the file or the note generator. The callback is scheduled
   by MicroPython between bytecodes, so it **does not run in the middle of
   a long C call** such as a screen fill **(verify on the bench)**.
2. **A 16 KB buffer.** At 16 kHz that is about 500 ms of audio, which is
   longer than any normal redraw.
3. **Modes must not make a full-screen fill while a sound is playing.**
   Only the analog face and the template's start-up do, and neither plays
   audio.

Things to measure early, on the real kit:

- The longest gap in the buffer's refilling while a screen fill runs.
- Whether a WiFi fetch (Library, calendar) causes dropouts. If it does,
  the Study Buddy plays nothing while it fetches.
- The click when I2S starts and stops. If it clicks, the amplifier stays
  running with silence between sounds.
- Whether full volume on 5 V disturbs the WiFi chip.

## Volume and Quiet Hours

- `VOLUME` in `config.py` sets the default level.
- A **mute**: holding UP and DOWN together for 1 second toggles it. The
  template handles this chord in every mode, so no mode has to, and a
  small speaker icon with a line through it shows on screen for a moment.
- **Quiet hours** (for example 9 PM to 7 AM) play every sound at one
  third of the volume, and reminders still show on the screen. The
  hours are set in `config.py`.
