#!/usr/bin/env python3
"""Render a CSS-animation HTML page to numbered PNG frames by seeking its timeline.

The page must animate with CSS @keyframes (or the Web Animations API) on one shared
loop. JavaScript timers (setInterval / requestAnimationFrame) are NOT captured: frames
are produced by setting animation.currentTime directly, so every animation is sampled
at an exact moment, independent of how fast the machine renders.

usage:
  render_frames.py PAGE.html --out DIR [--fps 30] [--secs 30] [--scale 1.5]
                   [--width 1280] [--height 720] [--workers 4] [--times 2,5,9.5]

  --times   comma-separated seconds: render only those moments (t_SS.SS.png), for
            contact sheets while iterating on the storyboard.

Frames go to DIR (use a temp directory, never the git repo). Elements with class
"no-video", ".pause-btn" or ".pause-input" are hidden so UI chrome stays out of the video.
Also accepts Design-canvas .dc.html pages (the x-dc wrappers are stripped).
"""
import argparse
import asyncio
import pathlib
import re
import sys

from playwright.async_api import async_playwright

HIDE_CSS = ".pause-btn,.pause-input,.no-video{display:none !important}"

LOAD_FONTS_JS = """
async () => {
  const seen = new Set();
  for (const el of document.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    seen.add(cs.fontWeight + ' 16px ' + cs.fontFamily);
  }
  await Promise.all([...seen].map(s =>
    document.fonts.load(s, 'AaBbCc0123456789:.,\\u00b0').catch(() => null)));
  await document.fonts.ready;
  return [...document.fonts].filter(f => f.status === 'loaded').length;
}
"""


def prepare(page_path: pathlib.Path, out_dir: pathlib.Path) -> pathlib.Path:
    src = page_path.read_text(encoding="utf-8")
    src = src.replace('<script src="./support.js"></script>', "")
    src = re.sub(r"</?x-dc>", "", src)
    src = re.sub(r"</?helmet>", "", src)
    src = re.sub(r'<script type="text/x-dc".*?</script>', "", src, flags=re.S)
    inject = f'<base href="{page_path.parent.resolve().as_uri()}/"><style>{HIDE_CSS}</style>'
    if "<head>" in src:
        src = src.replace("<head>", "<head>" + inject, 1)
    else:
        src = inject + src
    dst = out_dir / "_page.html"
    dst.write_text(src, encoding="utf-8")
    return dst


def frame_list(args):
    if args.times:
        return [(f"t_{float(t):05.2f}", float(t)) for t in args.times.split(",")]
    total = int(round(args.fps * args.secs))
    return [(f"f_{i:04d}", i / args.fps) for i in range(total)]


async def run_worker(ctx, url, frames, out_dir, info):
    page = await ctx.new_page()
    await page.goto(url, wait_until="networkidle")
    info["fonts"] = await page.evaluate(LOAD_FONTS_JS)
    info["animations"] = await page.evaluate(
        "document.getAnimations().forEach(a => a.pause()) || document.getAnimations().length"
    )
    for name, t in frames:
        await page.evaluate(
            "ms => document.getAnimations().forEach(a => { a.currentTime = ms; })", t * 1000
        )
        await page.screenshot(path=str(out_dir / f"{name}.png"))
    await page.close()


async def main(args):
    out_dir = pathlib.Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    page_file = prepare(pathlib.Path(args.page), out_dir)
    frames = frame_list(args)
    workers = max(1, min(args.workers, len(frames)))
    infos = [{} for _ in range(workers)]

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=args.scale,
        )
        await asyncio.gather(
            *[
                run_worker(ctx, page_file.as_uri(), frames[w::workers], out_dir, infos[w])
                for w in range(workers)
            ]
        )
        await browser.close()

    info = infos[0]
    print(f"fonts loaded: {info.get('fonts')}  animations seeked: {info.get('animations')}")
    if not info.get("animations"):
        print("WARNING: the page has no CSS animations; every frame will be identical.", file=sys.stderr)
    print(f"frames: {len(frames)} -> {out_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("page")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--secs", type=float, default=30)
    ap.add_argument("--scale", type=float, default=1.5)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--times", default="")
    asyncio.run(main(ap.parse_args()))
