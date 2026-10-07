"""Pre-flight for NISHIAI test sessions (run BEFORE any browser/product test).

Mechanically re-checks the environment lessons from docs/LECTII-TESTARE.md,
so they surface in ~10 seconds instead of mid-session debugging.
Protocol: whenever a lesson becomes mechanically checkable, add it here.
Usage: python test_preflight.py
"""
from __future__ import annotations

import pathlib
import socket
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
CFT_DLL = pathlib.Path(r"C:\Users\cw_26\nishiai-apps\chrome-win64\chrome.dll")
PORTS = [8077, 9223, 9224, 9226]

ok: list[str] = []
fail: list[str] = []
warn: list[str] = []


def port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def main() -> int:
    # files required by the extension tests
    for rel in ("testpages/consent.html", "testpages/tables.html",
                "test_e2e.py", "test_exporter.py", "test_activation.py",
                "cookie-decliner/content.js", "cookie-decliner/manifest.json"):
        (ok if (ROOT / rel).exists() else fail).append(f"file {rel}")

    # websocket client needed by every CDP test
    try:
        import websocket  # noqa: F401
        ok.append("python module websocket-client")
    except ImportError:
        fail.append("python module websocket-client (pip install websocket-client)")

    # test ports must be free (a live test browser = leftover processes, E7/F1)
    for port in PORTS:
        (ok if port_free(port) else fail).append(f"port {port} free")

    # E1: Edge must exist; CfT is policy-blocked since 7 oct — probe, don't assume
    if pathlib.Path(EDGE).exists():
        ok.append("Edge instalat (browserul de test implicit)")
    else:
        fail.append("Edge lipsa (cale standard)")

    if CFT_DLL.exists():
        try:
            r = subprocess.run(
                [str(CFT_DLL.parent / "chrome.exe"), "--headless", "--dump-dom", "about:blank"],
                capture_output=True, text=True, timeout=25)
            if "Application Control" in (r.stderr or ""):
                warn.append("CfT BLOCAT de Application Control (E1) — foloseste Edge headful")
            else:
                ok.append("CfT nu mai e blocat — poate fi folosit din nou")
        except subprocess.TimeoutExpired:
            warn.append("CfT probe timeout — verfica manual inainte de folosire")
    else:
        warn.append("CfT chrome.dll lipsa de pe disc")

    print("=== PRE-FLIGHT TESTARE ===")
    for line in ok:
        print(f"  OK   {line}")
    for line in warn:
        print(f"  WARN {line}")
    for line in fail:
        print(f"  FAIL {line}")
    print(f"Rezultat: {len(ok)} ok, {len(warn)} atenționări, {len(fail)} fail")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
