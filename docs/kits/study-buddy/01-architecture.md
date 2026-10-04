# Architecture

The Study Buddy is the smartwatch's
[five-mode program](../sw-gc9b72/12-main-template.md) with three additions:
a mode list that lives in a file, two small services that stay loaded in
every mode, and a Library for downloading new things.

## Two Kinds of Downloads

| | **Pack** | **Mode** |
|---|---|---|
| What it is | Data: quiz decks, quotes, events | A Python module (`mode_*.py`) |
| Format | JSON (see [Pack Formats](03-pack-formats.md)) | Python source |
| What it can do | Nothing. It only gets read. | Anything. MicroPython has no sandbox, so a mode can read `secrets.py`, rewrite files, or use the network. |
| Who writes one | Anyone, including students | The teacher (or an instructor-approved author) |
| Who publishes it | The teacher adds it to the class Library | The teacher adds it to the class Library |
| Who installs it | **Students and teachers**, from the Library | **Students and teachers**, from the Library |
| Install check | JSON parses and has the right `kind` | SHA-256 matches the manifest, and the person confirms |

Both students and instructors use the Library, so a student never needs
to copy a file or open Thonny to get a new deck or mode. What keeps that
safe is that students **choose from what the teacher has published**, and
cannot point the Library at an address of their own on the device.

!!! warning "Downloaded modes are trusted code"
    There is no sandbox on a Pico. The only protection is that modes come
    from a **teacher-controlled HTTPS address**, and that the manifest lists
    each file's SHA-256 hash. A student can still write their own packs
    freely. Never add a Library address you do not control.

    The settings that limit what a student can install live in
    `config.py`, which a student can also edit. They are **guardrails for
    honest mistakes, not security.** A student who wants to run their own
    code on their own Pico can always do so.

## Files on the Pico

```text
main.py              the template (from 12-main-template.py)
config.py  secrets.py
lib/                 gc9b72, shapes, watchparts, fonts  (as in the watch kit)
sound.py             resident audio service (always loaded)
reminders.py         resident reminder service (always loaded)
packs.py             reads and checks packs (size limits, kind)
modes.json           installed modes, in order, and which are pinned
mode_*.py            the modes (built-in and downloaded)
packs/               downloaded decks and quote files
user/events.json     the student's quizzes and tests
user/progress.json   quiz progress (see Flash Quiz)
audio/               optional recorded clips (.wav)
```

`modes.json` replaces the hard-coded `MODES` tuple in the template:

```json
{
  "modes": [
    {"module": "mode_reminder", "name": "Next Quiz", "pinned": true},
    {"module": "mode_quiz",     "name": "Flash Quiz", "pinned": true},
    {"module": "mode_quote",    "name": "Quote",      "pinned": true},
    {"module": "mode_study",    "name": "Study Timer","pinned": true},
    {"module": "mode_digital",  "name": "Digital",    "pinned": true},
    {"module": "mode_library",  "name": "Library",    "pinned": false}
  ]
}
```

## Changes to the Main Template

The template's contract does not change. A mode still has
`start(display, up, down, saved)`, `update(now)`, `on_mode(kind)`, and
`stop()`. What changes is the program around the modes:

1. **Read the mode list from `modes.json`.** If the file is missing or
   broken, fall back to the five built-in modes, so a bad download can
   never brick the device.
2. **Dots show only pinned modes.** MODE steps through the pinned modes
   only, and the dots draw one per pinned mode, with a maximum of 8. Modes
   that are not pinned are reached from the Library. The dot row is
   currently 16 px apart, so 8 dots fit in 112 px.
3. **Import `sound` and `reminders` before `loaded_before` is taken.** The
   template deletes every module a mode imported that was not loaded
   before it. If `sound.py` were imported by a mode, switching modes would
   delete it and tear down the I2S object mid-chime. Importing both at the
   top of the template keeps them resident.
4. **Add a reminder check to the main loop** (see below).
5. **Use only modes whose file exists.** A mode named in `modes.json` but
   missing from flash is skipped, not fatal.
