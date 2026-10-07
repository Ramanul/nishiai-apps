"""Pre-flight for NISHIAI test sessions (run BEFORE any browser/product test).

Mechanically re-checks the environment lessons from docs/LECTII-TESTARE.md,
so they surface in seconds instead of mid-session debugging.
Protocol: whenever a lesson becomes mechanically checkable, add it here.

v3 (2026-10-07, after Arena's review @ fe70806): P0 fixes —
- browser readiness is probed by LAUNCHING the browser headless and reading
  /json/version from its debug port (Edge --dump-dom writes nothing through a
  pipe on Windows, so stdout markers are unusable — see probe);
- `ready` = HTTP 200 with a webSocketDebuggerUrl. Failures classify as
  blocked-by-policy (Application Control text in stderr) / exe-missing /
  probe-error — never a silent green;
- explicit browser mode (--browser auto|edge|cft); exit code reflects the
  readiness of the browser the tests will actually use;
- probes run on isolated temp profiles and are reaped by Name+profile filter.

Usage: python test_preflight.py [--browser auto|edge|cft]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
EDGE_EXE = pathlib.Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
CFT_EXE = pathlib.Path(r"C:\Users\cw_26\nishiai-apps\chrome-win64\chrome.exe")
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


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def probe_browser(name: str, exe: pathlib.Path) -> str:
    """Launch-probe: headless + debug port + /json/version readback.

    Returns: ready | blocked-by-policy | exe-missing | probe-error.
    Edge --dump-dom emits nothing through a pipe on Windows, so we verify by
    serving CDP, not by stdout (Arena P0: no false green).
    """
    if not exe.exists():
        return "exe-missing"
    profile = tempfile.mkdtemp(prefix=f"pdfb-preflight-{name}-")
    port = _free_port()
    with tempfile.TemporaryFile() as errf:
        proc = subprocess.Popen(
            [str(exe), "--headless", "--no-first-run", f"--user-data-dir={profile}",
             f"--remote-debugging-port={port}", "--remote-allow-origins=*", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=errf)
        try:
            for _ in range(16):
                try:
                    with urllib.request.urlopen(
                            f"http://127.0.0.1:{port}/json/version", timeout=1) as r:
                        if r.status == 200 and "webSocketDebuggerUrl" in r.read().decode():
                            return "ready"
                except Exception:
                    time.sleep(0.5)
            errf.seek(0)
            err = errf.read().decode(errors="ignore")
            if "application control" in err.lower():
                return "blocked-by-policy"
            return "probe-error"
        finally:
            ps = ("Get-CimInstance Win32_Process -Filter "
                  f"\"Name='{exe.name}'\" | "
                  f"Where-Object {{ $_.CommandLine -like '*{profile}*' }} | "
                  "ForEach-Object { Stop-Process -Id $_.ProcessId -Force }")
            subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True)
            try:
                proc.kill()
            except OSError:
                pass
            shutil.rmtree(profile, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", choices=["auto", "edge", "cft"], default="auto",
                        help="browser the tests will use (auto = Edge, else CfT)")
    mode = parser.parse_args().browser

    for rel in ("testpages/consent.html", "testpages/tables.html",
                "test_e2e.py", "test_exporter.py", "test_activation.py",
                "cookie-decliner/content.js", "cookie-decliner/manifest.json"):
        (ok if (ROOT / rel).exists() else fail).append(f"file {rel}")

    try:
        import websocket  # noqa: F401
        ok.append("python module websocket-client")
    except ImportError:
        fail.append("python module websocket-client (pip install websocket-client)")

    for port in PORTS:
        (ok if port_free(port) else fail).append(f"port {port} free")

    states = {"edge": probe_browser("edge", EDGE_EXE), "cft": probe_browser("cft", CFT_EXE)}
    for name, st in states.items():
        print(f"  PROBE {name}: {st}")

    if mode == "auto":
        chosen = "edge" if states["edge"] == "ready" else "cft" if states["cft"] == "ready" else None
    else:
        chosen = mode if states[mode] == "ready" else None

    if chosen:
        ok.append(f"browser ales: {chosen} (probe ready)")
        other = "cft" if chosen == "edge" else "edge"
        if states[other] != "ready":
            warn.append(f"{other} nu e gata ({states[other]}) — content scripts doar headful (E2)")
    else:
        fail.append(f"niciun browser gata pentru --browser={mode}: {states}")

    print("=== PRE-FLIGHT TESTARE ===")
    for line in ok:
        print(f"  OK   {line}")
    for line in warn:
        print(f"  WARN {line}")
    for line in fail:
        print(f"  FAIL {line}")
    print(f"Rezultat: {len(ok)} ok, {len(warn)} atenționări, {len(fail)} fail "
          f"| browser: {chosen or 'niciunul'}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
