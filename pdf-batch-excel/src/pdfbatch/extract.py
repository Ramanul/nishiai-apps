"""PDF extraction with explicit failure classification.

Every PDF ends in exactly one of three states:
- ok        -> sheets carry the extracted tables (or text lines when a page has no table)
- needs_ocr -> no usable text layer (scanned or image-only); reported, never silently dropped
- error     -> the file could not be opened/parsed at all
"""
from __future__ import annotations

import pathlib

import pdfplumber

NEEDS_OCR_MIN_CHARS = 20


def extract_pdf(path: pathlib.Path) -> dict:
    """Extract tables/text from one PDF.

    Returns {'file', 'status', 'sheets', 'reason'} where sheets is a list of
    {'name', 'rows'} and rows is a list of lists of strings.
    """
    result = {"file": path.name, "status": "ok", "sheets": [], "reason": ""}
    try:
        with pdfplumber.open(path) as pdf:
            if not pdf.pages:
                result.update(status="error", reason="no pages")
                return result
            all_chars = 0
            tables: list[list[list[str]]] = []
            text_lines: list[str] = []
            for page in pdf.pages:
                text = page.extract_text() or ""
                all_chars += len(text.strip())
                text_lines.extend(line.strip() for line in text.splitlines() if line.strip())
                for table in page.extract_tables() or []:
                    rows = [[("" if cell is None else str(cell).strip()) for cell in row] for row in table]
                    if rows:
                        tables.append(rows)
        if all_chars < NEEDS_OCR_MIN_CHARS and not tables:
            result.update(status="needs_ocr", reason="no text layer (scanned or image-only)")
            return result
        if tables:
            for idx, rows in enumerate(tables, start=1):
                result["sheets"].append({"name": f"table_{idx}", "rows": rows})
        else:
            result["sheets"].append({"name": "text", "rows": [[line] for line in text_lines]})
        return result
    except Exception as exc:  # corrupt/encrypted/unknown PDFs end here, classified
        result.update(status="error", reason=f"{type(exc).__name__}: {exc}")
        return result
