#!/usr/bin/env python3
"""
Export each slide of a Content Machine carousel HTML to a native 1080x1350 PNG.

Screenshots the `.slide` ELEMENT (never the viewport) so each PNG is exactly
1080x1350 with no clip/scale/resize — the same trick the original system uses.
Waits on document.fonts.ready so embedded @font-face fonts render before capture.

Usage:
    python export_png.py <html_path> [output_dir]

Defaults output_dir to "<html_dir>/slides".

Requires Playwright + Chromium:
    pip install playwright && python -m playwright install chromium
    # or: npx playwright install chromium  (if using the node CLI elsewhere)
"""
import os
import sys


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: export_png.py <html_path> [output_dir]", file=sys.stderr)
        return 1

    html = os.path.abspath(sys.argv[1])
    if not os.path.isfile(html):
        print(f"error: HTML not found: {html}", file=sys.stderr)
        return 1

    out = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(html), "slides")
    os.makedirs(out, exist_ok=True)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        # device_scale_factor=1 => CSS px map 1:1, so a 1080x1350 .slide -> 1080x1350 px
        page = browser.new_page(
            viewport={"width": 1200, "height": 1400}, device_scale_factor=1)
        page.goto(f"file://{html}", wait_until="networkidle")

        # Force full-size capture even if the HTML opens in side-by-side preview mode,
        # and hide preview-only chrome (toggle button, Instagram mockup frame).
        page.evaluate(
            "() => {"
            "  document.querySelectorAll('.slide').forEach(s => s.classList.remove('preview-mode'));"
            "  document.querySelectorAll('.ig-frame, [data-preview-only]').forEach(e => e.style.display='none');"
            "}"
        )

        # Wait for embedded fonts to actually load — never trust a bare timeout.
        page.wait_for_timeout(2000)
        page.evaluate("() => document.fonts.ready")
        page.wait_for_timeout(2000)

        slides = page.locator(".slide")
        count = slides.count()
        if count == 0:
            print("error: no .slide elements found in HTML", file=sys.stderr)
            browser.close()
            return 1

        for i in range(count):
            slide = slides.nth(i)
            slide.scroll_into_view_if_needed()
            page.wait_for_timeout(300)
            slide.screenshot(path=os.path.join(out, f"slide_{i + 1:02d}.png"))

        browser.close()

    print(f"exported {count} slides -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
