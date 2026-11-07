# Knob Clock Kit: 30-second video recipe

This folder holds **only the steps** to build the kit's 30-second videos. The finished videos
are large and are **never stored in this repo**; they are written to `~/Movies`.

One build makes **two versions** of the same video, with the same picture story and the same
soundtrack:

| Version | Frame | Use it for | File in `~/Movies` | Instructions |
|---|---|---|---|---|
| **Portrait** (default) | 1080 x 1920, 9:16 | YouTube Shorts and other vertical feeds | `rect-tft-display-30s.mp4` | [PORTRAIT.md](PORTRAIT.md) |
| Landscape | 1920 x 1080, 16:9 | regular YouTube video, the web site, slides | `rect-tft-display-30s-landscape.mp4` | [LANDSCAPE.md](LANDSCAPE.md) |

YouTube only treats a short video as a Short when the frame is vertical (or square); a
horizontal 30-second video is just a regular video. Upload the portrait file for Shorts and the
landscape file everywhere else.

| File | What it is |
|---|---|
| `video.json` | the spec: formats, fps, storyboard, and the soundtrack (`music`) |
| `animation.html` | the picture: one self-contained CSS-animation page with both layouts, 30 s loop |
| `build.sh` | one-command rebuild |
| `README.md` | this file |
| `PORTRAIT.md` | build, layout and upload instructions for the portrait version |
| `LANDSCAPE.md` | build, layout and upload instructions for the landscape version |

## Rebuild

```bash
media/kits/rect-tft-display/build.sh --preview                    # about a minute: both formats, half size, 10 fps
media/kits/rect-tft-display/build.sh                              # full quality, both formats, a few minutes each
media/kits/rect-tft-display/build.sh --format portrait            # only the portrait video
media/kits/rect-tft-display/build.sh --format landscape           # only the landscape video
```

Output (outside the repo):

- `~/Movies/rect-tft-display-30s.mp4`: portrait, with the soundtrack (this is the one for YouTube Shorts)
- `~/Movies/rect-tft-display-30s-silent.mp4`: portrait, picture only
- `~/Movies/rect-tft-display-30s-landscape.mp4`: landscape, with the soundtrack
- `~/Movies/rect-tft-display-30s-landscape-silent.mp4`: landscape, picture only

## Needs

- `ffmpeg` and `ffprobe` (`brew install ffmpeg`)
- `python3` with `playwright` and `numpy` (`pip install playwright numpy && playwright install chromium`)
- a network connection for Google Fonts while rendering

## How it works

1. `make_soundtrack.py` synthesizes the chiptune track and the sound accents from `video.json`
   once; both versions use it.
2. For each format in `video.json` `formats`, `render_frames.py` opens `animation.html` in
   headless Chromium with `<html data-format="portrait|landscape">`, seeks every CSS animation
   to each frame time and saves PNGs to a temp directory.
3. `ffmpeg` encodes the frames to a silent H.264 MP4, then muxes the soundtrack.
4. The MP4s are copied to `~/Movies`, and `check_no_media_in_repo.sh` confirms no rendered
   media is inside the repo.

The engine lives in `skills/video-of-kit-generator/`. To change the videos, edit
`animation.html` (picture, both layouts) or `video.json` (sound and timing), then rebuild.
Keep animation event times and `music.accents` times in step.

## Storyboard

| Time | Scene | Caption |
|---|---|---|
| 0-3 s | Meet the kit | Meet the Knob Clock Kit |
| 3-8 s | Wire it | 12 wires join the Pico to the screen |
| 8-12 s | Power on, set time | It sets its own time over WiFi |
| 12-26 s | Five faces | Turn the knob to change the face |
| 26-30 s | 17 labs | Build it. Code it. Make time tick. |
