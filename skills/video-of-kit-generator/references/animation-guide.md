# Animation guide

The picture is one self-contained HTML page, `media/kits/{SLUG}/animation.html`, that plays a
30-second loop using **CSS animations only**. The renderer does not run the page in real
time. It sets `animation.currentTime` on every animation and screenshots, so the result is
exact on any machine.

**Start from `assets/examples/knob-clock-animation.html`.** It is a complete, working page in
the house style. Replace the hardware drawing, the screen faces, the captions and the times.

## Contract with the renderer

- Root element 1280 x 720 px (`width`/`height` in `video.json`), `position: relative`, with an
  opaque background.
- Every animation: `animation: NAME 30s linear infinite both` (or an easing; 30 s duration, infinite,
  `both`). Short repeating effects (a 1 s WiFi pulse) are fine; they are seeked too.
- **No JavaScript timers** (`setInterval`, `setTimeout`, `requestAnimationFrame`). They are not
  captured. No `<video>`/`<audio>`.
- Fonts: a Google Fonts `<link>`; the renderer waits for the fonts it finds in use.
- Anything with class `no-video` (and `.pause-btn`, `.pause-input`) is hidden in the render.
  Keep a pause checkbox in the page for people who open it in a browser.
- Relative assets (images) resolve from the recipe folder. Keep them small and in the recipe;
  prefer inline SVG/CSS over images.

## Layout grid (1280 x 720)

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

**Camera.** One wrapper (`.rig`, `transform-origin: 0 0`) with `transform: translate(tx,ty) scale(s)`.
To put rig point (px, py) at stage point (cx, cy): `tx = cx - s*px`, `ty = cy - s*py`.
Wide view s = 0.85 for build scenes, close view s = 1.15 for the screen. Keep the
same transform function list in every keyframe so it interpolates; use `ease-in-out`.

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
4. Camera, captions, pills/chips, progress, cover.
5. Render contact sheets at the scene mid-points (SKILL.md step 5) and fix.

## Pitfalls seen in practice

| Pitfall | Fix |
|---|---|
| Two `transform` animations on one element | nested wrappers |
| Text slightly too wide in the fallback font | keep headlines at most 40 characters and check the contact sheet |
| `position: fixed` inside the stage | use `absolute`; the root is the viewport |
| Heavy blur / large box-shadow on many layers slows the render | fine for 900 frames, but keep it to the hero parts |
| Mode names / values differ between pills, screens and captions | take them all from the storyboard |
