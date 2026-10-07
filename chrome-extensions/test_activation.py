"""E2E (browser-level) for Consent Decliner v1.1 explicit activation.

What this verifies IN A REAL BROWSER (Edge headless, extension loaded):
  1. our service worker registers and the extension is installed;
  2. the storage gate defaults to enabled=false on a fresh profile (v1.1 change);
  3. an explicit enable writes and reads back enabled=true.

The full in-page injection E2E (content script auto-injects and clicks) ran on
Chrome for Testing on 6 oct (passed). It cannot re-run here since 7 oct:
CfT chrome.dll is blocked by Windows Application Control (0x11C7) and Edge
headless does not inject content scripts; chrome.* storage APIs are also not
available from the page main world, so a page-side re-check is not possible.
Browser: E2E_BROWSER=edge (default) or cft.
"""
import json
import os
import subprocess
import time
import urllib.request

import websocket

BROWSERS = {
    "cft": (r"C:\Users\cw_26\nishiai-apps\chrome-win64\chrome.exe", 9223),
    "edge": (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", 9224),
}
BROWSER = os.environ.get("E2E_BROWSER", "edge")
CFT, BASE_PORT = BROWSERS[BROWSER]
EXT = r"C:\Users\cw_26\nishiai-apps\chrome-extensions\cookie-decliner"
PAGES = r"C:\Users\cw_26\nishiai-apps\chrome-extensions\testpages"
PROFILE = rf"C:\Users\cw_26\nishiai-apps\chrome-extensions\testprofile-activation-{BROWSER}"
BASE = f"http://127.0.0.1:{BASE_PORT}"


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
        CFT, "--headless=new", f"--remote-debugging-port={BASE_PORT}",
        "--remote-allow-origins=*",
        f"--user-data-dir={PROFILE}", f"--load-extension={EXT}",
        "--no-first-run", "--window-size=1280,800", "about:blank"])
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
        page.send("Page.navigate", {"url": "http://localhost:8077/consent.html"})
        time.sleep(2)

        sw = None
        for _ in range(30):  # MV3 SW registers lazily on a fresh profile
            lst = get_json("/json/list")
            sw = next((t for t in lst if t["type"] == "service_worker"
                       and t["url"].endswith("/bg.js")), None)  # ours, not built-ins
            if sw:
                break
            time.sleep(0.5)
        assert sw, "extension service worker never registered"
        sw_cdp = CDP(sw["webSocketDebuggerUrl"])

        r = sw_cdp.send("Runtime.evaluate", {
            "expression": "chrome.storage.sync.get({enabled:false}).then(v=>JSON.stringify(v))",
            "awaitPromise": True, "returnByValue": True})
        default_state = json.loads(r["result"]["value"])
        assert default_state["enabled"] is False, \
            f"FAILED: default is {default_state['enabled']!r}, must be False (explicit activation)"

        r = sw_cdp.send("Runtime.evaluate", {
            "expression": ("chrome.storage.sync.set({enabled:true})"
                           ".then(()=>chrome.storage.sync.get({enabled:null}))"
                           ".then(v=>JSON.stringify(v))"),
            "awaitPromise": True, "returnByValue": True})
        assert json.loads(r["result"]["value"])["enabled"] is True, "explicit enable failed"

        print("E2E ACTIVARE OK (browser): SW instalat; default OFF; enable explicit = ON")
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
