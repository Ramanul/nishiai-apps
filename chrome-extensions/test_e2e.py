"""E2E test for the two Chrome extensions via CDP (headless Chrome on :9223)."""
import json
import time
import urllib.request

import websocket

BASE = "http://127.0.0.1:9223"
DL_DIR = r"C:\Users\cw_26\nishiai-apps\chrome-extensions\test-downloads"


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
    out = {}
    lst = get_json("/json/list")
    ver = get_json("/json/version")
    browser = CDP(ver["webSocketDebuggerUrl"])
    browser.send("Browser.setDownloadBehavior",
                 {"behavior": "allow", "downloadPath": DL_DIR})

    sw = next((t for t in lst if t["type"] == "service_worker" and "chrome-extension://" in t["url"]), None)
    if sw:
        ext_id = sw["url"].split("/")[2]
    else:
        ext_id = "jmnaglohpchgjicbpiodkkhchdbiapfm"  # ID calculat din calea exteniei (SHA256)
    out["ext_id"] = ext_id

    page = CDP(next(t for t in lst if t["type"] == "page")["webSocketDebuggerUrl"])
    page.send("Page.enable")
    page.send("Page.navigate", {"url": "http://localhost:8077/tables.html"})
    time.sleep(1.5)

    tables = [[["Name", "Qty"], ["Cement", "12"], ["Steel", "40"]],
              [["City", "Pop"], ["Timisoara", "319k"]]]
    popup_url = (f"chrome-extension://{ext_id}/popup.html"
                 f"?tables={json.dumps(tables)}&host=test.local")
    browser.send("Target.createTarget", {"url": popup_url})
    time.sleep(2)

    lst2 = get_json("/json/list")
    popup_t = next(t for t in lst2 if "popup.html" in t.get("url", "") and ext_id in t.get("url", ""))
    time.sleep(1.5)
    popup = CDP(popup_t["webSocketDebuggerUrl"])
    popup.send("Runtime.enable")
    ev = popup.send("Runtime.evaluate", {
        "expression": "({name: chrome.runtime.getManifest().name, status: document.getElementById('status').textContent})",
        "returnByValue": True})
    if "result" not in ev or "value" not in ev.get("result", {}):
        out["popup_eval_raw"] = ev
    else:
        out["popup"] = ev["result"]["value"]
    popup.send("Runtime.evaluate", {"expression": "document.getElementById('download').click()"})
    time.sleep(2)

    import os
    os.makedirs(DL_DIR, exist_ok=True)
    out["downloaded"] = os.listdir(DL_DIR)
    if out["downloaded"]:
        with open(os.path.join(DL_DIR, out["downloaded"][0]), encoding="utf-8-sig") as f:
            out["csv"] = f.read()

    page.send("Page.navigate", {"url": "http://localhost:8077/consent.html"})
    time.sleep(4.5)
    out["consent"] = page.send("Runtime.evaluate", {
        "expression": ("({clicked: !!window.__rejectClicked, "
                       "bannerGone: !document.getElementById('onetrust-banner-sdk'), "
                       "declinerRan: !!window.__consentDeclinerClicked})"),
        "returnByValue": True})["result"]["value"]

    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
