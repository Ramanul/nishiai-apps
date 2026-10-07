"""Test fixtures: generate sample PDFs with fpdf2."""
from __future__ import annotations

import pytest
from fpdf import FPDF


def _table_pdf(path, rows: int = 3) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for header in ("Item", "Qty", "Price"):
        pdf.cell(40, 10, header, border=1)
    pdf.ln()
    for i in range(rows):
        pdf.cell(40, 10, f"Widget {i}", border=1)
        pdf.cell(40, 10, str(i + 1), border=1)
        pdf.cell(40, 10, f"{10.5 * (i + 1):.2f}", border=1)
        pdf.ln()
    pdf.output(str(path))


def _text_pdf(path) -> None:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 8, "Invoice 2026/101\nClient: Acme SRL\nTotal: 1250.00 RON")
    pdf.output(str(path))


def _blank_pdf(path) -> None:
    """No text layer at all — mimics a scanned/image-only PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.output(str(path))


@pytest.fixture()
def sample_folder(tmp_path: "pathlib.Path"):
    folder = tmp_path / "pdfs"
    folder.mkdir()
    _table_pdf(folder / "table_doc.pdf")
    _text_pdf(folder / "text_doc.pdf")
    _blank_pdf(folder / "scan_doc.pdf")
    return folder
