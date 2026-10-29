---
title: Mondaine Swiss Railway Clock
description: Explore a Swiss railway watch face and its sweep, hold, and minute-step sequence.
image: /sims/mondaine-railway-clock/mondaine-railway-clock.png
social:
  cards: false
---
# Mondaine Swiss Railway Clock

<iframe src="main.html" width="100%" height="582" scrolling="no" title="Interactive Swiss railway clock"></iframe>

[Run the clock fullscreen](./main.html){ .md-button .md-button--primary }

## About

Press **Start** to watch the red hand sweep. It completes one circuit in 58 simulated seconds, holds at twelve for two seconds, and then resumes. At 59 seconds into each cycle, the minute hand advances 6° and the hour hand advances 0.5° together. Both black hands remain still between steps. The exact step instant within the hold is a modeling choice.

Use **Replay pause** to return to 55 seconds in the current cycle without changing the playback state. **Speed** changes playback from real-time 1× to 10×; it preserves the 58:2 timing ratio. The clock starts paused at 10:10 and uses demonstration time rather than your computer's clock.

## Dial construction and historical scope

The face is a study of the SBB/Moser-Baer design associated with the **1952 “Normblatt für Zifferblätter”**, catalogued by the Museum für Gestaltung. It has a white ground, 60 rectangular marks, twelve heavier hour marks, tapered black hands, and the red signal-paddle second hand.

The original drawing could not be inspected directly during this implementation. The proportions below follow the normalized construction already present in this repository's Mondaine hardware kit; they are an approximation, not a verified dimensional transcription of the 1952 sheet. No modern brand logo is added.

One design unit, *a*, equals one hundredth of the dial diameter. Major marks extend from radius 36.5a to 48.5a and are 3.5a wide; minor marks extend from 45a to 48.5a and are 1.4a wide. The hour and minute hands reach 32a and 46a. The red disc has radius 5.25a and its center is 31.25a from the pivot.

Dial geometry and movement timing are separate choices. This model uses Mondaine's documented **58-second / 2-second stop2go** timing. The museum describes a roughly 1.5-second station-clock hold; this simulation does not claim that every historical railway movement used identical timing.

## Lesson Plan

**Audience:** high school beginners. **Time:** 5–10 minutes. **Prerequisite:** reading an analog clock.

**Learning objective (Bloom: Analyze):** Analyze the sequence of sweep, hold, and coupled minute/hour advance by changing playback speed and replaying the end of a minute.

1. Start at 1× and observe whether the red hand ticks or glides.
2. Choose **Replay pause**. Track the black hands as the red hand stops at twelve.
3. Pause playback and predict how far each black hand moves during the next hold.
4. Repeat at 5×. Explain why increasing playback speed leaves the order of events unchanged.

**Check your reasoning:** A complete cycle must still take 60 simulated seconds. How does a 58-second sweep leave room for a two-second hold? Why does the hour hand move only half a degree when the minute hand moves six degrees?

## Embed this MicroSim

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/mondaine-railway-clock/main.html"
        width="100%" height="582" scrolling="no"
        title="Interactive Swiss railway clock"></iframe>
```

## References

- [Museum für Gestaltung: SBB Bahnhofsuhr, including the 1952 technical drawing](https://www.eguide.ch/en/objekt/sbb-bahnhofsuhr/?pdf=2261). Historical design attribution and archive description.
- [Mondaine: What makes the stop2go watch so unique?](https://eu.mondaine.com/blogs/news/was-macht-mondaines-stop2go-uhr-so-einzigartig). Manufacturer description of the 58-second circuit and two-second hold.
- [SBB: Two seconds of standstill](https://commerce.sbb.ch/en/content/mondaine_wanduhr_stop2go). Explanation of the pause and minute advance.
