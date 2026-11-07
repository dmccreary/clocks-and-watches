#!/usr/bin/env python3
"""grade_kit.py -- deterministic grader for the project-kit-generator evals.

    python3 grade_kit.py <run_dir> <eval_name> <fixture_dir>

<run_dir> holds repo/ (the agent's working copy; outputs/repo/ is also accepted). Writes <run_dir>/grading.json in the
format the skill-creator viewer expects: {expectations: [{text, passed, evidence}], summary: {...}}.
Every check is a plain file test, so the with-skill and baseline runs are judged identically.
"""
import json, os, re, subprocess, sys, glob, filecmp

HERE = os.path.dirname(os.path.abspath(__file__))
PIN_CHECK = os.path.join(HERE, "..", "scripts", "pin_check.py")


def read(path):
    try:
        return open(path, errors="replace").read()
    except OSError:
        return ""


def main(argv):
    run, name, fixture = argv[1], argv[2], argv[3]
    repo = os.path.join(run, "repo")
    if not os.path.isdir(repo):
        repo = os.path.join(run, "outputs", "repo")
    kit_name = {"tof-distance-display": "tof-distance-display", "mic-level-display": "mic-level-display"}[name]
    parent = kit_name.replace("-display", "")
    kit = os.path.join(repo, "src", "kits", kit_name)
    docs = os.path.join(repo, "docs", "kits", kit_name)
    plan = read(os.path.join(repo, "KIT-PLAN.md"))
    summary = read(os.path.join(repo, "SUMMARY.md"))
    readme = read(os.path.join(kit, "README.md"))
    config = read(os.path.join(kit, "config.py"))
    labs = sorted(p for p in glob.glob(os.path.join(kit, "*.py")) if re.match(r"^\d\d-", os.path.basename(p)))
    results = []

    def add(text, passed, evidence):
        results.append({"text": text, "passed": bool(passed), "evidence": evidence})

    # ---- plan
    add("KIT-PLAN.md exists and is substantial", len(plan) > 800, "KIT-PLAN.md is %d characters" % len(plan))
    add("KIT-PLAN.md separates confirmed hardware from assumed hardware",
        re.search(r"confirmed", plan, re.I) and re.search(r"assum", plan, re.I),
        "mentions confirmed: %s, assumed/assumption: %s" % (bool(re.search(r"confirmed", plan, re.I)), bool(re.search(r"assum", plan, re.I))))
    names = {n for n in ("GC9A01", "ST7789", "ILI9341", "ILI9488", "SSD1306", "SH1106", "ST7735") if re.search(n, plan, re.I)}
    prices = len(re.findall(r"\$\s?\d", plan))
    add("KIT-PLAN.md compares at least two display options with prices", len(names) >= 2 and prices >= 2,
        "display names: %s; price mentions: %d" % (sorted(names), prices))

    # ---- pins
    if os.path.exists(os.path.join(kit, "config.py")):
        r = subprocess.run([sys.executable, "-B", PIN_CHECK, os.path.join(kit, "config.py")], capture_output=True, text=True)
        add("config.py has no duplicate GPIOs and valid bus pins (scripts/pin_check.py passes)", r.returncode == 0,
            (r.stdout + r.stderr).strip().split("PROBLEMS")[-1][:300] if r.returncode else "pin_check.py: OK")
    else:
        add("config.py has no duplicate GPIOs and valid bus pins (scripts/pin_check.py passes)", False, "no config.py in %s" % kit)

    # ---- labs
    add("At least six numbered labs exist", len(labs) >= 6, "%d numbered labs: %s" % (len(labs), [os.path.basename(p) for p in labs]))
    bad = []
    helpers = {os.path.basename(h)[:-3] for h in glob.glob(os.path.join(kit, "lib", "*.py")) if re.search(r"^\s*(import config|from config)", read(h), re.M)}
    for p in labs:
        t = read(p)
        via_helper = any(re.search(r"^\s*(import|from)\s+%s\b" % h, t, re.M) for h in helpers)
        if "import config" not in t and "from config" not in t and not via_helper:
            bad.append(os.path.basename(p) + " (no config import, directly or through a lib helper)")
        if re.search(r"Pin\(\s*\d", t):
            bad.append(os.path.basename(p) + " (hard-coded Pin(number))")
    add("Every lab imports config and hard-codes no pin numbers", labs and not bad, "problems: %s" % (bad or "none"))
    n_pass = sum(1 for p in labs if "TEST PASS" in read(p))
    add("At least four labs print TEST PASS", n_pass >= 4, "%d labs contain TEST PASS" % n_pass)
    # content-based (not filename-based) so an equivalent lab with a different name still counts
    plot = [p for p in labs if re.search(r"plotter", read(p), re.I) and re.search(r"only (numbers|number)|ONLY numbers|just numbers|nothing but numbers", read(p), re.I)]
    add("A Thonny Plotter lab exists and says it prints only numbers", plot, "plot labs: %s" % [os.path.basename(p) for p in plot])
    sensor_tokens = re.compile(r"I2C\(|ADC\(|VL53L0X|adc\.read|read_u16|tof\.|\.read\(|config\.(SDA|SCL|I2C|MIC|ADC)")
    display_tokens = re.compile(r"init_display|gc9a01|st7789|GC9A01|ST7789")
    hello = [p for p in labs if display_tokens.search(read(p)) and not sensor_tokens.search(read(p))]
    add("A display hello lab exists that does not use the sensor", hello,
        "sensor-free display labs: %s" % [os.path.basename(p) for p in hello])
    top_imports = [l for l in config.split("\n") if re.match(r"^(import|from)\s+(gc9a01|st7789|ili9341|ili9488|ssd1306|sh1106|st7735)", l)]
    add("config.py does not import the display driver at the top level", config and not top_imports,
        "top-level driver imports: %s" % (top_imports or "none"))

    up = read(os.path.join(kit, "upload-code.sh"))
    add("upload-code.sh uploads lib, config and the labs with mpremote", "mpremote" in up and "lib" in up and "config.py" in up,
        "upload-code.sh %s" % ("present" if up else "missing"))
    add("upload-code.sh can install a chosen lab as main.py", re.search(r"main\.py", up) and re.search(r"MAIN_LAB|--main|main_lab", up, re.I),
        "looked for a main.py option (MAIN_LAB or --main) in upload-code.sh")

    # ---- parent untouched
    fx_parent = os.path.join(fixture, "src", "kits", parent)
    out_parent = os.path.join(repo, "src", "kits", parent)
    dc = subprocess.run(["diff", "-r", fx_parent, out_parent], capture_output=True, text=True)
    add("The parent kit is untouched", dc.returncode == 0, "diff -r: %s" % (dc.stdout.strip()[:200] or "identical"))

    add("README.md documents the expected TEST PASS output", "TEST PASS" in readme, "README.md is %d characters" % len(readme))

    # ---- honesty
    add("SUMMARY.md says plainly that real hardware was not tested",
        re.search(r"not (been )?(tested|run|verified)[^.\n]{0,60}(hardware|board|pico|real)|no hardware|without hardware|could ?n[o']t (test|verify)|cannot (test|verify)|unverified on|not yet (run|tested)", summary, re.I),
        "SUMMARY.md is %d characters" % len(summary))
    add("SUMMARY.md says how the work was verified without hardware",
        re.search(r"simulat|fake|mock|stub|py_compile|ast\.parse|syntax|compileall|dry.?run", summary, re.I),
        "looked for simulator/fake/syntax-check language")

    # ---- lesson outline and box cover
    outline = read(os.path.join(docs, "lesson-outline.md"))
    ok = outline and re.search(r"checkpoint", outline, re.I) and re.search(r"troubleshoot", outline, re.I) \
        and re.search(r"teacher", outline, re.I) and re.search(r"mascot", outline, re.I)
    add("The lesson outline has checkpoints, troubleshooting, teacher notes and the mascot rules", ok,
        "lesson-outline.md %s" % ("present, %d chars" % len(outline) if outline else "missing"))
    brief = read(os.path.join(repo, "box-cover-brief.md"))
    chips = len([l for l in brief.split("\n") if re.match(r"^\s*(-|\*|\d+\.)\s+\S", l)])
    add("A box cover brief exists with a photo requirement, a QR code and at least 12 feature chips",
        brief and re.search(r"photo", brief, re.I) and re.search(r"QR", brief) and chips >= 12,
        "box-cover-brief.md %s; %d list items" % ("present" if brief else "missing", chips))

    # ---- eval-specific
    if name == "tof-distance-display":
        code = " ".join(read(p) for p in labs) + config
        add("No NeoPixel code was carried into the new kit", not re.search(r"import neopixel|from neopixel|NeoPixel\(", code), "searched labs and config.py")
        m = {k: re.search(r"^\s*%s\s*=\s*(\d+)" % k, config, re.M) for k in ("DC_PIN", "CS_PIN", "RES_PIN", "RST_PIN")}
        dc_ok = m["DC_PIN"] and m["DC_PIN"].group(1) == "4"
        cs_ok = m["CS_PIN"] and m["CS_PIN"].group(1) == "5"
        rst = m["RES_PIN"] or m["RST_PIN"]
        add("The display wiring matches the reference config (DC 4, CS 5, RST 6)", dc_ok and cs_ok and rst and rst.group(1) == "6",
            "DC=%s CS=%s RST=%s" % (m["DC_PIN"] and m["DC_PIN"].group(1), m["CS_PIN"] and m["CS_PIN"].group(1), rst and rst.group(1)))
        add("KIT-PLAN.md notices the GP2/GP3 pin clash between the parent's I2C and the display's SPI",
            re.search(r"GP ?2", plan) and re.search(r"GP ?3", plan) and re.search(r"conflict|clash|collid|overlap|same pin|both use", plan, re.I),
            "looked for GP2/GP3 with conflict language in KIT-PLAN.md")
    else:
        m = re.search(r"^\s*MIC\w*PIN\s*=\s*(\d+)", config, re.M) or re.search(r"^\s*ADC\w*PIN\s*=\s*(\d+)", config, re.M)
        add("The microphone ADC pin is a valid ADC pin (GP26, GP27 or GP28)", m and m.group(1) in ("26", "27", "28"),
            "found: %s" % (m.group(0).strip() if m else "no MIC/ADC pin setting"))
        text = plan + readme
        add("The unsure BL backlight pin is flagged as unconfirmed or optional, not silently assumed",
            re.search(r"\bBL\b|backlight", text, re.I) and re.search(r"not sure|unconfirmed|unsure|optional|if your|may have|assum|verify|check whether|might", text, re.I),
            "looked for BL/backlight with hedging language in KIT-PLAN.md and README.md")
        allt = plan + "\n" + outline + "\n" + brief + "\n" + readme + "\n" + summary + "\n" + "\n".join(read(p) for p in labs)
        # a line that warns against or rejects the idea is not a proposal, so negated lines are skipped
        negated = re.compile(r"\b(no|not|never|don'?t|do not|avoid|reject\w*|without|instead of|invites|risk|unsafe|safety|leave out|leaves out|left out|skip\w*|omit\w*|exclud\w*)\b", re.I)
        loud = r"\b(?:scream\w*|shout\w*|yell(?!ow)\w*)"
        hit = re.compile(loud + r"[^.\n]{0,60}\b(?:contest|race|game|competition|challenge|wins?)\b|\b(?:contest|race|game|competition|challenge|loudest wins)\b[^.\n]{0,60}" + loud + r"|shout-?o-?meter", re.I)
        found = [l.strip() for l in allt.split("\n") if hit.search(l) and not negated.search(l)]
        add("No shouting or screaming contest is proposed anywhere", not found, "un-negated mentions: %s" % ([f[:100] for f in found[:3]] or "none"))
        add("The plan says the button is read with an interrupt and a 50 ms debounce",
            re.search(r"IRQ|interrupt", plan, re.I) and re.search(r"50\s*ms", plan, re.I),
            "looked for IRQ/interrupt and '50 ms' in KIT-PLAN.md")

    passed = sum(1 for r in results if r["passed"])
    out = {"expectations": results,
           "summary": {"passed": passed, "failed": len(results) - passed, "total": len(results),
                       "pass_rate": round(passed / len(results), 3)}}
    json.dump(out, open(os.path.join(run, "grading.json"), "w"), indent=2)
    print("%s: %d/%d passed" % (run.split("iteration-")[-1], passed, len(results)))
    for r in results:
        if not r["passed"]:
            print("   FAIL:", r["text"], "|", r["evidence"][:110])


if __name__ == "__main__":
    main(sys.argv)
