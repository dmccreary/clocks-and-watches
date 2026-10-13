# Pack Formats

Packs are plain JSON, small enough to read in a text editor and to write
by hand. Every pack has:

| Field | Meaning |
|---|---|
| `version` | The format version. Always `1` for now. |
| `kind` | `pairs`, `quotes`, or `events`. A mode refuses a pack of the wrong kind. |
| `title` | A name of at most 20 characters, shown in the deck picker. |

## Limits

The Pico reads a whole pack into RAM, so packs are kept small. `packs.py`
refuses anything over these limits and prints why:

| Limit | Value | Why |
|---|---|---|
| File size | 40 KB | A 50-item deck is about 3 KB. 40 KB leaves plenty of RAM for the mode itself. |
| Pairs per deck | 300 | |
| Quotes per file | 300 | |
| Events | 50 | |
| Text length | 90 characters per field | Fits the screen at the big font in three lines. |

Anything bigger would need a streaming format (one JSON object per line,
read one line at a time). That is not part of version 1.

## Pairs Deck

```json
{
  "version": 1,
  "kind": "pairs",
  "title": "US Capitals",
  "prompt_ab": "Capital of\n{a}?",
  "prompt_ba": "{b} is the\ncapital of?",
  "default_direction": "ab",
  "pairs": [
    {"a": "Ohio",     "b": "Columbus",  "group": "Midwest"},
    {"a": "Alabama",  "b": "Montgomery","group": "South"},
    {"a": "Oregon",   "b": "Salem",     "group": "West"}
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `prompt_ab`, `prompt_ba` | Yes | Question text. `{a}` and `{b}` are replaced by the item's two sides. `\n` starts a new line. |
| `default_direction` | No | `ab` (default) or `ba`. |
| `pairs[].a`, `pairs[].b` | Yes | The two sides. They must be unique within the deck. |
| `pairs[].group` | No | A tag used to pick sensible wrong answers (see [Flash Quiz](02-features.md#choices)). |
| `pairs[].audio` | No | The name of a clip in `audio/` to play with the question (see [Audio](04-audio.md)). |

!!! tip "Students can write a deck in a spreadsheet"
    A deck is two columns of text. A short script on a computer turns a
    CSV with columns `a,b,group` into this JSON. The repo's
    `src/csv-to-json` folder has a starting point.

## Quotes File

```json
{
  "version": 1,
  "kind": "quotes",
  "title": "Keep Going",
  "quotes": [
    {
      "text": "Example quote text goes here.",
      "by": "Person's Name",
      "source": "Where this was verified: book, speech, and year",
      "tags": ["persist"]
    }
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `text` | Yes | The quote. |
| `by` | Yes | Who said it. Use `"Unknown"` if not verified. |
| `source` | Yes in a shipped deck | Where the attribution was checked. Not shown on screen. Packs a student makes for themselves may leave it out. |
| `tags` | No | `encourage`, `persist`, `curious`. Used for the quiz results screen. |

## Events File

This one is the student's own, saved as `user/events.json`:

```json
{
  "version": 1,
  "kind": "events",
  "title": "My Schedule",
  "events": [
    {
      "title": "Algebra quiz",
      "subject": "algebra",
      "kind": "quiz",
      "when": "2026-10-09T09:15",
      "remind": ["night_before", "morning_of", "hour_before"],
      "deck": "us-capitals"
    }
  ]
}
```

| Field | Required | Meaning |
|---|---|---|
| `title` | Yes | What shows on screen. |
| `subject` | No | A short lowercase word. Used for the optional spoken reminder (see [Audio](04-audio.md#level-2-composed-phrases)). |
| `kind` | No | `quiz`, `test`, `exam`, `homework`, `other`. Sets the color. |
| `when` | Yes | Local date and time as `YYYY-MM-DDTHH:MM`. Never has a time zone. |
| `remind` | No | Any of `night_before` (7 PM the day before), `morning_of` (7 AM), `hour_before`. Default is all three. |
| `deck` | No | The id of a deck to suggest practicing in the reminder screen. |

## Library Manifest

The Library's list of what can be downloaded. Its address is the `url` of
an entry in `LIBRARIES` in `config.py`.

```json
{
  "version": 1,
  "title": "Room 12 Library",
  "items": [
    {
      "id": "us-capitals",
      "type": "pack",
      "title": "US Capitals",
      "description": "All 50 states and capitals",
      "author": "Ms. Rivera",
      "featured": true,
      "file": "packs/us-capitals.json",
      "bytes": 2940,
      "sha256": "<64 hex digits>"
    },
    {
      "id": "mode-mathfacts",
      "type": "mode",
      "title": "Math Facts",
      "file": "modes/mode_mathfacts.py",
      "bytes": 5210,
      "sha256": "<64 hex digits>",
      "module": "mode_mathfacts",
      "needs": ["sound"]
    }
  ]
}
```

| Field | Meaning |
|---|---|
| `id` | A unique name for the item. |
| `type` | `pack` or `mode`. The screens call a pack a **deck**. |
| `title` | At most 20 characters. |
| `description` | A one-line summary of at most 40 characters, shown under the title on the Browse screen. |
| `author` | Optional. Who made it, such as a teacher or a student. Not shown on the device. |
| `featured` | Optional, default `false`. Featured items are listed first, with a star. |
| `file` | A path relative to the manifest. |
| `bytes` | The exact size. The download is rejected if it differs. |
| `sha256` | The file's hash. The download is rejected if it differs. |
| `module` | For a mode, the module name to add to `modes.json`. |
| `needs` | Modules on the Pico the mode requires. The Library refuses to install a mode if one is missing. |

A script on the teacher's computer (`tools/make_manifest.py`) generates
the manifest and the hashes, so nobody ever types a hash by hand. The
manifest's address goes in a device's `LIBRARIES` setting in `config.py`;
see [the Library](01-architecture.md#more-than-one-library).

## Saved Progress

`user/progress.json`, written by the quiz. Students do not edit it.

```json
{
  "version": 1,
  "decks": {
    "us-capitals": {"Ohio": 3, "Alabama": 1},
    "math-7": {"7x8": 2}
  },
  "study": {"2026-10-03": 50}
}
```

- Each deck maps an item's `a` text to its box (1, 2, or 3). Items not
  listed are box 1.
- `study` is the minutes of completed focus time per date.
- Entries older than 60 days in `study` are dropped when the file is
  saved. Items removed from a deck are dropped the next time it is played.
- If the file cannot be read, it is renamed `progress.bad` and a fresh
  one is started. A student never loses the ability to play.
