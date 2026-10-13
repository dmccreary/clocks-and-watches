# Knob Clock Kit: 30-second video recipe

This folder holds **only the steps** to build the kit's 30-second video. The finished videos
are large and are **never stored in this repo**; they are written to `~/Movies`.

| File | What it is |
|---|---|
| `video.json` | the spec: size, fps, storyboard, and the soundtrack (`music`) |
| `animation.html` | the picture: one self-contained CSS-animation page, 30 s loop |
| `build.sh` | one-command rebuild |
| `README.md` | this file |

## Rebuild

```bash
media/kits/rect-tft-display/build.sh --preview   # about 30 s: half size, 10 fps, proves the pipeline
media/kits/rect-tft-display/build.sh             # full quality: 1920x1080, 30 fps, a few minutes
```

Output (outside the repo):

- `~/Movies/rect-tft-display-30s.mp4`: with the soundtrack
- `~/Movies/rect-tft-display-30s-silent.mp4`: picture only

## Needs

- `ffmpeg` and `ffprobe` (`brew install ffmpeg`)
- `python3` with `playwright` and `numpy` (`pip install playwright numpy && playwright install chromium`)
- a network connection for Google Fonts while rendering

## How it works

1. `render_frames.py` opens `animation.html` in headless Chromium, seeks every CSS animation
   to each frame time and saves PNGs to a temp directory.
2. `ffmpeg` encodes them to a silent H.264 MP4.
3. `make_soundtrack.py` synthesizes the chiptune track and the sound accents from `video.json`.
4. `ffmpeg` muxes picture and sound, and the MP4 is copied to `~/Movies`.
5. `check_no_media_in_repo.sh` confirms no rendered media is inside the repo.

The engine lives in `skills/video-of-kit-generator/`. To change the video, edit
`animation.html` (picture) or `video.json` (sound and timing), then rebuild.
Keep animation event times and `music.accents` times in step.

## Storyboard

| Time | Scene | Caption |
|---|---|---|
| 0-3 s | Meet the kit | Meet the Knob Clock Kit |
| 3-8 s | Wire it | 12 wires join the Pico to the screen |
| 8-12 s | Power on, set time | It sets its own time over WiFi |
| 12-26 s | Five faces | Turn the knob to change the face |
| 26-30 s | 17 labs | Build it. Code it. Make time tick. |
