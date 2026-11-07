<!--
LESSON TEMPLATE for a student-facing kit page (docs/kits/<kit>/index.md).

Before you fill this in:
  1. Read the repo's CONTENT-GENERATION-GUIDELINES.md (reading level, mascot rules, vocabulary).
     On the SHT40 kit this was skipped at first and had to be checked after the fact.
  2. Have the REAL outputs of each lab in hand (copy them from a simulator run or the board).
     Expected-output blocks must be exact, not invented.
  3. Replace every double-brace token. scripts/check_lesson.py flags any that are left.

Style in one breath: 5th-grade reading level, second person ("you will wire"), sentences of 20
words or fewer, define every term at first use, spell out every acronym at first use, numbered
lists for every hardware step, an analogy for every abstract idea, and gentle humor.
Mascot: at most 6 admonitions per page, welcome first, celebration last, never back to back, 1-3
sentences each, image inside the body (never the title bar). The mascot slots below are the
proven six: welcome, tip, warning, encourage, thinking, celebration.
Delete these HTML comments when you are done.
-->
# {{LESSON TITLE: what students DO or SEE, e.g. "Show Temperature and Humidity on a Colorful Display"}}

![{{REAL PHOTO ALT: describe what the photo shows in full sentences}}](./{{kit-photo.jpg}}){ width="640" }

*{{One or two sentences: what the real kit is and which part is the star.}}*

![{{SIMULATOR IMAGE ALT: describe the screen}}](./{{display-face.png}}){ width="360" }

*{{Honest caption: "This picture was drawn by a screen simulator, so your real screen may look a little different."}}*

!!! mascot-welcome "Welcome to the {{Name}} Lesson"
    ![Monty waving welcome](../../img/mascot/welcome.png){ class="mascot-admonition-img" }
    {{Two or three sentences saying what they will build. End with the catchphrase.}}

## What You Will Learn

After this lesson you will be able to:

1. {{Wire a sensor and a color screen to a Raspberry Pi Pico.}}
2. {{Test each part on its own before you put them together.}}
3. {{One math or science idea per item: pixels and x-y positions, unit conversion, percent...}}
4. {{Read a short program and explain what it does.}}
5. {{Change a setting and predict what will happen.}}

## Lesson at a Glance

| Item | Details |
|------|---------|
| Grade level | {{6th grade (about age 11)}} |
| Time needed | {{About 90 minutes for Steps 1 to 10. Two 45-minute periods works well}} |
| Difficulty | {{Beginner}} |
| The big idea | {{Why this kit is more than a boring sensor lab}} |
| You should already know | {{prerequisite, with a link to the textbook chapter}} |
| New ideas in this lesson | {{comma list}} |
| Help you need | {{grown-up helper for the upload step}} |

## Meet Your Parts

| Part | What it does | Think of it like |
|------|--------------|------------------|
| {{Part}} | {{One sentence. **Bold** each term you define here.}} | {{an analogy}} |

### Why a {{Display Name}}?

<!-- Say what the kit is NOT ("We are not building a smartwatch"), what the cheap display is FOR
     (a window on the sensor), the price ("about $5"), and 1-2 facts that make the sensor the star,
     taken from the datasheet and already used in the README. -->

### {{Concept explainers: What Is Humidity? / What Is a Pixel? / How Do the Parts Talk?}}

## Parts You Need

| Part | Notes |
|------|-------|
| {{part}} | {{price; what to look for; "any ... works"}} |

{{Which jumper wires? Explain male-to-female if any part has pins that stick out.}}

## Step 1: Wire the Sensor

{{How to find pin 1 and count pins. Explain names like GP0 the first time.}}

!!! mascot-tip "Monty's Tip"
    ![Monty giving a tip](../../img/mascot/tip.png){ class="mascot-admonition-img" }
    {{A time-saver, e.g. pin names are printed on the back of the Pico.}}

