"""Adversarial / real-world-class tests: formula-like cells, corrupt and
encrypted PDFs, diacritics, multipage, hot-folder storm (frozen acceptance
matrix, docs/VERIFICARE-PLAN.md)."""
from __future__ import annotations

import csv
import json
import pathlib
import uuid

import pytest
from fpdf import FPDF
from openpyxl import load_workbook

from pdfbatch.__main__ import main
from pdfbatch.watcher import load_state, watch_pass

ARIAL = r"C:\Windows\Fonts\arial.ttf"


def _table_pdf(path, rows: int = 2, items=("Item", "Widget 1")) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for header in ("Item", "Qty"):
        pdf.cell(40, 10, header, border=1)
    pdf.ln()
    for i, name in enumerate(items[:rows]):
        pdf.cell(40, 10, name, border=1)
        pdf.cell(40, 10, str(i + 1), border=1)
        pdf.ln()
    pdf.output(str(path))


def _cell_pdf(path, cell_values: list[str]) -> None:
    """One bordered row holding the given literal values."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for value in cell_values:
        pdf.cell(45, 10, value, border=1)
    pdf.output(str(path))


def _unicode_pdf(path, text: str) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Arial", "", ARIAL)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, text)
    pdf.output(str(path))


def _all_cells(out: pathlib.Path):
    wb = load_workbook(out)
    return [c for ws in wb for row in ws.iter_rows() for c in row if c.value not in (None, "")]


def test_formula_like_cells_stay_literal(tmp_path):
    folder = tmp_path / "pdfs"
    folder.mkdir()
    _cell_pdf(folder / "formulas.pdf", ["=1+1", "+5", "-3", "@cmd", "SUM(A1)"])
    out = tmp_path / "out.xlsx"
    assert main(["run", str(folder), "-o", str(out)]) == 0
    cells = _all_cells(out)
    values = {str(c.value) for c in cells}
    for expected in ("=1+1", "+5", "-3", "@cmd", "SUM(A1)"):
        assert expected in values, f"missing literal {expected!r}"
    assert all(c.data_type != "f" for c in cells), "a formula reached the workbook"


def test_corrupt_pdf_classified_not_crash(tmp_path):
    folder = tmp_path / "pdfs"
    folder.mkdir()
    (folder / "corrupt.pdf").write_bytes(b"%PDF-1.4 garbage not a pdf at all")
    out = tmp_path / "out.xlsx"
    assert main(["run", str(folder), "-o", str(out)]) == 0
    # nothing readable: no workbook is produced, the errors report is the deliverable
    assert not out.exists()
    with (tmp_path / "out.errors.csv").open(encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["file"] == "corrupt.pdf"
    assert rows[0]["status"] == "error"
    assert rows[0]["reason"].strip()


def test_truncated_pdf_classified(tmp_path):
    folder = tmp_path / "pdfs"
    folder.mkdir()
    _table_pdf(folder / "full.pdf")
    raw = (folder / "full.pdf").read_bytes()
    (folder / "full.pdf").unlink()
    (folder / "truncated.pdf").write_bytes(raw[: int(len(raw) * 0.3)])
    out = tmp_path / "out.xlsx"
    assert main(["run", str(folder), "-o", str(out)]) == 0  # must not raise
    with (tmp_path / "out.errors.csv").open(encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 1
    assert rows[0]["status"] in {"error", "needs_ocr"}


@pytest.mark.skipif(not pathlib.Path(ARIAL).exists(), reason="arial.ttf missing")
def test_diacritics_preserved(tmp_path):
    folder = tmp_path / "pdfs"
    folder.mkdir()
    text = "Școala Gimnazială „Titu Maiorescu”\nTotal de plată: 1.250,00 lei — Ținutul Bărăganului"
    _unicode_pdf(folder / "diacritice.pdf", text)
    out = tmp_path / "out.xlsx"
    assert main(["run", str(folder), "-o", str(out)]) == 0
    values = " | ".join(str(c.value) for c in _all_cells(out))
    for fragment in ("Școala Gimnazială", "Titu Maiorescu", "Ținutul Bărăganului", "1.250,00 lei"):
        assert fragment in values, f"diacritics lost: {fragment!r}"


def test_multipage_all_tables_kept(tmp_path):
    folder = tmp_path / "pdfs"
    folder.mkdir()
    pdf = FPDF()
    for page in range(3):
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(40, 10, f"Page {page + 1}", border=1)
        pdf.ln()
        pdf.cell(40, 10, f"Row {page + 1}A", border=1)
        pdf.cell(40, 10, str(page + 1), border=1)
        pdf.ln()
    pdf.output(str(folder / "multi.pdf"))
    out = tmp_path / "out.xlsx"
    assert main(["run", str(folder), "-o", str(out)]) == 0
    wb = load_workbook(out)
    assert wb.sheetnames == ["multi"]  # one sheet per PDF, tables stacked
    values = [str(c.value) for row in wb["multi"].iter_rows() for c in row if c.value]
    for page in ("Page 1", "Page 2", "Page 3", "Row 3A"):
        assert page in values, f"page content lost: {page}"


def test_encrypted_pdf_classified(tmp_path):
    folder = tmp_path / "pdfs"
    folder.mkdir()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(40, 10, "Secret table", border=1)
    pdf.set_encryption(owner_password="owner-secret", user_password="user-secret")
    pdf.output(str(folder / "locked.pdf"))
    out = tmp_path / "out.xlsx"
    assert main(["run", str(folder), "-o", str(out)]) == 0
    with (tmp_path / "out.errors.csv").open(encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["file"] == "locked.pdf"
    assert rows[0]["status"] in {"error", "needs_ocr"}
    assert rows[0]["reason"].strip()


def test_hot_folder_100_operations_no_loss_no_dup(tmp_path):
    folder = tmp_path / "watch"
    folder.mkdir()
    out = tmp_path / "out.xlsx"
    state_path = out.parent / "out.xlsx.watch-state.json"
    state = load_state(state_path)

    created: dict[str, int] = {}
    names: list[str] = []
    for batch in range(20):  # 100 adds total
        for _ in range(5):
            name = f"doc-{uuid.uuid4().hex[:8]}.pdf"
            _table_pdf(folder / name, items=(f"W{batch}", "z"))
            names.append(name)
            created[name] = 1
        prev = {p.name: p.stat().st_size for p in folder.glob("*.pdf")}
        _, results, _ = watch_pass(folder, out, state, prev, state_path)
        assert all(r["status"] == "ok" for r in results)
        if batch % 4 == 3:  # replace one already-processed file
            victim = names[batch - 3]
            _table_pdf(folder / victim, items=(f"R{batch}", "z"))
            created[victim] += 1

    # 100 adds + 5 replacements processed; state knows every file exactly once
    processed = sum(created.values())
    assert len(state["files"]) == len(created) == 100
    assert processed == 105

    wb = load_workbook(out)
    assert len(wb.sheetnames) == 100  # one sheet per file, replacements kept clean
    seen = {}
    for name, entry in state["files"].items():
        assert entry["status"] == "ok"
        assert entry["sheet"]
        assert entry["sheet"].lower() not in seen, f"duplicate sheet {entry['sheet']}"
        seen[entry["sheet"].lower()] = name
