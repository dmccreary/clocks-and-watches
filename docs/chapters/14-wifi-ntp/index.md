---
title: WiFi, NTP, and Time Accuracy
description: Connecting the Pico W to WiFi, syncing time with NTP, converting UTC to local time, and correcting clock drift.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:44:13
version: 1.10
---

# WiFi, NTP, and Time Accuracy

## Summary

Students manage WiFi credentials in a secrets file, query NTP servers, and convert UTC to local time. They study clock accuracy and drift. After this chapter they can build a clock that sets itself from the internet.

## Concepts Covered

This chapter covers the following 21 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Network Configuration | 11 |
| WiFi Connectivity | 10 |
| Secrets File | 2 |
| WiFi SSID and Password | 1 |
| UTC Time | 21 |
| NTP Protocol | 16 |
| Timezone Conversion | 4 |
| Program Variants | 5 |
| Thonny Time Sync | 1 |
| NTP Client Server | 2 |
| Daylight Saving Time | 2 |
| Ntptime Library | 7 |
| Main RTC Program | 1 |
| NTP Stratum Hierarchy | 1 |
| NTP Time Sync | 6 |
| Main Buttons Program | 1 |
| Time Source Comparison | 1 |
| Main WiFi Program | 1 |
| Time Drift Compensation | 3 |
| Clock Drift | 1 |
| Clock Calibration | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)
- [Chapter 4: Control Flow, Functions, and Modules](../04-control-flow-functions/index.md)
- [Chapter 5: The Pico Platform: Pins, Files, and Firmware](../05-pico-platform/index.md)
- [Chapter 6: Getting the Time in MicroPython](../06-getting-time/index.md)
- [Chapter 7: Buttons, Interrupts, and State Machines](../07-buttons-state-machines/index.md)
- [Chapter 13: Real-Time Clocks and the DS3231](../13-real-time-clocks/index.md)

---

!!! mascot-welcome "A Clock That Sets Itself"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    Imagine plugging in a clock and having it find the exact time from the internet, adjust for your time zone, and even handle daylight saving. That's what this chapter builds with a Pico W and a few lines of code. Let's make time tick!

## Time From the Internet

A real-time clock keeps time well, but someone still has to set it, and it slowly drifts. The internet offers a better answer: servers around the world that broadcast the exact time. A Pico W can connect to WiFi, ask one of those servers, and set itself. This chapter walks through the whole chain: connecting to WiFi, using the Network Time Protocol (NTP), converting to your time zone, handling daylight saving, and choosing between the time sources you now know. The chapter ends with how to organize the different versions of a clock program.

## WiFi Connectivity

**WiFi connectivity** is the ability of the Pico W to join a wireless network. Only the **Pico W** can do this, since the plain Pico has no wireless chip (Chapter 5). The Pico W supports **2.4 GHz** WiFi only. If your network name exists only on the 5 GHz band, the Pico cannot see it.

The `network` module provides the tools. You create a **station interface** (the Pico acts as a client, like a phone), turn it on, and connect with a network name and password:

```python
import network
wlan = network.WLAN(network.STA_IF)   # station (client) mode
wlan.active(True)                     # turn the radio on
wlan.connect(SSID, PASSWORD)          # ask to join the network
print(wlan.isconnected())             # True once joined
```

Joining takes a few seconds, so a good program waits in a loop with a **timeout** so it does not hang forever:

```python
import time
def connect(ssid, password, timeout=15):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > timeout:
            return None                  # gave up
        time.sleep(0.5)
    return wlan
```

### WiFi SSID and Password

The **SSID** (service set identifier) is the name of the network, the label you see in your phone's WiFi list. It is **case-sensitive**, so `HomeWiFi` and `homewifi` are different networks. The **password** must match exactly, including capitals and symbols. Most home networks use WPA2, which requires 8 to 63 characters. Some networks, such as school networks with a sign-in page or enterprise login, will not work directly with a Pico. Ask your teacher for a compatible network or a guest network.

### Secrets File

Your WiFi password should never be written into a program you share or upload to a public repository. The standard solution is a separate file named **`secrets.py`** that holds your credentials and is never shared:

```python
# secrets.py: keep this file private
SSID = "MyHomeNetwork"
PASSWORD = "correct-horse-battery"
```

Your program then imports it:

```python
import secrets
wlan = connect(secrets.SSID, secrets.PASSWORD)
```

!!! mascot-warning "Keep the Password Off the Internet"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    If you commit `secrets.py` to a public Git repository, anyone can read your WiFi password, and bots really do scan for these. Add `secrets.py` to your `.gitignore` file (Chapter 5), and commit a `secrets_example.py` with fake values instead so classmates know what to fill in.

