---
title: Breadboard Connectivity Explorer
description: Hover over any hole of a half-size breadboard to light up every hole it is connected to, add jumper wires, peek at the hidden metal strips with X-ray view, and test yourself in Challenge mode.
image: /sims/breadboard-connectivity/breadboard-connectivity.png
og:image: /sims/breadboard-connectivity/breadboard-connectivity.png
twitter:image: /sims/breadboard-connectivity/breadboard-connectivity.png
social:
   cards: false
quality_score: 100
---

# Breadboard Connectivity Explorer

<iframe src="main.html" height="542px" width="100%" scrolling="no"></iframe>

[Run the Breadboard Connectivity Explorer Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A **breadboard** lets you build circuits without soldering. Hidden under the plastic are metal strips, and every hole touching the same strip is electrically connected. Knowing which holes share a strip is the single most important breadboard skill: most "my circuit doesn't work" problems are a wire one hole off.

This half-size board has:

- **30 numbered columns.** In each column, rows **a-e** share one strip and rows **f-j** share another.
- A **center channel** that separates the two halves, so a chip can straddle it without shorting its pins.
- Two **power rails** along each long edge, marked **+** (red) and **−** (blue). Each rail is one long strip that runs the length of the board.

Hover over any hole and every hole connected to it turns gold. Click two holes to add a green jumper wire and see how it joins two strips into one. Check **X-ray view** to see the metal strips themselves.

## How to Use

- **Hover** over a hole. The holes it is connected to turn gold, and the line under the title says how many.
- **Click** one hole, then another, to add a jumper wire between them. The message tells you whether the wire created a new connection or joined holes that were already connected. Click the same hole twice to cancel.
- Check **X-ray view** to show the hidden metal strips.
- Press **Clear jumpers** to remove all wires.
- Press **Challenge** to be quizzed. Two holes are marked **A** and **B** (sometimes with a jumper already placed). Press **Yes** or **No**, read the explanation, then press **Next question**. Press **Free play** to leave Challenge mode.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/breadboard-connectivity/main.html"
        height="542px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Analyze which holes on a breadboard are electrically connected.
- Explain why the center channel and the separate + and − rails matter.
- Predict how a jumper wire changes which holes are connected.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Read the Breadboard section of Chapter 2.

### Activities

1. **Explore (4 min):** Students hover over holes in rows a, e, f, and j of the same column and describe the pattern. Then turn on X-ray view to confirm.
2. **Jumper puzzle (4 min):** Ask students to connect hole a3 to hole j20 using as few jumpers as possible. (One jumper is enough, from any of a3-e3 to any of f20-j20.)
3. **Spot the useless wire (2 min):** Students add a jumper between c7 and e7 and read the message. Why does it do nothing?
4. **Challenge (5 min):** Students answer ten Challenge questions and record their score. Discuss any question type that tricked them.

### Assessment

- Students score at least 8 out of 10 in Challenge mode.
- Students can state which holes are connected to any given hole without the MicroSim.
- Students explain why connecting the + rail directly to the − rail is dangerous.

## References

1. [Breadboard (Wikipedia)](https://en.wikipedia.org/wiki/Breadboard) - History and layout of solderless breadboards.
2. [How to Use a Breadboard (SparkFun)](https://learn.sparkfun.com/tutorials/how-to-use-a-breadboard/all) - Photos of the metal strips inside a breadboard.
3. [Short circuit (Wikipedia)](https://en.wikipedia.org/wiki/Short_circuit) - Why joining the power rails directly is a problem.
4. [Dual in-line package (Wikipedia)](https://en.wikipedia.org/wiki/Dual_in-line_package) - Why chips straddle the center channel.
