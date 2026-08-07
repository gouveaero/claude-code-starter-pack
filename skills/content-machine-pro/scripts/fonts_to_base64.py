#!/usr/bin/env python3
"""
Build @font-face CSS with base64-embedded woff2, pulled from @fontsource via the
jsDelivr CDN. Embedding fonts as base64 (instead of a Google Fonts <link>) is what
makes the exported PNG render identically to the browser preview — headless Chromium
does not reliably fetch remote webfonts.

Embeds both `latin` and `latin-ext` subsets so PT-BR accents (ã, ç, é, õ...) render.

Usage:
    python fonts_to_base64.py "Barlow Condensed:900" "Plus Jakarta Sans:400,700,800"

Each arg is "Family Name:weight[,weight...]". Prints the CSS to stdout — paste it
into the <style> block of the carousel HTML. The CSS font-family name matches the
"Family Name" you pass, so reference it the same way in your CSS variables.

Family name -> @fontsource slug = lowercase, spaces -> hyphens
(e.g. "Barlow Condensed" -> "barlow-condensed").
"""
from __future__ import annotations  # so `bytes | None` works on Python 3.9

import base64
import sys
import urllib.request

CDN = "https://cdn.jsdelivr.net/npm/@fontsource/{slug}/files/{slug}-{subset}-{weight}-normal.woff2"
SUBSETS = ("latin", "latin-ext")


def slugify(family: str) -> str:
    return family.strip().lower().replace(" ", "-")


def fetch(url: str) -> bytes | None:
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return r.read()
    except Exception:
        return None


def face(family: str, weight: str) -> str:
    slug = slugify(family)
    srcs = []
    for subset in SUBSETS:
        data = fetch(CDN.format(slug=slug, subset=subset, weight=weight))
        if not data:
            continue
        b64 = base64.b64encode(data).decode("ascii")
        srcs.append(f"url(data:font/woff2;base64,{b64}) format('woff2')")
    if not srcs:
        print(f"  /* WARN: no files fetched for {family} {weight} (check slug '{slug}') */",
              file=sys.stderr)
        return ""
    # Multiple src lines (one per subset) are valid; the browser uses what it needs.
    src = ",\n       ".join(srcs)
    return (
        f"@font-face {{\n"
        f"  font-family: '{family}';\n"
        f"  font-style: normal;\n"
        f"  font-weight: {weight};\n"
        f"  font-display: block;\n"
        f"  src: {src};\n"
        f"}}\n"
    )


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    out = []
    for spec in sys.argv[1:]:
        if ":" not in spec:
            print(f"error: bad spec '{spec}', expected 'Family:weight'", file=sys.stderr)
            return 1
        family, weights = spec.rsplit(":", 1)
        for weight in weights.split(","):
            css = face(family.strip(), weight.strip())
            if css:
                out.append(css)
    sys.stdout.write("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
