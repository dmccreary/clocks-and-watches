---
name: video-of-kit-generator
description: Creates a 30-second animated explainer video with an upbeat chiptune soundtrack for a hardware kit in this book (docs/kits/{SLUG}), in TWO formats - portrait 1080x1920 (the default, required for YouTube Shorts) and landscape 1920x1080. Plans a storyboard from the kit docs, authors one CSS-animation page with a portrait and a landscape layout, renders it frame by frame with headless Chromium, synthesizes the music with sound accents synced to the picture, and muxes both MP4s. Stores only the recipe (spec, animation source, build script, per-format instructions) in media/kits/{SLUG}/ and writes the videos to ~/Movies, never into the git repo. Use when asked for a kit video, teaser or promo animation, a "30-second video of the kit", a vertical/portrait or YouTube Shorts version, or to add or refresh a kit video's soundtrack.
license: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
metadata:
  ibook.version: "1.1"
---

# Video of Kit Generator

**Version:** 1.1

Turns one kit (`docs/kits/{SLUG}/`) into a 30-second, 30 fps MP4 with an original upbeat
chiptune soundtrack, in **two versions** built from one recipe:

| Version | Frame | For | File in `~/Movies` |
|---|---|---|---|
| **Portrait** (the default) | 1080 x 1920, 9:16 | YouTube Shorts and other vertical feeds | `{NAME}.mp4` |
| Landscape | 1920 x 1080, 16:9 | regular YouTube, the site, slides | `{NAME}-landscape.mp4` |

Why two: YouTube only publishes a short video as a **Short** when the frame is vertical (or
square). A 30-second landscape video uploads as an ordinary video, so the portrait version is the
default and the one to upload for Shorts. Both share the same story, timing and soundtrack; the
picture is a looping CSS animation drawn from the kit's own docs, laid out once for each format.

Each kit's recipe folder carries the detailed instructions for each version
(`media/kits/{SLUG}/PORTRAIT.md` and `LANDSCAPE.md`): how to build it, what its layout does,
what to check, and how to upload or embed it.

## The storage rules (read first, they are not negotiable)

| What | Where | In git? |
|---|---|---|
| The recipe: `video.json`, `animation.html`, `build.sh`, `README.md`, `PORTRAIT.md`, `LANDSCAPE.md` | `media/kits/{SLUG}/` | **yes** (small text) |
| The finished videos (`*.mp4`), four files per kit | `~/Movies/{NAME}.mp4`, `{NAME}-silent.mp4` (portrait), `{NAME}-landscape.mp4`, `{NAME}-landscape-silent.mp4` | **never** |
| Frames, soundtrack WAV, contact sheets | a temp or scratchpad directory | **never** |

- Never write an `.mp4`, `.mov`, `.wav`, `.mp3`, `.gif` or a frames folder anywhere inside the repo,
  and never `git add` one. Do not copy a video into `docs/` to "embed" it.
- `scripts/build_video.sh` refuses to write when the output directory or the work directory is
  inside a git repo, and ends by running `scripts/check_no_media_in_repo.sh`.
- `media/.gitignore` (template: `assets/media-gitignore.txt`) is the second line of defense.
  Create it if it is missing.

## When to use

- "Make a video of the {name} kit", "a 30-second teaser / promo / explainer animation"
- "YouTube wants it vertical", "make a Shorts version", "a portrait / landscape version"
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
- If the existing `video.json` has **no `formats` block**, it is a one-format (landscape-only)
  recipe from before v1.1. Migrate it: add the `formats` block (step 3), add the layout tokens
  and the PORTRAIT block to `animation.html` (step 4), add `PORTRAIT.md` / `LANDSCAPE.md` (step
  6), then continue at step 5.

### 2. Read the kit and plan the storyboard

Read `references/storyboard-guide.md`. Produce the five-scene storyboard (the timeline below)
with a caption per scene, the list of face/mode screens to show, and an **event list**: the
second at which each visible event happens (wire lands, power on, knob turn, button press...).
Use only facts that are in the kit docs: names, pin labels, values, number of labs, age range.
Never invent specs, prices or claims. Captions must work in **both** formats: at most 40
characters, written so they break well on two lines in portrait. Plan a short portrait wording
for any long callout tag.

### 3. Write `video.json`

Start from `assets/examples/knob-clock-video.json`. Fill `slug`, `title`, `kit_docs`,
`storyboard`, the `formats` block (leave it as in the example unless a kit needs different
sizes), and the `music` block (read `references/soundtrack-guide.md`). Choose a BPM whose bar
length divides the scene boundaries (120 BPM: 2.0 s bars).

`formats` maps a format name to its stage size, scale and filename suffix:

```json
"formats": {
  "portrait":  { "default": true, "width": 720,  "height": 1280, "scale": 1.5, "suffix": "" },
  "landscape": {                   "width": 1280, "height": 720,  "scale": 1.5, "suffix": "-landscape" }
}
```

