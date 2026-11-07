#!/usr/bin/env python3
"""check_lesson.py -- check a student lesson page against the writing rules, mechanically.

    python3 check_lesson.py path/to/lesson.md [--acronyms USB,LED,SPI,...] [--max-words 20]

Checks (the rules in a typical CONTENT-GENERATION-GUIDELINES.md for a 10-year-old audience):
  HARD (exit code 1)
    * unfilled placeholders ({{...}}, TODO, XXX)
    * an image with no alt text, or a local image file that does not exist
    * more than 6 mascot admonitions, or two mascot admonitions back to back, or a
      mascot admonition longer than 3 sentences, or welcome not first / celebration not last
    * unbalanced code fences
  SOFT (warnings you should read)
    * words from the avoid list (initialize, utilize, implement ...)
    * prose sentences longer than --max-words (list items and paragraphs are separate
      chunks; `inline code` counts as one word)
    * an acronym whose first mention has no expansion nearby (a heuristic: look for
      "short for", "stands for", "means" or a parenthesis within 2 lines)
    * a "Wire ..." section that has no numbered list (hardware steps must be numbered)
It also prints the section list, prose word count and counts of checkpoints and quiz items,
so you can see the shape of the lesson at a glance.

This is a checker, not a judge: it cannot tell you whether the lesson is friendly.
"""
import re, sys, os

AVOID = ["initialize", "initializes", "instantiate", "subsequently", "utilize", "utilizes",
         "implement", "implements", "facilitate", "facilitates", "approximately"]
DEFAULT_ACRONYMS = ["USB", "LED", "SPI", "I2C", "SDA", "SCL", "GND", "VCC", "GPIO", "ADC", "PWM",
                    "RGB", "LCD", "OLED", "CSV", "CRC", "RST", "DC", "CS", "IDE"]


def strip_admonition_marker(line):
    return re.sub(r"^(\s*)(!!!|\?\?\?)\s+\S+\s*(\".*\")?", "", line)


