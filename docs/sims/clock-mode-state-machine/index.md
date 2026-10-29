---
title: Clock Mode State Machine
description: "A three-state clock (RUN, SET_HOUR, SET_MINUTE) driven by Mode and Cycle buttons, with a mock display, clickable state descriptions and a predict-the-next-state mode."
image: /sims/clock-mode-state-machine/clock-mode-state-machine.png
og:image: /sims/clock-mode-state-machine/clock-mode-state-machine.png
twitter:image: /sims/clock-mode-state-machine/clock-mode-state-machine.png
social:
   cards: false
quality_score: 100
---

# Clock Mode State Machine

<iframe src="main.html" height="504px" width="100%" scrolling="no"></iframe>

[Run the Clock Mode State Machine MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

A **state machine** organizes a program around a few named states. Each state decides what the display shows and what each button press does. This two-button clock has three states: **RUN** shows the time, **SET_HOUR** lets the Cycle button change the hour, and **SET_MINUTE** lets it change the minute. The Mode button always moves to the next state, wrapping from SET_MINUTE back to RUN, which is the line `mode = (mode + 1) % 3` in the chapter's program.

The gold circle is the current state, and the orange arrow shows where the next Mode press will go. Press **Cycle** and the mock clock changes only in the setting states; the field being set is highlighted (a real clock would flash it). Click any state to read what it does. Turn on **Predict** to name the next state before the highlight moves. The code box shows the Python line that each press runs.

This MicroSim supports the chapter [Buttons, Interrupts, and State Machines](../../chapters/07-buttons-state-machines/index.md).

## How to Use

1. Press **Mode** to move the gold highlight along the arrows.
2. Press **Cycle** in each state and watch the mock clock. In RUN nothing changes.
3. Click any circle to read what the display shows and what each button does in that state.
4. Check **Predict**, press **Mode**, then pick the state you think comes next.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/clock-mode-state-machine/main.html"
        height="504px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Apply a state machine to predict what a Mode press does in each state
- Predict what a Cycle press does to the hour and minute in each state
- Explain why the same button can mean different things in different states

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- The modulo wrap-around from Chapter 4
- Buttons and interrupts from earlier in this chapter

### Activities

1. **Exploration** (4 min): Set the clock to 14:05 using only the two buttons. Count how many presses it takes.
2. **Guided Practice** (6 min): Turn on Predict and go around the loop twice. Then explain why Cycle does nothing in RUN.
3. **Assessment** (5 min): Draw the state diagram for a clock that adds SET_ALARM_HOUR and SET_ALARM_MINUTE, and write the new modulo line.

### Assessment

- Students predict the next state correctly every time in Predict mode.
- Students set a requested time with the fewest presses.
- Students extend the diagram to five states and change % 3 to % 5.

## References

1. [Finite-state machine](https://en.wikipedia.org/wiki/Finite-state_machine) - Wikipedia article on states, events and transitions
2. [State diagram](https://en.wikipedia.org/wiki/State_diagram) - Wikipedia article on drawing states as circles and transitions as arrows
3. [vis-network documentation](https://visjs.github.io/vis-network/docs/network/) - the library used to draw this diagram