### Network Configuration

Once connected, the Pico receives a **network configuration** from the router, automatically, through a service called **DHCP**. Four values describe it:

| Value | Meaning |
|-------|---------|
| IP address | The Pico's unique address on your network |
| Subnet mask | Which addresses count as "local" |
| Gateway | The router that leads to the internet |
| DNS server | The service that turns names like `pool.ntp.org` into IP addresses |

Print them with `wlan.ifconfig()`, which returns a tuple of these four values in order. If you can see an IP address other than `0.0.0.0`, you are connected. The **DNS** entry matters for this chapter, because NTP servers are reached by name.

```python
print(wlan.ifconfig())    # ('192.168.1.42', '255.255.255.0', '192.168.1.1', '192.168.1.1')
```

## UTC Time

**UTC** (Coordinated Universal Time) is the world's standard reference time. It is the same everywhere on Earth at any instant, and it does **not** change for daylight saving. Every time zone is described as an offset from UTC.

Computers and servers exchange time in UTC so that no one has to guess which time zone a timestamp is in. The Pico follows the same rule when it syncs: the NTP server sends UTC, and **your program** converts it for display. It helps to keep this split in mind: **store and compare time in UTC, and convert to local time only when showing it to a person.**

## NTP Protocol

**NTP** (Network Time Protocol) is the internet standard for distributing accurate time, in use since 1985. It runs over UDP on port 123 and exchanges a small 48-byte message. The server's reply contains a timestamp counted in seconds since **January 1, 1900**, which is a third epoch to add to the two from Chapter 6:

| System | Epoch (time zero) |
|--------|-------------------|
| NTP | January 1, 1900 |
| Unix / internet | January 1, 1970 |
| MicroPython on the Pico | January 1, 2000 |

The library handles the conversion, subtracting 3,155,673,600 seconds (the number of seconds between 1900 and 2000). You will rarely do it yourself, but it explains why raw NTP numbers look strange.

### NTP Client-Server Model

NTP uses a **client-server** model. The Pico is the **client**: it sends a request to a **server** that holds accurate time. The server replies with timestamps, and the client uses them to set its clock. The Pico never gives time to anyone. The simple version used on microcontrollers, SNTP, takes the server's time as truth and is accurate to within a fraction of a second, limited by network delay.

By default the library asks `pool.ntp.org`, a shared name that hands out one of thousands of volunteer servers around the world.

### NTP Stratum Hierarchy

Not every NTP server is equally close to the true time. The **stratum** number says how many steps a server is from a reference clock:

| Stratum | Source |
|---------|--------|
| 0 | Atomic clocks and GPS receivers (the reference) |
| 1 | Servers directly connected to a stratum 0 device |
| 2 | Servers that sync from stratum 1 |
| 3 and up | Servers that sync from the level above |

Each step down adds a little delay and error, but even stratum 2 or 3 servers are accurate to a few milliseconds, far better than a clock needs. The pool servers you will reach are typically stratum 2 or 3.

#### Diagram: NTP Stratum Hierarchy

<details markdown="1">
<summary>NTP Stratum Hierarchy</summary>
Type: interactive diagram
**sim-id:** ntp-stratum-hierarchy<br/>
**Library:** vis-network<br/>
**Status:** Specified

**Learning objective:** Students will *understand* how time flows from atomic clocks down through NTP servers to a Pico (Bloom: Understanding).

**Layout:** A top-down tree. Top: "Atomic clock / GPS (Stratum 0)." Next: two stratum 1 servers. Below: four stratum 2 servers. At the bottom: "Your Pico W (client)."

**Interactions:**

- Clicking any node opens an infobox describing its role and typical accuracy.
- A "Send request" button animates a packet from the Pico up to a chosen server and the reply back down, showing timestamps.
- A slider "Network delay (ms)" changes the displayed error to show how delay limits accuracy.

**Responsive design:** The canvas fills the container width and calls `network.fit()` on resize.

Implementation: vis-network with hierarchical layout and an animated edge.
</details>

## The Ntptime Library

MicroPython includes a small library, **`ntptime`**, that does the whole NTP exchange in one call. The key function is `ntptime.settime()`, which asks the server, gets UTC, and **sets the Pico's internal RTC** to it.

```python
import ntptime
ntptime.settime()             # sets the internal clock to UTC
print(time.localtime())       # now shows UTC, not local time
```

After `settime()`, `localtime()` returns **UTC**, because MicroPython has no idea what your time zone is. You will convert it in the next section. The library can fail with an `OSError` such as `ETIMEDOUT` when the network is slow or the server does not answer, so always wrap it in a `try/except` (Chapter 4) and retry:

