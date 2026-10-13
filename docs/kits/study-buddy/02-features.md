# Features

Each feature is one mode. Screens are described for the round 360×360
display, where the usable area is the circle of radius `SAFE_RADIUS`
(168 px), narrower near the top and bottom. See
[Round-Screen Layout Rules](#round-screen-layout-rules) at the end.

## Button Conventions

Every study mode uses the buttons the same way, so students learn them
once:

| Button | Usual job in a study mode |
|---|---|
| **UP** | Move up, or the main action (start, next) |
| **DOWN** | Move down, or the secondary action (skip, back) |
| **MODE, short** | Switch to the next pinned mode. When a mode is in the middle of a task (an open question, a setting screen), it keeps MODE and uses it as **confirm**. |
| **MODE, long (1 s)** | Leave the task. Ends a quiz round, or backs out of a setting screen. |

This is the timer's rule from [Lab 12](../sw-gc9b72/12-main-template.md#the-buttons-changed-a-little),
applied everywhere.

---

## Next Quiz (`mode_reminder`)

**Goal:** "Remind me when my next algebra quiz is."

### The screen

```text
        NEXT QUIZ
      Algebra quiz
        2 days
        4 hours
   Fri Oct 9  9:15 AM
```

- The subject and kind use the big font, centered, in the event's color.
- The countdown shows the two largest units that are not zero: *2 days 4
  hours*, *3 hours 20 min*, *45 min*. Under an hour, it counts down in
  minutes and seconds.
- The date and time of the event sit below in the small font.
- UP and DOWN step through the next few upcoming events. A small
  "Event 1 of 4" line shows where you are. It sits above the template's
  dot strip, never in it.
- With no events, it shows "No events. Add some at: <address>" (see
  [Getting Events On](#getting-events-on)).

### When it chimes

Each event has up to three reminders. The default is all three:

| Reminder | When | Message on screen |
|---|---|---|
| `night_before` | 7:00 PM the day before | "Tomorrow: Algebra quiz" |
| `morning_of` | 7:00 AM that day | "Today: Algebra quiz" |
| `hour_before` | 60 minutes before | "In 1 hour: Algebra quiz" |

A reminder is skipped if its time has already passed when the event is
added, and if the Study Buddy is off when a reminder is due, the **most
recent** missed reminder shows at power-up as a banner on the first screen.
Events more than 24 hours past are dropped from the list.

When a reminder fires, the template switches to this mode and plays a chime
(see [Audio](04-audio.md)). Pressing any button stops the chime and shows
the event, and a second press returns to the previous mode.

### Rules

- Event times are local. The RTC already holds local time, so reminders
  use `time.mktime(time.localtime())` and need no time zone math.
- Reminders compare wall-clock seconds, never `ticks_ms()`. See
  [the reminder check](01-architecture.md#the-reminder-check).
- A reminder never interrupts a quiz question or a timer being set. The
  template waits up to 30 seconds.
- Up to 50 events are loaded. Extra events are ignored, and the Pico
  prints a warning.

### Getting events on

Three stages, each usable on its own:

| Stage | How | Cost |
|---|---|---|
| **v1: file** | The student edits `user/events.json` in Thonny. | Free, but needs a computer. |
| **v2: phone form** | Holding MODE in this mode opens a setup screen that starts a tiny web server on the Pico. The screen shows its address (and `studybuddy.local` if mDNS works **(verify)**). The student opens it on a phone, fills in a form (subject, kind, date, time), and the Pico writes `user/events.json`. | Needs a small `microdot`-style server in the Pico's RAM. Only runs while the student is in this screen. |
| **v3: calendar feed** | `secrets.py` holds a private `.ics` calendar address (Google Calendar, Canvas, and Google Classroom can all publish one). The Pico fetches it once a day, **streams** it a chunk at a time (never loading the whole file), and keeps events whose title contains *quiz*, *test*, or *exam*. | Calendar files can be hundreds of KB, so parsing must be streaming. The address is a secret and must never be printed or shown. |

!!! warning "The calendar address is a password"
    A private `.ics` address lets anyone who has it read the whole
    calendar. It goes in `secrets.py` (which is never shared) and is never
    printed in the Thonny shell.

---

## Flash Quiz (`mode_quiz`)

**Goal:** "Help quiz me on state capitals."

The same engine plays any **pairs deck**: state and capital, Spanish and
English, element and symbol, word and definition. See
[Pack Formats](03-pack-formats.md#pairs-deck).

### A round

1. **Pick a deck.** UP and DOWN choose among installed decks. MODE starts.
2. **Ten questions** per round. Each shows a prompt and four choices:
   ```text
        Capital of
          Ohio?

       > Columbus
         Cleveland
         Cincinnati
         Dayton
   ```
3. **Choose.** UP and DOWN move the `>` marker. **MODE confirms.**
4. **Feedback.** Right: the answer turns green, with a rising two-note
   jingle. Wrong: the picked answer turns red, the right one turns green,
   and a short low buzz plays. The screen waits for any button.
5. **Results.** "8 of 10", a bar of ten dots (green or red), and a
   message from the encouragement list (see [Daily Quote](#daily-quote-mode_quote)).
   MODE moves on, UP starts another round.

Holding MODE during a question ends the round and shows the results so far.

### Choices

The engine builds the wrong answers itself, so a deck only needs pairs:

- Take the other pairs' answers in the **same deck**.
- If an item has a `group` tag (for example `"region": "Midwest"`),
  prefer wrong answers from the same group. This makes the questions
  harder and more sensible.
- Never offer the right answer twice, and never offer two identical
  choices.
- A deck with fewer than 4 pairs offers as many choices as it has.
- **Direction.** Each round is *a→b* or *b→a*, chosen by the student before
  the round. Default is the deck's own `default_direction`.

### Remembering what you miss

The quiz keeps a simple three-box (Leitner) record per item:

| Box | Meaning | Chance of being asked |
|---|---|---|
| 1 | New, or missed recently | weight 5 |
| 2 | Got right once | weight 2 |
| 3 | Got right twice in a row | weight 1 |

Right moves an item up one box (to a maximum of 3), wrong sends it back to
box 1. Questions are chosen by weight, and never the same item twice
in a row. Records live in `user/progress.json` and are written at the end
of each round, not after every question, to avoid wearing out the flash.

The deck-picking screen shows how many items are in box 3, such as
"US Capitals 31/50".

### Math Facts

`mode_mathfacts` uses the same screens with questions generated on the
Pico, so no deck file is needed: times tables (2 to 12 chosen by the
student), plus addition, subtraction, and division. Wrong answers are near
misses (the answer ±1, ±2, or a neighboring table value), which is how
real mistakes happen. Progress is kept per table.

---

## Daily Quote (`mode_quote`)

**Goal:** "Give me encouraging and inspirational quotes about education."

- Shows one quote at a time, centered, with the speaker's name beneath it
  in a different color.
- **Quote of the day:** a quote chosen from the date alone, so the Study
  Buddy shows the same one all day and a different one tomorrow, with no
  need to store anything.
- **UP** shows another quote (random, not repeating until the whole deck
  has been shown). **DOWN** goes back one.
- A soft chime plays when the day's quote first appears.
- Quotes also feed the quiz's results screen and the "you've missed three
  in a row" message, using an optional `tags` list (`"encourage"`,
  `"persist"`, `"curious"`).

!!! warning "Check every attribution"
    Quotes are the easiest content to get wrong, because many famous
    lines are credited to people who never said them. Each quote in a
    shipped deck needs a `source` note, and a quote with no verified
    source is attributed to "Unknown" or left out. Making students check
    one quote's source is a good lab in itself.

### Layout

Text is wrapped by a **circle-aware** word-wrap: the number of characters
per line depends on how wide the circle is at that row. In the big font,
the middle rows hold about 20 characters and rows near the top and bottom
hold about 12. A quote that cannot fit in 9 lines in the big font uses the
small font instead.

---

## Study Timer (`mode_study`)

A countdown timer with two phases, built from
[`mode_timer.py`](../sw-gc9b72/11-countdown-timer.md):

- **Focus** (default 25 minutes), then **Break** (default 5 minutes), then
  repeat. A long break (15 minutes) follows every fourth focus session.
- The ring and the digits are the timer's. The ring is **blue** for focus
  and **green** for break.
- A chime marks each change of phase. Because the timer already hands the
  template a `wake_at`, it chimes in any mode.
- A hold of MODE sets the lengths, exactly like Lab 12's timer.
- **Study minutes today** (completed focus sessions only) add up and are
  shown on the idle screen as a ring that fills toward a daily goal.
  This reuses `TickRing` from `watchparts.py`.

---

## Library (`mode_library`)

See [Architecture](01-architecture.md#the-library-mode).

---

## Later Ideas

Not in the first version, listed so they are not forgotten:

- **Homework checklist.** UP and DOWN scroll, MODE ticks an item. Items
  come from the phone form.
- **Brain break.** A slow breathing animation with soft tones, started by
  a long press.
- **Spelling with sound.** Say the word through the speaker, then show
  four spellings. This needs a pack with audio files.
- **Spaced reminders for quiz prep.** If a quiz is in 3 days, the Study
  Buddy suggests a round of the matching deck.

## Round-Screen Layout Rules

The glass is a circle of radius 180, with `SAFE_RADIUS` 168 for anything
that must not be cut off. At a distance `d` from the center row, the safe
half-width is `sqrt(168² − d²)`:

| Row distance from center | Safe width | Big font (16 px) | Small font (8 px) |
|---|---|---|---|
| 0 | 336 px | 21 characters | 42 characters |
| 60 | 314 px | 19 | 39 |
| 100 | 270 px | 16 | 33 |
| 140 | 186 px | 11 | 23 |

Rules for every study mode:

1. Place short text (titles, one-word answers) near the top and bottom.
   Place long text in the middle rows.
2. A choice that does not fit in the big font drops to the small font
   instead of being cut off.
3. The bottom dot strip (y = 316 to 328) is the template's. Do not draw
   there.
4. Redraw only what changed, as every watch face does, and avoid
   full-screen fills while audio plays.
