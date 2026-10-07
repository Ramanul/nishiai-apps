"""Pre-flight for NISHIAI test sessions (run BEFORE any browser/product test).

Mechanically re-checks the environment lessons from docs/LECTII-TESTARE.md.
Protocol: whenever a lesson becomes mechanically checkable, add it here.

v4 (2026-10-07, Arena P1/P2 round): 
- probe classification split into classify_probe() with unit tests
  (tests/test_preflight_unit.py) — regression guard against false green;
- occupied ports report the owning PID (and process name, best effort);
- browser paths discovered from candidates + env override
  (NISHIAI_EDGE_EXE / NISHIAI_CFT_EXE), executables verified by launch probe;
- final machine-readable summary line (PREFLIGHT-JSON) for handoff records;
- two layers stay separate: this preflight = capabilities; behavioral smoke =
  test_activation.py (run it after preflight — see playbook F5).

Usage: python test_preflight.py [--browser auto|edge|cft]
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
PORTS = [8077, 9223, 9224, 9226]

EDGE_CANDIDATES = [
    os.environ.get("NISHIAI_EDGE_EXE", ""),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
CFT_CANDIDATES = [
    os.environ.get("NISHIAI_CFT_EXE", ""),
    r"C:\Users\cw_26\nishiai-apps\chrome-win64\chrome.exe",
]

ok: list[str] = []
fail: list[str] = []
warn: list[str] = []


def classify_probe(ready: bool, stderr: str, timed_out: bool) -> str:
    """Classify a launch-probe outcome. ready requires an actual HTTP success;
    anything else must be explained (policy block, timeout, unknown) — the
    caller NEVER maps a non-ready outcome to green."""
    if ready:
        return "ready"
    if timed_out:
        return "probe-error"
    if "application control" in (stderr or "").lower():
        return "blocked-by-policy"
    return "probe-error"


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

    Edge --dump-dom emits nothing through a pipe on Windows, so readiness is
    verified by serving CDP, not by stdout (Arena P0: no false green).
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
        ready, timed_out = False, False
        try:
            for _ in range(16):
                try:
                    with urllib.request.urlopen(
                            f"http://127.0.0.1:{port}/json/version", timeout=1) as r:
                        if r.status == 200 and "webSocketDebuggerUrl" in r.read().decode():
                            ready = True
                            break
                except Exception:
                    time.sleep(0.5)
            else:
                timed_out = True
            errf.seek(0)
            stderr = errf.read().decode(errors="ignore")
            return classify_probe(ready, stderr, timed_out)
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


def find_browser(candidates: list[str]) -> pathlib.Path | None:
    for c in candidates:
        if c and pathlib.Path(c).exists():
            return pathlib.Path(c)
    return None


def port_owner(pid_lookup: int) -> str:
    """Best-effort process name for a PID (Windows tasklist)."""
    try:
        r = subprocess.run(["tasklist", "/FI", f"PID eq {pid_lookup}", "/FO", "CSV"],
                           capture_output=True, text=True, timeout=10)
        lines = [l for l in (r.stdout or "").splitlines() if l.strip()]
        if len(lines) >= 2:
            return lines[1].split('","')[0].strip('"')
    except Exception:
        pass
    return "necunoscut"


def occupied_port_pids(port: int) -> list[int]:
    try:
        r = subprocess.run(["netstat", "-ano"], capture_output=True, text=True, timeout=15)
        pids: set[int] = set()
        for line in (r.stdout or "").splitlines():
            parts = line.split()
            if len(parts) >= 5 and parts[1].endswith(f":{port}") and parts[3] == "LISTENING":
                try:
                    pids.add(int(parts[4]))
                except ValueError:
                    pass
        return sorted(pids)
    except Exception:
        return []


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", choices=["auto", "edge", "cft"], default="auto",
                        help="browser the tests will use (auto = Edge, else CfT)")
    mode = parser.parse_args().browser

    for rel in ("testpages/consent.html", "testpages/tables.html",
                "test_e2e.py", "test_exporter.py", "test_activation.py",
                "test_preflight_unit.py",
                "cookie-decliner/content.js", "cookie-decliner/manifest.json"):
        (ok if (ROOT / rel).exists() else fail).append(f"file {rel}")

    try:
        import websocket  # noqa: F401
        ok.append("python module websocket-client")
    except ImportError:
        fail.append("python module websocket-client (pip install websocket-client)")

    for port in PORTS:
        if port_free(port):
            ok.append(f"port {port} free")
        else:
            pids = occupied_port_pids(port)
            names = [f"{pid} ({port_owner(pid)})" for pid in pids]
            fail.append(f"port {port} OCUPAT de PID {', '.join(names) or 'necunoscut'} "
                        f"— proces de test rămas viu? (F1/E7)")

    edge_exe = find_browser(EDGE_CANDIDATES)
    cft_exe = find_browser(CFT_CANDIDATES)
    states = {
        "edge": probe_browser("edge", edge_exe) if edge_exe else "exe-missing",
        "cft": probe_browser("cft", cft_exe) if cft_exe else "exe-missing",
    }
    for name, st in states.items():
        print(f"  PROBE {name}: {st}")
    if edge_exe:
        ok.append(f"Edge găsit: {edge_exe}")
    if cft_exe:
        ok.append(f"CfT găsit: {cft_exe}")

    if mode == "auto":
        chosen = "edge" if states["edge"] == "ready" else "cft" if states["cft"] == "ready" else None
    else:
        chosen = mode if states[mode] == "ready" else None

    if chosen:
        ok.append(f"browser ales: {chosen} (probe ready)")
        other = "cft" if chosen == "edge" else "edge"
        if states[other] != "ready":
            warn.append(f"{other} nu e gata ({states[other]}) — content scripts doar headful (E2)")
        warn.append("preflight verifică CAPABILITĂȚI; comportamentul real (injectare + click) "
                    "se verifică cu test_activation.py — vezi F5")
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
    print("PREFLIGHT-JSON: " + json.dumps({
        "browser": chosen, "probe": states, "ok": len(ok),
        "warn": len(warn), "fail": len(fail)}, ensure_ascii=False))
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