```python
def sync_time(retries=3):
    for _ in range(retries):
        try:
            ntptime.settime()
            return True
        except OSError:
            time.sleep(2)
    return False
```

### NTP Time Sync

**NTP time sync** is the complete routine: connect to WiFi, get UTC from the server, set the clock, and remember when you did it. A good clock syncs when it starts and then again on a schedule, such as every few hours, to cancel drift.

Servers are shared by everyone, so be a polite client. Do not sync more than once every several minutes. A clock that syncs once every 6 to 24 hours is more than accurate enough.

!!! mascot-tip "Retry, Then Carry On"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    WiFi and NTP fail sometimes for ordinary reasons. Try a few times, and if it still fails, keep running on the clock's own time and try again later instead of crashing. A clock that keeps ticking is better than one that stops to argue with the router.

#### Diagram: NTP Sync Flow

<details markdown="1">
<summary>NTP Sync Flow</summary>
Type: workflow diagram
**sim-id:** ntp-sync-flow<br/>
**Library:** Mermaid<br/>
**Status:** Specified

**Learning objective:** Students will *sequence* the steps of a time sync and *identify* what to do at each failure point (Bloom: Understanding, Applying).

**Nodes:** Start, read `secrets.py`, connect WiFi (timeout?), `ntptime.settime()` (success?), apply time zone offset and DST, update display, wait N hours, back to connect. Failure branches go to "Retry" and then "Keep running on last known time."

**Interactions:** Every node has a Mermaid `click` directive that shows the code for the step. Two toggle buttons, "WiFi fails" and "NTP fails," light up the retry paths.

**Responsive design:** The diagram scales to container width.

Implementation: Mermaid flowchart with click callbacks.
</details>

## Timezone Conversion

**Timezone conversion** turns UTC into your local time by adding a fixed **offset** in hours. For example, Central Time in the United States is 6 hours behind UTC in winter (offset −6) and 5 behind in summer (offset −5). Because the Pico stores time as a count of seconds, the conversion is one addition, and MicroPython takes care of carrying over into the next or previous day:

```python
import time
OFFSET_HOURS = -6                        # Central Standard Time

utc_secs = time.time()                   # seconds since 2000, in UTC
local_secs = utc_secs + OFFSET_HOURS * 3600
year, month, day, hour, minute, second, wd, yd = time.localtime(local_secs)
```

| Zone | Standard offset | Daylight offset |
|------|-----------------|-----------------|
| US Eastern | −5 | −4 |
| US Central (Minnesota) | −6 | −5 |
| US Mountain | −7 | −6 |
| US Pacific | −8 | −7 |
| UTC | 0 | 0 |
| Central Europe | +1 | +2 |
| India | +5.5 | (none) |

Some zones use half-hour offsets, as India does, so store the offset as a number that can have a fraction (5.5 hours is 19,800 seconds).

**Worked example.** It is 01:30 UTC on the 15th. Central Standard Time is UTC −6, so the local time is 19:30 on the **14th**. Because the calculation is done on seconds, the date rolls back correctly without extra code.

!!! mascot-thinking "UTC Inside, Local Outside"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Keep your clock's internal time in UTC, the same for everyone, and convert to local time only in the last step before drawing digits. Then moving your clock to another time zone, or handling daylight saving, changes one number in one place.

#### Diagram: Timezone Converter

<details markdown="1">
<summary>Timezone Converter</summary>
Type: MicroSim
**sim-id:** timezone-converter<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *apply* offsets to convert UTC to local time, including date rollovers (Bloom: Applying).

**Visual elements:** A world strip map with time-zone bands, and a digital clock for UTC and one for the selected zone.

**Controls:** A UTC time slider (0 to 24 hours plus a date), a zone dropdown with the table above, a "DST on/off" toggle, and a "Predict" mode asking for the local time before revealing it.

**Behavior:** When the conversion crosses midnight, the date changes and the display highlights it.

**Responsive design:** The map and clocks stack vertically below 600 px.

Implementation: p5.js using integer second arithmetic.
</details>

### Daylight Saving Time

**Daylight saving time (DST)** is the practice of moving clocks forward one hour in the warm months. In the United States, DST begins at 2:00 a.m. on the **second Sunday in March** and ends at 2:00 a.m. on the **first Sunday in November**. During DST the offset is one hour larger, so Central Time becomes −5.

The Pico does not know about DST, so your program must. The rule needs the date of "the nth Sunday of a month," which you can find using the weekday from Chapter 6:

