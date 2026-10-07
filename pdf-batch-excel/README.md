# pdfbatch — PDF Batch → Excel

Local Windows utility (NISHIAI product #1): batch-process a folder of PDFs into
one Excel workbook, with an explicit error report. No cloud, no uploads.

## Usage

One-shot batch (v0.1):

```
python -m pdfbatch run <folder-with-pdfs> -o out.xlsx
```

Hot-folder watcher (v0.2) — drop PDFs into the folder, results accumulate in the workbook:

```
python -m pdfbatch watch <folder-with-pdfs> -o out.xlsx [--interval 2] [--once]
```

- One Excel sheet per readable PDF (extracted tables stacked; text-only PDFs get their lines).
- `out.errors.csv` lists every file with status `ok` / `needs_ocr` / `error` and a reason.
  Scanned (image-only) PDFs are flagged `needs_ocr` — never silently dropped.
- `watch` processes a file only after its size is stable across two consecutive scans
  (copy finished), keeps its state in `out.xlsx.watch-state.json`, and replaces a file's
  sheet when the file changes. `--once` = single pass (Task Scheduler friendly); Ctrl+C stops.

## Install (dev)

```
pip install -e .
pip install pytest fpdf2   # tests only
pytest
```

See `SPEC.md` for the v0.1 scope and what is intentionally out (GUI, hot-folder watcher,
supplier profiles, OCR — planned v0.2+).
