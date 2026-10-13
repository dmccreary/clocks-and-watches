#!/usr/bin/env python3
"""Synthesize the 30 s upbeat chiptune soundtrack for a kit video from video.json.

House style: square/triangle chiptune, 120 BPM by default, I-V-vi-IV in C major, drums
that come in section by section, plus short sound accents synced to the picture
(wires connecting, power-on jingle, knob clicks, button presses, a counting scale).

Everything is synthesized from scratch with numpy, so the track is original and carries
no licensing questions. Output is a 16-bit stereo 44.1 kHz WAV: write it to a temp
directory or ~/Movies, never into the git repo.

usage: make_soundtrack.py VIDEO.json OUT.wav
See references/soundtrack-guide.md for every field of the "music" block.
"""
import json
import sys
import wave

import numpy as np

SR = 44100

# chord library: arpeggio tones, bass root (midi), one-bar lead phrase (eighth_index, midi, length_in_eighths)
CHORDS = {
    "C": {"arp": [60, 64, 67, 72], "bass": 48,
          "lead": [(0, 76, 1), (1, 79, 1), (2, 84, 2), (4, 83, 1), (5, 79, 1), (6, 76, 2)]},
    "G": {"arp": [62, 67, 71, 74], "bass": 43,
          "lead": [(0, 74, 1), (1, 79, 1), (2, 83, 2), (4, 81, 1), (5, 79, 1), (6, 74, 2)]},
    "Am": {"arp": [60, 64, 69, 72], "bass": 45,
           "lead": [(0, 72, 1), (1, 76, 1), (2, 81, 2), (4, 79, 1), (5, 76, 1), (6, 72, 2)]},
    "F": {"arp": [60, 65, 69, 72], "bass": 41,
          "lead": [(0, 72, 1), (1, 77, 1), (2, 81, 2), (4, 79, 1), (5, 77, 1), (6, 76, 1), (7, 74, 1)]},
    "Dm": {"arp": [62, 65, 69, 74], "bass": 50,
           "lead": [(0, 74, 1), (1, 77, 1), (2, 81, 2), (4, 79, 1), (5, 77, 1), (6, 74, 2)]},
    "Em": {"arp": [64, 67, 71, 76], "bass": 52,
           "lead": [(0, 71, 1), (1, 76, 1), (2, 79, 2), (4, 76, 1), (5, 74, 1), (6, 71, 2)]},
}
BASS_PAT = [0, 0, 12, 0, 0, 12, 7, 12]
ARP_PAT = [0, 1, 2, 3, 2, 1, 2, 1] * 2
PRESET_SCALES = {
    "pentatonic12": [60, 62, 64, 67, 69, 72, 74, 76, 79, 81, 84, 86],
    "major17": [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84, 86, 88],
}


