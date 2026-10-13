"""Build Chrome Web Store upload packages for the NISHIAI extensions.

Usage: python store/build_packages.py            (from the repo root)

For each extension in chrome-extensions/<name>/ it:
  * copies only runtime files (manifest, js, html, css, icons) — tests and test pages stay out;
  * removes the "key" field from manifest.json (the Web Store rejects uploads that contain it;
    the key only pins the extension ID for local development);
  * checks that the declared icons exist and have the declared pixel size;
  * writes store/dist/<name>-<version>.zip and prints its SHA-256.

Exit code is non-zero if any check fails, so the script can gate a CI job.
"""
from __future__ import annotations

import hashlib
import io
import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXT_DIR = ROOT / "chrome-extensions"
DIST = ROOT / "store" / "dist"
EXTENSIONS = ("table-exporter", "cookie-decliner")
RUNTIME_SUFFIXES = {".js", ".html", ".css", ".png", ".json"}


def png_size(path: Path) -> tuple[int, int]:
    """Read width/height from a PNG header without third-party libraries."""
    with path.open("rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path.name} is not a PNG file")
    return struct.unpack(">II", head[16:24])


def build(name: str) -> list[str]:
    errors: list[str] = []
    src = EXT_DIR / name
    manifest_path = src / "manifest.json"
    if not manifest_path.is_file():
        return [f"{name}: manifest.json missing"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.pop("key", None)

    declared: dict[str, str] = {}
    declared.update(manifest.get("icons", {}))
    declared.update(manifest.get("action", {}).get("default_icon", {}))
    for size, rel in declared.items():
        icon = src / rel
        if not icon.is_file():
            errors.append(f"{name}: icon {rel} missing")
            continue
        w, h = png_size(icon)
        if (w, h) != (int(size), int(size)):
            errors.append(f"{name}: icon {rel} is {w}x{h}, manifest says {size}")

    files = sorted(
        p for p in src.rglob("*")
        if p.is_file() and p.suffix in RUNTIME_SUFFIXES and p.name != "manifest.json"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
        for p in files:
            zf.write(p, p.relative_to(src).as_posix())

    if errors:
        return errors
    DIST.mkdir(parents=True, exist_ok=True)
    out = DIST / f"{name}-{manifest['version']}.zip"
    out.write_bytes(buf.getvalue())
    digest = hashlib.sha256(buf.getvalue()).hexdigest()
    print(f"OK  {out.relative_to(ROOT)}  {len(files) + 1} files  sha256={digest}")
    return []


def main() -> int:
    problems: list[str] = []
    for name in EXTENSIONS:
        problems += build(name)
    for msg in problems:
        print(f"ERR {msg}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
