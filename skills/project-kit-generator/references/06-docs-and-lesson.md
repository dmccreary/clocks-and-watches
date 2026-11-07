# 06. Documentation: the kit README and the student lesson

Two documents, kept in step: `src/kits/<kit>/README.md` (build and maintain the kit) and
`docs/kits/<kit>/index.md` (the friendly lesson a 10-12 year old follows). Templates:
`assets/templates/kit-readme-template.md` and `assets/templates/lesson-template.md`.

## Read the guidelines first

If the repo has a `CONTENT-GENERATION-GUIDELINES.md` (learning-micropython does), read it **before writing a
word a student will read**. On the SHT40 kit this was skipped, the README was written in the parent README's
tone, and the gaps (unspelled acronyms, wiring as a table without numbered steps, one lab teaching too much)
were only found afterwards. The rules that mattered:

- 5th-grade reading level; sentences of 20 words or fewer; active voice; second person.
- Define every technical term the first time; spell out every acronym at first use (SPI = Serial Peripheral
  Interface; a pin label like CS = Chip Select gets its meaning in the wiring list, not only in the table below it).
- Concrete analogies (a sponge for humidity, a road and a highway for I2C and SPI, a spring for a pull-up).
- Hardware steps are **numbered lists**, never prose. A table alone is not enough.
- Every code block has an inline comment on each non-obvious line, followed by a "what each line does" table or
  numbered walk-through. One new concept per example.
- Avoid words: initialize, instantiate, subsequently, utilize, implement, facilitate, approximately.
- Prices are plain `$5`; math is `\( ... \)` and `\[ ... \]`, never `$...$`.
- Alt text describes what the image shows.
- Mascot (Monty): **at most 6 admonitions**, welcome first, celebration last, never back to back, 1-3 sentences,
  image inside the body, no gendered pronouns. Slots that worked: welcome (top), tip (finding pins), warning (VBUS),
  encourage (start of "how the code works"), thinking (the deepest idea), celebration (the end).

Then run `scripts/check_lesson.py lesson.md`. It flags hard errors (placeholders, images without alt text or a file,
mascot rules, unbalanced fences) and soft ones (avoid-list words, long sentences, unexplained acronyms, wiring
sections without numbered steps). Read the soft list; it over-reports on list items, so use judgment.

## The lesson, section by section

| Section | Job |
|---------|-----|
| Photo, then simulator picture, honest captions | the first thing a student sees is the real kit |
| Welcome (mascot) | what you will build in 3 sentences |
| What You Will Learn | 5-8 outcomes: wire, test each part, one math/science idea each, read code, change a setting |
| Lesson at a Glance | grade, time, difficulty, "The big idea", prerequisites (linked), new ideas, help needed |
| Meet Your Parts (+ "Why a ... Display?") | analogy table; say what the kit is NOT; the price of the cheap display; the sensor's best facts |
| Parts You Need | with prices; which jumper wires |
| Steps | one part or one idea per step, each ending in a **Checkpoint** |
| Science Time | prediction / what happened / why, with safe experiments only |
| How the Code Works | four "Pieces", one idea each, code + explanation + a worked example that matches the picture |
| Change a Setting | edit one number in config.py, predict first, warn that re-uploading resets it |
| Extension step | the button and modes; wiring, test lab, mode grid picture, controls table |
| Challenges | 3-4, easy to hard, **each one tested** (below) |
| Troubleshooting | symptom / fix table, extended every time hardware shows a new symptom |
| Quiz | 6-8 collapsible questions with working shown |
| Words to Know | every term defined in the lesson |
| For Teachers | two-period plan, before-class list, common trouble spots, check for understanding |
| Source Code, References | file table with the real file names, 4-5 sources with a line on why |

Checkpoints are the heart of the "test each part" habit: sensor first, then the display alone, then both.
If something fails later, the student already knows which part is fine.

## Numbers that must match the code

Copy, never invent: expected console output, "Uploaded N files" (count `lib/*.py` + config + labs + main.py), file
lists, pin tables, thresholds (65/78/90), pixel arithmetic, the number of quiz questions in the teacher notes,
line counts ("the full program is 273 lines"). When code changes, grep the lesson and README for the old value.

## Math and science ties that land with this age

Celsius to Fahrenheit (with the picture's own numbers: 22.5 x 9 / 5 + 32 = 72.5), percent of a bar (120 px x 48.2 %
= 57 dots), centring arithmetic (12 x 16 = 192, half is 96, 120 - 96 = 24), position along a colour line
(50 to 95 F: 72.5 is 0.5), relative humidity as a sponge, the y axis pointing down. Each is a worked example a
student can check against the screen.

## Challenges must be solvable

Before printing a challenge, apply the described change to a **scratch copy** of the lab and run it in the simulator
(the SHT40 challenges were tested this way: yellow ring, Celsius as the big number, mood words for humidity, a ring that
follows the temperature). The stretch challenge should teach a real cost: redrawing a 900-call ring every second is
slow, so "only redraw when the colour changes" (and the hint about `global`). Give a hint that names the function or line.

## Pictures

- **Simulator pictures** (`scripts/simlib.py: round_rgba, grid`) are transparent round images: one for the top of the
  lesson, one per lab state you explain (hello, colour bands, sensor failure), one grid of all modes, one grid of the
  character's moods. Caption them honestly: "drawn by a screen simulator, so your real screen may look a little
  different".
- **The real photo** comes from the user. Use it at the top with a full alt text describing everything visible. A phone
  photo is 1-4 MB; offer a smaller copy for the page.
- Never say a picture is a photo when it is a render. Replace renders with photos when you get them.
- Alt text: what the image shows, including the numbers on the screen.
- If the user adds an image, run `check_lesson.py`; it will tell you about a missing alt text. Report it; do not edit
  their addition unasked.

## Reframing the kit honestly

When the user clarifies what the kit is ("we are not building a smartwatch, we are using a $5 smartwatch display to see
the sensor"), change the **text everywhere a student reads it**: lesson title and intro, headings ("Run the Sensor Display"),
step text, table cells, alt texts, quiz and glossary, teacher notes, README, printed messages and comments in the labs,
and displayed names (the first mode "Watch" became "Classic"). Then grep for the old word and keep only the intentional
ones (verbs, "made for smartwatches", identifiers, file names). Ask before renaming **files and code identifiers**: that
touches the upload script, links, images and tests.

## MkDocs

- Put the page at `docs/kits/<kit>/index.md` with its images beside it. Relative image paths: `./image.png`.
- Add a nav entry under Kits in `mkdocs.yml` only when asked (that file often has the user's uncommitted edits); show
  the two lines you would add. **Never add `navigation.tabs`**; if you see it, tell the user to remove it.
- Verify with `scripts/scratch_mkdocs_build.py` (a repo-clean build: the social plugin writes `.cache`) and look at the
  page with `scripts/headless_shot.sh`. **Never start or stop `mkdocs serve`**: the user runs it in their own terminal.
- After the build, count: mascot admonitions (6), quiz blocks, math blocks, images that resolved.
- Link to sibling lessons and textbook chapters with relative paths and confirm they exist.

## Keep the docs alive

Hardware findings change docs: a debounce rule, a new troubleshooting row, an expected output line that gained a message,
the count of uploaded files. After every change to the kit, list what in the README and lesson quotes it, and update both.
