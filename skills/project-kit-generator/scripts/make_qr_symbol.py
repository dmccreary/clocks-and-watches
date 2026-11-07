#!/usr/bin/env python3
"""make_qr_symbol.py -- make a QR code as an inline SVG <symbol> for the box cover.

    python3 make_qr_symbol.py https://example.github.io/my-book/kits/my-kit/ [--id qr-kit] [--border 2]

Prints an <svg width="0" height="0"> block holding one <symbol id="qr-kit"> (white square plus
black runs). Paste it once near the top of the cover's <body>, then draw the code as many
times as you like with:

    <svg class="qr" viewBox="0 0 N N" role="img" aria-label="QR code for the kit lesson">
      <use href="#qr-kit"/>
    </svg>

(the script prints the exact viewBox to use). One symbol used twice keeps the file small, and
the two covers on a sheet cannot drift apart.

Needs the `segno` library (pip install segno). Error correction is level M, so the code
still scans if a corner gets a smudge of glue.
"""
import sys

try:
    import segno
except ImportError:
    raise SystemExit("pip install segno")


def main(argv):
    if len(argv) < 2:
        raise SystemExit(__doc__)
    url = argv[1]
    sym_id = argv[argv.index("--id") + 1] if "--id" in argv else "qr-kit"
    border = int(argv[argv.index("--border") + 1]) if "--border" in argv else 2
    qr = segno.make(url, error="m")
    matrix = [list(row) for row in qr.matrix]
    n = len(matrix) + 2 * border

    runs = []
    for y, row in enumerate(matrix):
        x = 0
        while x < len(row):
            if row[x]:
                start = x
                while x < len(row) and row[x]:
                    x += 1
                runs.append("M%d,%dh%dv1h-%dz" % (start + border, y + border, x - start, x - start))
            else:
                x += 1
    print('<svg width="0" height="0" style="position:absolute" aria-hidden="true">')
    print('  <symbol id="%s" viewBox="0 0 %d %d">' % (sym_id, n, n))
    print('    <rect width="%d" height="%d" fill="#ffffff"/>' % (n, n))
    print('    <path fill="#0f172a" d="%s"/>' % "".join(runs))
    print("  </symbol>")
    print("</svg>")
    print("<!-- use with: viewBox=\"0 0 %d %d\" -->" % (n, n), file=sys.stderr)
    print("QR is %dx%d modules (+%d border). Print it at 0.8 inch or larger so phone cameras can read it."
          % (len(matrix), len(matrix), border), file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv)
