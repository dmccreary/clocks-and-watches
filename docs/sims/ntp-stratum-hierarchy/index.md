---
title: NTP Stratum Hierarchy
description: A vis-network tree showing how time flows from atomic clocks through stratum 1 and stratum 2 NTP servers to a Pico W, with a step-by-step request and reply that shows the four NTP timestamps and how network delay limits accuracy.
image: /sims/ntp-stratum-hierarchy/ntp-stratum-hierarchy.png
og:image: /sims/ntp-stratum-hierarchy/ntp-stratum-hierarchy.png
twitter:image: /sims/ntp-stratum-hierarchy/ntp-stratum-hierarchy.png
social:
   cards: false
quality_score: 100
---

# NTP Stratum Hierarchy

<iframe src="main.html" height="562px" width="100%" scrolling="no"></iframe>

[Run the NTP Stratum Hierarchy MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

When your Pico W calls `ntptime.settime()`, the time it receives has traveled a long way. It starts at a **stratum 0** reference, an atomic clock or a GPS satellite, and flows down through layers of servers. The **stratum** number counts how many steps a server is from the reference:

- **Stratum 0**: atomic clocks and GPS. They are the reference and are not on the internet.
- **Stratum 1**: servers wired directly to a stratum 0 clock, such as `time.nist.gov`.
- **Stratum 2**: servers that sync from stratum 1 over the internet. Most `pool.ntp.org` servers are stratum 2 or 3.
- **Your Pico W**: the client. It asks for the time and never gives it out.

Each step adds a little error, but the biggest limit on your Pico's accuracy is the **network delay** between the Pico and the server. NTP measures four timestamps to estimate and cancel that delay:

| Timestamp | Recorded by | Moment |
|-----------|-------------|--------|
| T1 | Pico clock | Request leaves the Pico |
| T2 | Server clock | Request arrives at the server |
| T3 | Server clock | Reply leaves the server |
| T4 | Pico clock | Reply arrives at the Pico |

The round trip is \( (T4 - T1) - (T3 - T2) \), and the correction to the Pico's clock is \( \frac{(T2 - T1) + (T3 - T4)}{2} \). The formula assumes the trip up and the trip back take the same time. They rarely do, so the error can be as large as half the round trip. In this MicroSim the Pico's clock starts 2.350 seconds slow, and the request takes 20 percent longer than the reply, so you can see the estimate land close to, but not exactly on, the true correction.

## How to Use

1. **Click** any box to read its role and typical accuracy in the yellow panel.
2. Choose a server in **Ask server**. A dashed red line connects it to the Pico.
3. Press **Send request**. A red packet travels from the Pico to the server and T1 and T2 appear. Press the button again to have the server reply (T3), and once more to bring the reply back (T4) and see the round trip, the correction, and the error limit.
4. Drag **Delay (one way)** from 5 to 300 ms and send another request. Watch the error limit grow with the delay.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/ntp-stratum-hierarchy/main.html"
        height="562px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objective

Students will understand how time flows from atomic clocks down through NTP servers to a Pico (Bloom: Understanding).

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- WiFi connection on the Pico W (Chapter 14)
- UTC and epochs (Chapters 6 and 14)

### Activities

1. **Trace the path** (3 min): Students click from the atomic clock down to the Pico and write one sentence about each stratum.
2. **Step through an exchange** (5 min): With a 40 ms delay, students step through a request and record T1 to T4. They verify the round-trip formula by hand.
3. **Change the delay** (4 min): Students repeat the exchange at 10 ms and at 300 ms and compare the error limits. What matters more for the Pico's accuracy: the server's stratum or the network delay?
4. **Discuss** (3 min): Why is a stratum 2 server close to you often a better choice than a stratum 1 server on the other side of the world?

### Assessment

- What does stratum 2 mean? (Two steps from a reference clock.)
- If the round trip is 100 ms, what is the worst-case error of the sync? (About 50 ms.)
- Explain why the Pico records T1 and T4 with its own clock, but T2 and T3 come from the server's clock.

## References

1. [Network Time Protocol](https://en.wikipedia.org/wiki/Network_Time_Protocol) - Wikipedia; covers strata and the clock synchronization algorithm.
2. [RFC 5905: Network Time Protocol Version 4](https://datatracker.ietf.org/doc/html/rfc5905) - The NTP specification, including the T1 to T4 offset and delay formulas.
3. [NIST Internet Time Service](https://www.nist.gov/pml/time-and-frequency-division/time-distribution/internet-time-service-its) - The stratum 1 servers behind `time.nist.gov`.
4. [NTP Pool Project](https://www.ntppool.org/) - The volunteer servers behind `pool.ntp.org`.
5. [vis-network documentation](https://visjs.github.io/vis-network/docs/network/) - The graph library used by this MicroSim.