The `default` format has the plain `{NAME}.mp4`; the other gets its suffix. Width x scale and
height x scale must come out at 1080x1920 and 1920x1080.

### 4. Author `animation.html`: one page, two layouts

Read `references/animation-guide.md` (especially "Two formats"), then copy
`assets/examples/knob-clock-animation.html` to `$RECIPE/animation.html` and adapt it: the
hardware drawing, the screen faces, the captions, the event times, and the keyframe percentages
(seconds / 30 x 100). Keep the chrome (loop cover, caption slots, progress bar, camera rig, pill
and chip rows) unless the storyboard says otherwise. The page must be self-contained and animate
with CSS only.

The page carries **both** layouts. Layout numbers live in `:root` tokens (landscape) and in the
`:root[data-format=portrait]` block at the end of the stylesheet. Author landscape first, then
re-tune the portrait block: caption position, the three camera poses, tag positions and sizes,
pill/chip wrapping. Do not duplicate the keyframes and do not fork the page.

### 5. Look at test frames before spending minutes on a render

Render the same moments in both formats and tile them. Do this for every change; it takes
seconds, a full render takes minutes.

```bash
T=$(mktemp -d)                              # outside the repo
TIMES=1.5,5,9.5,14,20.5,25,28,29
for F in portrait landscape; do
  python3 -I $SKILL/scripts/render_frames.py $RECIPE/animation.html --out $T/$F \
          --format $F --scale 1 --times $TIMES
done
$SKILL/scripts/contact_sheet.sh $T/portrait  $T/portrait.png  4 --safe   # yellow = Shorts safe box
$SKILL/scripts/contact_sheet.sh $T/landscape $T/landscape.png 4
```

Open both sheets with the Read tool and check: captions fit (one line landscape, one or two
lines portrait, no orphan word); no text overlaps a part; fonts are the intended ones (not a
fallback); every scene shows what the storyboard says; the first and last frames are the
fade-from/to-background cover. **Portrait only:** captions, callout tags, the controls and the
screen are inside the yellow safe box; the whole kit is readable at the wide pose. A
`render_frames.py` warning that the page is "larger than the portrait frame" means the page has
no portrait layout. Fix, then re-render the same times. Iterate here, not in the full render.

### 6. Install the build entry points and the per-format instructions

- Copy `assets/build.sh` to `$RECIPE/build.sh` (`chmod +x`).
- Fill `assets/recipe-README-template.md` into `$RECIPE/README.md` (replace `{SLUG}`, `{TITLE}`,
  `{NAME}` and the storyboard rows).
- Fill `assets/recipe-PORTRAIT-template.md` into `$RECIPE/PORTRAIT.md` and
  `assets/recipe-LANDSCAPE-template.md` into `$RECIPE/LANDSCAPE.md`. Replace `{SLUG}`, `{TITLE}`,
  `{NAME}` and write `{KIT_NOTES}` for this kit: its camera path with times, how each caption
  wraps, the short tag wordings, the pill/chip wrapping. Those notes are what makes the
  instructions "detailed" for this kit; do not leave the placeholder.

The recipe must be rebuildable by one command, and each format must be documented.

### 7. Build

```bash
$RECIPE/build.sh --preview     # about a minute: both formats, half size, 10 fps; proves the pipeline
$RECIPE/build.sh               # full quality, both formats; a few minutes each (900 PNG frames)
$RECIPE/build.sh --format portrait     # one format only (portrait | landscape)
```

Run the full build in the background and wait for it. The soundtrack is synthesized once and
muxed into both. Output in `~/Movies`:

- `{NAME}.mp4` and `{NAME}-silent.mp4`: portrait, with and without music
- `{NAME}-landscape.mp4` and `{NAME}-landscape-silent.mp4`: landscape, with and without music

Delete any `-preview` files from `~/Movies` when done. Before a full build, check whether
`~/Movies/{NAME}.mp4` already exists: in recipes from before v1.1 that name was the landscape
video, and the build replaces it with the portrait one. Tell the user.

### 8. Verify (the script prints these per format; read them)

| Check | Pass |
|---|---|
| Duration | 30.0 s (+/- 0.1) |
| Frame | portrait `1080x1920`, landscape `1920x1080` (full build) |
| fps | 30 (full build) |
| Integrated loudness | -16 to -12 LUFS |
| True peak | at or below -0.3 dBFS |
| Repo hygiene | `OK: no rendered media inside <repo>` |
| `git status` | only `media/kits/{SLUG}/` and `media/.gitignore` are new |

You cannot listen to the track. Say so, and give the user the path and `open <file>` so they
can. A spectrogram (`ffmpeg -i x.wav -lavfi showspectrumpic=s=1400x500 spec.png`) is a quick
sanity check for rumble or clipping.

### 9. Report

