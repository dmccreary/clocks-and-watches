# Animation guide

The picture is one self-contained HTML page, `media/kits/{SLUG}/animation.html`, that plays a
30-second loop using **CSS animations only**. The renderer does not run the page in real
time. It sets `animation.currentTime` on every animation and screenshots, so the result is
exact on any machine.

**One page, two layouts.** The same page renders both videos: the story, the keyframes and the
timing are shared, and a `data-format` attribute on `<html>` switches the layout between
**portrait** (720 x 1280, the default, YouTube Shorts) and **landscape** (1280 x 720). See
"Two formats" below. Never fork the page into two files: the event times would drift apart.

**Start from `assets/examples/knob-clock-animation.html`.** It is a complete, working page in
the house style with both layouts. Replace the hardware drawing, the screen faces, the captions
and the times; keep the token block and the PORTRAIT block and re-tune them.

## Contract with the renderer

- Root element `--W` x `--H` px (landscape 1280 x 720, portrait 720 x 1280; they come from
  `video.json` `formats`), `position: relative`, with an opaque background.
- The renderer writes `<html data-format="portrait|landscape">` before the page loads. Style
  the portrait layout under `:root[data-format=portrait]`; landscape is the base.
- Every animation: `animation: NAME 30s linear infinite both` (or an easing; 30 s duration, infinite,
  `both`). Short repeating effects (a 1 s WiFi pulse) are fine; they are seeked too.
- **No JavaScript timers** (`setInterval`, `setTimeout`, `requestAnimationFrame`). They are not
  captured. No `<video>`/`<audio>`. The one allowed script is the one-time layout switch that
  reads `?format=portrait` so people can preview the vertical layout in a browser.
- Fonts: a Google Fonts `<link>`; the renderer waits for the fonts it finds in use.
- Anything with class `no-video` (and `.pause-btn`, `.pause-input`) is hidden in the render.
  Keep a pause checkbox in the page for people who open it in a browser.
- Relative assets (images) resolve from the recipe folder. Keep them small and in the recipe;
  prefer inline SVG/CSS over images.

## Two formats

| | portrait (default) | landscape |
|---|---|---|
| Stage | 720 x 1280 | 1280 x 720 |
| Output (scale 1.5) | 1080 x 1920, 9:16 | 1920 x 1080, 16:9 |
| Goes to | YouTube Shorts (vertical, up to 3 min) | YouTube, the site, slides |
| File | `{NAME}.mp4` | `{NAME}-landscape.mp4` |

### Layout tokens

Every number that differs between formats is a CSS custom property on `:root`, overridden for
portrait. The keyframes never contain a layout number that differs, so they are shared.

| Token | Controls |
|---|---|
| `--W`, `--H` | stage size |
| `--cap-l`, `--cap-t`, `--cap-w`, `--kick-fs`, `--kick-ls`, `--head-fs`, `--head-mt` | caption block |
| `--band-t` | top of the pills / chips band (also the pause button) |
| `--prog-l`, `--prog-t`, `--prog-w` | progress bar; ticks use `--f` (fraction of 30 s) |
| `--pills-l`, `--pills-w`, `--pill-fs`, `--pill-pad`, `--pill-gap` | mode pills (they wrap) |
| `--chips-l`, `--chips-w`, `--chip-sz`, `--chip-fs`, `--chip-gap` | lab chips (they wrap) |
| `--tag-fs`, `--tag-pad` | callout tags |
| `--cam-wide`, `--cam-mid`, `--cam-close` | camera poses, each `translate() scale()` |

Narrow `--pills-w` / `--chips-w` on purpose so the row wraps evenly (3 + 2 pills, 9 + 8 chips),
rather than leaving one orphan.

### Camera: three poses

`cam` goes wide (meet the kit) -> mid (wire it) -> close (the screen) -> wide (finale).
Landscape sets `--cam-mid` equal to `--cam-wide`, so it only pushes in. Portrait uses all three
because a 1350 px wide rig is only 700 px across at s = 0.52: the build scene needs its own
closer pose to be readable.

To put rig point (px, py) at stage point (cx, cy): `tx = cx - s*px`, `ty = cy - s*py`. Aim each
pose's centre at the middle of the portrait stage band (y 360-880, centre about 620).

### Portrait grid (720 x 1280)

Shorts draws its own UI over the video: the status bar at the top, the title / channel /
subscribe at the bottom (roughly the bottom 20 %) and like / comment / share down the right
(roughly 12 %). YouTube publishes no organic safe zone and third-party figures disagree, so the
box below is a conservative composite. Check the result on a phone.

| Band | y | Content |
|---|---|---|
| Top margin | 0-165 | empty (status bar, Shorts header) |
| Caption | 170-340 | kicker 18 px caps + headline 52 px bold, 1-2 lines, left x = 40, width 580 |
| Stage | 360-880 | the rig, moved by the camera |
| Pills / chips | 905-1000 | pills wrap 3 + 2, chips wrap 9 + 8, centred on x = 340 |
| Progress | 1014 | thin bar, x 40-620 |
| Bottom margin | 1025-1280 | empty (title, channel, subscribe) |

Safe box (stage px): **x 40-640, y 165-1025**. At output scale 1.5 that is x 60-960, y 248-1538.
Keep captions, tags, the knob and the screen inside it. The board's decorative edges may bleed.

### Idioms for the portrait layout

- **Move positions into classes.** An inline `style="left:..;top:.."` cannot be overridden by
  the portrait block. Give every positioned callout a class and set `left/top` in CSS.
