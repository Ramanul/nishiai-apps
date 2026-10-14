"""Generează un PDF „scanat” de demonstrație: un inventar cu date inventate.

Datele sunt fictive (fără persoane, firme sau cifre reale). Imaginea e rotită ușor,
cu zgomot și contrast redus, ca un scan real. Rulare: python genereaza_scan.py
"""
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

random.seed(7)
# Fonturi: DEMO_FONT / DEMO_FONT_BOLD (căi .ttf) au prioritate; altfel căutăm DejaVu în locurile
# uzuale (Linux, Windows cu DejaVu instalat). Dacă nu există, folosim fontul implicit Pillow
# (cere Pillow >= 10.1); imaginea iese, doar diacriticele pot arăta altfel.
_CANDIDATI = {
    "regular": ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/DejaVuSans.ttf"],
    "bold": ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "C:/Windows/Fonts/DejaVuSans-Bold.ttf"],
}


def font(stil, marime):
    env = os.environ.get("DEMO_FONT_BOLD" if stil == "bold" else "DEMO_FONT")
    for cale in ([env] if env else []) + _CANDIDATI[stil]:
        if cale and os.path.exists(cale):
            return ImageFont.truetype(cale, marime)
    return ImageFont.load_default(size=marime)

ITEMS = ["Hârtie A4 80g", "Toner negru", "Pix gel albastru", "Dosar plic", "Capsator", "Capse 24/6",
         "Marker permanent", "Bandă adezivă", "Plic C4", "Caiet A5", "Biblioraft 8 cm", "Post-it 76x76",
         "Calculator birou", "Foarfecă", "Lipici stick", "Separator carton"]

def randuri():
    out = []
    for i, nume in enumerate(ITEMS, 1):
        cant = random.randint(2, 60)
        pret = round(random.uniform(1.5, 95.0), 2)
        out.append((i, f"P-{1000 + i * 7}", nume, cant, pret, round(cant * pret, 2)))
    return out

def main(dest="inventar-scanat.pdf"):
    W, H = 1654, 2339  # A4 la 200 dpi
    img = Image.new("L", (W, H), 250)
    d = ImageDraw.Draw(img)
    f, fb, ft = font("regular", 30), font("bold", 30), font("bold", 44)
    d.text((120, 120), "INVENTAR MAGAZIE — DEPOZIT 2 (date demonstrative)", font=ft, fill=20)
    d.text((120, 190), "Data: 03.10.2026      Gestionar: ___________      Pagina 1/1", font=f, fill=40)
    cols = [120, 200, 380, 960, 1110, 1310, 1540]
    head = ["Nr.", "Cod", "Denumire", "Cant.", "Preț unit.", "Valoare"]
    y = 290
    for x, t in zip(cols, head):
        d.text((x + 8, y + 10), t, font=fb, fill=15)
    rows = randuri()
    for r in rows:
        y += 62
        vals = [str(r[0]), r[1], r[2], str(r[3]), f"{r[4]:.2f}".replace(".", ","), f"{r[5]:,.2f}".replace(",", " ").replace(".", ",")]
        for x, t in zip(cols, vals):
            d.text((x + 8, y + 12), t, font=f, fill=random.randint(10, 60))
    total = round(sum(r[5] for r in rows), 2)
    y += 62
    d.text((960 + 8, y + 12), "TOTAL", font=fb, fill=15)
    d.text((1310 + 8, y + 12), f"{total:,.2f}".replace(",", " ").replace(".", ","), font=fb, fill=15)
    for yy in range(290, y + 63, 62):
        d.line((cols[0], yy, cols[-1], yy), fill=90, width=2)
    for x in cols:
        d.line((x, 290, x, y + 62), fill=90, width=2)
    # aspect de scan: rotire, zgomot, blur ușor
    img = img.rotate(0.8, resample=Image.BICUBIC, fillcolor=245)
    px = img.load()
    for _ in range(60000):
        px[random.randrange(W), random.randrange(H)] = random.randint(150, 230)
    img = img.filter(ImageFilter.GaussianBlur(0.7))
    img.convert("RGB").save(dest, "PDF", resolution=200)
    return rows, total

if __name__ == "__main__":
    rows, total = main()
    print(len(rows), "rânduri; total", total)