```python
from time import mktime, localtime

def is_dst_us(utc_secs, std_offset):
    """True if US daylight saving is in effect at this UTC time."""
    year = localtime(utc_secs)[0]

    def nth_sunday(month, n):
        first = mktime((year, month, 1, 0, 0, 0, 0, 0))
        wd = localtime(first)[6]                  # Monday = 0 ... Sunday = 6
        return 1 + (6 - wd) % 7 + 7 * (n - 1)

    start = mktime((year, 3, nth_sunday(3, 2), 2, 0, 0, 0, 0)) - std_offset * 3600
    end = mktime((year, 11, nth_sunday(11, 1), 2, 0, 0, 0, 0)) - (std_offset + 1) * 3600
    return start <= utc_secs < end
```

The function computes when DST starts and ends in UTC, and checks whether the current time falls between them. In 2026 it starts March 8 and ends November 1. Then the offset is `std_offset + 1` when the function returns `True`. Laws change, so the rules may differ where you live and in other years. Some regions, like Arizona, do not observe DST at all.

## Time Source Comparison

You now have four different ways to give a clock its time. Each one has a different strength.

| Source | Accuracy | Survives power-off? | Needs | Best for |
|--------|----------|---------------------|-------|----------|
| Thonny time sync | About 1 second | No | A computer over USB | Development and testing |
| Internal RTC | About 30 ppm (2.6 s/day) | No | Nothing | Short runs between syncs |
| DS3231 | About 2 ppm (5 s/month) | Yes (battery) | I2C wiring and a coin cell | Clocks with no WiFi |
| NTP over WiFi | Milliseconds | No (re-sync on boot) | Pico W and WiFi | Always-connected clocks |

A robust clock combines them: read the DS3231 at startup so the time is right immediately, then correct it from NTP whenever WiFi is available, and write the corrected time back to the DS3231.

### Thonny Time Sync

When you connect Thonny to a Pico, it sets the Pico's internal clock to your **computer's local time**. That is why `localtime()` looks right while you develop. But this is a development convenience only: unplug the Pico and the time is gone. It also causes a subtle mix-up. Thonny sets **local** time, while `ntptime` sets **UTC**, so a program that works while connected to Thonny can be several hours off when it runs alone. Decide on one convention (UTC in the RTC and convert for display is best) and test the program by unplugging from Thonny.

## Clock Drift

**Clock drift** is the slow error that builds up as a clock runs faster or slower than true time. It comes from tiny frequency errors in the crystal. You measure it by comparing the clock to a reference after a known time:

\[ \text{drift (ppm)} = \frac{\text{error in seconds}}{\text{elapsed seconds}} \times 10^6 \]

**Worked example.** A clock is 3 seconds fast after 10 days (864,000 seconds). Its drift is \( 3 / 864{,}000 \times 10^6 \approx 3.5 \) ppm, about what you would expect from a DS3231 at room temperature.

### Time Drift Compensation

**Time drift compensation** means correcting for drift, either by resetting the clock regularly or by adjusting for its known error. The simplest and most reliable method is periodic resynchronization. How often depends on how much error you can tolerate:

\[ \text{sync interval} = \frac{\text{tolerated error}}{\text{drift rate}} \]

For a Pico crystal at 30 ppm and a tolerance of 1 second, the interval is \( 1 / 0.00003 \approx 33{,}000 \) seconds, or about 9 hours. Syncing once a day gives a worst-case error of about 2.6 seconds, and syncing every 6 hours keeps it below about 0.7 seconds.

### Clock Calibration

**Clock calibration** is measuring a specific clock's drift over a long enough time and then applying a correction for that individual unit. The steps are:

1. Set the clock to a reference (NTP) at a known moment.
2. Let it run for several days without correction.
3. Compare it to the reference and compute the drift in ppm.
4. Apply the correction: for example, the DS3231 has an **aging offset** register (`0x10`) that shifts its frequency in small steps, and software can subtract the measured drift.

Calibration is rarely needed for a clock that syncs over WiFi, but it is the tool of choice for an offline DS3231 clock that must be very accurate.

#### Diagram: Sync Interval Calculator

<details markdown="1">
<summary>Sync Interval Calculator</summary>
Type: chart
**sim-id:** sync-interval-calculator<br/>
**Library:** Chart.js<br/>
**Status:** Specified

**Learning objective:** Students will *calculate* how often a clock must resynchronize for a given accuracy goal (Bloom: Applying, Evaluating).

**Visual elements:** A sawtooth line chart showing error growing between syncs and resetting to zero at each sync, over 3 days.

**Controls:** Sliders for drift (1 to 100 ppm) and sync interval (1 to 48 hours); a readout "Worst-case error: X seconds" and "Sync interval needed for 1 s accuracy." A preset menu selects Pico crystal (30 ppm), DS1307 (20), DS3231 (2).

