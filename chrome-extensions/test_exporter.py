"""Re-test doar pentru Table Exporter: reload popup -> download -> verifica CSV."""
import json
import os
import time
import urllib.request

import websocket

BASE = "http://127.0.0.1:9223"
DL_DIR = r"C:\Users\cw_26\nishiai-apps\chrome-extensions\test-downloads"
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
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
