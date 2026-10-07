"""CLI entry point: python -m pdfbatch run <folder> -o out.xlsx"""
from __future__ import annotations

import argparse
import pathlib
import sys
import time

from .extract import extract_pdf
from .excel_out import write_errors, write_workbook
from .watcher import load_state, scan_sizes, watch_pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pdfbatch",
        description="Batch PDF tables -> one Excel workbook + error report (local, no cloud)",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)
    run = sub.add_parser("run", help="process every PDF in a folder")
    run.add_argument("folder", type=pathlib.Path, help="folder containing PDF files")
    run.add_argument("-o", "--out", type=pathlib.Path, default=pathlib.Path("out.xlsx"), help="output workbook path")

    watch = sub.add_parser("watch", help="watch a folder and process PDFs as they arrive")
    watch.add_argument("folder", type=pathlib.Path, help="folder to watch")
    watch.add_argument("-o", "--out", type=pathlib.Path, default=pathlib.Path("out.xlsx"), help="output workbook path")
    watch.add_argument("--interval", type=float, default=2.0, help="seconds between scans (default 2)")
    watch.add_argument("--once", action="store_true", help="single scan pass, then exit")
    args = parser.parse_args(argv)

    if args.cmd == "run":
        folder = args.folder
        if not folder.is_dir():
            print(f"error: {folder} is not a directory", file=sys.stderr)
            return 2
        pdfs = sorted(folder.glob("*.pdf"))
        if not pdfs:
            print(f"error: no PDF files in {folder}", file=sys.stderr)
            return 2
        results = [extract_pdf(path) for path in pdfs]
        write_workbook(results, args.out)
        errors_path = args.out.with_suffix(".errors.csv")
        write_errors(results, errors_path)
        ok = sum(1 for r in results if r["status"] == "ok")
        print(f"done: {ok}/{len(results)} files extracted -> {args.out}")
        print(f"errors report -> {errors_path}")
        return 0

    if args.cmd == "watch":
        folder = args.folder
        if not folder.is_dir():
            print(f"error: {folder} is not a directory", file=sys.stderr)
            return 2
        state_path = args.out.parent / (args.out.name + ".watch-state.json")
        state = load_state(state_path)
        prev_sizes = scan_sizes(folder)
        try:
            while True:
                time.sleep(max(args.interval, 0.05))
                prev_sizes, results, _assigned = watch_pass(folder, args.out, state, prev_sizes, state_path)
                if results:
                    names = ", ".join(r["file"] for r in results)
                    ok = sum(1 for r in results if r["status"] == "ok")
                    print(f"watch: {len(results)} file(s) processed ({ok} ok): {names} -> {args.out}")
                elif args.once:
                    print("watch: nothing new")
                if args.once:
                    return 0
        except KeyboardInterrupt:
            print("watch: stopped")
            return 0

    return 1  # unreachable: subparsers are required


if __name__ == "__main__":
    sys.exit(main())
