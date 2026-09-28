---
title: Design, Testing, and AI-Assisted Development
description: Planning, design trade-offs, cost, testing, debugging, using generative AI, peer review, and presenting a custom clock project.
generated_by: claude skill chapter-content-generator
date: 2026-09-28 14:54:39
version: 1.10
---

# Design, Testing, and AI-Assisted Development

## Summary

Students plan a project, weigh design trade-offs and cost, and test and debug systematically. They use generative AI responsibly and review code. After this chapter they can design, build, and present their own clock.

## Concepts Covered

This chapter covers the following 21 concepts from the learning graph:

| Concept | Concept Impact Score |
|---------|-----------------------|
| Project Planning | 24 |
| Generative AI Prompts | 3 |
| Bill of Materials | 8 |
| Cost Analysis | 6 |
| AI Code Generation | 2 |
| Component Sourcing | 1 |
| Design Trade-Offs | 5 |
| Debugging Techniques | 9 |
| AI Code Review | 1 |
| Final Presentation | 1 |
| Enclosure Design | 2 |
| User Experience Design | 1 |
| Troubleshooting | 7 |
| Logic Analyzer Basics | 1 |
| Peer Review | 2 |
| Display Flicker Fix | 1 |
| Hardware Testing | 3 |
| Integration Testing | 1 |
| Code Walkthrough | 1 |
| Systematic Debugging | 1 |
| Watch Band Integration | 1 |

## Prerequisites

This chapter builds on concepts from:

- [Chapter 1: Computational Thinking and Physical Computing](../01-foundations/index.md)
- [Chapter 2: Electronics Fundamentals and Breadboard Wiring](../02-electronics-fundamentals/index.md)
- [Chapter 3: MicroPython Basics: Variables and Data Types](../03-micropython-basics/index.md)
- [Chapter 4: Control Flow, Functions, and Modules](../04-control-flow-functions/index.md)
- [Chapter 8: Communication Buses: I2C, SPI, and UART](../08-communication-buses/index.md)
- [Chapter 9: LED Displays and the First Digital Clock](../09-led-displays/index.md)
- [Chapter 11: OLED Displays and Framebuffers](../11-oled-framebuffers/index.md)
- [Chapter 14: WiFi, NTP, and Time Accuracy](../14-wifi-ntp/index.md)
- [Chapter 15: Color Displays and Smartwatch Faces](../15-color-displays/index.md)

---

