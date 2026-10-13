"""End-to-end check + Chrome Web Store screenshots for the two NISHIAI extensions.

Run (Linux, needs a display for extensions):  xvfb-run -a python store/make_screenshots.py

What it does
  1. Serves store/demo/ on 127.0.0.1:8765.
  2. Loads each unpacked extension in Chromium (Playwright) and exercises it on the demo page:
       - Table Exporter: builds the CSV for the page's tables and downloads it; checks the BOM,
         that plain numbers (-0.8%, +6.7%) stay numbers and that formula-like cells are neutralised.
       - Consent Decliner: with the extension off the banner stays; after switching it on in the
         popup and reloading, the page records "rejected" (the Accept button is never clicked).
  3. Composes 1280x800 screenshots and 440x280 promo tiles into store/assets/<extension>/.

Exit code 1 if any check fails. Raw captures go to a temporary folder, not to the repo.

Note: the popup is opened as an extension page and fed the demo page's tables through its
built-in test hook (?tables=...), because Chrome only grants activeTab after a real toolbar click.
The CSV logic and the download path are the production code.
"""
from __future__ import annotations

import base64
import csv
import functools
import http.server
import io
import json
import sys
import tempfile
import threading
import time
import urllib.parse
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DEMO = ROOT / "store" / "demo"
ASSETS = ROOT / "store" / "assets"
EXT = ROOT / "chrome-extensions"
PORT = 8765
FAILS: list[str] = []


def check(cond: bool, msg: str) -> None:
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


