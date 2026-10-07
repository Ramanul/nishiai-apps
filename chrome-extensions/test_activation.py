"""Full browser E2E for Consent Decliner v1.1 explicit activation (default OFF).

Runs on a REAL browser window (no headless): content script auto-injects and
must click "Reject all" only after an explicit enable. Measured from the page
main world via the page's own click handler (window.__rejectClicked) and the
banner removal — content-script window markers are invisible from the main
world (isolated world).

Browser: E2E_BROWSER=edge (default — signed, policy-trusted; CfT chrome.dll is
blocked by Windows Application Control since 7 oct) or E2E_BROWSER=cft.
Note: Edge/Chrome HEADLESS does not inject content scripts — headful required.
"""
import json
import os
import subprocess
import time
import urllib.request

import websocket

BROWSERS = {
    "cft": (r"C:\Users\cw_26\nishiai-apps\chrome-win64\chrome.exe", 9223),
    "edge": (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", 9226),
}
BROWSER = os.environ.get("E2E_BROWSER", "edge")
CFT, BASE_PORT = BROWSERS[BROWSER]
EXT = r"C:\Users\cw_26\nishiai-apps\chrome-extensions\cookie-decliner"
PAGES = r"C:\Users\cw_26\nishiai-apps\chrome-extensions\testpages"
PROFILE = rf"C:\Users\cw_26\nishiai-apps\chrome-extensions\testprofile-e2e-{BROWSER}"
BASE = f"http://127.0.0.1:{BASE_PORT}"

MEASURE = ("JSON.stringify({rejectClicked: !!window.__rejectClicked, "
           "bannerGone: !document.getElementById('onetrust-banner-sdk')})")


def get_json(path):
    with urllib.request.urlopen(BASE + path) as r:
        return json.loads(r.read())


class CDP:
    def __init__(self, ws_url):
        self.ws = websocket.create_connection(ws_url, timeout=15)
        self.id = 0

    def send(self, method, params=None):
        self.id += 1
        self.ws.send(json.dumps({"id": self.id, "method": method, "params": params or {}}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == self.id:
                if "error" in msg:
                    raise RuntimeError(msg["error"])
                return msg.get("result", {})


def main():
    server = subprocess.Popen(
        ["python", "-m", "http.server", "8077"], cwd=PAGES,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    chrome = subprocess.Popen([
        CFT, f"--remote-debugging-port={BASE_PORT}",
        "--remote-allow-origins=*",
        f"--user-data-dir={PROFILE}", f"--load-extension={EXT}",
        "--no-first-run", "--window-size=1100,700", "about:blank"])
    try:
        for _ in range(40):
            try:
                get_json("/json/version")
                break
            except Exception:
                time.sleep(0.5)
        lst = get_json("/json/list")
        page = CDP(next(t for t in lst if t["type"] == "page")["webSocketDebuggerUrl"])
        page.send("Page.enable")

        # PASS 1 — fresh profile, storage gate default OFF: banner must stay untouched
        page.send("Page.navigate", {"url": "http://localhost:8077/consent.html"})
        time.sleep(8)  # content script retries up to ~4.2s after injection
        state1 = json.loads(page.send("Runtime.evaluate", {
            "expression": MEASURE, "returnByValue": True})["result"]["value"])
        assert state1["rejectClicked"] is False, "FAILED: clicked while default OFF"
        assert state1["bannerGone"] is False, "FAILED: banner touched while default OFF"

        # extension service worker (ours = /bg.js, not browser built-ins)
        sw = None
        for _ in range(20):
            for t in get_json("/json/list"):
                if t["type"] == "service_worker" and t["url"].endswith("/bg.js"):
                    sw = t
                    break
            if sw:
                break
            time.sleep(0.5)
        assert sw, "extension service worker never registered"
        sw_cdp = CDP(sw["webSocketDebuggerUrl"])

        # PASS 2 — explicit enable, new page load: "Reject all" must be clicked
        r = sw_cdp.send("Runtime.evaluate", {
            "expression": ("chrome.storage.sync.set({enabled:true})"
                           ".then(()=>chrome.storage.sync.get({enabled:null}))"
                           ".then(v=>JSON.stringify(v))"),
            "awaitPromise": True, "returnByValue": True})
        assert json.loads(r["result"]["value"])["enabled"] is True, "explicit enable failed"
        page.send("Page.navigate", {"url": "http://localhost:8077/consent.html?x=2"})
        time.sleep(8)
        state2 = json.loads(page.send("Runtime.evaluate", {
            "expression": MEASURE, "returnByValue": True})["result"]["value"])
        assert state2["rejectClicked"] is True, "FAILED: no reject click after enable"
        assert state2["bannerGone"] is True, "FAILED: banner still present after enable"

        print("E2E COMPLET OK (fereastra reala): default OFF = banner neatins; "
              "enable explicit -> 'Reject all' apasat + banner eliminat")
        return 0
    finally:
        try:
            chrome.kill()
        except OSError:
            pass
        server.kill()
        ps = ("Get-CimInstance Win32_Process -Filter \"Name='msedge.exe' or Name='chrome.exe'\" | "
              f"Where-Object {{ $_.CommandLine -like '*{PROFILE}*' }} | "
              "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }")
        subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)


if __name__ == "__main__":
    raise SystemExit(main())