- **Shorter text where it does not fit.** `<span class="l-only"> . screen + knob + K0</span>`
  is hidden in portrait (`:root[data-format=portrait] .l-only{display:none}`). Add the mirror
  `.p-only` the same way if portrait needs different wording.
- **Larger type for tags.** Tags live inside the scaled rig. At s = 0.5-0.85 a 16 px tag is
  8-14 px on screen, too small on a phone. Use `--tag-fs` of about 26 px in portrait and
  re-place the tags so they do not collide or leave the safe box.
- **Balance headlines.** `text-wrap: balance` on `.head` stops a one-word second line.
- **Right-edge tags.** The knob and the K0 callouts sit on the right of the board; keep their
  right edge inside x = 640 at the close pose (rig x <= (640 - tx) / s).

## Layout grid (landscape, 1280 x 720)

| Band | y | Content |
|---|---|---|
| Caption | 30-104 | kicker 15 px caps + headline 44 px bold, left at x = 64 |
| Stage | 110-640 | the "rig": parts and screen, moved by the camera |
| Pills / chips | 650-694 | mode pills (12-26 s) swap for lab chips (26-30 s) |
| Progress | 704-708 | thin bar filling over 30 s with scene ticks |
| Pause button | 650-694 at x = 1172 | 44 px target, hidden in the render |

## Seconds to percent

`percent = seconds / 30 * 100`. Anchors: 1 s = 3.333 %, 0.5 s = 1.667 %, 3 s = 10 %,
8 s = 26.667 %, 12 s = 40 %, 26 s = 86.667 %, 29.2 s = 97.333 %.

## Idioms that work

**Hold, then change (a window).** Group identical states:

```css
@keyframes fAnalog {
  0%,47.98% {opacity:0}
  48%,56.65% {opacity:1}
  56.667%,100% {opacity:0}
}
```

A hard cut needs a gap of about 0.02 % (0.006 s) between the last "off" and first "on"
percentages. The same percentage twice is an error.

**Fade in / hold / fade out (captions).** `0%,A% {opacity:0; transform:translateY(10px)}`
`B%,C% {opacity:1; transform:translateY(0)}` `D%,100% {opacity:0; transform:translateY(-8px)}`
with A..D about 0.4 s and 0.3 s apart.

**Loop seam.** A full-stage cover in the background color: opaque 0-0.6 s, fades out by 1.6 s,
fades back in from 29.2 s to 30 s. Everything may reset invisibly under it.

**Camera.** One wrapper (`.rig`, `transform-origin: 0 0`) with `transform: var(--cam-*)`.
Keep the same transform function list in every pose so it interpolates; use `ease-in-out`.
Wide view s = 0.85 for landscape build scenes, close view s = 1.15 for the screen.

**Stagger without a leaking reset.** `animation-delay: Ns` shifts the whole cycle, including
its reset, by N seconds. That reset can become visible in the next loop. Fix: wrap the
staggered group in a parent whose own animation (no delay) is `opacity:0` until just before
the stagger starts and again before the loop ends, so every reset happens under it.
(Wires, lab chips.)

**State colors with variables.** Put `--off` and `--on` on the element and use `var()` inside
the keyframes: one keyframe set per window, reused by dots and pills.

**Counters and strips.** A column of lines inside an `overflow:hidden` window, moved by
`translateY` with `steps(N,end)`. N lines, one per tick. Faithful and cheap.

**Rotation and press on the same part.** Use nested wrappers (outer scale for the press, inner
rotate for the turn); two animations on one element's `transform` overwrite each other.

**Pixel-accurate screens.** Author the screen at its native size (for example 160 x 128) in a
box scaled with `transform: scale(2.75)`, `transform-origin: 0 0`. Use a pixel font (VT323) for
text. Copy colors from the real screenshots.

**Ripples.** One keyframe set with a pulse at every event time: a pre-hold keyframe 0.03 %
before each pulse so the opacity does not ramp up between events.

## Authoring order

1. Static layout of every scene's end state (no animation); get the geometry right.
2. Faces/modes as layers stacked in the same box, `opacity:0`.
3. Add the master keyframes from the event list (percent table).
4. Camera, captions, pills/chips, progress, cover. **Landscape first, then the portrait block.**
5. Render contact sheets at the scene mid-points **for both formats** (SKILL.md step 5) and fix.
6. Overlay the safe box on the portrait sheet (see SKILL.md step 5) and fix anything outside it.

## Pitfalls seen in practice

| Pitfall | Fix |
|---|---|
| Two `transform` animations on one element | nested wrappers |
| Text slightly too wide in the fallback font | keep headlines at most 40 characters and check the contact sheet |
| `position: fixed` inside the stage | use `absolute`; the root is the viewport |
| Heavy blur / large box-shadow on many layers slows the render | fine for 900 frames, but keep it to the hero parts |
| Mode names / values differ between pills, screens and captions | take them all from the storyboard |
| Portrait render looks like a cropped landscape page | the page has no portrait block; `render_frames.py` warns that the page is larger than the frame |
| Portrait tag or caption cannot be moved | its position is an inline `style`; move it to a class |
| Portrait headline leaves one word on the second line | `text-wrap: balance` on `.head`, or shorten the caption |
| Content under the Shorts UI | keep it inside the safe box; verify the overlay sheet |
| Single frames differ slightly between two renders | parallel workers; use `--workers 1` when diffing frames |
