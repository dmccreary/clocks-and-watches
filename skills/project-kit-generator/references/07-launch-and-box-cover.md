# 07. Launch: session log, memory, the box cover, and committing

The kit is not finished when the code passes. It is finished when someone can find it on a shelf, build it, and trust the
notes about it.

## Reporting back (every turn)

End each turn with a short message in this order, and keep it plain:

1. **What now exists** (three lines at most) and whether it was run on real hardware.
2. **What was verified, how** (simulator scenarios, tests), and **what was not** (real timing, memory, the interrupt on
   the board). If the user has since run something, state exactly what their output proves and what it does not.
3. **Choices you made that they may want to change** (mode order, what `main.py` runs, timings, what you did not rename).
4. **The short checklist of things only they can check** (05-verification.md).
5. **What you did not do** (commit, upload, edit their files) and offer the next step.

Do not over-claim. "All tests pass" means the simulator; say so.

## The session log (`logs/<kit>-generation.md`)

Template: `assets/templates/session-log-template.md`. It records the prompts verbatim, a timeline, the facts the design
depends on, **every design decision with its reason and the alternative**, the files, the verification (with a "what this does
not prove" list), the mistakes and their fixes, a guideline check, and the loose ends. Write it when asked and update it when
the kit changes; if the user edits it, treat their version as current and do not revert it. Mention any place it is now out of
date rather than rewriting history.

The mistakes section is the most valuable part for the next kit. Examples worth keeping: a rule read too late, a comment that
claimed the wrong string length, a simulator that dropped files into the kit, an assumption about hardware that was wrong.

## Memory

Save **durable user preferences** as memory files (they will apply to the next kit), not facts the repo already records:

- rules the user states ("always use an IRQ for buttons, 50 ms debounce"),
- safety choices ("no activities that make students hyperventilate"),
- corrections ("do not assume the kit has a NeoPixel; ask"),
- setup facts that are not in the code (plain Pico, MicroPython v1.29.0).

One fact per file, a one-line index entry each, and check for an existing memory first.

## The box cover

A printable cover (6 x 4 inch, two per Letter sheet) turns a kit into a product: a bin of unlabelled boxes all look the same, a bin
with covers lets a student find the kit from across the room. It is also where the fun name, the real photo and the simulator art
pay off.

Assets go in `artwork/<brand>/` (the SHT40 kit uses `artwork/thinking-spot/`):

| File | What it is |
|------|------------|
| `<kit>-kit-photo.jpg` | a REAL photo of the assembled kit (ask the user; never a stock or listing image) |
| `<kit>-<character>-rainbow.png` | a strip of 5 round screens in their moods (cold blue to hot red), rendered by the simulator (`round_rgba` + `grid`, 5 columns) |
| `<brand>-logo.jpg` | the brand logo, if the user has one |
| `<kit>-box-cover.html` | the printable cover |

Steps:

1. Ask for the photo, the brand name/logo (or "none"), the audience line, and the lesson URL. Confirm the fun **title**.
2. Render the hero strip from the simulator (five states of the most expressive mode).
3. Write the copy (the part that needs judgment):
   - **Title** = what students do or see ("Mood Ring Thermometer"); **tagline** = sensor and display in plain words;
     **subtitle** = audience ("Hands-On Coding Kit for Ages 10+").
   - **18 chips** (2-5 words each): mix what they LEARN ("Pixels & X-Y Coordinates", "Celsius to Fahrenheit Math", "Percent
     Math You Can See", "How Chips Talk to Each Other", "Think Like a Scientist") with what they MAKE and DO ("6 Colorful Display
     Modes", "Buddy Shivers, Smiles & Sweats", "Finger Test: Reach 90 F!", "Records That Survive Unplugging"), plus the promises ("No
     Soldering Required", "Wire It Up Yourself", "Free Online Textbook & Quizzes"). Only claim what the kit does.
   - Mascot (Monty) with the bubble "Let's build something amazing!", the site URL, and a QR code.
4. QR: `python3 scripts/make_qr_symbol.py <lesson-url> --id qr-kit` and paste the output into `QR_SYMBOL_BLOCK`. It is drawn once and
   reused on both covers. Print at 0.75 inch or larger; error level M survives a smudge of glue.
5. Fill the template: `python3 scripts/fill_box_cover.py values.json <out>.html`. It fails if a token is left, an image is missing
   or the chips are not 18 + 18. Image paths are relative to the OUTPUT file (use `../../docs/img/mascot/welcome.png` style paths if the
   cover lives in `artwork/`).
6. **Look at it**: `scripts/headless_shot.sh cover.html cover.png 800 1100` and open the PNG. Check the title fits, the chips do not wrap,
   the photo frame shows the display, and the QR is crisp. Scan the QR with a phone if you can.
7. Optional print guide page `docs/kits/<kit>/box-cover/index.md` (as the plain SHT40 kit has): open the HTML, click Print, **Letter, Portrait,
   Scale 100% (not "Fit to printable area"), Background graphics on**, cut along the dashed line. Add the nav entry only when asked.

There is also a sibling skill, `kit-box-cover-generator` (in the robot-faces repo), with a different house style and a `{{PLACEHOLDER}}`
template. Use it when the user wants the robot-faces family look; otherwise use this one and say which you used.

## Committing and pushing

Only commit or push when the user asks (they may say "when done, do a git commit and push"). Then:

- Stage **only the files this task created** (`git add <paths>`, never `git add -A`); the working tree usually holds the user's other
  uncommitted work (docs, mkdocs.yml, the kit itself). Show them what was left out and offer a second commit.
- Follow the repo's message style; one subject line under 72 characters and a short body saying why. Add the attribution lines the
  session asks for.
- Check the branch and the remote before pushing. Report the commit hash and that the push succeeded.
- "Publish" in the user's own vocabulary means: add, commit, push **and** `mkdocs gh-deploy`. Do not deploy unless they say publish.

## After the kit ships

Add what you learned to this skill (a new display, a new sensor idea, a new mistake). The skill is the memory of the next kit's mistakes.
