# Roadmap and Risks

## Build Order

The Study Buddy has its own lab numbers, starting at 01. The code is in
`src/kits/study-buddy`. Each lab ends with something that works on its
own, so the kit is useful after any of them.

"The template" below means the five-mode program from the smartwatch kit's
[Lab 12](../sw-gc9b72/12-main-template.md). It is copied into the Study
Buddy folder in Lab 09, when the first mode needs it.

Labs 03 to 08 are the **sound labs**. Lab 03 builds and proves the sound
module, and labs 04 to 08 are short, fun programs that show what the
speaker can do. The study features start at Lab 09.

| Lab | Status | Builds | Needs | Result |
|---|---|---|---|---|
| **01: Blink the Onboard LED** | Done, run on the board | `01-blink-onboard-led.py` | The Pico | The board and firmware work. |
| **02: Kit Checkup (Probe)** | Done, run on the board | `02-probe.py`: the watch kit's checkup plus a speaker section (pin rule, gain pin, three beeps). | Lab 01 | A report on the board, files, WiFi, buttons, SPI, speaker, and display. |
| **03: Speaker Test** | Done. Run on the board by Dan on 2026-10-06, and the sounds all worked | `03-sound-test.py`, `sound.py`, `sfx.py`. Tones, a scale, named sounds, then the one-core-versus-two-cores experiment. | The amplifier and speaker | Beeps and melodies that keep playing while the Pico freezes. |
| **04: Hear the Range** | Done. Run on the board three times on 2026-10-06 | `04-hear-the-range.py`: a 20 Hz to 20 kHz sweep. Press UP when you first hear it and when it vanishes. | Lab 03 | Each student finds their own hearing range, and sees how a small speaker behaves down low. |
| **05: Five Voices** | Done. Run on the board by Dan on 2026-10-06 and works as expected | `05-waveforms.py`: sine, triangle, square, saw, and noise, with the wave drawn on the screen. | Lab 03 | Timbre: why the same note sounds different. |
| **06: Sound Effects Gallery** | Done. Run on the board by Dan on 2026-10-06 and all the effects work | `06-sound-effects.py`: 21 effects from `sfx.py`, each with its recipe. | Lab 03 | Sound effects built from slides, waves, and noise. |
| **07: Ringtones** | Done. Run on the board by Dan on 2026-10-06 and works fine | `07-ringtones.py`: four traditional tunes stored as RTTTL text, with the current note on screen. | Lab 03 | A whole song in one line of text. |
| **08: Button Theremin** | Done. Run on the board by Dan on 2026-10-06 and works | `08-button-theremin.py`: hold UP or DOWN to slide the pitch, with the nearest note and how far off it is. | Lab 03 | A playable instrument with smooth pitch. |
| **09: Study Timer** | | `mode_study.py`: focus and break phases, with chimes and a daily minutes ring. Copies in the template and `mode_timer.py`. | Lab 03 | A Pomodoro timer. The first useful study feature, and almost free. |
| **10: Quote of the Day** | | `mode_quote.py`, `packs.py`, and the circle-aware word-wrap. | Lab 09 | Quotes that fit the round screen. |
| **11: Flash Quiz** | | `mode_quiz.py` and `mode_mathfacts.py`, with the choice builder, the three-box memory, and `progress.json`. | Labs 03 and 10 | A working drill, with generated math facts. |
| **12: A Deck of Your Own** | | The pairs deck format, and a CSV-to-deck script. Students make a *US Capitals* deck and one of their own. | Lab 11 | Students author content. |
| **13: Next Quiz** | | `mode_reminder.py`, `reminders.py`, and the wall-clock check in the main loop. | Labs 03 and 09 | Chimes for a quiz that is days away. |
| **14: The Library** | | `mode_library.py` with Browse and Installed tabs, free-space display, remove, and pinning. The manifest, hashing, `modes.json` replacing the `MODES` tuple, and the teacher's `tools/make_manifest.py`. | Labs 09 and 11 | Students and teachers can add and remove modes and decks without a computer. |
| **15: Add Events From Your Phone** | | A small web server on the Pico and a form. Later, the calendar feed. | Lab 13 | No computer needed to add a quiz. |

Lab 09 is the next real milestone. It proves the study-mode button
conventions, and everything after it builds on those.

