# Storyboard guide

How to turn `docs/kits/{SLUG}/` into the five scenes, the captions and the event list that
drive both the animation and the soundtrack.

## 1. Pull these facts from the kit docs (and nothing else)

| Need | Where to find it |
|---|---|
| Kit name and one-line pitch | `index.md` title and the sentence under it |
| Audience | "Ages ..." line |
| Parts that must appear | "What's in the kit" table |
| Connections | "How it is wired" table: pin names and wire colors |
| Safety callout (if any) | the `mascot-warning` admonition (for example "3V3, never 5 V") |
| Screens / modes / faces | the lab that combines them (the "main template" lab) and its `img/*.png` |
| Controls and what they do | "How the controls work" table |
| Number of labs | the labs table |
| Real sample values | the kit photo and lab screenshots (times, temperatures, lap times) |

Look at the real screen pictures (`Read` the PNGs) and copy their colors and layout. Use the
same sample values on every screen so the story is consistent (one time, one date).

Never invent specs, prices, performance numbers or claims. If a fact is not in the docs,
leave it out.

## 2. The five scenes

| # | Time | Purpose | Typical content |
|---|---|---|---|
| 1 | 0-3 s | Hook: what is this? | kit name, parts rise into place |
| 2 | 3-8 s | Build: how it goes together | connections draw in, part labels, safety callout |
| 3 | 8-12 s | Power on: it comes alive | camera pushes in; boot screen; first screen with real values |
| 4 | 12-26 s | Use: what it does | each face / mode in turn, with control callouts |
| 5 | 26-30 s | Finale: where to go next | labs counting up, one closing line, fade out |

Fewer than three modes: slow each down (4-5 s) and show the controls working for longer.
More than five: group them, or show five and mention "and more" in the closing line.

## 3. Captions

Each scene has a **kicker** (small caps line) and a **headline** (one line).

- Kicker: at most 40 characters, sentence fragment: `Step 1 · Wire it`, `17 labs · ages 10 and up`.
- Headline: at most 40 characters at 44 px bold; action verbs: "Turn the knob to change the face".
- Plain words for the reading level in the kit's "Ages" line. No jargon the kit does not teach.
- The closing line is the only place for a slogan.
- **Both formats share the caption text.** Landscape shows the headline on one line; portrait
  (a 580 px wide column at 52 px) wraps it to two lines, so a 40-character headline is the
  ceiling and 34 or fewer is comfortable. Write it so it breaks well at a phrase boundary
  ("Turn the knob / to change the face"); the page balances the two lines.
- A kicker must fit one line in portrait (580 px at 18 px caps is about 40 characters).

## 3a. Labels that need a shorter portrait wording

Callout tags sit on the hardware and are larger in portrait, so a long label may not fit. Plan a
short form for each tag: "Display board" instead of "Display board · screen + knob + K0". Mark
the dropped tail with `class="l-only"` in the page. Tags near the right edge of the board must
end inside the safe box at the close camera pose.

## 4. Mode / face pills and the lab chips

- A row of **pills** (bottom band) names the modes; the active one lights with the screen.
- A row of **chips** numbered 01..N counts the labs in the finale. N = number of labs.

## 5. The event list (drives the sound)

Write every visible event with its second. Example (Knob Clock Kit):

| t (s) | Event | Sound accent |
|---|---|---|
| 4.4 + 0.15 i | wire i lands (12 wires) | rising pentatonic bells |
| 7.55 | power LED | start-up jingle (4 bells) |
| 10.4 | real time appears | single high bell |
| 14.4, 17.0, 19.6, 23.2, 26.0 | knob click to the next face | click |
| 20.0, 23.8 | K0 pressed | boop |
| 21.4, 22.6 | knob pushed (lap) | ping |
| 26.65 + 0.14 k | lab chip k lights | rising major scale |
| 29.0 | closing line done | final chord stab |

These same numbers go into the animation's keyframe percentages and into
`video.json` -> `music.accents`. Change one, change the other.

## 6. Accessibility

The animation root carries a one-paragraph `aria-label` that describes the whole video in
words (what the parts are, what the kit does, how many labs). Write it from the storyboard.

## 7. Checklist before authoring

- [ ] five scenes with captions, each headline at most 40 characters (one line landscape, two portrait)
- [ ] a short portrait wording for every long callout tag
- [ ] mode list and the sample values used on every screen
- [ ] event list with seconds
- [ ] chosen BPM so scene boundaries fall on bar lines (see soundtrack guide)
- [ ] no claim that is not in the kit docs
