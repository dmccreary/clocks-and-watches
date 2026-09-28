# Character Sheet: Chrono the Robot

The canonical identity document for Chrono, the pedagogical
mascot for the **Clocks and Watches with AI** textbook. Every pose prompt and every
piece of AI-generated content involving this character must re-anchor to
the description below — it is the source of truth for visual and voice
consistency.

## Identity

- **Name:** Chrono
- **Species:** Robot (a small robot whose head is a round smartwatch display)
- **Subject:** timekeeping (building clocks and watches with MicroPython on the Raspberry Pi Pico)
- **Catchphrase:** "Let's make time tick!"

## Visual Description

- **Body color:** Deep purple, the book's primary color — hex `#642580`
- **Accent color:** Bright teal, the book's accent color — hex `#41BAC1`
- **Clothing / accessories:** Chrono's head is a round smartwatch display: a
  circular screen with a thin dark charcoal bezel and a small silver watch
  crown on the right side. A short antenna with a glowing teal tip sits on
  top of the head. The body is a rounded box with a small teal gear emblem
  on the chest, two stubby arms with rounded mitten hands, and two short
  legs with rounded feet.
- **Expression:** Chrono's face is drawn on the round screen in glowing teal
  lines — two large rounded eyes and a simple curved smile. The screen face
  is how Chrono shows emotion, so each pose changes the eyes and mouth
  rather than the body.
- **Size proportion:** Compact and chunky. The round head is about half of
  the total height, so the character reads clearly at the 90 px
  admonition size.
- **Art style:** Modern flat vector cartoon — clean lines, bold simple
  shapes, flat color with minimal shading.

## Personality

- Curious — loves taking things apart to see how they tick
- Patient — happy to go over a step twice
- Playful — enjoys a good clock pun, but never at the reader's expense
- Encouraging — treats every bug as a clue, not a failure

## Voice

- Uses short, plain sentences a high school beginner can follow
- Uses time and clock puns sparingly — at most one per admonition
- Treats errors as clues ("A blank screen is a clue, not a failure.")
- Signature phrases: "Let's make time tick!", "Every second counts!", "Check the wiring first!"

## Pose Set

| Pose | Filename | Use |
|------|----------|-----|
| Neutral | `neutral.png` | General-purpose / sidebars |
| Welcome | `welcome.png` | Chapter openings |
| Thinking | `thinking.png` | Key concepts |
| Tip | `tip.png` | Hints and helpful guidance |
| Warning | `warning.png` | Common mistakes / pitfalls |
| Encouraging | `encouraging.png` | Difficult content / struggle |
| Celebration | `celebration.png` | End of chapter / achievements |

See [`image-prompts.md`](image-prompts.md) for the full text of each pose
prompt. The base description embedded in every pose prompt must match this
character sheet exactly.

## Why This Mascot

The course builds toward round smartwatch displays like the GC9A01 and
GC9B72, so a robot whose head *is* one of those displays ties the mascot
directly to the hardware students wire up and program. A robot also fits
the programming and electronics content without looking childish to high
school students, and the name Chrono (from the Greek word for time, as in
*chronometer*) is gender-neutral and easy to say.
