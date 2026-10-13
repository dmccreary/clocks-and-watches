# Soundtrack guide

`scripts/make_soundtrack.py video.json out.wav` synthesizes an original upbeat chiptune track
with numpy: no samples, no licensing questions. The same `video.json` (`music` block) always
produces the same bytes (seeded).

## Sound design in one paragraph

120 BPM, C major, I-V-vi-IV (C G Am F), one chord per bar, last bar resolves to C. Layers
come in section by section so the music follows the story: arpeggio (always), hi-hats and bass
(build), kick (power on), snare and lead melody (use), then a final chord stab and fade.
Short **accents** (bells, clicks, boops) are placed at the exact seconds of on-screen events.

## Tempo grid

A bar is `240 / bpm` seconds. Choose a BPM whose bar divides your scene boundaries:

| BPM | Bar | Bars in 30 s | Feel |
|---|---|---|---|
| 96 | 2.5 s | 12 | relaxed |
| 120 | 2.0 s | 15 | upbeat (default); 3, 8, 12, 26 s are on beats |
| 128 | 1.875 s | 16 | energetic |
| 160 | 1.5 s | 20 | fast |

## The `music` block

| Field | Default | Meaning |
|---|---|---|
| `seed` | 7 | noise seed (drums, clicks); keep for reproducible output |
| `bpm` | 120 | tempo |
| `transpose` | 0 | semitones; applies to all pitched layers and midi accents |
| `progression` | `["C","G","Am","F"]` | chord per bar, cycling; library: C, G, Am, F, Dm, Em |
| `final_chord`, `final_at` | `"C"`, duration - 1 | last bar's chord; time after which layers stop (stab lands here) |
| `fade_in`, `fade_out` | 1.2, 1.1 | seconds; match the picture's cover fades |
| `limiter_drive`, `peak` | 1.6, 0.78 | soft-limiter strength; final peak (0.7-0.85) |
| `layers.arp` | on | `from`, `gain`, `gain_full`, `full_from` (gain steps up at `full_from`) |
| `layers.bass` | on | `from`, `gain` |
| `layers.hats` | on | `from`, `soft_gain`, `full_from` (open hats and backbeat feel from here) |
| `layers.kick` | on | `from`, `gain` (four on the floor) |
| `layers.snare` | on | `from`, `gain` (beats 2 and 4) |
| `layers.lead` | on | `from`, `to`, `gain` (pulse melody with echo) |
| `layers.riser` | off | `from`, `dur`: noise + sweep rising into the power-on |

Omit a layer key to turn it off.

## Accents

All times in seconds. Processed in list order.

| `type` | Fields | Use |
|---|---|---|
| `scale` | `t`, `step`, `preset` (`pentatonic12`, `major17`) or `notes`, `dur`, `gain`, `pan` | something connecting or counting up |
| `bell` | `t`, `midi` or `hz`, `dur`, `gain`, `pan` | a jingle note, a "done" ding, a lap ping |
| `click` | `t`, `pitch`, `gain`, `pan` | a knob detent or switch |
| `boop` | `t`, `f0`, `f1`, `dur`, `gain`, `pan` | a button press |
| `stab` | `t`, `notes`, `bass` | the closing chord (also plays a kick) |

Accents sit under the music. Keep gains at 0.14-0.34; louder accents mask the lead.

## Syncing to the picture

Take every accent time from the storyboard's event list: the same number that sets the
keyframe percentage in `animation.html`. Wire draw `t = 3.2 s + stagger` becomes a bell at the
end of the draw. A knob turn at 14.4 s is a click at 14.4.

## Loudness targets

| Measure | Target |
|---|---|
| Integrated loudness | -16 to -12 LUFS (default track: -13.7) |
| True peak | at or below -0.3 dBFS |

`build_video.sh` prints both and warns. If it is hot, lower `music.peak`; if quiet, raise
`peak` or `limiter_drive`.

## Checks

```bash
python3 -I scripts/make_soundtrack.py video.json "$TMP/track.wav"
ffmpeg -hide_banner -nostats -i "$TMP/track.wav" -af "ebur128=peak=true:framelog=quiet" -f null - 2>&1 | sed -n '/Summary/,$p'
ffmpeg -y -loglevel error -i "$TMP/track.wav" -lavfi "showspectrumpic=s=1400x500:legend=1:scale=log:fscale=log" "$TMP/spec.png"
```

In the spectrogram you should see: arpeggio only until about 3 s, a bass band from the
bass `from`, a noise riser, kicks from the kick `from`, and a fade at the end. A strong
vertical comb below 100 Hz in the intro means a DC offset (pulse waves are zero-mean in this
engine, so it should not appear).

## Extending the engine

- New chord: add an entry to `CHORDS` in `make_soundtrack.py` (`arp` tones, `bass` root,
  `lead` phrase as `(eighth_index, midi, length_in_eighths)`), then use its name in `progression`.
- New accent type: add a branch in the accents loop; keep the list-order processing so existing
  recipes stay byte-identical.
- The Knob Clock Kit's `video.json` reproduces its approved track exactly; run
  `cmp` against a stored WAV after any change to the engine.
