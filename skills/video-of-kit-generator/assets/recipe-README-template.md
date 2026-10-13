# {TITLE}: 30-second video recipe

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
media/kits/{SLUG}/build.sh --preview   # about 30 s: half size, 10 fps, proves the pipeline
media/kits/{SLUG}/build.sh             # full quality: 1920x1080, 30 fps, a few minutes
```

Output (outside the repo):

- `~/Movies/{NAME}.mp4`: with the soundtrack
- `~/Movies/{NAME}-silent.mp4`: picture only

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
