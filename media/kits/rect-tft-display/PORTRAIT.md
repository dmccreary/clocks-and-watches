# Knob Clock Kit: portrait video (the default)

| | |
|---|---|
| Frame | **1080 x 1920**, 9:16 vertical |
| Length | 30 s, 30 fps, H.264 video + AAC audio |
| Made for | YouTube Shorts and other vertical feeds (phones, stories) |
| File | `~/Movies/rect-tft-display-30s.mp4` (with sound), `~/Movies/rect-tft-display-30s-silent.mp4` (picture only) |
| Source | `animation.html` rendered with `data-format="portrait"` (a 720 x 1280 stage at x1.5) |

This is the default version. Use it whenever a video must be vertical. The landscape twin is
described in [LANDSCAPE.md](LANDSCAPE.md); the story, timing and soundtrack are identical.

## 1. Build

```bash
media/kits/rect-tft-display/build.sh --format portrait --preview   # about a minute: 360x640, 10 fps, proves the pipeline
media/kits/rect-tft-display/build.sh --format portrait             # full quality, a few minutes (900 frames)
```

Plain `build.sh` builds both versions. The build prints the frame size, duration and loudness,
and ends with `OK: no rendered media inside <repo>`. Read those lines:

| Check | Pass |
|---|---|
| Frame | `1080x1920` |
| Duration | 30.0 s (+/- 0.1) |
| Integrated loudness | -16 to -12 LUFS |
| True peak | at or below -0.3 dBFS |

## 2. What the portrait layout does differently

The portrait video is **not** the landscape video cropped. The same page re-lays itself out
for a tall frame; the animation timeline is unchanged.

| Part | Portrait | Landscape |
|---|---|---|
| Caption | top third, left aligned, headline 52 px on up to two lines | top band, 44 px on one line |
| Camera | wide shot (whole kit), then a **mid shot** while wiring, then a close shot of the screen, then wide again | wide, then close on the screen, then wide |
| Callout tags | larger type (26 px), shorter wording where needed | 16 px |
| Mode pills | wrap to two rows | one row |
| Lab chips | wrap to two rows | one row |
| Progress bar | inside the safe box, above the bottom margin | bottom edge |

### Safe zone

Shorts draws its own interface over the picture: the status bar and header at the top, the
title / channel / subscribe at the bottom (roughly the bottom 20 %), and like / comment / share
down the right edge (roughly the right 12 %). YouTube does not publish an exact organic safe
zone and third-party figures disagree, so this recipe uses a conservative box:

| Edge | Keep clear | At 1080 x 1920 |
|---|---|---|
| Top | 165 stage px | 248 px |
| Bottom | 255 stage px | 382 px |
| Left | 40 stage px | 60 px |
| Right | 80 stage px | 120 px |

Captions, callout tags, the controls and the screen must sit inside the box. Check it:

```bash
T=$(mktemp -d)
python3 -I skills/video-of-kit-generator/scripts/render_frames.py media/kits/rect-tft-display/animation.html \
  --out $T --format portrait --scale 1 --times 1.5,5,9.5,14,20,25,28,29
skills/video-of-kit-generator/scripts/contact_sheet.sh $T $T/sheet.png 4 --safe
```

Open `$T/sheet.png`. The yellow box is the safe zone. Nothing important may cross it.

## 3. Notes for this kit

### Camera path

| Time | Pose | What the viewer sees |
|---|---|---|
| 0-3 s | wide (scale 0.52) | the whole kit: breadboard and Pico on the left, display board on the right; tags "Pico 2 W · the brain" and "Display board" |
| 3-8 s | mid (scale 0.85), moving in at 3-4 s | the Pico and the 12 wires landing on the board's pin header; amber tag "VCC to 3V3 · never 5 V" |
| 8-26 s | close (scale 0.8), moving in at 8-9.2 s | the display board fills the width; five faces in turn; tags "Turn: next face", "Push: lap", "K0: start / stop" |
| 26-30 s | wide, moving out at 26-27.4 s | the whole kit again; the 17 lab chips count up under it |

