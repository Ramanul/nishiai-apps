"""Pre-flight for NISHIAI test sessions (run BEFORE any browser/product test).

Mechanically re-checks the environment lessons from docs/LECTII-TESTARE.md,
so they surface in seconds instead of mid-session debugging.
Protocol: whenever a lesson becomes mechanically checkable, add it here.

v2 (2026-10-07, after Arena's review @ fe70806): P0 fixes —
- CfT probe requires returncode 0 AND a real output marker; any other failure
  is `probe-error`, never a green "CfT ready" (no false positives);
- explicit browser mode (--browser auto|edge|cft) and the exit code reflects
  the readiness of the browser the tests will actually use;
- Edge readiness is probed by launching it (headless launch probe), not just
  by checking that a file exists; headful-only limits stay in the playbook (E2).

Usage: python test_preflight.py [--browser auto|edge|cft]
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import socket
import subprocess
import sys
import tempfile

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


def probe_browser(name: str, exe: pathlib.Path) -> str:
    """Launch-probe a Chromium browser with an isolated temp profile.

    Returns one of: ready | blocked-by-policy | exe-missing | probe-error.
    `ready` demands returncode 0 AND real DOM output — never just "no error text".
    """
    if not exe.exists():
        return "exe-missing"
    profile = tempfile.mkdtemp(prefix=f"pdfb-preflight-{name}-")
    try:
        r = subprocess.run(
            [str(exe), "--headless", "--no-first-run",
             f"--user-data-dir={profile}", "--dump-dom", "about:blank"],
            capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and "<html" in (r.stdout or "").lower():
            return "ready"
        if "application control" in (r.stderr or "").lower():
            return "blocked-by-policy"
        return "probe-error"
    except subprocess.TimeoutExpired:
        return "probe-error"
    except OSError:
        return "probe-error"
    finally:
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
            warn.append(f"{other} nu e gata ({states[other]}) — foloseste Edge headful pentru content scripts (E2)")
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
