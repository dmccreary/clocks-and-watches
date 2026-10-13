---
name: video-of-kit-generator
description: Creates a 30-second animated explainer video with an upbeat chiptune soundtrack for a hardware kit in this book (docs/kits/{SLUG}). Plans a storyboard from the kit docs, authors a CSS-animation page, renders it frame by frame with headless Chromium, synthesizes the music with sound accents synced to the picture, and muxes an MP4. Stores only the recipe (spec, animation source, build script) in media/kits/{SLUG}/ and writes the videos to ~/Movies, never into the git repo. Use when asked for a kit video, teaser or promo animation, a "30-second video of the kit", or to add or refresh a kit video's soundtrack.
license: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
metadata:
  ibook.version: "1.0"
---

# Video of Kit Generator

**Version:** 1.0

Turns one kit (`docs/kits/{SLUG}/`) into a 30-second, 1920x1080, 30 fps MP4 with an
original upbeat chiptune soundtrack. The picture is a looping CSS animation drawn from the
kit's own docs; the music is synthesized with sound accents synced to what is on screen.

## The storage rules (read first, they are not negotiable)

| What | Where | In git? |
|---|---|---|
| The recipe: `video.json`, `animation.html`, `build.sh`, `README.md` | `media/kits/{SLUG}/` | **yes** (small text) |
| The finished videos (`*.mp4`) | `~/Movies/{SLUG}-30s.mp4` and `{SLUG}-30s-silent.mp4` | **never** |
| Frames, soundtrack WAV, contact sheets | a temp or scratchpad directory | **never** |

- Never write an `.mp4`, `.mov`, `.wav`, `.mp3`, `.gif` or a frames folder anywhere inside the repo,
  and never `git add` one. Do not copy a video into `docs/` to "embed" it.
- `scripts/build_video.sh` refuses to write when the output directory or the work directory is
  inside a git repo, and ends by running `scripts/check_no_media_in_repo.sh`.
- `media/.gitignore` (template: `assets/media-gitignore.txt`) is the second line of defense.
  Create it if it is missing.

## When to use

- "Make a video of the {name} kit", "a 30-second teaser / promo / explainer animation"
- "Add a soundtrack to the kit video", "re-render the kit video with the new face"

Not for: slide decks or narrated audio (`book-media-generator`), or interactive MicroSims
(`microsim-generator`).

## Inputs

1. **SLUG**: the folder name under `docs/kits/` (for example `rect-tft-display`). If the user
   gives a kit name instead, `ls docs/kits` and map it; ask only if two kits could match.
2. The kit's docs: `docs/kits/{SLUG}/index.md` first, then the photos and the lab pages you
   need for exact values (screens, pin labels, mode names).

## Prerequisites (check once; stop and tell the user if missing)

```bash
command -v ffmpeg ffprobe                      # brew install ffmpeg
python3 -I -c "import playwright, numpy"      # pip install playwright numpy && playwright install chromium
```

The mkdocs conda env's `python3` already has both. The soundtrack needs only numpy, so it
runs anywhere. Fonts come from Google Fonts (Rubik, VT323), so rendering needs a network
connection.

## Workflow

Set `SKILL=~/.claude/skills/video-of-kit-generator` and `RECIPE=media/kits/{SLUG}`.

### 1. Preflight

- `mkdir -p $RECIPE`. If `media/.gitignore` is missing, copy `assets/media-gitignore.txt` to it.
- If `$RECIPE/video.json` already exists, this is a **refresh**: read it and `animation.html`,
  change only what was asked, and skip to step 5.

### 2. Read the kit and plan the storyboard

Read `references/storyboard-guide.md`. Produce the five-scene storyboard (the timeline below)
with a caption per scene, the list of face/mode screens to show, and an **event list**: the
second at which each visible event happens (wire lands, power on, knob turn, button press...).
Use only facts that are in the kit docs: names, pin labels, values, number of labs, age range.
Never invent specs, prices or claims.

### 3. Write `video.json`

Start from `assets/examples/knob-clock-video.json`. Fill `slug`, `title`, `kit_docs`,
`storyboard`, and the `music` block (read `references/soundtrack-guide.md`). Choose a BPM
whose bar length divides the scene boundaries (120 BPM: 2.0 s bars).

### 4. Author `animation.html`

Read `references/animation-guide.md`, then copy `assets/examples/knob-clock-animation.html` to
`$RECIPE/animation.html` and adapt it: the hardware drawing, the screen faces, the captions,
the event times, and the keyframe percentages (seconds / 30 x 100). Keep the chrome (loop
cover, caption slots, progress bar, camera rig, pill and chip rows) unless the storyboard
says otherwise. The page must be self-contained and animate with CSS only.

### 5. Look at test frames before spending minutes on a render