1. {{Unplug the Pico from the USB cable. Never wire a board that has power.}}
2. {{Push the Pico into the breadboard...}}
3. {{Connect sensor **VIN** (power in) to Pico **pin 36 (3V3 OUT)**...}}
4. {{One numbered step per wire, with the pin's meaning in brackets at first use.}}

| Sensor pin | Pico pin | Pico name | What it does |
|------------|----------|-----------|--------------|
| {{VIN}} | {{36}} | {{3V3 OUT}} | {{Power in}} |

!!! mascot-warning "Watch Out!"
    ![Monty warning](../../img/mascot/warning.png){ class="mascot-admonition-img" }
    {{The one mistake that damages parts (VBUS/5 V), and exactly how to avoid it.}}

## Step 2: Put the Code on the Pico

{{Define "upload". A grown-up helper runs upload-code.sh. Show the command in a bash block with
inline comments. Table of what gets copied. The count in "Uploaded N files" must match the real
number. Give a Thonny alternative in one sentence.}}

## Step 3: Test the Sensor

{{Checkpoint ladder: run lab 01, then lab 02, show the exact expected output for each.}}

```
{{exact expected output}}
```

**Checkpoint 1:** {{Do both say TEST PASS? If not, see Troubleshooting.}}

## Step 4: Wire the Display

<!-- Numbered steps, one per wire. Then the pin table. Then the mix-up warning (two parts with the
     same pin NAMES but different pins). Then the optional-pin note (BL backlight). Then the heat
     note if it matters. -->

## Step 5: Say Hello

{{Run the display hello lab. Explain x and y (y grows DOWN). Show the core code with an inline
comment on every non-obvious line, then "What Each Line Does", then the arithmetic as a puzzle
table (12 letters x 16 dots = 192 ...) that matches the lab's printed numbers.}}

**Checkpoint 2:** {{Can you read "Hello World!"? ...}}

## Step 6: Run the {{Sensor Display}}

{{Run the first real display lab. List what each part of the screen means (numbered).
Show the color table.}}

**Checkpoint 3:** {{Do you see numbers change when you breathe on the sensor?}}

## Step 7: Make It Stand Alone

{{main.py: a Pico runs it by itself. Steps: stop, close Thonny, unplug, phone charger, watch it start.}}

## Step 8: Science Time

<!-- Prediction / what happened / why table. Experiments must be SAFE: no water near electronics,
     nothing that makes students breathe hard (no breath races, no holding breath). -->

## Step 9: How the Code Works

!!! mascot-encourage "You Can Do This!"
    ![Monty encouraging](../../img/mascot/encouraging.png){ class="mascot-admonition-img" }
    {{Reading code feels like a new language. Normal. One small piece at a time.}}

<!-- Four "Pieces", ONE new idea each: a short code block with inline comments, a "what it does"
     table or numbered walk-through, and a worked example that matches the picture at the top.
     Put the thinking mascot on the deepest idea (e.g. why the screen never flickers). -->

## Step 10: Change a Setting

{{Numbered steps to change one number in config.py, "Predict first:", and the warning that
re-running the upload script resets it.}}

## Step 11: Add a Button and More Modes

<!-- Wire the button; test it with the button lab (expected output); show the mode grid picture;
     a controls table (tap / hold / long hold); the heartbeat LED; the color-gradient idea as a
     percent problem; "Try It" bullets. -->

## Challenges

<!-- 3-4, easy to hard. EVERY challenge must be solved and run in the simulator before you print it,
     and the hint must name the function or line to change. Stretch challenge: the performance
     trap (redraw only when the value changes). -->

## Troubleshooting

| What you see | What to try |
|--------------|-------------|
| {{symptom}} | {{fix}} |

## Check Your Understanding

??? question "1. {{question}} (Click to reveal the answer)"
    {{answer with the working shown}}

## Words to Know

| Word | What it means |
|------|---------------|
| {{term}} | {{definition in plain words}} |

!!! mascot-celebration "Great Work, Maker!"
    ![Monty celebrating](../../img/mascot/celebration.png){ class="mascot-admonition-img" }
    {{What they built and learned, then a call-forward to what they can build next.}}

## For Teachers

### Two-Period Plan

| Period | Time | Activity |
|--------|------|----------|
| 1 | {{5 min}} | {{Hook}} |

{{Which steps do not fit and how to use them.}}

### Before Class

1. {{install mpremote; test-upload one Pico; pre-load the rest; check jumper wires fit the display pins}}

### Common Trouble Spots

- {{the mix-ups you actually saw: same pin names on two parts, y grows down, what humidity means,
  main.py makes Thonny look stuck, loose button wires}}

### Check for Understanding

{{The one question that shows they understood, with the answer you want.}}

## Source Code

The whole kit lives in one folder, [`src/kits/{{kit-name}}/`]({{github url}}):

| File | What it does |
|------|--------------|
| `config.py` | Every pin number and setting, in one place |

## References

1. [{{Datasheet}}]({{url}}) - {{publisher}} - {{what it is for}}.
