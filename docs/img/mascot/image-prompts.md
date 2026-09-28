# Chrono Image Prompts

Self-contained prompts for generating the seven Chrono poses. Paste the
opening instruction first, then one pose prompt at a time, into the same
image-generator conversation so the drawing style stays consistent.

Every prompt repeats the full base description from
[`character-sheet.md`](character-sheet.md). If the character sheet changes,
update every prompt below in the same edit.

After saving each image into this folder, trim the transparent padding:

```sh
python "$BK_HOME/src/image-utils/trim-padding-from-image.py" docs/img/mascot/POSE.png
```

## Opening Instruction

```
I am about to ask you to generate seven different poses for a book mascot.
Please use a consistent drawing style for all seven images.
```

## 1. Neutral — `neutral.png`

```
Please generate a new pose for Chrono the Robot.
A modern flat vector cartoon illustration of Chrono the Robot, a friendly
pedagogical mascot for a high school textbook about building clocks and
watches with MicroPython. Chrono is a small, rounded robot with a deep purple
body (#642580) and bright teal accents (#41BAC1). Chrono's head is a round
smartwatch display: a circular screen with a thin dark charcoal bezel and a
small silver watch crown on the right side. Chrono's face is drawn on the
screen in glowing teal lines. A short antenna with a glowing teal tip sits on
top of the head. The body is a rounded box with a small teal gear emblem on
the chest, two stubby arms with rounded mitten hands, and two short legs with
rounded feet. The character is compact and chunky, with the round head about
half of the total height, so it reads clearly at small icon size.
Style: modern flat vector cartoon, clean lines, bold simple shapes, flat color
with minimal shading, transparent background with alpha channel, suitable for
embedding in educational content. No text in image.

Chrono stands upright in a relaxed, neutral pose facing the viewer directly.
The screen face shows two large rounded eyes and a calm, friendly
closed-mouth smile. Both arms rest naturally at the sides with no specific
gesture. The pose is balanced and unassuming, suitable as a general-purpose
default illustration.

Please generate a new RGBA PNG image now with a fully transparent alpha-channel background.
The background MUST be fully transparent with an alpha channel.
DO NOT use a white, black or a checkered background.
```

## 2. Welcome — `welcome.png`

```
Please generate a new welcome pose for Chrono the Robot.
A modern flat vector cartoon illustration of Chrono the Robot, a friendly
pedagogical mascot for a high school textbook about building clocks and
watches with MicroPython. Chrono is a small, rounded robot with a deep purple
body (#642580) and bright teal accents (#41BAC1). Chrono's head is a round
smartwatch display: a circular screen with a thin dark charcoal bezel and a
small silver watch crown on the right side. Chrono's face is drawn on the
screen in glowing teal lines. A short antenna with a glowing teal tip sits on
top of the head. The body is a rounded box with a small teal gear emblem on
the chest, two stubby arms with rounded mitten hands, and two short legs with
rounded feet. The character is compact and chunky, with the round head about
half of the total height, so it reads clearly at small icon size.
Style: modern flat vector cartoon, clean lines, bold simple shapes, flat color
with minimal shading, transparent background with alpha channel, suitable for
embedding in educational content. No text in image.

Chrono is waving cheerfully with one raised hand, facing the viewer. The
screen face shows bright, happy eyes and a wide open smile. The pose says
"welcome" and "let's get started."

Please generate a new RGBA PNG image now with a fully transparent alpha-channel background.
The background MUST be fully transparent with an alpha channel.
DO NOT use a white, black or a checkered background.
```

## 3. Thinking — `thinking.png`

```
Please generate a new thinking pose for Chrono the Robot.
A modern flat vector cartoon illustration of Chrono the Robot, a friendly
pedagogical mascot for a high school textbook about building clocks and
watches with MicroPython. Chrono is a small, rounded robot with a deep purple
body (#642580) and bright teal accents (#41BAC1). Chrono's head is a round
smartwatch display: a circular screen with a thin dark charcoal bezel and a
small silver watch crown on the right side. Chrono's face is drawn on the
screen in glowing teal lines. A short antenna with a glowing teal tip sits on
top of the head. The body is a rounded box with a small teal gear emblem on
the chest, two stubby arms with rounded mitten hands, and two short legs with
rounded feet. The character is compact and chunky, with the round head about
half of the total height, so it reads clearly at small icon size.
Style: modern flat vector cartoon, clean lines, bold simple shapes, flat color
with minimal shading, transparent background with alpha channel, suitable for
embedding in educational content. No text in image.

Chrono has one hand on the chin of the round screen in a thoughtful pose.
The screen face shows eyes glancing up and to the side and a small, flat,
thoughtful mouth. A small glowing lightbulb floats above the antenna. The
pose suggests deep thinking and discovery.

Please generate a new RGBA PNG image now with a fully transparent alpha-channel background.
The background MUST be fully transparent with an alpha channel.
DO NOT use a white, black or a checkered background.
```

## 4. Tip — `tip.png`

