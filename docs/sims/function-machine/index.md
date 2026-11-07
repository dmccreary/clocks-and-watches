---
title: Function Machine
description: "Functions drawn as machines: argument tokens enter chutes named after the parameters and the return value comes out, including a write-your-own lambda."
image: /sims/function-machine/function-machine.png
og:image: /sims/function-machine/function-machine.png
twitter:image: /sims/function-machine/function-machine.png
social:
   cards: false
quality_score: 100
---

# Function Machine

<iframe src="main.html" height="452px" width="100%" scrolling="no"></iframe>

[Run the Function Machine MicroSim Fullscreen](./main.html){ .md-button .md-button--primary }
<br/>
[Edit in the p5.js Editor](https://editor.p5js.org/)

## About This MicroSim

A **function** takes input values called **arguments**, assigns them to its **parameters**, runs its body, and hands back a **return value**. Picturing a function as a machine with input chutes and an output chute helps make the difference between parameters (the chute labels) and arguments (the tokens you drop in) concrete.

Choose a function from the menu: the chapter's `to_12_hour(hour24)`, `split_seconds(total)` (which returns a tuple of three values), or `add(a, b)`. Type the arguments and press **Run**: the tokens drop into the chutes, the gears turn, and the return value slides out. The code card shows the `def` and the call. Pick **Write your own** to type a one-line lambda such as `lambda m: m * 60`. For safety, the machine only understands numbers, the parameter names, `+ - * / // %`, parentheses and commas.

This MicroSim supports the chapter [Control Flow, Functions, and Modules](../../chapters/04-control-flow-functions/index.md).

## How to Use

1. Pick a function from the menu. Its definition appears in the code card.
2. Type a number for each argument in the boxes below the menu.
3. Press **Run** and watch the tokens go in and the return value come out.
4. Choose **Write your own (lambda)**, type a lambda in the bottom box, set the arguments and press **Run**. Error messages explain any problem.

## Iframe Embed Code

You can add this MicroSim to any web page by adding this to your HTML:

```html
<iframe src="https://dmccreary.github.io/clocks-and-watches/sims/function-machine/main.html"
        height="452px"
        width="100%"
        scrolling="no"></iframe>
```

## Lesson Plan

### Learning Objectives

Students will be able to:

- Explain a function as a machine that turns arguments into a return value
- Match each argument to the parameter name it is assigned to
- Create a one-line lambda function and test it with different arguments

### Grade Level

9-12 (high school)

### Duration

10-15 minutes

### Prerequisites

- Arithmetic operators including // and %
- Variables and assignment

### Activities

1. **Exploration** (4 min): Run `to_12_hour` for 0, 9, 12, 13 and 23. Write down each result.
2. **Guided Practice** (6 min): Run `split_seconds` for 3600, 3661 and 45296. Explain why it returns three values.
3. **Create** (5 min): Write your own lambda that turns minutes into seconds, and one that takes hours and minutes and returns minutes since midnight.

### Assessment

- Students predict `to_12_hour(0)` and `to_12_hour(12)` before running them.
- Students write a working two-parameter lambda.
- Students explain the difference between a parameter and an argument using the chute picture.

## References

1. [Python Tutorial: Defining Functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions) - official introduction to def and return
2. [Python Tutorial: Lambda Expressions](https://docs.python.org/3/tutorial/controlflow.html#lambda-expressions) - official introduction to lambda
3. [Function (computer programming)](https://en.wikipedia.org/wiki/Function_(computer_programming)) - Wikipedia article on functions