def serve_demo() -> http.server.ThreadingHTTPServer:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DEMO))
    handler.log_message = lambda *a, **k: None  # type: ignore[assignment]
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def data_uri(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def ext_context(p, ext_dir: Path, profile: Path):
    ctx = p.chromium.launch_persistent_context(
        str(profile), headless=False, accept_downloads=True,
        viewport={"width": 1280, "height": 800},
        args=[f"--disable-extensions-except={ext_dir}", f"--load-extension={ext_dir}"],
    )
    sw = ctx.service_workers[0] if ctx.service_workers else ctx.wait_for_event("serviceworker", timeout=15000)
    return ctx, sw.url.split("/")[2]


def run_table_exporter(p, raw: Path) -> None:
    ctx, ext_id = ext_context(p, EXT / "table-exporter", raw / "profile-te")
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{PORT}/tables.html")
    page.screenshot(path=str(raw / "te-page.png"))
    tables = page.evaluate(
        "[...document.querySelectorAll('table')].map(t => [...t.rows].map(r => "
        "[...r.cells].map(c => c.innerText.replace(/\\s+/g,' ').trim())))"
    )
    q = urllib.parse.quote(json.dumps(tables))
    popup = ctx.new_page()
    popup.set_viewport_size({"width": 304, "height": 190})
    popup.goto(f"chrome-extension://{ext_id}/popup.html?tables={q}&host=example.com")
    popup.wait_for_function("document.getElementById('status').textContent.startsWith('Found')")
    check(popup.inner_text("#status") == "Found 3 tables on example.com.", "popup counts the 3 demo tables")
    popup.screenshot(path=str(raw / "te-popup.png"))
    with popup.expect_download() as dl:
        popup.click("#download")
    csv_path = raw / "tables.csv"
    dl.value.save_as(str(csv_path))
    data = csv_path.read_bytes()
    check(data.startswith(b"\xef\xbb\xbf"), "CSV starts with a UTF-8 BOM")
    text = data.decode("utf-8-sig")
    check('"-0.8%"' in text and '"+6.7%"' in text, "plain numbers stay numbers (-0.8%, +6.7%)")
    check('"\'=HYPERLINK(' in text, "formula cell is neutralised with a leading quote")
    check('"\'@ restock' in text, "@-cell is neutralised")
    rows = list(csv.reader(io.StringIO(text)))
    check(len(rows) == 5 + 1 + 4 + 1 + 3, "CSV has all rows plus one blank separator per table")
    ctx.close()

    # CSV preview rendered like a spreadsheet, for screenshot 2.
    html_rows = "".join(
        "<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" if r else "<tr class='gap'><td colspan=5></td></tr>"
        for r in rows
    )
    (raw / "csv.html").write_text(
        "<html><body style='margin:0;font:15px DejaVu Sans,sans-serif;background:#fff'>"
        "<table style='border-collapse:collapse'>" + html_rows + "</table>"
        "<style>td{border:1px solid #d9dee5;padding:6px 10px;min-width:90px}tr:first-child td{background:#eef2f6;font-weight:600}"
        "tr.gap td{border:0;height:10px}</style></body></html>",
        encoding="utf-8",
    )


def run_cookie_decliner(p, raw: Path) -> None:
    ctx, ext_id = ext_context(p, EXT / "cookie-decliner", raw / "profile-cd")
    page = ctx.new_page()
    page.goto(f"http://127.0.0.1:{PORT}/consent.html")
    time.sleep(2.5)
    check(page.inner_text("#status") == "", "extension is off by default: banner left alone")
    page.screenshot(path=str(raw / "cd-before.png"))
    popup = ctx.new_page()
    popup.set_viewport_size({"width": 284, "height": 200})
    popup.goto(f"chrome-extension://{ext_id}/popup.html")
    popup.click("#enabled")
    time.sleep(0.5)
    page.reload()
    try:
        page.wait_for_function("document.getElementById('status').textContent !== ''", timeout=8000)
    except Exception:
        pass
    check(page.inner_text("#status") == "rejected", "after enabling, the banner is rejected (never accepted)")
    page.screenshot(path=str(raw / "cd-after.png"))
    popup.reload()
    time.sleep(0.5)
    popup.screenshot(path=str(raw / "cd-popup.png"))
    ctx.close()


CARD_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{width:1280px;height:800px;background:#0f1720;color:#e9eef5;font-family:'DejaVu Sans',sans-serif;
     padding:56px 64px;overflow:hidden}
h1{font-size:44px;line-height:1.15;margin-bottom:14px}
.sub{font-size:22px;color:#a9b8c9;margin-bottom:36px}
.shot{border-radius:12px;box-shadow:0 18px 48px rgba(0,0,0,.45);display:block}
.row{display:flex;gap:36px;align-items:flex-start}
.tag{display:inline-block;background:#13202b;border:1px solid #2b3b4c;border-radius:999px;padding:9px 18px;
     font-size:18px;color:#cfe0ee;margin:0 10px 10px 0}
.label{font-size:18px;color:#6fd3a8;margin-bottom:10px;letter-spacing:1px;text-transform:uppercase}
"""


def compose(p, raw: Path) -> None:
    te, cd = ASSETS / "table-exporter", ASSETS / "cookie-decliner"
    te.mkdir(parents=True, exist_ok=True)
    cd.mkdir(parents=True, exist_ok=True)
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1280, "height": 800})

    page.goto(f"file://{raw / 'csv.html'}")
    page.screenshot(path=str(raw / "csv.png"), full_page=True)

    def render(html: str, out: Path, size=(1280, 800)) -> None:
        page.set_viewport_size({"width": size[0], "height": size[1]})
        page.set_content(html, wait_until="load")
        page.screenshot(path=str(out))

    render(f"""<style>{CARD_CSS}</style>
      <h1>Every table on the page, to CSV in one click</h1>
      <div class="sub">Open a page, click the icon, download. Runs 100% locally.</div>
      <div class="row"><img class="shot" src="{data_uri(raw / 'te-page.png')}" style="width:800px">
      <img class="shot" src="{data_uri(raw / 'te-popup.png')}" style="width:300px;margin-top:40px"></div>""",
           te / "screenshot-1.png")
    render(f"""<style>{CARD_CSS}</style>
      <h1>Spreadsheet-safe output</h1>
      <div class="sub">Numbers stay numbers. Cells that would run as formulas are kept as plain text.</div>
      <div class="row"><img class="shot" src="{data_uri(raw / 'csv.png')}" style="max-width:820px;max-height:520px">
      <div><div class="label">Checked on every build</div>
      <span class="tag">-0.8% stays a number</span><br><span class="tag">=HYPERLINK(…) kept as text</span><br>
      <span class="tag">UTF-8 with BOM for Excel</span><br><span class="tag">all tables, one file</span></div></div>""",
           te / "screenshot-2.png")
    render(f"""<style>{CARD_CSS}</style>
      <h1>Cookie banners, rejected for you</h1>
      <div class="sub">It clicks the site's own “Reject all”. It never clicks “Accept”.</div>
      <div class="row"><div><div class="label">Before</div><img class="shot" src="{data_uri(raw / 'cd-before.png')}" style="width:560px"></div>
      <div><div class="label">After</div><img class="shot" src="{data_uri(raw / 'cd-after.png')}" style="width:560px"></div></div>""",
           cd / "screenshot-1.png")
    render(f"""<style>{CARD_CSS}</style>
      <h1>Off until you switch it on</h1>
      <div class="sub">One switch in the popup. Stores only your choice and a local counter.</div>
      <div class="row"><img class="shot" src="{data_uri(raw / 'cd-popup.png')}" style="width:300px">
      <div><span class="tag">no account</span><br><span class="tag">no tracking, no network requests</span><br>
      <span class="tag">works on OneTrust, Cookiebot, Quantcast, Didomi, Sourcepoint</span></div></div>""",
           cd / "screenshot-2.png")

    for name, title, line, folder in (
        ("table-exporter", "Table Exporter", "Tables to CSV in one click", te),
        ("cookie-decliner", "Consent Decliner", "Rejects cookie banners for you", cd),
    ):
        icon = data_uri(EXT / name / "icons" / "icon128.png")
        render(f"""<style>{CARD_CSS} body{{width:440px;height:280px;padding:36px}}</style>
          <img src="{icon}" style="width:72px;height:72px;margin-bottom:18px">
          <h1 style="font-size:30px">{title}</h1><div class="sub" style="font-size:17px">{line}</div>""",
               folder / "promo-440x280.png", size=(440, 280))
    browser.close()


def main() -> int:
    srv = serve_demo()
    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        raw = Path(tmp)
        run_table_exporter(p, raw)
        run_cookie_decliner(p, raw)
        compose(p, raw)
    srv.shutdown()
    print("RESULT:", "OK" if not FAILS else f"{len(FAILS)} failure(s)")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
