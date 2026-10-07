# Spec — PDF Batch → Excel (MVP v0.1)

- **Goal:** Windows utility (CLI first) that batch-processes a folder of PDFs and produces one XLSX workbook + a machine-readable error report. No cloud, no uploads.
- **Input:** a folder path containing PDF files. **Output:** `out.xlsx` (one sheet per PDF: extracted tables, or text lines when no tables) + `errors.csv` (per-file status).
- **Extraction engine:** pdfplumber (tables + text, local). Scanned/image-only PDFs are flagged in errors.csv as `needs_ocr` — never silently dropped, never sent to output as empty (Zero Zgomot rule).
- **Acceptance criteria:** (1) `python -m pdfbatch run <folder> -o out.xlsx` exits 0 on a folder with text-based PDFs; (2) out.xlsx contains one sheet per readable PDF with real extracted content; (3) errors.csv lists every unreadable/scanned/corrupt PDF with a reason; (4) pytest suite green on this Windows machine.
- **Out of scope v0.1:** GUI, hot-folder watcher, supplier profiles, OCR, packaging/installer (v0.2+).

# v0.2 — hot-folder watcher

- **Goal:** process PDFs as they arrive in a folder, incrementally, without reprocessing unchanged files.
- **CLI:** `python -m pdfbatch watch <folder> -o out.xlsx [--interval 2] [--once]`.
- **Eligibility:** a file is processed when its size is identical on two consecutive scans
  (copy finished) AND it differs from the saved state (name + size + mtime).
- **State:** `<out>.watch-state.json` next to the workbook, atomic replace; `errors.csv`
  is regenerated from state on every active pass (full history of files seen).
- **Replacement:** a changed file is reprocessed and its sheet is replaced (no duplicates).
- **Acceptance criteria:** (1) `watch --once` on a fresh folder produces the same workbook
  as `run`; (2) a second `--once` after adding one PDF adds exactly one sheet and reprocesses
  nothing else; (3) overwriting a PDF replaces its sheet content; (4) Ctrl+C exits 0; (5) pytest green.
- **Known limit:** stability check is size-based — a copy paused with an identical size can be
  picked up early; it lands in `errors.csv` and is reprocessed when it changes again.
- **Out of scope v0.2:** GUI, supplier profiles, OCR, packaging/installer (v0.3+).