The close pose is placed so the knob (the control the video is about) ends at about x = 643 on
the 720 px stage, right at the edge of the margin that Shorts covers with its buttons. Do not
push the close pose further right.

### Captions as they wrap in the 580 px column

| Scene | Kicker (one line) | Headline (two lines) |
|---|---|---|
| Meet the kit | A desk clock you build and code yourself | Meet the Knob / Clock Kit |
| Wire it | Step 1 · Wire it | 12 wires join the / Pico to the screen |
| Power on | Step 2 · Power it on | It sets its own / time over WiFi |
| Use it | Step 3 · Use it | Turn the knob to / change the face |
| Finale | 17 labs · ages 10 and up | Build it. Code it. / Make time tick. |

### Pills, chips and tags

- Mode pills wrap 3 + 2: Weather, Analog, Digital / Stopwatch, Timer.
- Lab chips wrap 9 + 8: 01-09 / 10-17.
- The display-board tag reads **Display board** in portrait and **Display board · screen +
  knob + K0** in landscape (the tail is a `class="l-only"` span).
- Portrait tags are 26 px (16 px in landscape) and are re-placed in the `PORTRAIT` block of
  `animation.html`: `.tag-pico`, `.tag-board`, `.tag-vcc`, `.tag-turn`, `.tag-push`, `.tag-k0`.

### Changing this kit's portrait layout

Edit only the `PORTRAIT` block at the end of the stylesheet in `animation.html` (the
`:root[data-format=portrait]` rules). Do not touch the keyframes for a portrait-only tweak:
they are shared with landscape and the soundtrack depends on their timing.

## 4. Before you upload

- [ ] `ffprobe` says 1080x1920 and 30.0 s (the build printed it).
- [ ] You are about to upload `rect-tft-display-30s.mp4`, not `-silent` and not `-landscape`.
- [ ] Open the file in QuickTime. The caption is readable, nothing sits in the yellow margins,
      and the last second fades out cleanly. (You, not Claude, have to listen: the soundtrack is
      synthesized and cannot be checked by ear from the build.)

## 5. Upload to YouTube as a Short

1. Open YouTube Studio (studio.youtube.com) and choose **Create > Upload videos**.
2. Pick `~/Movies/rect-tft-display-30s.mp4`.
3. Title: lead with the kit name, then what it does. Description: link to the kit page in the
   book. Adding `#Shorts` to the title or description is common practice; it is not required, a
   vertical video of up to three minutes is treated as a Short.
4. Answer the **Made for kids** question. YouTube requires it on every upload and the choice is
   yours (it changes comments and personalization).
5. Choose visibility and **Save**. When processing finishes, the video appears under
   **Content > Shorts** in Studio and its address has the form `youtube.com/shorts/ID`.

To show it on the site, upload it to YouTube and embed by URL. Never copy the MP4 into `docs/`.
A vertical video needs a vertical frame or YouTube pillarboxes it:

```html
<iframe src="https://www.youtube.com/embed/VIDEO_ID" title="Knob Clock Kit in 30 seconds"
        style="aspect-ratio:9/16;width:min(100%,360px);border:0" allowfullscreen></iframe>
```

## 6. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| YouTube shows it as a normal video, not a Short | the frame is not vertical: `ffprobe` the file you uploaded; it must be `rect-tft-display-30s.mp4` |
| Build warns "page is ... larger than the portrait frame" | `animation.html` has no portrait layout; add the PORTRAIT block (see `references/animation-guide.md`) |
| Caption or a tag hidden under the Shorts interface | it is outside the safe box; move it and recheck with `contact_sheet.sh --safe` |
| A tag is unreadable on a phone | raise `--tag-fs` in the portrait token block and re-place the tag |
| Headline leaves one word on its own line | shorten it or keep `text-wrap: balance` on `.head` |
| An old landscape file sits under the same name in `~/Movies` | before this recipe had two versions, `rect-tft-display-30s.mp4` was landscape; rebuild to replace it |
