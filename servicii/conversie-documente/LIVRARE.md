# Procedura de livrare și controlul calității

Cine face ce: Claude face conversia și verificarea. Alexandru acceptă comanda, trimite fișierele în chat și predă rezultatul pe platformă.

## Pași
1. **Mostră:** înainte de ofertă, Claude citește o pagină și confirmă lizibilitatea. Dacă peste 5% din celule sunt nesigure, prețul crește sau se refuză.
2. **Extragere, trecerea 1:** citire asistată de AI (Claude, vizual). OCR-ul clasic (tesseract) se folosește doar ca semnal secundar, pentru că pe tabele cu grilă eșuează (vezi `demo/`).
3. **Extragere, trecerea 2:** recitire independentă a valorilor numerice. Orice diferență între treceri se rezolvă privind din nou imaginea, la zoom.
4. **Pentru Word / Google Docs:** trecerea a doua compară textul cu sursa, pagină cu pagină: numărul de paragrafe, titluri și elemente de listă, apoi ordinea lor. Diferențele se corectează înainte de livrare.
5. **Verificări aritmetice în Excel**, cu formule, nu calculate „de mână”:
   - cantitate × preț = valoare;
   - suma rândurilor = totalul tipărit pe document.
6. **Livrare:** fișierul, foaia „Note” cu sursa și lista celulelor `[ILIZIBIL]` (sau „nimic ilizibil”), plus un mesaj scurt cu rezultatul verificării.

## Criterii de acceptanță (înainte de predare)
- [ ] Toate rândurile din sursă există în fișier (număr de rânduri identic).
- [ ] Coloana „Diferență” e 0 peste tot sau fiecare abatere e explicată în „Note”.
- [ ] Suma rândurilor e egală cu totalul tipărit pe document (unde există).
- [ ] Numerele sunt stocate ca numere, nu ca text, în formatul cerut (1,234.56 sau 1.234,56).
- [ ] Nicio valoare ghicită: tot ce e nesigur apare ca `[ILIZIBIL]`.
- [ ] Word / Google Docs: titlurile, listele și ordinea paragrafelor corespund sursei; numărul de paragrafe pe pagină a fost comparat.
- [ ] Fișierul se deschide corect în LibreOffice; Excel nu e disponibil pentru verificare.

## Date și confidențialitate
- Fișierele clientului nu intră în acest repo public. Copiile de lucru din spațiul temporar al sesiunii se șterg după livrare.
- Conversia se face cu Claude (Anthropic), prin contul Claude **Pro** al lui Alexandru, un produs pentru consumatori. Retenția la furnizor, conform paginii Anthropic „How long do you store my data?” (verificată 2026-10-14):
  - o conversație ștearsă dispare imediat din istoric și e eliminată din sistemele de backend **în cel mult 30 de zile**;
  - dacă setarea de antrenare a modelelor e **activă**, conversațiile pot fi păstrate de-identificat **până la 5 ani**;
  - dacă un chat e semnalat pentru încălcarea politicii de utilizare, datele pot fi păstrate până la 2 ani.
- **Condiții înainte de prima comandă:**
  1. setarea de antrenare a modelelor („Help improve Claude”) e **oprită** în contul folosit;
  2. fiecare comandă se lucrează într-o conversație separată, ștearsă după livrare.
  Fără ele, FAQ-ul din `GIG.md` nu e adevărat și nu se acceptă fișiere.
- Clientului îi spunem asta înainte să primim fișierele (textul e în `GIG.md`, la FAQ). Refuzăm documentele cu date sensibile: identitate, medicale, financiare personale.
