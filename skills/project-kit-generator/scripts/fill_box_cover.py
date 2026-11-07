#!/usr/bin/env python3
"""fill_box_cover.py -- fill the box-cover template from a small JSON file and verify it.

    python3 fill_box_cover.py values.json out.html [--template path/to/box-cover-template.html]

values.json holds one entry per {{TOKEN}} in the template (without the braces), for example:

    {
      "PAGE_TITLE": "Mood Ring Thermometer - Box Cover",
      "TITLE": "Mood Ring Thermometer",
      "TAGLINE_HTML": "SHT40 Sensor Kit: Temperature &amp; Humidity<br>on a Colorful Display",
      "SUBTITLE": "Hands-On Coding Kit for Ages 10+",
      "LOGO_SRC": "brand-logo.jpg",          "LOGO_ALT": "The brand logo",
      "HERO_ART_SRC": "modes-rainbow.png",   "HERO_ART_ALT": "Five round screens ...",
      "PHOTO_SRC": "kit-photo.jpg",          "PHOTO_ALT": "The real kit on a breadboard ...",
      "FEATURE_1": "Wire It Up Yourself",    ...  up to "FEATURE_18": "...",
      "MASCOT_SRC": "../../docs/img/mascot/welcome.png", "MASCOT_ALT": "Monty waving hello",
      "BUBBLE_TEXT": "Let&rsquo;s build something amazing!",
      "SITE_URL": "example.github.io/my-book",
      "QR_SYMBOL_ID": "qr-kit", "QR_VIEWBOX": "0 0 41 41",
      "QR_ARIA": "QR code for the kit lesson", "QR_CAPTION": "Scan for the lesson",
      "QR_SYMBOL_BLOCK": "<paste the output of make_qr_symbol.py>"
    }

Image paths are relative to the OUTPUT html file. After filling, the script checks that
  * no {{ token is left,
  * every local <img src> file exists,
  * there are exactly 18 feature chips with text.
Exit code 1 if any check fails, so it is safe to use in a loop while you tune the copy.

Writing the copy (this is the part that needs judgment; the script cannot do it):
  * Name the kit for what students DO or SEE, not the part number ("Mood Ring Thermometer",
    not "SHT40 Temp Display Lab").
  * Chips are skills and thrills, 2-5 words each, mixing what they will learn ("Percent Math You
    Can See", "How Chips Talk to Each Other") with what they will make ("Buddy Shivers, Smiles &
    Sweats", "Finger Test: Reach 90F!"). Only claim what the kit really does.
  * The photo is the REAL kit (a phone photo is fine). Never a stock image or a listing shot.
"""
import json, os, re, sys


def main(argv):
    if len(argv) < 3:
        raise SystemExit(__doc__)
    values = json.load(open(argv[1]))
    out = os.path.abspath(argv[2])
    here = os.path.dirname(os.path.abspath(__file__))
    tpl = argv[argv.index("--template") + 1] if "--template" in argv else os.path.join(
        here, "..", "assets", "templates", "box-cover-template.html")
    text = open(tpl).read()
    for key, val in values.items():
        text = text.replace("{{%s}}" % key, str(val))

    problems = []
    left = sorted(set(re.findall(r"\{\{[A-Z_0-9]+\}\}", text)))
    if left:
        problems.append("unfilled tokens: %s" % ", ".join(left))
    base = os.path.dirname(out)
    for src in sorted(set(re.findall(r'<img[^>]*\ssrc="([^"]+)"', text))):
        if not src.startswith(("http", "data:")) and not os.path.exists(os.path.normpath(os.path.join(base, src))):
            problems.append("image not found (relative to the output file): %s" % src)
    chips = re.findall(r'<div class="feature">([^<]*)</div>', text)
    if len(chips) != 36 or any(not c.strip() for c in chips):      # 18 chips on each of the 2 covers
        problems.append("expected 18 non-empty feature chips per cover, found %d chips in total" % len(chips))

    open(out, "w").write(text)
    print("wrote", out)
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  -", p)
        return 1
    print("OK: no tokens left, every image exists, 18 chips per cover.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