```bash
T=$(mktemp -d)                              # outside the repo
python3 -I $SKILL/scripts/render_frames.py $RECIPE/animation.html --out $T \
        --scale 1 --times 1.5,6,9.5,12.5,16,20,24,28
cd $T && ffmpeg -y -loglevel error -i t_01.50.png -i t_06.00.png -i t_09.50.png -i t_12.50.png \
  -filter_complex "[0]scale=800:-1[a];[1]scale=800:-1[b];[2]scale=800:-1[c];[3]scale=800:-1[d];[a][b]hstack[r1];[c][d]hstack[r2];[r1][r2]vstack" sheet1.png
```

Open the contact sheets with the Read tool and check: captions fit on one line; no text
overlaps a part; fonts are the intended ones (not a fallback); every scene shows what the
storyboard says; the first and last frames are the fade-from/to-background cover. Fix, then
re-render the same times. Iterate here, not in the full render.

### 6. Install the build entry points

Copy `assets/build.sh` to `$RECIPE/build.sh` (`chmod +x`) and fill
`assets/recipe-README-template.md` into `$RECIPE/README.md` (replace `{SLUG}`, `{TITLE}`,
`{NAME}`). The recipe must be rebuildable by one command.

### 7. Build

```bash
$RECIPE/build.sh --preview     # about 30 s: half size, 10 fps; proves the pipeline
$RECIPE/build.sh               # full quality; a few minutes (900 PNG frames)
```

Run the full build in the background and wait for it. Output:
`~/Movies/{NAME}.mp4` (with music) and `~/Movies/{NAME}-silent.mp4`. Delete any `-preview`
files from `~/Movies` when done.

### 8. Verify (the script prints these; read them)

| Check | Pass |
|---|---|
| Duration | 30.0 s (+/- 0.1) |
| Resolution / fps | 1920x1080, 30 fps (full build) |
| Integrated loudness | -16 to -12 LUFS |
| True peak | at or below -0.3 dBFS |
| Repo hygiene | `OK: no rendered media inside <repo>` |
| `git status` | only `media/kits/{SLUG}/` and `media/.gitignore` are new |

You cannot listen to the track. Say so, and give the user the path and `open <file>` so they
can. A spectrogram (`ffmpeg -i x.wav -lavfi showspectrumpic=s=1400x500 spec.png`) is a quick
sanity check for rumble or clipping.

### 9. Report

Give: the video path(s) in `~/Movies`, duration/size/loudness, what the recipe folder
contains, the one-line rebuild command, and the sound accents so the user can ask to remove
them. If they want it on the site, they upload it and embed by URL; do not copy it into the repo.

## The 30-second house timeline

| Time | Scene | Picture | Music |
|---|---|---|---|
| 0-3 s | Meet the kit | fade in from background; parts rise into place; caption 1 | soft arpeggio fades in |
| 3-8 s | Build it | connections draw in (wires, cables), labels, safety callout | hats, then bass at 4 s; riser 6-7.5 s |
| 8-12 s | Power on | camera pushes in; boot screen, then the first real screen | start-up jingle 7.5 s; kick from 8 s |
| 12-26 s | Use it | 3-5 faces or modes, 2.5-3.5 s each; control callouts; mode pills | full band + lead melody; clicks, boops |
| 26-30 s | Finale | camera pulls back; lab chips count up; closing line; fade out | counting scale; final chord 29 s; fade |

Scene boundaries land on bar lines at 120 BPM (2.0 s bars): 3 s = beat 6, 8 / 12 / 26 s = bars 4 / 6 / 13.

## Files in this skill

| File | Purpose |
|---|---|
| `scripts/build_video.sh` | recipe folder in, MP4 in `~/Movies` out; runs all the steps and checks |
| `scripts/render_frames.py` | seeks the page's CSS animations and screenshots frames (Playwright) |
| `scripts/make_soundtrack.py` | `video.json` in, WAV out; numpy chiptune synth with sync accents |
| `scripts/check_no_media_in_repo.sh` | fails if rendered media sits inside the repo |
| `assets/examples/` | the finished Knob Clock Kit animation and spec: the house style to copy |
| `assets/build.sh`, `assets/recipe-README-template.md`, `assets/media-gitignore.txt` | recipe boilerplate |
| `references/storyboard-guide.md` | what to pull from the kit docs; scenes, captions, event lists |
| `references/animation-guide.md` | layout grid, keyframe math, idioms, pitfalls |
| `references/soundtrack-guide.md` | `music` block fields, tempo grid, accents, loudness targets |

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| Every frame identical, "no CSS animations" warning | page animates with JS timers; convert to CSS keyframes |
| Text in the wrong font | Google Fonts blocked or the family name is misspelled in the page |
| Elements visible on the second loop but not the first | a positive `animation-delay` shifted the reset; see the stagger idiom in the animation guide |
| Hard cut shows a flicker frame | adjacent keyframes closer than 0.02 s share a percentage; separate them |
| Build says REFUSING | the output or work directory is inside a git repo; use `~/Movies` and a temp dir |
| Music too loud or quiet | adjust `music.peak` (0.7 to 0.85) and `limiter_drive` |
