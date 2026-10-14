"""Transcrierea manuală-asistată a inventar-scanat.pdf → inventar.xlsx, cu verificări.

Valorile din TRANSCRIERE sunt citite din imagine (nu din generator). Foaia „Verificare”
recalculează cant×preț și totalul cu formule Excel, ca orice abatere să fie vizibilă.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import FormulaRule

TRANSCRIERE = [
    (1, "P-1007", "Hârtie A4 80g", 22, 90.13, 1982.86),
    (2, "P-1014", "Toner negru", 27, 62.36, 1683.72),
    (3, "P-1021", "Pix gel albastru", 6, 78.29, 469.74),
    (4, "P-1028", "Dosar plic", 8, 35.69, 285.52),
    (5, "P-1035", "Capsator", 5, 86.56, 432.80),
    (6, "P-1042", "Capse 24/6", 15, 5.01, 75.15),
    (7, "P-1049", "Marker permanent", 29, 40.60, 1177.40),
    (8, "P-1056", "Bandă adezivă", 17, 9.98, 169.66),
    (9, "P-1063", "Plic C4", 29, 7.03, 203.87),
    (10, "P-1070", "Caiet A5", 38, 13.08, 497.04),
    (11, "P-1077", "Biblioraft 8 cm", 16, 60.46, 967.36),
    (12, "P-1084", "Post-it 76x76", 39, 90.11, 3514.29),
    (13, "P-1091", "Calculator birou", 38, 56.25, 2137.50),
    (14, "P-1098", "Foarfecă", 5, 92.78, 463.90),
    (15, "P-1105", "Lipici stick", 4, 53.55, 214.20),
    (16, "P-1112", "Separator carton", 10, 28.58, 285.80),
]
TOTAL_DOC = 14560.81

def main(dest="inventar.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Inventar"
    head = ["Nr.", "Cod", "Denumire", "Cant.", "Preț unit.", "Valoare (document)",
            "Valoare (recalculată)", "Diferență"]
    ws.append(head)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F4E78")
        c.alignment = Alignment(horizontal="center", wrap_text=True)
    for i, r in enumerate(TRANSCRIERE, start=2):
        ws.append(list(r) + [f"=ROUND(D{i}*E{i},2)", f"=ROUND(F{i}-G{i},2)"])
    last = len(TRANSCRIERE) + 1
    t = last + 1
    ws.cell(t, 3, "TOTAL").font = Font(bold=True)
    ws.cell(t, 6, f"=SUM(F2:F{last})").font = Font(bold=True)
    ws.cell(t, 7, f"=SUM(G2:G{last})").font = Font(bold=True)
    ws.cell(t, 8, f"=ROUND(F{t}-G{t},2)").font = Font(bold=True)
    ws.cell(t + 1, 3, "Total tipărit pe document")
    ws.cell(t + 1, 6, TOTAL_DOC)
    ws.cell(t + 2, 3, "Diferență față de totalul tipărit")
    ws.cell(t + 2, 6, f"=ROUND(F{t}-F{t+1},2)")
    for row in ws.iter_rows(min_row=2, min_col=5, max_col=8):
        for c in row:
            c.number_format = "#,##0.00"
    red = PatternFill("solid", fgColor="F8CBAD")
    ws.conditional_formatting.add(f"H2:H{t}", FormulaRule(formula=["H2<>0"], fill=red))
    ws.conditional_formatting.add(f"F{t+2}", FormulaRule(formula=[f"F{t+2}<>0"], fill=red))
    for col, w in zip("ABCDEFGH", [6, 10, 22, 8, 11, 18, 20, 11]):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"
    note = wb.create_sheet("Note")
    for line in ["Sursă: inventar-scanat.pdf (date demonstrative, fictive).",
                 "Coloanele G și H recalculează cant × preț; orice diferență nenulă e colorată.",
                 "Rândul „Diferență față de totalul tipărit” compară suma rândurilor cu totalul de pe document.",
                 "Celulele ilizibile ar fi marcate [ILIZIBIL] și listate aici, nu ghicite."]:
        note.append([line])
    note.column_dimensions["A"].width = 100
    wb.save(dest)

if __name__ == "__main__":
    main()
