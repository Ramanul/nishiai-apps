# Protocol de lucru — nishiai-apps

Versiune 2026-10-13. Înlocuiește, pentru acest repo, regula 6 din `izz-ro/docs/colaborare.md`
(merge doar cu „da” per acțiune), la decizia lui Alexandru din 13 oct. 2026.

## Ce se face automat
- Branch-uri, commit-uri, PR-uri și **merge în `main`** — fără aprobare per acțiune, dacă:
  1. testele relevante trec (pytest pentru `pdf-batch-excel`, `store/make_screenshots.py` pentru extensii);
  2. diff-ul a fost recitit pe același SHA: de un alt agent când lucrul vine de la un agent extern
     (Codex, Jules, Arena), altfel de autor, cu lista schimbărilor în descrierea PR-ului;
  3. nu se atinge nimic din lista „doar Alexandru” de mai jos.

## Ce cere un singur „da” pe lot
Tot ce devine public în afara repo-ului: trimiterea unei extensii în magazin, publicarea unui actor
Apify, listări Etsy, profil sau propuneri pe Upwork. Lotul se arată exact, Alexandru răspunde o dată.

## Doar Alexandru
Parole, conturi noi, verificarea identității, CNP, IBAN, formulare fiscale, cumpărături.

## Reguli de date
- Repo-ul e public: fără date personale, facturi reale, chei sau tokeni.
- Cod pentru produse vândute nu trece prin Arena (termenii Arena 3.3, 3.4 și 5(i)).
- Codul plătit, când va exista, stă într-un repo privat separat; aici rămâne vitrina.

## Verificare
Fiecare raport separă: verificat (comandă + rezultat) · neverificat · blocat.