def main(cfg_path, out_path):
    cfg = json.load(open(cfg_path))
    music = cfg["music"]
    DUR = float(cfg.get("duration", 30))
    N = int(SR * DUR)
    L = np.zeros(N, np.float32)
    R = np.zeros(N, np.float32)
    rng = np.random.default_rng(music.get("seed", 7))

    bpm = float(music.get("bpm", 120))
    BEAT = 60.0 / bpm
    BAR = 4 * BEAT
    EIGHTH = BEAT / 2
    SIXTEENTH = BEAT / 4
    tr = int(music.get("transpose", 0))
    layers = music.get("layers", {})
    FINAL = float(music.get("final_at", DUR - 1.0))
    progression = music.get("progression", ["C", "G", "Am", "F"])
    final_chord = music.get("final_chord", "C")
    n_bars = int(np.ceil(DUR / BAR))

    # ---------- helpers ----------
    def tt(d):
        return np.arange(int(d * SR)) / SR

    def hz(m):
        return 440.0 * 2 ** ((m + tr - 69) / 12)

    def put(sig, t0, gain=1.0, pan=0.5):
        i = int(round(t0 * SR))
        if i >= N or i + len(sig) <= 0:
            return
        n = min(len(sig), N - i)
        gl = np.cos(pan * np.pi / 2) * gain
        gr = np.sin(pan * np.pi / 2) * gain
        L[i:i + n] += sig[:n] * gl
        R[i:i + n] += sig[:n] * gr

    def env(n, a=0.003, tau=0.1, rel=0.006):
        t = np.arange(n) / SR
        e = np.minimum(1.0, t / a) * np.exp(-t / tau)
        r = int(rel * SR)
        if 0 < r < n:
            e[-r:] *= np.linspace(1, 0, r)
        return e

    def pulse(f, d, duty):
        ph = (f * tt(d)) % 1.0
        return np.where(ph < duty, 1.0, -1.0) - (2 * duty - 1)  # zero-mean: no DC thump

    def tri(f, d):
        ph = (f * tt(d)) % 1.0
        return 4 * np.abs(ph - 0.5) - 1

    def bell(f, d):
        t = tt(d)
        s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t)
             + 0.15 * np.sin(2 * np.pi * 3 * f * t))
        return s * env(len(t), a=0.002, tau=d / 4.0)

    def hp_noise(d):
        x = rng.standard_normal(int(d * SR))
        return np.diff(x, prepend=0.0)

    def kick():
        t = tt(0.22)
        f = 45 + 120 * np.exp(-t / 0.025)
        ph = 2 * np.pi * np.cumsum(f) / SR
        return np.sin(ph) * np.exp(-t / 0.08) * np.minimum(1, t / 0.001)

    def snare():
        t = tt(0.2)
        noise = rng.standard_normal(len(t)) * np.exp(-t / 0.055)
        tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t / 0.04) * 0.5
        return (noise + tone) * 0.6

    def hat(open_=False):
        d = 0.2 if open_ else 0.06
        t = tt(d)
        return hp_noise(d) * np.exp(-t / (0.06 if open_ else 0.015)) * 0.5

    def click(pitch=900.0):
        n = int(0.05 * SR)
        t = np.arange(n) / SR
        s = hp_noise(0.05) * np.exp(-t / 0.004) * 0.7
        s += np.sin(2 * np.pi * pitch * t) * np.exp(-t / 0.012)
        s += np.sin(2 * np.pi * 140 * t) * np.exp(-t / 0.02) * 0.8
        return s

    def boop(f0, f1, d=0.11):
        t = tt(d)
        f = f0 + (f1 - f0) * (t / d)
        ph = 2 * np.pi * np.cumsum(f) / SR
        return np.sin(ph) * env(len(t), a=0.004, tau=0.06)

    kick_s = kick()
    snare_s = snare()

    def chord_of(bar):
        name = final_chord if bar == n_bars - 1 else progression[bar % len(progression)]
        return CHORDS[name]

    # ---------- bar-by-bar music ----------
    a = layers.get("arp")
    b = layers.get("bass")
    h = layers.get("hats")
    k = layers.get("kick")
    s = layers.get("snare")
    ld = layers.get("lead")

    for bar in range(n_bars):
        t_bar = bar * BAR
        ch = chord_of(bar)

        if a is not None:
            gain = a.get("gain", 0.10) if t_bar < a.get("full_from", 8.0) else a.get("gain_full", 0.13)
            dur = max(0.12, SIXTEENTH * 1.28)
            for j in range(16):
                t = t_bar + j * SIXTEENTH
                if t >= FINAL:
                    break
                if t < a.get("from", 0.0):
                    continue
                f = hz(ch["arp"][ARP_PAT[j]])
                sig = pulse(f, dur, 0.125) * env(int(dur * SR), tau=0.07)
                g = gain * (1.25 if j % 4 == 0 else 1.0)
                put(sig, t, g, 0.35)
                put(sig, t + EIGHTH, g * 0.28, 0.68)  # ping-pong echo

        if b is not None and t_bar >= b.get("from", 4.0):
            dur = EIGHTH * 0.96
            for i in range(8):
                t = t_bar + i * EIGHTH
                if t >= FINAL:
                    break
                f = hz(ch["bass"] + BASS_PAT[i])
                sig = (0.7 * tri(f, dur) + 0.3 * pulse(f, dur, 0.5)) * env(int(dur * SR), a=0.003, tau=0.2)
                put(sig, t, b.get("gain", 0.30), 0.5)

        if h is not None:
            for i in range(8):
                t = t_bar + i * EIGHTH
                if t < h.get("from", 3.0) or t >= FINAL:
                    continue
                off = (i % 2 == 1)
                if t >= h.get("full_from", 12.0):
                    put(hat(open_=off), t, 0.16 if off else 0.11, 0.58)
                else:
                    put(hat(False), t, h.get("soft_gain", 0.08), 0.58)

        for beat in range(4):
            t = t_bar + beat * BEAT
            if t >= FINAL:
                continue
            if k is not None and t >= k.get("from", 8.0):
                put(kick_s, t, k.get("gain", 0.85), 0.5)
            if s is not None and t >= s.get("from", 12.0) and beat in (1, 3):
                put(snare_s, t, s.get("gain", 0.45), 0.5)

        if ld is not None and ld.get("from", 12.0) <= t_bar < ld.get("to", 26.0):
            for (idx, m, ln) in ch["lead"]:
                t = t_bar + idx * EIGHTH
                d = ln * EIGHTH
                n = int(d * SR)
                f = hz(m)
                sig = pulse(f, d, 0.25) * env(n, a=0.004, tau=d * 0.9, rel=0.01)
                sig = sig * (0.65 + 0.35 * np.exp(-tt(d) / 0.1))
                put(sig, t, ld.get("gain", 0.17), 0.62)
                put(sig, t + 3 * SIXTEENTH, ld.get("gain", 0.17) * 0.3, 0.30)  # dotted-eighth echo

    # ---------- riser into the power-on ----------
    r = layers.get("riser")
    if r is not None:
        rd = float(r["dur"])
        t = tt(rd)
        ramp = (t / rd) ** 2
        put(hp_noise(rd) * ramp, r["from"], 0.18, 0.5)
        sweep_f = 300 + 1500 * (t / rd) ** 2
        put(np.sin(2 * np.pi * np.cumsum(sweep_f) / SR) * ramp, r["from"], 0.10, 0.5)

    # ---------- accents synced to the picture (processed in list order) ----------
    for ac in music.get("accents", []):
        typ = ac["type"]
        t0 = float(ac["t"])
        pan = ac.get("pan", 0.5)
        if typ == "scale":
            notes = ac.get("notes") or PRESET_SCALES[ac["preset"]]
            for i, m in enumerate(notes):
                put(bell(hz(m), ac.get("dur", 0.2)), t0 + ac["step"] * i, ac.get("gain", 0.15), pan)
        elif typ == "bell":
            f = ac["hz"] if "hz" in ac else hz(ac["midi"])
            put(bell(f, ac.get("dur", 0.3)), t0, ac.get("gain", 0.2), pan)
        elif typ == "click":
            put(click(ac.get("pitch", 900.0)), t0, ac.get("gain", 0.34), ac.get("pan", 0.62))
        elif typ == "boop":
            put(boop(ac.get("f0", 520), ac.get("f1", 820), ac.get("dur", 0.11)), t0,
                ac.get("gain", 0.30), ac.get("pan", 0.4))
        elif typ == "stab":
            d = 1.0
            for m in ac.get("notes", [60, 64, 67, 72, 76]):
                sig = pulse(hz(m), d, 0.25) * env(int(d * SR), a=0.003, tau=0.35, rel=0.02)
                put(sig, t0, 0.11, 0.5)
            put(tri(hz(ac.get("bass", 36)), 1.0) * env(int(1.0 * SR), a=0.003, tau=0.4), t0, 0.45, 0.5)
            put(kick_s, t0, 0.9, 0.5)
        else:
            raise SystemExit(f"unknown accent type: {typ}")

    # ---------- master ----------
    t_all = np.arange(N) / SR
    fade_in = np.clip(t_all / float(music.get("fade_in", 1.2)), 0, 1)
    fade_out = np.clip((DUR - t_all) / float(music.get("fade_out", 1.1)), 0, 1)
    fade = (fade_in * fade_out).astype(np.float32)
    L *= fade
    R *= fade

    drive = float(music.get("limiter_drive", 1.6))
    L = np.tanh(drive * L)  # soft limiter: tames kick peaks, lifts overall level
    R = np.tanh(drive * R)
    peak = max(np.abs(L).max(), np.abs(R).max())
    scale_out = float(music.get("peak", 0.78)) / peak
    L *= scale_out
    R *= scale_out

    pcm = np.empty(N * 2, np.int16)
    pcm[0::2] = np.clip(L * 32767, -32768, 32767).astype(np.int16)
    pcm[1::2] = np.clip(R * 32767, -32768, 32767).astype(np.int16)
    with wave.open(out_path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {out_path}  ({DUR:.0f} s, {bpm:g} BPM, {n_bars} bars)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    main(sys.argv[1], sys.argv[2])
