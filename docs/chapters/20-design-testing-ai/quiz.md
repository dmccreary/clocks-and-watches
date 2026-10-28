# Quiz: Design, Testing, and AI-Assisted Development

Test your understanding of project planning, design trade-offs, testing, debugging, and using AI responsibly with these review questions.

---

#### 1. In a must-should-could requirements list, what should be finished before you start any "could" item?

<div class="upper-alpha" markdown>
1. The enclosure for the clock
2. The final presentation slides
3. A second prototype of the whole clock
4. Every "must" item
</div>

??? question "Show Answer"
    The correct answer is **D**. The must-should-could list protects you from over-promising. You finish every "must", such as showing the correct time, before touching a "could", such as an alarm. Planning in this order, with steps that each end in something you can see working, means you always have a working version to fall back on if time runs short.

    **Concept Tested:** Project Planning

    **See:** [Project Planning](index.md#project-planning)

---

#### 2. Why does the chapter recommend testing each hardware part by itself before combining them?

<div class="upper-alpha" markdown>
1. A part that misbehaves alone will misbehave in the finished clock, and its fault is easier to find when it is the only thing connected
2. Parts that are tested alone no longer need to be tested again once they are combined
3. Individual tests are required by the Pico before it will run a program
4. Testing a part alone makes it more accurate when it is later connected
</div>

??? question "Show Answer"
    The correct answer is **A**. Hardware testing checks each physical part by itself, from the bottom up: power, wires, the Pico, buttons, I2C devices, and then the display. When you add a new part, add only that part and then test, so a failure points to exactly one change. Integration testing is still needed afterward, because two parts that work alone can fail as a pair.

    **Concept Tested:** Hardware Testing

    **See:** [Hardware Testing](index.md#hardware-testing)

---

#### 3. Why does a display often flash or blink if the program clears the whole screen before every update?

<div class="upper-alpha" markdown>
1. Clearing the screen resets the SPI baudrate to a lower value
2. Clearing the screen erases the display driver from memory
3. For a moment the viewer sees a blank screen before the new picture is drawn
4. Clearing the screen turns off the backlight until the next restart
</div>

??? question "Show Answer"
    The correct answer is **C**. On direct write screens, a clear followed by a redraw shows a blank screen in between, which looks like a flash. The fixes, in order of effectiveness, are to avoid clearing by drawing text with a background color, to draw the static parts once, to erase only the old bounding box, and to update less often. Also check the supply, because a backlight or WiFi that dips the voltage can cause visible flicker.

    **Concept Tested:** Display Flicker Fix

    **See:** [Display Flicker Fix](index.md#display-flicker-fix)

---

#### 4. A decision matrix gives readability a weight of 3, cost a weight of 4, and power a weight of 2. Design X scores 4, 3, and 5 on those qualities, and Design Y scores 5, 2, and 3. Which design wins?

<div class="upper-alpha" markdown>
1. Design Y, with a weighted total of 29
2. Design X, with a weighted total of 34
3. Design X, with a weighted total of 12
4. Neither, because the totals tie at 31
</div>

??? question "Show Answer"
    The correct answer is **B**. Multiply each score by its weight and add. For Design X: 3 × 4 + 4 × 3 + 2 × 5 = 12 + 12 + 10 = 34. For Design Y: 3 × 5 + 4 × 2 + 2 × 3 = 15 + 8 + 6 = 29. Design X wins because it does better on the heavily weighted cost. Different weights could reverse the result, which is why the weights capture your own priorities.

    **Concept Tested:** Design Trade-Offs

    **See:** [Design Trade-Offs](index.md#design-trade-offs)

---

#### 5. A bill of materials totals \$17.89. Adding a 15 percent allowance for spares, about what budget should you plan?

<div class="upper-alpha" markdown>
1. About \$20.57
2. About \$18.04
3. About \$32.89
4. About \$17.89
</div>

??? question "Show Answer"
    The correct answer is **A**. Fifteen percent of \$17.89 is about \$2.68, so the planned budget is \$17.89 + \$2.68 = \$20.57. A good BOM includes 10 to 20 percent extra for spares because jumper wires and cheap modules do fail. Adding just 15 cents gives option B, and adding 15 dollars gives option C. Both misread what a percentage allowance means.

    **Concept Tested:** Bill of Materials

    **See:** [Bill of Materials](index.md#bill-of-materials)

---

#### 6. An AI-written alarm program uses `sleep(60)` in its main loop, and pressing the buttons seems to do nothing for up to a minute. What is the diagnosis?

<div class="upper-alpha" markdown>
1. The buttons need pull-down resistors instead of pull-ups
2. The AI used physical pin numbers instead of GP numbers
3. The `sleep()` function is not available in MicroPython
4. The blocking sleep stops the loop from checking buttons; non-blocking `ticks_ms()` timing is needed
</div>

??? question "Show Answer"
    The correct answer is **D**. While the program sleeps it does nothing else, so presses during the sleep are never noticed. Blocking code is one of the common problems in AI-generated programs, along with regular-Python-only calls, wrong pin numbering, invented driver calls, and missing setup. The fix is the non-blocking `ticks_diff()` pattern from earlier chapters. Run every line on the real board and verify the result.

    **Concept Tested:** AI Code Generation

    **See:** [AI Code Generation](index.md#ai-code-generation)

---

#### 7. A logic analyzer capture shows the address byte on an I2C bus, but the ninth clock pulse shows no acknowledgment. What does this tell you?

<div class="upper-alpha" markdown>
1. The device answered correctly but the baudrate is too low
2. The device did not respond, so check the address, the wiring, and the pull-ups
3. The Pico's clock is running too fast for the device
4. The device acknowledged but then sent no data bytes
</div>

??? question "Show Answer"
    The correct answer is **B**. After the address byte, an I2C device that heard its address pulls SDA low during the ninth clock pulse to acknowledge. No acknowledgment means the device did not respond: the address is wrong, the wiring is wrong, or the pull-up resistors are missing. A logic analyzer is the electronics version of a print statement, because it shows what is actually happening on the wires.

    **Concept Tested:** Logic Analyzer Basics

    **See:** [Logic Analyzer Basics](index.md#logic-analyzer-basics)

---

#### 8. A clock shows the wrong date right after midnight on December 31. What is the best first step in a systematic debugging plan?

<div class="upper-alpha" markdown>
1. Rewrite all of the date code from scratch
2. Replace the DS3231 with a new module
3. Reproduce it quickly by setting the time to 23:59:50 on December 31 and watching the rollover
4. Paste the code into an AI tool and use whatever it returns without testing
</div>

??? question "Show Answer"
    The correct answer is **C**. Systematic debugging starts by reproducing the bug on purpose, every time. Setting the clock to 23:59:50 and watching ten seconds is far faster than waiting for a year to end. After that, you form one hypothesis, run one test, and change one thing at a time. Rewriting code or replacing parts without a hypothesis is random poking and teaches you nothing.

    **Concept Tested:** Systematic Debugging

    **See:** [Systematic Debugging](index.md#systematic-debugging)

---

#### 9. A student says, "The AI wrote this code, so if it fails, it is not my responsibility." Which response is best?

<div class="upper-alpha" markdown>
1. You are responsible for every line you submit, so run it on the real board and be able to explain it
2. That is correct, because AI-written code is always tested before it is given out
3. That is correct as long as you mention which AI tool wrote the code
4. That is correct if the program compiles without any errors
</div>

??? question "Show Answer"
    The correct answer is **A**. AI tools produce a draft from a fast but overconfident assistant. They invent functions that do not exist in MicroPython and say so with total confidence. You are responsible for every line you submit, no matter who or what wrote it. If you cannot explain the code, you are not finished: ask the AI to explain it, then check the explanation against the documentation.

    **Concept Tested:** AI Code Review

    **See:** [AI Code Generation](index.md#ai-code-generation)

---

#### 10. Which plan is the best way to organize a five-to-seven-minute final presentation of a clock project?

<div class="upper-alpha" markdown>
1. Read the program aloud line by line for the full time
2. Goal, live demo with a backup video, trade-offs, one bug found by systematic debugging, BOM total, AI use, and next steps
3. Show only the finished clock and leave out anything that went wrong
4. Show only the live demo and skip the parts list and the testing story
</div>

??? question "Show Answer"
    The correct answer is **B**. A strong presentation covers the goal, a live demo with a backup video in case something fails, the design trade-offs, one bug and how you found it, the bill of materials and its total, how you used AI and one thing it got wrong, and your next steps. Presenters are judged on the whole process, not only the finished object, so a clock debugged with clear thinking can beat one that worked by luck.

    **Concept Tested:** Final Presentation

    **See:** [Final Presentation](index.md#final-presentation)
