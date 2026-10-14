# Decizii radar

## 2026-10-14 — Apify Store: nimic de construit

**Verdict:** PACHET-2 (actor Apify) se oprește ca produs de venit. Se reia doar dacă un radar ulterior găsește o nișă care trece pragul.

**Date:** `radar_apify_2026-10-14.csv`, obținute din API-ul public Apify Store.
- Am scanat primii 6.065 de actori după popularitate, din 87.158.
- Din ei am selectat 18 nișe în care liderul **din această primă trecere** era slab: rată de eșec ≥10% sau rating <4. Unele nișe le-am căutat cu un termen mai larg (de exemplu „impressum”, „email pattern”, „enrich google maps”).
- Pentru fiecare nișă am căutat în tot Store-ul și am numărat concurenții activi.
- Coloana `lider` din CSV e liderul găsit de căutarea în tot Store-ul. În mai multe nișe (de exemplu sofascore, coles) acesta e alt actor, mai puternic decât cel care a dus la selecție. Asta întărește verdictul: nișele sunt mai ocupate decât arăta prima trecere.

**Pragul:** liderul are ≥20 utilizatori pe 30 de zile, iar nișa are ≤3 concurenți activi (cu ≥5 utilizatori pe 30 de zile). Rezultat: 0 nișe din 18 trec.

**Cele mai apropiate de prag:**

| Nișă | Concurenți activi | Utilizatori/30 zile, total nișă | Eșecul liderului |
|---|---|---|---|
| pagesjaunes | 4 | ~107 | 37% |
| Udemy | 4 | ~89 | 28% |
| sitemap | 5 | ~223 | 32% |

**Venit estimat** pentru cel mai bun caz: ~20–60 $/lună brut, înainte de costul de compute. E aproape de pragul de plată de 20 $.

**Motiv:** piața e saturată de producători automați. Cererea pentru nișele slab servite e mică (~100–200 de utilizatori pe lună în toată nișa).

**Unghi orb cunoscut:** Store-ul nu arată cererea neservită, adică site-urile pentru care nu există încă actor. Ea se măsoară din cererile repetate pe Upwork și Fiverr, în FLUX-2, partea 2.

**Condiție de redeschidere:**
- o nișă trece pragul; sau
- apare o comandă plătită care cere un actor; atunci actorul se construiește pe banii clientului și se publică după aceea.

## 2026-10-14 — Cererea din emailuri (FLUX-2, partea 2)

**Date:** `cerere_freelancer_2026-10-14.csv` conține 75 de proiecte din 8 digesturi Freelancer.com primite în perioada 6–14 oct. Digesturile sunt filtrate după competențele din profil (PDF, Data Entry, Excel), deci arată cererea pentru acest profil, nu toată piața. Upwork și Fiverr n-au trimis alerte de proiecte în perioada asta.

| Categorie | Proiecte | Pondere |
|---|---|---|
| PDF/scan → Word/Docs/TXT | 27 | 36% |
| PDF/scan/formulare → Excel | 16 | 21% |
| Scraping / extragere web | 7 | 9% |
| Automatizare / utilitar custom | 6 | 8% |
| Altele (design, recovery, nepotrivite) | 19 | 25% |

**Ce reiese:**
- **57% din cerere e conversie de documente** (PDF sau scan → format editabil). E exact serviciul „PDF în Excel/Word” planificat pe Fiverr.
- 4 proiecte cer explicit lucru manual, fără OCR. Pe acestea le refuzăm: regula Fiverr cere respectarea cererilor „fără AI”, iar asta aplicăm peste tot.
- Bugetele sunt intervale alese de client dintr-o listă fixă a platformei (de exemplu €14–117 sau €117–350), nu prețuri efectiv plătite. Ofertele câștigătoare sunt de obicei sub mijlocul intervalului.

**Verdict:** pista cu cerere repetată e conversia de documente. Prioritatea trece pe:
1. pachet de serviciu „PDF/scan → Excel/Word” pe Fiverr și Freelancer.com;
2. utilitarul `pdf-batch-excel`, ca unealtă internă de producție (nu ca produs separat).