6. **Handle the mute chord.** UP and DOWN held together for 1 second
   toggles the sound in every mode (see [Audio](04-audio.md#volume-and-quiet-hours)).
7. **Honor a mode's optional `busy` flag.** It is a module-level variable
   a mode sets to `True` while it must not be interrupted. A mode that
   does not have one is never busy.

### The reminder check

`wake_at` cannot be used for reminders. It is a `time.ticks_ms()` value,
and on this port `ticks_ms()` wraps after about 12 days **(verify)**, with
`ticks_diff()` only reliable for about half that. A quiz next Friday can
be farther away than the tick counter can say.

Reminders use the **wall clock** instead. Since `wifi_time.sync_time()`
sets the RTC to local time, `time.mktime(time.localtime())` is a plain
integer that can be compared with an event's local time. Nothing in the
timer's `wake_at` mechanism changes.

The resident `reminders.py` loads `user/events.json` once, works out the
next time anything should fire, and keeps just that one integer. The
main loop does one integer comparison per pass:

```python
if reminders.due(now_seconds):          # next fire time has passed
    event = reminders.pop_due()
    sound.chime("reminder")
    switch_to(index_of("mode_reminder"), alert=event)
```

When a reminder fires, the template switches straight to `mode_reminder`
(the same trick the countdown timer uses for its alarm), whatever mode is
showing. Switching modes from a reminder never interrupts an **active quiz
question or a timer being set**: those modes return `True` from `on_mode()`
and also set `busy = True`, and the template waits, up to 30 seconds,
before switching.

## The Library Mode

`mode_library.py` is the only part that downloads anything. It is built
for an 11-year-old to use alone, so the screens use plain words. Hashes,
manifests, and byte counts never appear on screen.

### Two tabs: Browse and Installed

The Library keeps MODE for itself, as the quiz does, so a short press
confirms. The tabs switch with a **hold of MODE**, the same gesture other
modes use to leave a task or change the view:

| Tab | What it shows | UP / DOWN | Hold UP | Hold DOWN |
|---|---|---|---|---|
| **Browse** | What the Library offers, **featured** items first | Move between items | Install the item | (nothing) |
| **Installed** | What is on this device, with **free space** ("1.2 MB free") | Move between items | Pin or unpin a mode | **Remove** the item |

Built-in modes cannot be removed. Removing a deck also removes that deck's
saved progress after a "Remove it?" confirm that takes a second press, so
a slip of the finger does not lose a month of practice.

### Browse screen

Each item gets one screen:

```text
        US Capitals
   All 50 states and capitals
   
       DECK   3 KB
     hold UP to get it
```

- A **title**, a one-line `description`, a type (**DECK** for a pack,
  **MODE** for code), a size, and **GOT IT** if already installed.
- A mode's confirm screen says, in plain words, "This adds a new mode from
  your teacher's library. Hold UP again to add it." That is all.
- Items needing a module the device lacks show "Needs: sound" and cannot be
  installed.
- Items the teacher marks `featured` appear first, with a star.

### Installing

1. Connect to WiFi and fetch the manifest. With one library in
   `LIBRARIES` (see below) the Browse tab opens straight away. With more
   than one, a short first screen lists them by `name`, and UP, DOWN, and
   MODE choose.
2. Download to a temporary file, check the byte count and SHA-256, then
   rename it into place. A failed download never replaces a working file.
   On failure the screen says "Didn't work. Try again.", with the reason
   (WiFi, download, or damaged file) in the Thonny shell only.
3. For a mode, add it to `modes.json` as **not pinned**. The Installed tab
   lets the student pin or unpin it. Only up to 8 can be pinned.
4. Play the `right` jingle, and show "Got it!"

### More than one library

`config.py` lists the libraries the device may use:

```python
LIBRARIES = (
    {"name": "Class",  "url": "https://example.org/room12/manifest.json",
     "modes": True},
    {"name": "Friends", "url": "https://example.org/shared/manifest.json",
     "modes": False},
)
```

| Field | Meaning |
|---|---|
| `name` | Shown when choosing between libraries. |
| `url` | The manifest's address. HTTPS. |
| `modes` | `True` to show modes from this library. `False` hides every item of type `mode`, so a library of student-made decks can never put code on a device. |

The student-facing screens never ask for an address. Only a person
editing `config.py` can add a library, and the setup guide tells them not
to add one they do not control. A teacher who wants younger students to
get **decks only** sets `"modes": False` for every library, and installs
modes on the devices ahead of time.

### What the teacher does

| Task | How |
|---|---|
| Publish a deck or mode | Put the file in a folder and run the manifest script on the computer. It writes `manifest.json` with each file's size and hash. Nobody types a hash. |
| Review student decks | Students hand in a deck file. The teacher checks it, including each quote's `source`, then adds it to the class folder. |
| Feature an item | Set `"featured": true` in the item's entry, or pass `--featured` to the script. |
| Retire an item | Remove it from the folder and run the script again. Devices that already have it keep it. |
| Pre-install for a class | Put the files on the Pico with `upload-code.sh`, so a student's first run needs no WiFi. |

The manifest script is `tools/make_manifest.py` in the kit's folder
(written in Lab 09).

`hashlib.sha256` is available in MicroPython's rp2 builds **(verify on the
firmware version the kit ships)**. Downloads use HTTPS. Whether the Pico
2 W's TLS stack can reach GitHub Pages reliably is a **verify** item; if
not, the fallback is a teacher-run web server on the school network.

### The manifest

See [Pack Formats](03-pack-formats.md#library-manifest) for the exact
fields. The manifest is a flat list, so a school can publish its own and
point a device at it with one entry in `LIBRARIES`.

## What a Mode Must Follow

All the watch kit's rules still apply, plus three new ones:

- Do not draw in the dot strip at the bottom.
- Do not clear the screen except in `start()`.
- **Do not make a full-screen fill (131 ms) while a sound is playing.**
  See [Audio](04-audio.md#playback-must-survive-drawing).
- Set `busy = True` while the student is in the middle of something that
  must not be interrupted by a reminder.
- Read packs through the helper in `packs.py`, which enforces size limits,
  instead of opening files directly.
