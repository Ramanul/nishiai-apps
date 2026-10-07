"""Hot-folder watcher: incremental processing with on-disk state.

A file is eligible when its size is identical on two consecutive scans (the
copy finished) and it differs from the saved state (name + size + mtime).
State lives next to the workbook as `<out>.watch-state.json` and is replaced
atomically after every pass that processed something.
"""
from __future__ import annotations

import json
import pathlib

from .excel_out import append_results, write_errors
from .extract import extract_pdf


def scan_sizes(folder: pathlib.Path) -> dict[str, int]:
    """Snapshot {pdf name: size} used for copy-stability detection."""
    return {p.name: p.stat().st_size for p in sorted(folder.glob("*.pdf"))}


def load_state(state_path: pathlib.Path) -> dict:
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(state.get("files"), dict):
                return state
        except (json.JSONDecodeError, OSError):
            pass
    return {"files": {}}


def _save_state(state_path: pathlib.Path, state: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = state_path.with_name(state_path.name + ".tmp")
    tmp.write_text(json.dumps(state, indent=1), encoding="utf-8")
    tmp.replace(state_path)


def watch_pass(
    folder: pathlib.Path,
    out_path: pathlib.Path,
    state: dict,
    prev_sizes: dict[str, int],
    state_path: pathlib.Path,
) -> tuple[dict[str, int], list[dict], dict[str, str]]:
    """One scan pass. Returns (current sizes, results, file -> sheet title)."""
    cur_sizes = scan_sizes(folder)
    todo: list[pathlib.Path] = []
    for name, size in cur_sizes.items():
        if prev_sizes.get(name) != size:
            continue  # new or still being copied: wait for a stable second scan
        path = folder / name
        try:
            st = path.stat()
        except OSError:
            continue
        entry = state["files"].get(name)
        if entry and entry.get("size") == st.st_size and entry.get("mtime") == st.st_mtime:
            continue  # already processed, unchanged
        todo.append(path)

    if not todo:
        return cur_sizes, [], {}

    results: list[dict] = []
    processed: list[pathlib.Path] = []
    for path in todo:
        try:
            before = path.stat()
        except OSError:
            continue
        try:
            result = extract_pdf(path)
        except Exception as exc:  # extract_pdf classifies its own; belt for the unexpected
            result = {"file": path.name, "status": "error", "sheets": [], "reason": f"{type(exc).__name__}: {exc}"}
        try:
            after = path.stat()
        except OSError:
            continue  # vanished mid-pass; retried on the next pass
        if (before.st_size, before.st_mtime) != (after.st_size, after.st_mtime):
            continue  # rewritten while reading: drop this read, retry on the next pass
        results.append(result)
        processed.append(path)

    previous_sheets = {
        name: state["files"][name]["sheet"]
        for name in (p.name for p in processed)
        if name in state["files"] and state["files"][name].get("sheet")
    }
    assigned = append_results(out_path, results, previous_sheets)

    for path, result in zip(processed, results):
        try:
            st = path.stat()
        except OSError:
            continue  # vanished mid-pass; retried on the next pass
        state["files"][path.name] = {
            "size": st.st_size,
            "mtime": st.st_mtime,
            "status": result["status"],
            "reason": result["reason"],
            "sheet": assigned.get(path.name, ""),
        }

    rows = [
        {"file": name, "status": v.get("status", ""), "reason": v.get("reason", "")}
        for name, v in state["files"].items()
    ]
    write_errors(rows, out_path.with_suffix(".errors.csv"))
    _save_state(state_path, state)
    return cur_sizes, results, assigned
