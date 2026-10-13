"""Render Upwork portfolio thumbnails (1200x900) from HTML with Playwright.

Usage: python render_thumbs.py <out_dir>
Produces izz-pipeline.jpg and pdf-batch-excel.jpg. Facts on the cards come from the
repositories (counted on 2026-10-13): izz-ro SOURCES=93, hourly cron, 34 workflows,
1,659 test functions; pdf-batch-excel statuses ok / needs_ocr / error.
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1200px; height: 900px; font-family: 'DejaVu Sans', Arial, sans-serif;
       background: #0f1720; color: #e9eef5; padding: 72px 72px 110px; position: relative; overflow: hidden;
       display: flex; flex-direction: column; justify-content: center; }
.kicker { font-size: 26px; letter-spacing: 3px; text-transform: uppercase; color: #6fd3a8; }
h1 { font-size: 72px; line-height: 1.08; margin: 18px 0 22px; font-weight: 700; }
.sub { font-size: 30px; color: #a9b8c9; }
.flow { display: flex; flex-wrap: wrap; align-items: center; gap: 14px; margin-top: 60px; }
.node { background: #18232f; border: 2px solid #2b3b4c; border-radius: 18px; padding: 18px 20px;
        font-size: 24px; font-weight: 600; white-space: nowrap; }
.arrow { font-size: 30px; color: #6fd3a8; }
.chips { display: flex; flex-wrap: wrap; gap: 16px; margin-top: 60px; }
.chip { background: #13202b; border: 1px solid #2b3b4c; border-radius: 999px; padding: 14px 24px;
        font-size: 25px; color: #cfe0ee; }
.chip b { color: #ffffff; }
.foot { position: absolute; left: 72px; bottom: 56px; font-size: 22px; color: #6f8396; }
"""

IZZ = f"""<html><head><style>{BASE_CSS}</style></head><body>
<div class="kicker">Python · GitHub Actions · Cloudflare</div>
<h1>Automated news pipeline</h1>
<div class="sub">Ingestion, clustering and AI summaries, running every hour</div>
<div class="flow">
  <div class="node">93 sources</div><div class="arrow">→</div>
  <div class="node">dedupe + cluster</div><div class="arrow">→</div>
  <div class="node">AI summary + checks</div><div class="arrow">→</div>
  <div class="node">static site</div>
</div>
<div class="chips">
  <div class="chip"><b>34</b> automated workflows</div>
  <div class="chip"><b>1,659</b> automated tests</div>
  <div class="chip">monitoring + failover</div>
  <div class="chip">free-tier hosting</div>
</div>
<div class="foot">github.com/Ramanul/izz-ro</div>
</body></html>"""

PDF = f"""<html><head><style>{BASE_CSS}
.grid {{ display: grid; grid-template-columns: repeat(4, 150px); gap: 8px; }}
.cell {{ height: 44px; background: #18232f; border: 1px solid #2b3b4c; border-radius: 6px; }}
.cell.h {{ background: #1f3a2e; border-color: #2f6b52; }}
.row {{ display: flex; align-items: center; gap: 40px; margin-top: 60px; }}
.doc {{ width: 120px; height: 156px; border-radius: 12px; background: #e9eef5; color: #0f1720;
        display: flex; align-items: flex-end; justify-content: center; padding-bottom: 18px;
        font-size: 26px; font-weight: 700; }}
.st {{ display: inline-block; border-radius: 10px; padding: 10px 18px; font-size: 24px; font-weight: 700; margin-right: 12px; }}
.ok {{ background: #1f3a2e; color: #7fe0b2; }} .ocr {{ background: #3a331f; color: #f0cf7a; }} .err {{ background: #3a1f24; color: #f39aa5; }}
</style></head><body>
<div class="kicker">Python · Windows · Excel</div>
<h1>PDF to Excel, in batch</h1>
<div class="sub">One workbook for a whole folder, with an explicit error report</div>
<div class="row">
  <div class="doc">PDF</div><div class="doc">PDF</div><div class="doc">PDF</div>
  <div class="arrow">→</div>
  <div class="grid">
    <div class="cell h"></div><div class="cell h"></div><div class="cell h"></div><div class="cell h"></div>
    <div class="cell"></div><div class="cell"></div><div class="cell"></div><div class="cell"></div>
    <div class="cell"></div><div class="cell"></div><div class="cell"></div><div class="cell"></div>
  </div>
</div>
<div style="margin-top:56px">
  <span class="st ok">ok</span><span class="st ocr">needs_ocr</span><span class="st err">error</span>
  <span class="sub" style="font-size:24px">every file accounted for, nothing silently dropped</span>
</div>
<div class="foot">github.com/Ramanul/nishiai-apps · formula-safe cells · hot-folder mode</div>
</body></html>"""


def main(out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1200, "height": 900})
        for name, html in (("izz-pipeline", IZZ), ("pdf-batch-excel", PDF)):
            page.set_content(html, wait_until="load")
            page.screenshot(path=str(out / f"{name}.jpg"), type="jpeg", quality=80)
        browser.close()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