**Responsive design:** The chart resizes to the container.

Implementation: Chart.js line chart with a generated sawtooth dataset.
</details>

## Program Variants

A **program variant** is a version of the main clock program built for a particular set of hardware or features. Different kits have different parts, so rather than one giant program full of `if` statements, we keep several small variants that share the same modules and drivers. The naming convention makes the choice obvious. You copy exactly one variant to the Pico as `main.py` (Chapter 5) to select it.

| File | Time source | Input | Chapter |
|------|-------------|-------|---------|
| `main-buttons.py` | Internal RTC, set by buttons | Two buttons | 7 |
| `main-rtc.py` | DS3231 battery-backed | Buttons (optional) | 13 |
| `main-w.py` | NTP over WiFi (Pico W) | None needed | 14 |

Variants stay small because they import shared code, such as `config.py`, the display driver, and the time helpers, instead of copying it (Chapter 4). Keep the banner in each variant so you can tell which one is running.

### Main Buttons Program

`main-buttons.py` is the offline variant. It uses the internal RTC and lets the user set the hour and minute with the mode-cycling state machine from Chapter 7. It needs no WiFi and no extra chips, so it works on any Pico, but it forgets the time at power-off.

### Main RTC Program

`main-rtc.py` adds the DS3231. At startup it reads the battery-backed time and copies it into the internal clock with `machine.RTC().datetime(...)` (Chapter 13). If the user sets the time with the buttons, it writes the new value to the DS3231 as well. This variant survives power outages.

### Main WiFi Program

`main-w.py` is the internet variant for the Pico W. It connects, syncs with NTP, applies the timezone and DST rules, and then displays the local time. Here is a complete skeleton that prints the local time in the Shell:

```python
NAME = "main-w.py"
VERSION = "1.0"
print("{} v{}".format(NAME, VERSION))

import network, ntptime, time
import secrets

STD_OFFSET = -6                           # US Central Standard Time

def connect(timeout=15):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > timeout:
            return False
        time.sleep(0.5)
    return True

def sync():
    for _ in range(3):
        try:
            ntptime.settime()             # RTC now holds UTC
            return True
        except OSError:
            time.sleep(2)
    return False

def local_now():
    utc = time.time()
    offset = STD_OFFSET + (1 if is_dst_us(utc, STD_OFFSET) else 0)
    return time.localtime(utc + offset * 3600)

# is_dst_us() is the function from the Daylight Saving Time section

if connect() and sync():
    print("Synced")
else:
    print("Sync failed; using existing time")

while True:
    h, m, s = local_now()[3:6]
    print(f"{h:02d}:{m:02d}:{s:02d}")
    time.sleep(1)
```

Put `is_dst_us()` above `local_now()` in your file, then add your display code in place of `print`.

## Putting It Together

| Step | Tool |
|------|------|
| Join WiFi | `network.WLAN(STA_IF)`, `connect()`, timeout loop |
| Hide the password | `secrets.py` plus `.gitignore` |
| Get exact time | `ntptime.settime()` (UTC) |
| Show local time | Add offset ± DST, then `localtime()` |
| Keep it accurate | Resync every few hours; use the DS3231 as a fallback |

## Key Takeaways

- The Pico W joins 2.4 GHz WiFi with `network.WLAN`; store credentials in a private `secrets.py`.
- NTP delivers UTC from a hierarchy of servers; `ntptime.settime()` sets the RTC to UTC.
- Convert to local time by adding an offset in seconds, plus one hour when daylight saving is in effect.
- Store UTC internally and convert only for display.
- Drift in ppm tells you how often to resync: interval = tolerated error ÷ drift rate.
- Choose a time source, or combine them, by accuracy, power-off survival, and required hardware.
- Program variants (`main-buttons.py`, `main-rtc.py`, `main-w.py`) keep each hardware setup simple.

!!! mascot-celebration "Your Clock Sets Itself"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now join WiFi, fetch UTC with NTP, convert to local time with daylight saving, and choose how often to resync. A clock that corrects itself is a real milestone. Every second counts!

## Practice Questions

1. Why should `secrets.py` be listed in `.gitignore`?
2. It is 03:15 UTC. What is the local time in US Central Standard Time (UTC−6), and on what day?
3. A Pico crystal drifts 30 ppm. How often must you resync to stay within 0.5 seconds?
4. Explain why the time on your Pico can be hours off after unplugging from Thonny, even though it looked right before.
5. Choose a time source for a wall clock with no WiFi that must stay within one minute a year, and justify it.
