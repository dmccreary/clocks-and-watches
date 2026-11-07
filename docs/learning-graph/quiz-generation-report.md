# Quiz Generation Quality Report

Generated: 2026-10-28  
Execution Mode: Serial (1 agent)  
Wall-clock Time: 14 minutes 3 seconds

## Overall Statistics

- **Total Chapters:** 20
- **Total Questions:** 200
- **Avg Questions per Chapter:** 10.0
- **Overall Quality Score:** 92/100 (automated rubric below; not a substitute for human review)

## Per-Chapter Summary

| Chapter | Type | Questions | Bloom's mix (R/U/Ap/An/E/C) | Answers (A/B/C/D) | Listed concepts tested |
|---------|------|-----------|-----------------------------|-------------------|------------------------|
| Ch 1: Computational Thinking and Physical Computing | introductory | 10 | 4/3/2/1/0/0 | 2/3/3/2 | 8 of 13 (62%) |
| Ch 2: Electronics Fundamentals and Breadboard Wiring | introductory | 10 | 2/4/3/1/0/0 | 3/2/2/3 | 10 of 24 (42%) |
| Ch 3: MicroPython Basics: Variables and Data Types | introductory | 10 | 3/3/3/1/0/0 | 2/3/2/3 | 9 of 20 (45%) |
| Ch 4: Control Flow, Functions, and Modules | intermediate | 10 | 2/3/3/2/0/0 | 3/2/2/3 | 10 of 19 (53%) |
| Ch 5: The Pico Platform: Pins, Files, and Firmware | intermediate | 10 | 2/3/3/2/0/0 | 3/2/3/2 | 10 of 19 (53%) |
| Ch 6: Getting the Time in MicroPython | intermediate | 10 | 2/3/3/2/0/0 | 3/2/3/2 | 10 of 22 (45%) |
| Ch 7: Buttons, Interrupts, and State Machines | intermediate | 10 | 2/3/3/2/0/0 | 3/2/3/2 | 10 of 13 (77%) |
| Ch 8: Communication Buses: I2C, SPI, and UART | intermediate | 10 | 2/3/3/2/0/0 | 2/3/2/3 | 10 of 23 (43%) |
| Ch 9: LED Displays and the First Digital Clock | intermediate | 10 | 2/3/3/2/0/0 | 2/3/3/2 | 7 of 11 (64%) |
| Ch 10: Coordinates, Trigonometry, and Clock Geometry | intermediate | 10 | 2/3/3/2/0/0 | 3/2/3/2 | 8 of 13 (62%) |
| Ch 11: OLED Displays and Framebuffers | intermediate | 10 | 2/3/3/2/0/0 | 3/3/2/2 | 8 of 14 (57%) |
| Ch 12: Drawing Shapes, Text, and Animation | intermediate | 10 | 2/3/3/2/0/0 | 2/3/3/2 | 9 of 19 (47%) |
| Ch 13: Real-Time Clocks and the DS3231 | intermediate | 10 | 2/3/3/2/0/0 | 2/3/3/2 | 8 of 11 (73%) |
| Ch 14: WiFi, NTP, and Time Accuracy | intermediate | 10 | 2/3/3/2/0/0 | 3/2/3/2 | 10 of 21 (48%) |
| Ch 15: Color Displays and Smartwatch Faces | intermediate | 10 | 2/3/3/2/0/0 | 3/3/2/2 | 8 of 20 (40%) |
| Ch 16: NeoPixels and Shift Register Clocks | intermediate | 10 | 2/3/3/2/0/0 | 2/3/2/3 | 9 of 20 (45%) |
| Ch 17: Sound, Alarms, and Timers | intermediate | 10 | 2/3/3/2/0/0 | 3/2/2/3 | 8 of 16 (50%) |
| Ch 18: Sensors, Power, and Low-Power Design | advanced | 10 | 1/3/3/2/1/0 | 2/3/2/3 | 9 of 22 (41%) |
| Ch 19: E-Paper and Weather Displays | advanced | 10 | 1/2/3/2/1/1 | 3/2/3/2 | 8 of 9 (89%) |
| Ch 20: Design, Testing, and AI-Assisted Development | advanced | 10 | 1/2/2/3/1/1 | 3/3/2/2 | 10 of 21 (48%) |

## Bloom's Taxonomy Distribution (Overall)

Targets are the average of each chapter's own target (introductory chapters 1-3, intermediate 4-17, advanced 18-20).

| Level | Actual | Target | Deviation |
|-------|--------|--------|-----------|
| Remember | 20.0% (40) | 25.8% | -5.8% ✓ |
| Understand | 29.5% (59) | 30.0% | -0.5% ✓ |
| Apply | 29.0% (58) | 27.0% | +2.0% ✓ |
| Analyze | 19.0% (38) | 15.0% | +4.0% ✓ |
| Evaluate | 1.5% (3) | 1.5% | +0.0% ✓ |
| Create | 1.0% (2) | 0.8% | +0.2% ✓ |

Largest deviation is 5.8 percentage points (Remember is under target), inside the ±15% tolerance. Evaluate and Create questions appear only in Chapters 18 to 20, as intended.

## Answer Balance (Overall)

- A: 26.0% (52/200)
- B: 25.5% (51/200)
- C: 25.0% (50/200)
- D: 23.5% (47/200)

Every chapter has 2 or 3 correct answers per letter, and no letter repeats more than twice in a row.

## Explanation Quality

- Every question has an explanation of 50 to 79 words (average 62); the target is 50 to 100.
- Every explanation names the correct letter, explains why the distractors are wrong where useful, and ends with a **Concept Tested** label and a **See** link.

## Link Validation

All 200 **See** links point to `index.md` in the same chapter folder, and every `#anchor` was checked against the headings of that chapter's `index.md` using the MkDocs heading-slug rules. No broken anchors were found. A full `mkdocs build` into a scratch folder reported no warnings about the quiz pages.

## Concept Coverage

Across all chapters, 179 of 350 learning-graph concepts listed in the chapters (51%) are named as the **Concept Tested** for at least one question. With 10 questions per chapter and 11 to 24 concepts per chapter, the 75% target in the skill is not reachable for most chapters. Questions were weighted toward concepts with high concept impact scores.

## Quality Rubric (automated)

| Check | Points | Result |
|-------|--------|--------|
| Format, structure, and links (10 questions, 4 options, one correct answer, valid anchors) | 25 / 25 | All 20 files pass |
| Answer balance (20 to 30% per letter) | 15 / 15 | 23.5% to 26.0% |
| Bloom's distribution (within tolerance of target) | 23 / 25 | Largest deviation 5.8 points |
| Explanation quality (50 to 100 words, concept label, link) | 15 / 15 | All 200 pass |
| Concept coverage (51% of listed concepts vs 75% target) | 14 / 20 | Limited by 10 questions per chapter |
| **Total** | **92 / 100** | |

This rubric checks structure and balance. It cannot judge whether each distractor is plausible or whether each question has a single defensible answer, so the instructor should read the questions before using them for grading.

## Recommendations

1. Have a teacher read through at least one quiz per unit for ambiguity and reading level; the checks above are mechanical.
2. Chapters 2, 3, 6, 8, 14, 15, 16, 18, and 20 cover 20 or more concepts. If broader coverage is wanted, raise those quizzes to 12 questions.
3. Re-run this skill after major chapter edits, since the **See** anchors depend on the chapter headings.
4. `quiz-bank.json` holds all questions with Bloom's level, difficulty, concept, and source anchor, ready for LMS export or a practice chatbot.
