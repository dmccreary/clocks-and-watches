---
title: Alarm State Machine
description: Press alarm events and watch an alarm clock's state machine move between IDLE, ARMED, RINGING and SNOOZED while a small clock model and the alarm_on, ringing and fired variables update.
image: /sims/alarm-state-machine/alarm-state-machine.png
og:image: /sims/alarm-state-machine/alarm-state-machine.png
twitter:image: /sims/alarm-state-machine/alarm-state-machine.png
social:
   cards: false
quality_score: 0
---

# Alarm State Machine

<iframe src="main.html" height="502px" width="100%" scrolling="no"></iframe>

[Run the Alarm State Machine MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

An alarm clock is a **state machine**: at any moment it is in exactly one state, and an
**event** (a button press or the passing of time) moves it along an arrow to the next
state. This diagram has four states:

| State | What the clock is doing |
|-------|-------------------------|
| **IDLE** | The alarm is switched off |
| **ARMED** | The alarm is on and waiting for the alarm time |
| **RINGING** | The tone is playing |
| **SNOOZED** | The tone is silent and a new ring time, 9 minutes later, is stored |

Each arrow is labeled with the event that causes it. Press an event button and the
highlight follows the matching arrow. If no arrow with that label leaves the current state,
the event is **ignored**, which is exactly what a real state machine does. The black clock
panel shows the time, the alarm time (07:30) and the next ring time, and the gray box shows
the variables from the chapter's code: `alarm_on`, `ringing` and `fired`.

## How to Use

1. **Before every press, predict** which arrow the highlight will follow, or whether the
   event will be ignored.
2. Press **Toggle alarm** to arm the alarm, then **Time matches** to jump the clock to 07:30.
3. Try **Snooze**, **Stop** and **60 seconds pass**, and read the message box after each one.
4. Click any state box to see what that state means and which variable values hold in it.
5. Press **Reset** to return to IDLE at 07:29.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/alarm-state-machine/main.html"
        height="502px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Grade Level
9-12 (Clocks and Watches with AI)

### Duration
15 minutes

### Prerequisites

- State machines and button events (Chapter 7)
- The alarm and snooze code in Chapter 17

### Learning Objectives

Students will be able to:

- Apply a state diagram to predict the next state after a sequence of events
- Explain why the `fired` flag stops the alarm from restarting during the same minute
- Calculate the new ring time after one or more snoozes

### Activities

1. **Predict a sequence** (5 min): Starting from Reset, write down the state after each event in
   this list: Toggle alarm, Time matches, Snooze, Snooze, 60 seconds pass. Then press the buttons
   and check each prediction. (Hint: what does the first Snooze do, and does the second one have an arrow?)
2. **Find the guard** (5 min): Ring the alarm, press **Stop**, then press **Time matches** again.
   Why does it not ring? Which variable blocks it, and which event clears it?
3. **Snooze math** (5 min): Ring the alarm, snooze, let the snooze ring, and snooze again. What is
   the next ring time? Check it against `snooze(7, 39)` from the chapter.

### Assessment

- Given a starting state and a list of events, the student writes the final state and variable values.
- The student explains that `fired` prevents a second ring during the minute that already matched.
- The student identifies which events are ignored in each state and why.

## References

1. [Finite-state machine](https://en.wikipedia.org/wiki/Finite-state_machine) - Wikipedia article on states, events and transitions.
2. [Snooze button](https://en.wikipedia.org/wiki/Snooze_button) - Wikipedia article on the history of the snooze button and its traditional nine-minute delay.
3. [DS3231 datasheet (Analog Devices)](https://www.analog.com/en/products/ds3231.html) - The real-time clock chip with two built-in alarms used in Chapter 13 and Chapter 17.
4. [vis-network documentation](https://visjs.github.io/vis-network/docs/network/) - The library that draws the state diagram.