```
Please generate a new tip pose for Chrono the Robot.
A modern flat vector cartoon illustration of Chrono the Robot, a friendly
pedagogical mascot for a high school textbook about building clocks and
watches with MicroPython. Chrono is a small, rounded robot with a deep purple
body (#642580) and bright teal accents (#41BAC1). Chrono's head is a round
smartwatch display: a circular screen with a thin dark charcoal bezel and a
small silver watch crown on the right side. Chrono's face is drawn on the
screen in glowing teal lines. A short antenna with a glowing teal tip sits on
top of the head. The body is a rounded box with a small teal gear emblem on
the chest, two stubby arms with rounded mitten hands, and two short legs with
rounded feet. The character is compact and chunky, with the round head about
half of the total height, so it reads clearly at small icon size.
Style: modern flat vector cartoon, clean lines, bold simple shapes, flat color
with minimal shading, transparent background with alpha channel, suitable for
embedding in educational content. No text in image.

Chrono is pointing upward with one hand as if sharing an important tip. The
screen face shows one eye winking and a knowing, helpful smile. A small
four-pointed star sparkles near the raised hand.

Please generate a new RGBA PNG image now with a fully transparent alpha-channel background.
The background MUST be fully transparent with an alpha channel.
DO NOT use a white, black or a checkered background.
```

## 5. Warning — `warning.png`

```
Please generate a new friendly warning pose for Chrono the Robot.
A modern flat vector cartoon illustration of Chrono the Robot, a friendly
pedagogical mascot for a high school textbook about building clocks and
watches with MicroPython. Chrono is a small, rounded robot with a deep purple
body (#642580) and bright teal accents (#41BAC1). Chrono's head is a round
smartwatch display: a circular screen with a thin dark charcoal bezel and a
small silver watch crown on the right side. Chrono's face is drawn on the
screen in glowing teal lines. A short antenna with a glowing teal tip sits on
top of the head. The body is a rounded box with a small teal gear emblem on
the chest, two stubby arms with rounded mitten hands, and two short legs with
rounded feet. The character is compact and chunky, with the round head about
half of the total height, so it reads clearly at small icon size.
Style: modern flat vector cartoon, clean lines, bold simple shapes, flat color
with minimal shading, transparent background with alpha channel, suitable for
embedding in educational content. No text in image.

Chrono holds up both hands, palms out, in a gentle "be careful" gesture. The
screen face shows concerned but caring eyes with slanted brows and a small
wavy mouth. The antenna tip glows amber instead of teal, and a small amber
exclamation-mark symbol floats beside the head.

Please generate a new RGBA PNG image now with a fully transparent alpha-channel background.
The background MUST be fully transparent with an alpha channel.
DO NOT use a white, black or a checkered background.
```

## 6. Encouraging — `encouraging.png`

```
Please generate a new encouraging pose for Chrono the Robot.
A modern flat vector cartoon illustration of Chrono the Robot, a friendly
pedagogical mascot for a high school textbook about building clocks and
watches with MicroPython. Chrono is a small, rounded robot with a deep purple
body (#642580) and bright teal accents (#41BAC1). Chrono's head is a round
smartwatch display: a circular screen with a thin dark charcoal bezel and a
small silver watch crown on the right side. Chrono's face is drawn on the
screen in glowing teal lines. A short antenna with a glowing teal tip sits on
top of the head. The body is a rounded box with a small teal gear emblem on
the chest, two stubby arms with rounded mitten hands, and two short legs with
rounded feet. The character is compact and chunky, with the round head about
half of the total height, so it reads clearly at small icon size.
Style: modern flat vector cartoon, clean lines, bold simple shapes, flat color
with minimal shading, transparent background with alpha channel, suitable for
embedding in educational content. No text in image.

Chrono gives a thumbs-up with one hand and leans slightly toward the viewer.
The screen face shows warm, gently curved eyes and a reassuring, supportive
smile. The pose radiates calm confidence and "you can do it" energy.

Please generate a new RGBA PNG image now with a fully transparent alpha-channel background.
The background MUST be fully transparent with an alpha channel.
DO NOT use a white, black or a checkered background.
```

## 7. Celebration — `celebration.png`

```
Please generate a new celebration pose for Chrono the Robot.
A modern flat vector cartoon illustration of Chrono the Robot, a friendly
pedagogical mascot for a high school textbook about building clocks and
watches with MicroPython. Chrono is a small, rounded robot with a deep purple
body (#642580) and bright teal accents (#41BAC1). Chrono's head is a round
smartwatch display: a circular screen with a thin dark charcoal bezel and a
small silver watch crown on the right side. Chrono's face is drawn on the
screen in glowing teal lines. A short antenna with a glowing teal tip sits on
top of the head. The body is a rounded box with a small teal gear emblem on
the chest, two stubby arms with rounded mitten hands, and two short legs with
rounded feet. The character is compact and chunky, with the round head about
half of the total height, so it reads clearly at small icon size.
Style: modern flat vector cartoon, clean lines, bold simple shapes, flat color
with minimal shading, transparent background with alpha channel, suitable for
embedding in educational content. No text in image.

Chrono is jumping with both arms raised high in celebration. The screen face
shows joyful eyes squeezed into happy upward arcs and a big open smile.
Small teal, purple, and gold confetti pieces and stars burst around the
character. Use saturated confetti colors, not pale ones.

Please generate a new RGBA PNG image now with a fully transparent alpha-channel background.
The background MUST be fully transparent with an alpha channel.
DO NOT use a white, black or a checkered background.
```