!!! mascot-welcome "Your Turn to Design"
    ![Chrono waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    You've collected every skill you need. Now you'll plan your own clock, test it, fix what breaks, use AI as a helper without letting it drive, and show it off. This is where you become the designer. Let's make time tick!

## From Following to Designing

The earlier chapters taught parts: displays, buses, sensors, sound, and power. A real project asks you to choose among them, fit them together, and make them work. This chapter covers the whole journey in the order you will live it: **plan and design**, **source and build**, **test and debug**, **use AI wisely**, and **review and present**. The habits here matter as much as any single piece of code.

## Project Planning

**Project planning** is deciding what you will build, how, and in what order, before you buy parts or write code. A short plan saves hours of rework. A good plan answers five questions:

| Question | Example answer |
|----------|----------------|
| **Goal:** what should it do? | "Show the time and outdoor temperature on a round display" |
| **User:** who uses it, and where? | "Me, on my desk, glancing across the room" |
| **Constraints:** budget, time, skills? | "\$30, three weeks, no soldering" |
| **Requirements:** must, should, could? | Must: show correct time. Should: auto-dim. Could: alarm |
| **Risks:** what might go wrong? | "Display arrives late or has different pins" |

Use the decomposition skill from Chapter 1 to split the goal into small tasks, and order them so that something works early. A dependable order is:

1. Get the Pico running (blink an LED).
2. Get the display showing anything at all.
3. Show the time.
4. Add inputs (buttons).
5. Add extras one at a time (sound, sensors, WiFi).
6. Build the enclosure.

Each step ends with something you can see working, so you always have a working version to fall back on. The **must-should-could** list protects you from over-promising: finish every "must" before touching a "could."

## Design Trade-Offs

Every design choice gives up something to gain something else. A **design trade-off** is a decision where improving one quality worsens another. You have met many already: a bigger display costs more and uses more power, a faster SPI speed risks garbled pixels, and WiFi sync gives accuracy at the price of battery life.

The main qualities for a clock are cost, display readability, power consumption, accuracy, and user experience. A **decision matrix** compares designs fairly. Give each quality a **weight** by importance and each design a **score** from 1 to 5, then multiply and add.

**Worked example.** A student compares two designs for a bedside clock. Weights: readability 4, cost 2, power 1, accuracy 3.

| Quality | Weight | TM1637 LED clock | Round color watch |
|---------|--------|------------------|-------------------|
| Readability (in the dark) | 4 | 5 | 4 |
| Cost | 2 | 5 | 2 |
| Power | 1 | 4 | 2 |
| Accuracy (with WiFi sync) | 3 | 3 | 5 |
| **Weighted total** | | \( 20+10+4+9 = 43 \) | \( 16+4+2+15 = 37 \) |

The LED clock wins for this user. A student who wants a wearable, or who gives power and accuracy higher weights, could reach the opposite answer, and that is the point: the weights capture *your* priorities, so the decision is explained rather than guessed.

#### Diagram: Design Decision Matrix

<details markdown="1">
<summary>Design Decision Matrix</summary>
Type: MicroSim
**sim-id:** design-decision-matrix<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *evaluate* competing clock designs by weighting criteria and *justify* a choice (Bloom: Evaluating).

**Visual elements:** A table with criteria as rows and up to four designs as columns, with slider inputs for the weights and 1 to 5 score cells. A bar chart on the right shows each design's weighted total, with the winner highlighted.

**Controls:** Sliders for each criterion's weight (0 to 5); editable scores; presets loading the worked example; a "Sensitivity" button that reports how much a weight must change before the winner flips.

**Responsive design:** The table scrolls horizontally on narrow screens and the chart moves below it.

Implementation: p5.js with a weighted sum.
</details>

## Cost Analysis

**Cost analysis** is working out what a project really costs, so it stays inside the budget. Add the cost of every part, then add shipping, spare parts, and tools you do not already own.

### Bill of Materials

A **bill of materials (BOM)** is the complete list of parts in a project, with quantity, price, and source. It is the document you buy from and the one that lets someone else rebuild your clock. Here is a sample for a simple OLED clock with a real-time clock. Prices marked "est." are rough estimates, so replace them with the actual listing price.

| Part | Qty | Unit cost | Total | Source |
|------|-----|-----------|-------|--------|
| Raspberry Pi Pico W | 1 | \$5.99 | \$5.99 | Micro Center |
| 128×64 SSD1306 OLED | 1 | \$3.50 | \$3.50 | Online marketplace |
| DS3231 RTC module | 1 | \$3.00 | \$3.00 | Online marketplace |
| Half-size breadboard | 1 | \$2.00 est. | \$2.00 | Bulk pack |
| Jumper wires (pack) | 1 | \$3.00 est. | \$3.00 | Online marketplace |
| Push buttons | 2 | \$0.20 est. | \$0.40 | Online marketplace |
| **Total** | | | **\$17.89** | |

A good BOM includes 10 to 20 percent more budget for spares, since jumper wires and cheap modules do fail. The [Purchasing Parts guide](../../setup/02-purchasing-parts.md) explains where the course sources its parts.

### Component Sourcing

**Component sourcing** is where you buy parts. Local electronics stores are fast and easy to return to. Online marketplaces are cheaper but slower, and their listings can be wrong, which is a trap.

!!! mascot-warning "Listings Can Lie"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    A real example from this course: some listings for the 2.1 inch round display claim a 640 by 640 resolution, but the silkscreen on the board reads 360 by 360, which is what the driver expects. Cheap listings can misstate resolution, controller, and voltage. Before ordering, look for the controller chip name, a pin list, and a datasheet, and read the reviews for people using it with MicroPython.

Sourcing habits that pay off:

- Buy from sellers who show the controller chip and pin labels in the photos.
- Order one or two extra of anything cheap.
- Buy breadboards and jumpers in bulk.
- Match your parts to a driver library that already exists.

## User Experience Design

**User experience (UX) design** is making the clock pleasant and obvious to use for the person who uses it. A clock is glanced at for a second, so the design has to work at a glance.

| Principle | In practice |
|-----------|-------------|
| Glanceable | Large digits, the time as the biggest thing on screen |
| Readable | High contrast, right brightness for the room (Chapter 18) |
| Consistent | Each button always means the same thing |
| Forgiving | Setting mode times out back to run mode after 10 seconds |
| Responsive | Beep or flash on a press, so the user knows it registered |
| Honest | Shows when the time source has failed |

Watch someone else use your clock without explaining it. Wherever they hesitate is a UX problem, and you will learn more from two minutes of watching than from an hour of thinking.

## Enclosure Design

An **enclosure** is the case that holds the electronics. It protects the parts, hides the wires, and makes the project look finished. Simple options include the acrylic mount from Chapter 2, a box cut from foam board, or a 3D-printed or laser-cut case.

Design checklist: measure the parts with calipers before cutting, leave openings for the USB cable and buttons, make the bezel cover the display's unusable edge (the safe radius from Chapter 15), and give the light sensor a small window (Chapter 18). Keep wires from being pulled by fastening them so that a tug does not yank a connector loose.

### Watch Band Integration

A **watch band integration** turns a round-display board into something you can wear. The main challenges are size, comfort, and safety: a LiPo battery and bare board pressed against skin need insulation, a rounded back plate, and no exposed contacts. The case needs lugs sized for a standard strap width (commonly 20 or 22 mm) so an ordinary watch band fits, and the weight should sit close to the wrist. All-in-one boards from Chapter 18 make this much easier than a wired breadboard build.

## Hardware Testing

**Hardware testing** means checking each physical part *by itself* before you combine them. A part that misbehaves alone will misbehave in the finished clock, and it is much easier to find the fault when it is the only thing connected.

| Part | Simple test |
|------|-------------|
| Power | Multimeter shows 3.3 V on the rail |
| Wires | Continuity beep between the two ends |
| Pico | Blink the on-board LED |
| Buttons | Print `value()` when pressed |
| I2C devices | Run the scanner (Chapter 8) |
| Display | `fill()` with a bright color, then draw a border |

Test in this order, from the bottom up, and record the result of each test.

!!! mascot-tip "One Change at a Time"
    ![Chrono with a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    When you add a new part, add only that part, then test. If something breaks, you know exactly which change did it. Wiring five things and then wondering what went wrong is how afternoons disappear.

## Integration Testing

**Integration testing** checks that parts still work *together*. Two parts can each work alone and still fail as a pair: WiFi can brown out the supply and garble the display (Chapter 18), or an interrupt can interrupt a drawing routine (Chapter 7).

Plan the tests around the times that break clocks:

| Test | What to check |
|------|---------------|
| Midnight | 23:59:59 rolls to 00:00:00 and the date advances |
| Noon and 12-hour display | 11:59 AM to 12:00 PM, and 12:59 to 1:00 |
| Month and year end | Jan 31 to Feb 1; Dec 31 to Jan 1 |
| Leap day | Feb 28 to Feb 29 in a leap year |
| Daylight saving change | The hour jumps at the correct time (Chapter 14) |
| Power loss | Unplug it; it returns with the correct time |
| Long run | Leave it 24 hours; check drift and memory (`gc.mem_free()`) |

To test rollovers quickly, set the time to 23:59:50 with your set-time function and watch for ten seconds, instead of waiting a day.

## Troubleshooting

**Troubleshooting** is finding and fixing the cause of a problem. Most problems fall into a few families, so knowing the common ones makes you fast. This table collects the ones from earlier chapters:

| Symptom | Likely cause | Where to look |
|---------|--------------|---------------|
| Display is blank | Missing `show()`, wrong pins, no power | Chapter 11 |
| I2C scan finds nothing | SDA and SCL swapped, no ground, wrong pin pair | Chapter 8 |
| Colors are wrong | RGB/BGR order or byte swap | Chapter 15 |
| Garbled pixels | SPI baudrate too high, long wires | Chapters 8, 11 |
| Button counts many times | Contact bounce | Chapter 7 |
| Time shows 2021 after power-up | No RTC or sync | Chapters 6, 13 |
| Time is hours off | Time zone or DST, or Thonny local vs UTC | Chapter 14 |
| Random resets | Brownout: weak supply or big load | Chapter 18 |
| Program does not start by itself | Not saved as `main.py` | Chapter 5 |
| WiFi will not connect | 5 GHz network, wrong password | Chapter 14 |

Work from the cheapest, most likely cause to the most expensive. Check power and wiring before code, and code before blaming the hardware.

#### Diagram: Troubleshooting Decision Tree

<details markdown="1">
<summary>Troubleshooting Decision Tree</summary>
Type: workflow diagram
**sim-id:** troubleshooting-decision-tree<br/>
**Library:** Mermaid<br/>
**Status:** Specified

**Learning objective:** Students will *analyze* a symptom and *select* the most likely cause and the next test (Bloom: Analyzing).

**Nodes:** A root "What is the symptom?" leading to branches: nothing on the display, wrong image, wrong time, buttons misbehave, random resets. Each branch asks yes/no questions ("Does the I2C scan find the device?") and ends at a suggested fix and the chapter to review.

**Interactions:** Every node has a Mermaid `click` directive that shows the reasoning and the test to run. A "Start over" button resets the path, and a breadcrumb shows the questions answered so far.

**Responsive design:** The diagram scales to container width.

Implementation: Mermaid flowchart with click callbacks.
</details>

### Debugging Techniques

**Debugging** is finding and fixing bugs in code. These are the techniques you already know, gathered in one list:

- **Print debugging** (Chapter 3): print the value of a variable, labeled, at key points.
- **Read the traceback:** the last line names the error; the line above names where.
- **Isolate:** run the smallest piece that shows the problem, in the REPL.
- **Check types:** print `type(x)`, since an `int` may really be a `str` or `float`.
- **Compare with a working example:** the kit's sample code is a known-good reference.
- **Rubber duck:** explain the code out loud, line by line, to a friend or even a rubber duck. Explaining often reveals the bug.

### Systematic Debugging

**Systematic debugging** is debugging as a scientific method instead of random poking. It has four repeating steps:

1. **Reproduce:** make the bug happen on purpose, every time.
2. **Hypothesize:** guess one cause, in writing.
3. **Test:** run one experiment that would prove the guess wrong.
4. **Fix and verify:** change one thing, then confirm the bug is gone and nothing else broke.

A powerful trick is **divide and conquer**: comment out half the program and see whether the bug remains, then halve again, until you have cornered it in a few lines. Version control (Chapter 5) helps here as well, since you can compare the current code with the last version that worked.

!!! mascot-thinking "Every Bug Is an Experiment"
    ![Chrono thinking](../../img/mascot/thinking.png){ class="mascot-admonition-img" }
    Treat a bug as a question the computer is answering honestly: "here is what your code really does." Form a guess, design a test that could prove it wrong, and let the result guide you. Random changes teach you nothing, but a good experiment teaches you something every time.

### Display Flicker Fix

A display that flashes or blinks with every update is a common problem, especially on the direct write screens of Chapter 15. The usual cause is **clearing the whole screen and redrawing it**, so for a moment the viewer sees a blank screen. Fixes, in order of effectiveness:

1. **Do not clear.** Draw text with a background color so the new characters cover the old ones (Chapter 15).
2. **Draw the static parts once,** such as the dial and labels, and update only what changed.
3. **Erase just the old bounding box** before drawing the new item (Chapter 12).
4. **Update less often.** If the time changes once per second, do not redraw ten times per second.
5. **Check the supply.** A backlight or WiFi that dips the voltage can cause visible flicker (Chapter 18).

### Logic Analyzer Basics

Sometimes the fault is in the signals themselves: a bus that does not answer, or timing that is off. A **logic analyzer** is a small tool that records several digital signals over time and shows them as waveforms on your computer. Inexpensive USB models cost about ten dollars, and free software can decode I2C and SPI traffic into readable bytes.

Connect one channel to SDA, another to SCL, and one to ground, then trigger a capture while your program talks to the device. You can see the start condition, the address byte, and whether the device answered. If the address is sent and the ninth clock shows no acknowledgment, the device did not respond: you have the wrong address, the wrong wiring, or no pull-up resistors. You can also measure the real clock speed, and see contact bounce on a button.

A logic analyzer is the electronics version of a print statement: it shows what is *actually* happening on the wires, which may be different from what you think you told it to do.

#### Diagram: Logic Analyzer Trace Reader

<details markdown="1">
<summary>Logic Analyzer Trace Reader</summary>
Type: MicroSim
**sim-id:** logic-analyzer-trace-reader<br/>
**Library:** p5.js<br/>
**Status:** Specified

**Learning objective:** Students will *interpret* a captured I2C waveform and *diagnose* a missing acknowledgment (Bloom: Analyzing).

**Visual elements:** Two stacked digital traces labeled SCL and SDA, with a time axis and an annotation layer that decodes start, address, read/write bit, ACK, data bytes, and stop.

**Controls:** A dropdown chooses a scenario: *good write to 0x3C*, *wrong address (no ACK)*, *missing pull-ups (slow edges)*, and *button bounce on a GPIO*. Clicking any part of the waveform opens an infobox naming what it is. A "Diagnose" quiz asks what is wrong and gives feedback.

**Responsive design:** The trace scrolls horizontally on narrow screens.

Implementation: p5.js with pre-defined waveform arrays.
</details>

## Using Generative AI

Generative AI tools such as ChatGPT and Claude can explain code, draft programs, and spot mistakes. They are powerful helpers, and like any powerful tool they work best when you understand what they do well and where they fail. See [AI in the Classroom](../../setup/05-ai-in-the-classroom.md) and the [sample prompts](../../prompts/index.md) for this course's approach.

### Generative AI Prompts

A **prompt** is the instruction you give the AI. The quality of the answer depends on the quality of the prompt. A strong prompt states:

- **Context:** the board (Pico W), firmware (MicroPython), display, and libraries.
- **Goal:** exactly what you want the program to do.
- **Constraints:** no blocking loops, use `config.py`, print the name and version banner.
- **Examples:** paste a working program and say "just like this one, but with red digits."
- **Output format:** "explain each change" or "return only the changed function."

Here is a sample prompt:

```text
I have a Raspberry Pi Pico W running MicroPython with a 128x64 SSD1306 OLED
on I2C (SDA GP0, SCL GP1) and a DS3231 at 0x68. Below is my working program.
Add a snooze feature: pressing the button on GP14 while the alarm is ringing
should stop it and set it to ring again in 9 minutes. Do not use sleep();
use ticks_ms(). Explain each change in one sentence.
```

The context, goal, constraint, and format are all in the prompt. Vague prompts like "make my clock better" produce vague code.

### AI Code Generation

**AI code generation** is having the AI write code for you. Treat the result as a **draft from a fast but overconfident assistant**. It often looks correct and is wrong in small ways, especially for MicroPython, which is far less common than regular Python.

!!! mascot-warning "Confident and Wrong"
    ![Chrono warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    AI tools often invent functions that don't exist in MicroPython, use modules like `datetime` that the Pico doesn't have, or mix up GP numbers and pin numbers. They say it with total confidence. Run every line on the real board, and when it fails, paste the exact error message back to the AI.

Common problems to look for:

| Problem | Example |
|---------|---------|
| Regular Python only | `datetime.now()`, `time.strftime()` |
| Wrong pin numbering | Uses physical pin numbers in `Pin()` |
| Blocking code | `sleep(60)` inside the main loop |
| Invented driver calls | `display.draw_circle()` on a driver with no such method |
| Missing setup | No `oled.show()` or `fill(0)` |

You are responsible for every line you submit, no matter who or what wrote it. If you cannot explain the code, you are not finished: ask the AI to explain it, then check the explanation against the documentation.

### AI Code Review

**AI code review** flips the roles: you write the code and the AI checks it. It is very good at spotting things a tired human misses. A useful prompt:

```text
Review this MicroPython clock program for a Raspberry Pi Pico W. Look for:
bugs at midnight and noon, blocking loops, unhandled exceptions from WiFi,
memory problems, and unclear names. List issues by severity and suggest a fix
for each. Do not rewrite the whole program.
```

Treat each finding as a **hypothesis** to verify, not a fact. Some suggestions will be wrong, and some will not apply to MicroPython. Test the ones you accept, and decline the rest.

## Human Review

### Peer Review

**Peer review** is having a classmate examine your project, and examining theirs in return. A fresh pair of eyes catches problems you can no longer see. Use a short checklist:

- Does it run from a fresh power-up, with no computer?
- Are pin numbers in `config.py` and names clear?
- Does each file print its name and version?
- Are secrets kept out of shared files?
- Does the wiring match the diagram?

Give feedback that is specific and kind. A useful format is **I like, I wish, What if**: "I like the big digits. I wish the buttons beeped. What if the alarm got louder over time?"

### Code Walkthrough

A **code walkthrough** is a meeting in which the author explains the code line by line while others follow along and ask questions. Its power comes from *tracing with real values*: pick a specific time, such as 23:59:59, and step through the code as if you were the Pico, saying what each variable holds after each line. Rollover and off-by-one bugs tend to show up within minutes. Keep the walkthrough short (10 to 15 minutes) and focus on the code, not the person.

## Final Presentation

The **final presentation** is where you show your clock and explain your thinking. Aim for five to seven minutes with this structure:

1. **The goal:** what you set out to build, and for whom.
2. **A live demo,** with a backup video in case something fails.
3. **Design trade-offs:** the choices you made and what you gave up (cost, readability, power, accuracy, user experience).
4. **What went wrong:** one bug and how you found it, using systematic debugging.
5. **Cost:** your bill of materials and total.
6. **AI:** how you used it, one thing it got wrong, and how you caught it.
7. **Next steps:** what you would add with more time.

Presenters are judged on the whole process, not only on the finished object. A clock that did not fully work but was debugged with clear thinking can be a better project than one that worked by luck.

| Criterion | Excellent looks like |
|-----------|----------------------|
| Function | Runs by itself and shows the correct time |
| Design | Trade-offs are explained with evidence |
| Testing | Rollovers and power loss were tested |
| Process | The plan, BOM, and debugging are documented |
| Communication | Clear, on time, and the demo works |

## Key Takeaways

- Plan first: goal, user, constraints, must-should-could requirements, and a build order that always leaves something working.
- A weighted decision matrix turns design trade-offs into an explained decision.
- A bill of materials with a spares allowance keeps the project on budget; verify listings before you buy.
- Test each part alone (hardware testing), then together, including midnight, month end, leap day, and power loss.
- Debug by reproducing, hypothesizing, testing, and changing one thing at a time.
- Flicker is fixed by not clearing the screen and updating only what changed.
- Use AI with clear prompts, verify everything it writes on the real board, and take responsibility for your code.
- Peer reviews, code walkthroughs, and a good presentation make a project trustworthy and shareable.

!!! mascot-celebration "You're a Clock Builder"
    ![Chrono celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    You can now plan a project, weigh trade-offs, test and debug like an engineer, use AI wisely, and present your work. That's every skill in this book, and you built a clock with them. Every second counts, and yours were well spent!

## Practice Questions

1. Write a must-should-could list for a stopwatch that also shows the time.
2. Use the decision matrix method to compare an OLED clock and an e-paper clock for a solar-powered outdoor clock. Which qualities would you weight most heavily?
3. Make a bill of materials for a TM1637 clock with an RTC, including a 15 percent spares allowance.
4. Your clock shows the wrong date after midnight on December 31. Describe a systematic debugging plan, starting with how you reproduce it quickly.
5. An AI gives you a program that calls `time.strftime()`. What is the problem, and what would you do?
