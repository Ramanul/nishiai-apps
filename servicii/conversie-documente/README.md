# Conversie documente — pachet de serviciu (FLUX-3)

Conversia PDF/scan → Excel/Word e 57% din cererea potrivită profilului în radarul din 2026-10-14 (vezi `docs/radar/DECIZII.md`).

| Fișier | Ce conține |
|---|---|
| `GIG.md` | listarea Fiverr (EN), cu pachete, FAQ și cerințe de comandă; profilul Freelancer.com; regulile de refuz |
| `OFERTE.md` | 3 șabloane de ofertă (A: → Word; B1: tabele → Excel; B2: formulare → Excel) |
| `LIVRARE.md` | pașii de livrare și criteriile de acceptanță dinainte de predare |
| `demo/` | portofoliu cu date fictive: scan → Excel cu verificări, plus imaginea înainte/după 1280×769 |

## Verificat (2026-10-14)
- `demo/inventar.xlsx` are 16 rânduri × 6 coloane = 96 de celule. Toate 96 coincid cu datele generatorului.
- Suma rândurilor (14.560,81) e egală cu totalul tipărit, iar formulele se calculează în LibreOffice.
- Tesseract `--psm 6` n-a citit tabelul cu grilă (text inutilizabil). Acesta e motivul pentru care citirea principală e cea vizuală.

## Neverificat
Prețurile pieței, limita de oferte gratuite pe Freelancer.com și categoria exactă din Fiverr. Se verifică la publicare.

## Poarta lui Alexandru
Contul de vânzător pe Fiverr, publicarea gig-ului și trimiterea ofertelor pe Freelancer.com/Upwork.
