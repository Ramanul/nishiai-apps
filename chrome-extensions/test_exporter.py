"""Re-test doar pentru Table Exporter: reload popup -> download -> verifica CSV."""
import json
import os
import time
import urllib.request

import websocket

BASE = "http://127.0.0.1:9223"
DL_DIR = r"C:\Users\cw_26\nishiai-apps-public\chrome-extensions\test-downloads"
EXT_ID = "jmnaglohpchgjicbpiodkkhchdbiapfm"


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
    popup_t = next(t for t in lst if "popup.html" in t.get("url", "") and EXT_ID in t.get("url", ""))
    popup = CDP(popup_t["webSocketDebuggerUrl"])
    popup.send("Page.enable")
    popup.send("Page.reload")
    time.sleep(2)
    ev = popup.send("Runtime.evaluate", {
        "expression": "({name: chrome.runtime.getManifest().name, status: document.getElementById('status').textContent})",
        "returnByValue": True})["result"]["value"]
    out["popup"] = ev
    os.makedirs(DL_DIR, exist_ok=True)
    popup.send("Runtime.evaluate", {"expression": "document.getElementById('download').click()"})
    time.sleep(2)
    out["downloaded"] = os.listdir(DL_DIR)
    if out["downloaded"]:
        with open(os.path.join(DL_DIR, out["downloaded"][0]), encoding="utf-8-sig") as f:
            out["csv"] = f.read()
    # formula-prefix hardening (OWASP: = + - @ execute as formulas in Excel)
    out["formula_csv"] = popup.send("Runtime.evaluate", {
        "expression": "window.__buildCSV([[\"=1+1\", \"@x\", \"-5\", \"plain\"]])",
        "returnByValue": True})["result"]["value"]
    print(json.dumps(out, ensure_ascii=False, indent=1))
    assert out["popup"] and out["popup"]["name"], "popup did not report a manifest name"
    assert out["downloaded"], "no CSV was downloaded"
    assert "'=1+1" in out["formula_csv"] and "'@x" in out["formula_csv"], out["formula_csv"]
    assert '"plain"' in out["formula_csv"], out["formula_csv"]


if __name__ == "__main__":
    main()
    print("EXPORTER-OK")


if __name__ == "__main__":
    main()