!!! note "What has been tried"
    **Labs 01 to 08 have all been run on the board** (2026-10-04 to
    2026-10-06) and work. Lab 03's sounds worked and it reproduced the
    two-core results. Lab 04 ran three sweeps in a row with no errors, which
    also exercises `link` and 44.1 kHz audio. Lab 05 worked as expected: all
    five waves, noise included, and the pictures of them. In lab 06 all the
    effects worked. Lab 07's ringtones work fine, which exercises
    `rtttl_notes()`, the tune parser. Lab 08 works, which exercises the held
    note with `pitch()`, `hold()`, and `release()`.

    Before they were run, labs 05 to 08 had their screens drawn through the
    display simulator with a stand-in for the sound module. The simulator
    cannot run the real compiled synthesizer, so the board runs are the
    real test.

    Still to check: a long flash write while a sound plays, and whether
    the core-0 gap in lab 03 is audible by ear (the counters show it).

### What the first kit run showed

Labs 01 and 02 were run on a real Pico 2 W with the Study Buddy wiring on
2026-10-04:

| Check | Result |
|---|---|
| Board | Pico 2 W (RP2350), MicroPython 1.29.0, 150 MHz |
| Heap free after the probe loaded | 419 KB |
| Flash | 4 MB chip, 2.5 MB filesystem, 2.4 MB free with the kit's files on it |
| I2S pin rule | LRC on GP21 is one more than BCLK on GP20, so `I2S()` accepts it |
| I2S timing | 0.76 s of audio accepted in 0.63 s, which is what the 16 kHz clock should give |
| Sound | Heard (three rising beeps) |
| Display | Four color bars shown, full fill 130 ms, same as the watch kit |
| WiFi | The home network is visible but weak, about -72 dBm, and a single scan sometimes misses it, so the probe rescans twice before it warns |

### Lab 04 results: three sweeps

One adult tester ran the hearing-range sweep three times on the real kit
(speaker volume capped at 30), pressing UP when the tone was first heard
and again when it vanished:

| Run | First heard | Stopped hearing |
|---|---|---|
| 1 | 73 Hz | 11,068 Hz |
| 2 | 107 Hz | 11,122 Hz |
| 3 | 57 Hz | 10,171 Hz |

- **The high end was steady**: about 10 to 11 kHz, with a spread of about
  9%, which is about what button-press reaction time produces (the sweep
  climbs roughly 11% in the 250 ms a press takes). It is where the tone
  faded out *for this listener, on this speaker, at this volume*. It is
  not a hearing test: a small speaker also loses output at the top of its
  range, and the answer moves with the volume.
- **The low end was a surprise.** The speaker is too small to make much
  true bass, yet something was heard from 57 to 107 Hz. That is probably
  not the pure tone but distortion (extra notes at two and three times the
  frequency) or a buzz from loose wiring. The wide spread fits a listener
  judging where a buzz begins. The test is to repeat at a lower volume: if
  the first-heard number jumps up, it was distortion. The lab's result
  screen and comments were reworded to say this instead of claiming the
  speaker is silent down low.

### Changes still to make to the copied files

The Study Buddy folder started as a copy of the watch kit's shared files.
Already done: `config.py` has the I2S pins, the gain pin, `GAIN_DB`,
`VOLUME`, and `set_gain()`, and `02-probe.py` has the speaker section.

| File | Change |
|---|---|
| `12-main-template.py` (copied in Lab 09) | Read `modes.json`. Pin up to 8 modes. Import `sound` and `reminders` before the module snapshot. Add the wall-clock reminder check. Wait for a mode's `busy` flag before switching for a reminder. |
| `config.py` | Add `QUIET_START_HOUR` and `QUIET_END_HOUR`, and the `LIBRARIES` list (each with a `name`, a `url`, and a `modes` flag). |
| `mode_timer.py` (copied in Lab 09) | Use `sound.play("done")` instead of the optional piezo buzzer. |
| `upload-code.sh` | Copy the new modules and create the `packs/`, `user/`, and `audio/` folders. |
| `secrets-template.py` | Add `CALENDAR_URL` for the calendar feed. |

## Risks

