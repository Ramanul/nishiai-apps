# nishiai-apps

Small, local-first products by NISHIAI (Alexandru Stanciu). No cloud, no telemetry, no uploads.

| Product | What it does | Status |
|---|---|---|
| [`pdf-batch-excel/`](pdf-batch-excel/) | Windows CLI: batch-convert PDF tables to one XLSX workbook + explicit error report (`ok` / `needs_ocr` / `error`). Hot-folder watcher included. | v0.2, tested (pytest 9/9) |
| [`chrome-extensions/table-exporter/`](chrome-extensions/table-exporter/) | Chrome MV3 extension: export page tables to CSV. | tested E2E |
| [`chrome-extensions/cookie-decliner/`](chrome-extensions/cookie-decliner/) | Chrome MV3 extension: clicks "Reject all" on consent banners. | tested E2E |
| [`csv-viewer/`](csv-viewer/) | Android (Kotlin/Compose) CSV viewer: open from SAF, search/filter. | v1.0, tested on emulator |

## Verification before release

All four products go through the frozen acceptance matrix in
[`docs/VERIFICARE-PLAN.md`](docs/VERIFICARE-PLAN.md) before any store publication.
"100%" means: every case in the declared, frozen matrix passes — not "every website/invoice
in the world". Residual risks are written down per product in the same document.

Private (never committed here): real invoices, credentials, store-account paperwork.
