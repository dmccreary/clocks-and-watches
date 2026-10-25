# {TITLE}: landscape video

| | |
|---|---|
| Frame | **1920 x 1080**, 16:9 horizontal |
| Length | 30 s, 30 fps, H.264 video + AAC audio |
| Made for | regular YouTube videos, the book web site, slide decks, LinkedIn, email |
| File | `~/Movies/{NAME}-landscape.mp4` (with sound), `~/Movies/{NAME}-landscape-silent.mp4` (picture only) |
| Source | `animation.html` rendered with `data-format="landscape"` (a 1280 x 720 stage at x1.5) |

This is the secondary version. **It cannot be a YouTube Short**: Shorts must be vertical. For
Shorts use the portrait version, described in [PORTRAIT.md](PORTRAIT.md). The story, timing
and soundtrack are identical in both.

## 1. Build

```bash
media/kits/{SLUG}/build.sh --format landscape --preview   # about a minute: 640x360, 10 fps, proves the pipeline
media/kits/{SLUG}/build.sh --format landscape             # full quality, a few minutes (900 frames)
```

Plain `build.sh` builds both versions. Read the lines the build prints:

| Check | Pass |
|---|---|
| Frame | `1920x1080` |
| Duration | 30.0 s (+/- 0.1) |
| Integrated loudness | -16 to -12 LUFS |
| True peak | at or below -0.3 dBFS |
| Repo hygiene | `OK: no rendered media inside <repo>` |

## 2. Layout

| Band (stage px, 1280 x 720) | y | Content |
|---|---|---|
| Caption | 30-104 | kicker 15 px caps + headline 44 px bold on one line, left at x = 64 |
| Stage | 110-640 | the hardware and the screen, moved by the camera |
| Pills / chips | 650-694 | mode pills (12-26 s) swap for lab chips (26-30 s) |
| Progress | 704-708 | thin bar over 30 s with scene ticks |

Camera: wide shot, push in to the screen at 8-9.2 s, hold, pull back at 26-27.4 s.
There is no platform interface over a landscape video, so the whole frame is usable.

## 3. Notes for this kit

{KIT_NOTES}

## 4. Before you upload or embed

- [ ] The build printed `1920x1080` and 30.0 s.
- [ ] You picked `{NAME}-landscape.mp4` (with sound), not `-silent`, and not the portrait file.
- [ ] You opened it and it looks right. You, not Claude, have to listen to the soundtrack.

## 5. Use it

**As a regular YouTube video.** In YouTube Studio choose **Create > Upload videos**, pick
`~/Movies/{NAME}-landscape.mp4`, write a title and a description that links to the kit page,
answer the **Made for kids** question (required; your choice), and Save. A custom thumbnail
helps a regular video. Make a still from the same renderer, outside the repo:

```bash
T=$(mktemp -d)
python3 -I skills/video-of-kit-generator/scripts/render_frames.py media/kits/{SLUG}/animation.html \
  --out $T --format landscape --scale 1.5 --times 14
open $T/t_14.00.png      # a 1920 x 1080 still of the kit mid-demo; upload it as the thumbnail
```

**On the book's site.** Upload to YouTube first and embed by URL. Never copy the MP4 into
`docs/`.

```html
<iframe src="https://www.youtube.com/embed/VIDEO_ID" title="{TITLE} in 30 seconds"
        style="aspect-ratio:16/9;width:100%;border:0" allowfullscreen></iframe>
```

**In slides or email.** Use the file from `~/Movies` directly. If a deck cannot play audio,
use `{NAME}-landscape-silent.mp4`.

## 6. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| YouTube will not make it a Short | landscape cannot be a Short; upload `{NAME}.mp4` (portrait) for that |
| Frame is not 1920x1080 | `formats.landscape` in `video.json` was changed; width 1280, height 720, scale 1.5 give 1920x1080 |
| Music too loud or quiet | adjust `music.peak` (0.7 to 0.85) and `limiter_drive` in `video.json` |
| Text in the wrong font | Google Fonts was unreachable while rendering; check the network and rebuild |