| Risk | Why it matters | What to do |
|---|---|---|
| **Downloaded modes are unsandboxed code** | A bad mode could read the WiFi password or break the device. | Teacher-controlled HTTPS address only, hash check, confirm screen, and a `modes.json` fallback so a broken mode cannot stop the watch from starting. Packs carry no code. |
| **Audio dropouts during drawing or freezes** | The display blocks the Pico for up to 232 ms, and a WiFi connect blocked it for 9.5 s. | Fixed by running the sound on core 1 with a 256 ms reserve. Measured: no underruns through a 1.2 s freeze, a flash write, garbage collection, or a WiFi connect (see [Audio](04-audio.md#playback-must-survive-drawing-and-freezing)). Still to check: a long flash write, by ear. |
| **Tick counter wraps** | A reminder days away cannot use `ticks_ms()`. | Use the wall clock for reminders. |
| **The RTC resets on power loss** | A device with no battery loses the time. | It resyncs over WiFi at power-up. With no WiFi, reminders stay quiet and the screen says "Clock not set". |
| **Flash wear** | Flash typically survives about 100,000 erases per block. | Write progress at the end of a round, not each question. |
| **Flash space for audio** | The 2.5 MB filesystem holds about 1.5 minutes of speech. | 11 kHz clips first, then a 16 MB board or an SD card. |
| **A private calendar address leaks** | It gives read access to a student's calendar. | Keep it in `secrets.py` and never print or display it. |
| **Wrong attributions on quotes** | Students learn a false fact. | A required `source` note on every shipped quote. |
| **Students' schedules and scores** | Quiz dates and results are about a child. | Everything stays on the device. Nothing is sent anywhere except the calendar fetch the student sets up. |
| **Students install code themselves** | Students use the Library, so they can add a mode that has a bug and hangs the device. | Students only see what the teacher published, a mode can never stop the device from starting (`modes.json` falls back to the built-in modes), and the Installed tab lets a student remove a mode without a computer. Mode installs also need a confirm screen. |
| **A student runs out of flash** | Many decks and modes, plus audio, fill the filesystem. | The Installed tab shows free space, the Library refuses an install that would leave under 200 KB free, and it says so in plain words. |
| **TLS to the Library host** | Some hosts are hard for a small board to reach over HTTPS. | Test GitHub Pages on a real Pico in Lab 14. Fall back to a school server. |

## Open Questions

1. **Where will the class Library live?** The book's GitHub Pages site is
   the simplest home, but only if the Pico's TLS works with it.
2. **How do student-made decks reach other students?** In version 1 a
   student hands the deck to the teacher, who reviews it and adds it to the
   class Library. A second, decks-only "Friends" library that students
   can post to directly (`"modes": false`) would be faster, but it needs a
   place to post and someone to watch it.
3. **Is flash enough, or do we want a 16 MB board in the kit?** This
   depends on how much recorded speech we want. Level 1 and level 2 fit on
   the current board.
4. **Is a fourth button worth it?** A dedicated SELECT button would remove
   the "MODE confirms inside a quiz" rule. It would also make the Study
   Buddy different from the smartwatch wiring.
5. **Should reminders speak, or chime and show text?** Level 1 is the
   cheapest, and level 2 needs recording a vocabulary.
6. **Do younger students get decks only?** The `modes` setting on each
   library can hide code downloads. Is that the default for the youngest
   classes, with the teacher installing modes ahead of time?

## Decisions

| Decision | Date |
|---|---|
| The speaker is on GP18 to GP21, not GP10 to GP12 as first drafted: LRC on GP21, BCLK on GP20, DIN on GP19, and the amplifier's GAIN pin on GP18, so software can pick 6, 9, or 12 dB. The I2S pin rule (LRC is BCLK plus one) holds. This leaves GP8 to GP12 free for a micro-SD card on hardware SPI1. | 2026-10-04 |
| The kit's speaker is the **8 ohm, 2 W** version. It had no markings, so its DC resistance was measured with a multimeter at 7.4 ohms. | 2026-10-06 |
| The Study Buddy has its own lab numbers: 01 is Blink the Onboard LED and 02 is the Probe. The speaker test and everything after move to 03 and up. | 2026-10-04 |
| The code goes in a new folder, `src/kits/study-buddy`, not in `src/kits/sw-gc9b72`. Like the other kits it is self-contained, so it holds its own copy of `lib/`, `config.py`, and `wifi_time.py`. If the copies drift apart, a shared `lib` is a later cleanup. | 2026-10-03 |
| **Both students and instructors use the Library.** The Library screens are written for a student to use alone, and the teacher gets a manifest script and a curation workflow. See [the Library](01-architecture.md#the-library-mode). | 2026-10-03 |
