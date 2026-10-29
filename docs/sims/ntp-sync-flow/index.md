---
title: NTP Sync Flow
description: A Mermaid flowchart of a Pico W time sync, from reading secrets.py to waiting for the next sync, with clickable steps that show their MicroPython code and toggles that light up the WiFi and NTP retry paths.
image: /sims/ntp-sync-flow/ntp-sync-flow.png
og:image: /sims/ntp-sync-flow/ntp-sync-flow.png
twitter:image: /sims/ntp-sync-flow/ntp-sync-flow.png
social:
   cards: false
quality_score: 100
---

# NTP Sync Flow

<iframe src="main.html" height="692px" width="100%" scrolling="no"></iframe>

[Run the NTP Sync Flow MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

A WiFi clock repeats the same routine for as long as it runs: connect, ask an NTP server for the time, convert it to local time, show it, wait, and do it again. Real networks fail sometimes, so a good clock also plans for two kinds of trouble:

- **WiFi fails**: the router is busy, the signal is weak, or the password is wrong. The Pico gives up after a timeout and retries a few times.
- **NTP fails**: WiFi works, but the server does not answer, and `ntptime.settime()` raises an `OSError`. The Pico catches the error and retries.

If the retries run out, the clock does not crash. It **keeps running on its last known time**, because its internal RTC keeps counting, and it tries again at the next scheduled sync. The green path in the flowchart is the normal route; the orange paths are the retries and the fallback.

The code for each step comes from the `main-w.py` program in Chapter 14.

## How to Use

1. Read the flowchart from **Start** at the top. The green path shows what happens when everything works.
2. **Click** (or hover over) any box to see the MicroPython code for that step in the panel on the right.
3. Press **WiFi fails** to light up the WiFi retry path in orange. Notice that the NTP steps are never reached.
4. Press **NTP fails** to light up the NTP retry path instead. Press the active button again to return to the normal path.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/ntp-sync-flow/main.html"
        height="692px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objective

Students will sequence the steps of a time sync and identify what to do at each failure point (Bloom: Understanding, Applying).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- WiFi connection, `secrets.py`, and `ntptime` (Chapter 14)
- `try` and `except` (Chapter 4)

### Activities

1. **Sequence** (4 min): Before opening the MicroSim, give students the step names on cards and have them put the steps in order. Then compare with the flowchart.
2. **Match code to steps** (4 min): Students click each box and point to the matching lines in the chapter's `main-w.py` program.
3. **Failure drill** (4 min): For each toggle, students describe in one sentence what the user of the clock would see on the display while the failure happens.
4. **Extend** (3 min): Where would you add a step that writes the synced time back to a DS3231 (Chapter 13)? Sketch the new box and its arrows.

### Assessment

- Put these steps in order: apply time zone offset, connect to WiFi, `ntptime.settime()`, read `secrets.py`.
- What exception does `ntptime.settime()` raise when the server does not answer, and how should the program handle it? (`OSError`; catch it, wait, and retry a few times.)
- Explain why "keep running on last known time" is a better fallback than stopping the program.

## References

1. [Network Time Protocol](https://en.wikipedia.org/wiki/Network_Time_Protocol) - Wikipedia overview of NTP.
2. [Connecting to the Internet with Raspberry Pi Pico W](https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf) - Raspberry Pi guide to WiFi on the Pico W.
3. [MicroPython network module](https://docs.micropython.org/en/latest/library/network.html) - Documentation for `network.WLAN`.
4. [Mermaid flowchart syntax](https://mermaid.js.org/syntax/flowchart.html) - The diagram language used by this MicroSim, including `click` callbacks.
