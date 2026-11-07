#!/usr/bin/env python3
"""scratch_mkdocs_build.py -- build the MkDocs site into a scratch folder, without touching the repo.

    python3 scratch_mkdocs_build.py <repo_root> <scratch_dir> [--mkdocs /path/to/mkdocs]

Why not just `mkdocs build`? Two reasons that bit us:
  * the Material `social` plugin writes card images into <repo>/.cache, which dirties the repo
  * the repo's own `mkdocs serve` (which the user runs in their own terminal) must never be
    started, stopped or disturbed, and a normal build writes into ./site

This copies mkdocs.yml to <scratch_dir>/mkdocs-scratch.yml with the `social` plugin and any
`hooks:` block removed (the hook exists only for the social plugin), points docs_dir at the
repo's docs folder by absolute path, points site_dir at the scratch folder, builds quietly,
and reports the exit code and any warnings. Broken image paths and broken relative links show
up as warnings here.

Then look at the result: scripts/headless_shot.sh renders a built page to a PNG.
"""
import os, re, subprocess, sys, shutil


def find_mkdocs(argv):
    if "--mkdocs" in argv:
        return argv[argv.index("--mkdocs") + 1]
    for c in (shutil.which("mkdocs"),
              "/usr/local/Caskroom/miniforge/base/envs/mkdocs/bin/mkdocs",
              os.path.expanduser("~/miniforge3/envs/mkdocs/bin/mkdocs")):
        if c and os.path.exists(c):
            return c
    raise SystemExit("mkdocs not found. Pass --mkdocs /path/to/mkdocs (use the `mkdocs` conda env).")


def main(argv):
    if len(argv) < 3:
        raise SystemExit(__doc__)
    repo, scratch = os.path.abspath(argv[1]), os.path.abspath(argv[2])
    os.makedirs(scratch, exist_ok=True)
    src = open(os.path.join(repo, "mkdocs.yml")).read()

    out, skipping = [], False
    for line in src.split("\n"):
        if re.match(r"^\s*-\s+social\s*$", line):
            continue
        if line.startswith("hooks:"):
            skipping = True
            continue
        if skipping:
            if line.startswith("  - "):
                continue
            skipping = False
        if re.match(r"^(docs_dir|site_dir):", line):
            continue
        out.append(line)
    out.append("docs_dir: %s" % os.path.join(repo, "docs"))
    out.append("site_dir: %s" % os.path.join(scratch, "site"))
    cfg = os.path.join(scratch, "mkdocs-scratch.yml")
    open(cfg, "w").write("\n".join(out) + "\n")

    if "navigation.tabs" in src:
        print("NOTE: mkdocs.yml contains navigation.tabs. The user's rule is to NEVER use it. Tell them to remove it.")

    result = subprocess.run([find_mkdocs(argv), "build", "-q", "-f", cfg],
                            capture_output=True, text=True, cwd=repo)
    print("mkdocs build exit code:", result.returncode)
    text = (result.stdout + result.stderr).strip()
    print(text[:3000] if text else "(no warnings)")
    print("site written to:", os.path.join(scratch, "site"))
    return result.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv))