Give: both video paths in `~/Movies` and which is which (portrait = default = the one for
YouTube Shorts; landscape = regular YouTube / the site), duration/size/loudness, what the recipe
folder contains, the one-line rebuild command, and the sound accents so the user can ask to
remove them. Point to `PORTRAIT.md` / `LANDSCAPE.md` for upload steps. If they want it on the
site, they upload it and embed by URL; do not copy it into the repo.

## The 30-second house timeline

| Time | Scene | Picture | Music |
|---|---|---|---|
| 0-3 s | Meet the kit | fade in from background; parts rise into place; caption 1 | soft arpeggio fades in |
| 3-8 s | Build it | connections draw in (wires, cables), labels, safety callout | hats, then bass at 4 s; riser 6-7.5 s |
| 8-12 s | Power on | camera pushes in; boot screen, then the first real screen | start-up jingle 7.5 s; kick from 8 s |
| 12-26 s | Use it | 3-5 faces or modes, 2.5-3.5 s each; control callouts; mode pills | full band + lead melody; clicks, boops |
| 26-30 s | Finale | camera pulls back; lab chips count up; closing line; fade out | counting scale; final chord 29 s; fade |

Scene boundaries land on bar lines at 120 BPM (2.0 s bars): 3 s = beat 6, 8 / 12 / 26 s = bars 4 / 6 / 13.
The timeline is the same in both formats; only the framing differs (portrait adds a mid camera
pose for the build scene and wraps the pills, chips and headlines).

## Portrait versus landscape at a glance

| | Portrait (default) | Landscape |
|---|---|---|
| Stage / output | 720 x 1280 / 1080 x 1920 | 1280 x 720 / 1920 x 1080 |
| Caption | top third, 52 px, up to 2 lines | top band, 44 px, 1 line |
| Camera | wide, mid, close, wide | wide, close, wide |
| Pills / chips | wrap to two rows | one row |
| Callout tags | 26 px, short wording | 16 px |
| Keep clear | top 165, bottom 255, left 40, right 80 stage px (Shorts interface) | nothing |
| Goes to | YouTube Shorts | regular YouTube, the site, slides |

## Files in this skill

| File | Purpose |
|---|---|
| `scripts/build_video.sh` | recipe folder in, MP4s in `~/Movies` out; one soundtrack, one pass per format; runs all the checks |
| `scripts/render_frames.py` | seeks the page's CSS animations and screenshots frames (Playwright); `--format` picks the layout |
| `scripts/make_soundtrack.py` | `video.json` in, WAV out; numpy chiptune synth with sync accents |
| `scripts/contact_sheet.sh` | tiles test frames into one image, either orientation; `--safe` overlays the Shorts safe box |
| `scripts/check_no_media_in_repo.sh` | fails if rendered media sits inside the repo |
| `assets/examples/` | the finished Knob Clock Kit animation (both layouts) and spec: the house style to copy |
| `assets/build.sh`, `assets/media-gitignore.txt` | recipe boilerplate |
| `assets/recipe-README-template.md`, `assets/recipe-PORTRAIT-template.md`, `assets/recipe-LANDSCAPE-template.md` | the per-kit README and the per-format instructions |
| `references/storyboard-guide.md` | what to pull from the kit docs; scenes, captions, event lists |
| `references/animation-guide.md` | the two layouts, tokens, camera poses, safe zone, keyframe math, idioms, pitfalls |
| `references/soundtrack-guide.md` | `music` block fields, tempo grid, accents, loudness targets |

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| YouTube shows the upload as a normal video, not a Short | the file is not vertical: upload `{NAME}.mp4` (portrait), not `-landscape`; `ffprobe` should say 1080x1920 |
| Portrait render looks like a cropped landscape page, "page is larger than the portrait frame" | `animation.html` has no portrait block: add the layout tokens and the PORTRAIT block (animation guide, "Two formats") |
| Portrait caption or tag sits under the Shorts interface | it is outside the safe box: move it and re-check with `contact_sheet.sh --safe` |
| A callout cannot be moved in portrait | its position is an inline `style`: move it to a class |
| Build stops after the first format | a command inside the format loop is reading stdin: give it `-nostdin` / `< /dev/null` |
| Every frame identical, "no CSS animations" warning | page animates with JS timers; convert to CSS keyframes |
| Text in the wrong font | Google Fonts blocked or the family name is misspelled in the page |
| Elements visible on the second loop but not the first | a positive `animation-delay` shifted the reset; see the stagger idiom in the animation guide |
| Hard cut shows a flicker frame | adjacent keyframes closer than 0.02 s share a percentage; separate them |
| Build says REFUSING | the output or work directory is inside a git repo; use `~/Movies` and a temp dir |
| Music too loud or quiet | adjust `music.peak` (0.7 to 0.85) and `limiter_drive` |
| Two renders of one frame differ by a few pixels | parallel workers composite slightly differently; compare with `--workers 1` |