def prose_chunks(lines):
    """Yield (line_number, text) chunks of student-facing prose: paragraphs and list items,
    skipping code fences, tables, headings, images and math."""
    chunk, start, fence, math = [], None, False, False

    def flush():
        nonlocal chunk, start
        if chunk:
            yield_list.append((start, " ".join(chunk)))
        chunk, start = [], None

    yield_list = []
    for i, raw in enumerate(lines, 1):
        st = raw.strip()
        if st.startswith("```"):
            flush(); fence = not fence; continue
        if fence:
            continue
        if st.startswith("\\["):
            flush(); math = True; continue
        if math:
            if st.startswith("\\]"):
                math = False
            continue
        if not st or st.startswith(("|", "![", "#", "<")):
            flush(); continue
        if re.match(r"^(!!!|\?\?\?)\s", st):
            flush(); continue
        if re.match(r"^(\d+\.|-)\s", st):
            flush(); start = i
            chunk.append(re.sub(r"^(\d+\.|-)\s+", "", st)); continue
        if not chunk:
            start = i
        chunk.append(st)
    flush()
    return yield_list


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    path = argv[1]
    max_words = int(argv[argv.index("--max-words") + 1]) if "--max-words" in argv else 20
    acr = DEFAULT_ACRONYMS
    if "--acronyms" in argv:
        acr = argv[argv.index("--acronyms") + 1].split(",")
    text = open(path).read()
    lines = text.split("\n")
    base = os.path.dirname(os.path.abspath(path))
    hard, soft = [], []

    # placeholders
    for i, l in enumerate(lines, 1):
        if re.search(r"\{\{|\bTODO\b|\bXXX\b", l):
            hard.append("line %d: unfilled placeholder: %s" % (i, l.strip()[:80]))

    # fences
    if sum(1 for l in lines if l.strip().startswith("```")) % 2:
        hard.append("unbalanced ``` code fences")

    # images: alt text and files
    for i, l in enumerate(lines, 1):
        for m in re.finditer(r"!\[([^\]]*)\]\(([^)\s]+)", l):
            alt, src = m.group(1).strip(), m.group(2)
            if not alt:
                hard.append("line %d: image with no alt text: %s" % (i, src))
            if not re.match(r"https?:", src) and not os.path.exists(os.path.normpath(os.path.join(base, src))):
                hard.append("line %d: image file not found: %s" % (i, src))

    # mascot rules
    mascots = []
    for i, l in enumerate(lines):
        m = re.match(r"^!!!\s+(mascot-[a-z]+)", l)
        if m:
            j, body = i + 1, []
            while j < len(lines) and (lines[j].startswith("    ") or not lines[j].strip()):
                if lines[j].strip() and not lines[j].strip().startswith("!["):
                    body.append(lines[j].strip())
                elif not lines[j].strip() and body:
                    break
                j += 1
            sentences = len([s for s in re.split(r"(?<=[.!?])\s+", " ".join(body)) if s.strip()])
            mascots.append((i + 1, m.group(1), j, sentences))
    if len(mascots) > 6:
        hard.append("%d mascot admonitions (limit 6)" % len(mascots))
    for a, b in zip(mascots, mascots[1:]):
        gap_lines = [l for l in lines[a[2]:b[0] - 1] if l.strip()]
        if not gap_lines:
            hard.append("mascot admonitions at lines %d and %d are back to back" % (a[0], b[0]))
    for ln, kind, _, n in mascots:
        if n > 3:
            hard.append("line %d: %s has %d sentences (limit 3)" % (ln, kind, n))
    if mascots:
        if mascots[0][1] != "mascot-welcome":
            hard.append("the first mascot admonition should be mascot-welcome (is %s)" % mascots[0][1])
        if len(mascots) > 1 and mascots[-1][1] != "mascot-celebration":
            soft.append("the last mascot admonition is %s, not mascot-celebration" % mascots[-1][1])

    # prose checks
    chunks = prose_chunks(lines)
    prose_words = 0
    for ln, chunk in chunks:
        chunk = strip_admonition_marker(chunk)
        plain = re.sub(r"`[^`]*`", "X", chunk)
        prose_words += len(plain.split())
        for w in AVOID:
            if re.search(r"\b%s\b" % w, plain, re.I):
                soft.append("line %d: avoid-list word '%s'" % (ln, w))
        for s in re.split(r"(?<=[.!?])\s+", plain):
            n = len(s.split())
            if n > max_words:
                soft.append("line %d: %d-word sentence: %s..." % (ln, n, s[:70]))

    # acronyms: first mention should be expanded nearby
    for a in acr:
        pat = re.compile(r"(?<![A-Za-z0-9])%s(?![A-Za-z0-9])" % re.escape(a))
        for i, l in enumerate(lines):
            code = l.strip().startswith(("```", "|")) and False
            if pat.search(l) and not l.lstrip().startswith(("#", "![")):
                window = " ".join(lines[i:i + 3]).lower()
                if not re.search(r"short for|stands for|means|\(|spelled", window):
                    soft.append("line %d: first mention of %s has no expansion nearby" % (i + 1, a))
                break

    # "Wire" sections need a numbered list
    for i, l in enumerate(lines):
        if re.match(r"^#{2,3}\s+.*\bWire\b", l):
            j = i + 1
            section = []
            while j < len(lines) and not re.match(r"^#{2,3}\s", lines[j]):
                section.append(lines[j]); j += 1
            if not any(re.match(r"^\s*\d+\.\s", s) for s in section):
                soft.append("line %d: '%s' has no numbered steps" % (i + 1, l.strip("# ")))

    # shape of the lesson
    heads = [re.sub(r"^#+\s+", "", l) for l in lines if re.match(r"^##\s", l)]
    print("Sections:", " | ".join(heads))
    print("Prose words (no code/tables): ~%d | checkpoints: %d | quiz items: %d | mascots: %s" % (
        prose_words, len(re.findall(r"\*\*Checkpoint", text)), len(re.findall(r"^\?\?\? question", text, re.M)),
        ", ".join(m[1].replace("mascot-", "") for m in mascots) or "none"))
    print("\nHARD problems: %d" % len(hard))
    for h in hard:
        print("  X", h)
    print("SOFT warnings: %d" % len(soft))
    for s in soft[:60]:
        print("  -", s)
    if len(soft) > 60:
        print("  ... and %d more" % (len(soft) - 60))
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
