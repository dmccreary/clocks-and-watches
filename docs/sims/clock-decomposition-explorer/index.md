---
title: Clock Decomposition Explorer
description: Explore a tree that breaks a digital clock into five sub-problems and thirteen small tasks, then pick a bug symptom and see which task is the most likely suspect.
image: /sims/clock-decomposition-explorer/clock-decomposition-explorer.png
og:image: /sims/clock-decomposition-explorer/clock-decomposition-explorer.png
twitter:image: /sims/clock-decomposition-explorer/clock-decomposition-explorer.png
social:
   cards: false
quality_score: 100
---

# Clock Decomposition Explorer

<iframe src="main.html" height="494px" width="100%" scrolling="no"></iframe>

[Run the Clock Decomposition Explorer Fullscreen](./main.html){ .md-button .md-button--primary }

## About This MicroSim

**Decomposition** means breaking a big problem into smaller problems that are each easy enough to solve and test on their own. This tree breaks "build a digital clock" into the five pieces from the chapter (Keep Time, Split Time, Format Time, Draw Time, and Handle Input) and then splits each piece into two or three small tasks.

The tree reads from left to right: the whole problem in purple, the five sub-problems in teal, and the small tasks in light teal. Every small task can be checked by itself, and the info panel tells you how.

The **Symptom** menu turns the tree into a debugging tool. Pick a bug such as "Colon does not flash" and the task most likely to contain it pulses red, along with the reasoning that rules out the other pieces. This is the same two-question narrowing the chapter's worked example uses for a clock that shows 3:05 instead of 15:05.

## How to Use

- **Click** any box to read what that piece does and a "Test it alone" idea.
- **Hover** over a box to highlight its path back to the whole clock in orange.
- Choose a bug from the **Symptom** menu. The suspect task pulses red, and the panel explains why that task is the best place to start looking.
- Use the green arrow and zoom buttons to move around the tree. (When you open the MicroSim fullscreen, you can also drag and scroll-zoom.)

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/clock-decomposition-explorer/main.html"
        height="494px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

By the end of this activity, students will be able to:

- Analyze a digital clock by breaking it into sub-problems and smaller tasks.
- Identify which sub-problem a given symptom most likely belongs to.
- Describe how to test one small piece of a program by itself.

### Grade Level

9-12 (Clocks and Watches with AI)

### Duration

10-15 minutes

### Prerequisites

- Read the Decomposition section of Chapter 1.

### Activities

1. **Explore (4 min):** Students click each teal box and read its job. Ask them to say, in one sentence, why Split Time and Format Time are separate pieces.
2. **Predict the suspect (5 min):** Before choosing each symptom, students write down which small task they think is guilty. Then they select the symptom and compare.
3. **Invent a bug (4 min):** In pairs, one student describes a new symptom ("the clock shows 9:5 instead of 9:05") and the partner finds the task in the tree.
4. **Test plans (2 min):** Each student picks one small task and writes a one-line test for it without looking at the panel, then checks the panel.

### Assessment

- Given a symptom, students name the sub-problem and the small task most likely to contain the bug.
- Students explain why the other sub-problems can be ruled out for that symptom.
- Students write a test that checks one small task by itself.

## References

1. [Decomposition (computer science) (Wikipedia)](https://en.wikipedia.org/wiki/Decomposition_(computer_science)) - Breaking a system into parts that are easier to understand and build.
2. [Computational thinking (Wikipedia)](https://en.wikipedia.org/wiki/Computational_thinking) - The four thinking skills, including decomposition.
3. [Unit testing (Wikipedia)](https://en.wikipedia.org/wiki/Unit_testing) - Testing small pieces of a program one at a time.
4. [vis-network documentation](https://visjs.github.io/vis-network/docs/network/) - The library used to draw this tree.
