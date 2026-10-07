Verificarea din 2026-10-07 confirmă commitul curent (istoric, la data planului) 1a03e6836c2b680066fbb90cea18faea7dbbbd9a și blobul docs/colaborare.md 02b5b6900b013a356cd9daf796981a4cb8239b90.

Plan independentă de verificare înainte de publicare

Limită importantă: acesta este un plan de consultare, nu un raport de testare și nu o implementare. Repo-ul local nishiai-apps nu este conectat la sesiune; nu am rulat produsele, nu am descărcat corpusuri și nu am creat sau modificat fișiere. HTTPS prin instrumentele web a funcționat, așa că am verificat documentație și metadate publice. Nicio publicare, ramură sau PR înainte ca Alexandru să vadă și să aprobe planul complet.

Starea dovezilor
Stare	Ce înseamnă aici
verificat-Arena	SHA-ul commitului și blobului; pagini publice, documentație și metadate de licență/corpus menționate mai jos. Verificarea metadatelor nu înseamnă că am descărcat sau inspectat fișierele de date.
verificat-ZCode	Nicio rulare nu poate fi încadrată astfel în această sesiune: nu am primit loguri sau artefacte de test pentru verificare.
neverificat	Codul, build-urile, comportamentul produselor, datele efective din corpusuri și istoricul testelor raportat de ZCode/utilizator. Rămâne valabil ca raportare, nu ca rezultat reprodus independent.
blocat	Verificarea independentă a produselor este blocată de lipsa repo-ului și a build-urilor. Pentru unele praguri mai trebuie înghețate contractul de ieșire, permisiunile și dispozitivul minim acceptat.

Așadar, istoricul raportat — pdf-batch-excel cu 9/9 pytest și 3 demo-uri, Table Exporter cu un E2E, Consent Decliner cu testare minimală și CSV Viewer cu o probă pe emulator — este un punct de pornire neverificat, nu o aprobare de publicare.

Reguli comune pentru toate cele patru produse
Înghețăm contractul și versiunea înainte să măsurăm. Pentru fiecare test se notează commitul/buildul, sistemul și versiunile de toolchain, testul, rezultatul așteptat și cel observat.
Fiecare fișier public de test primește manifest: URL exact, autor, licență, data accesării/descărcării, dimensiune, SHA-256, format, codare/delimitator și versiunea etalonului. Metadatele găsite online sunt candidați de corpus, nu confirmarea că fișierul brut este disponibil sau identic.
Facturile brute nu intră în repo public și nu se pun în chat. Pentru orice set real, Alexandru aprobă proveniența, licența, tratarea PII și locul de stocare. În repo public rămân doar fixtures sintetice și, dacă este sigur, manifesturi/hash-uri fără valori sensibile.
„100%” se referă numai la matricea finită înghețată: toate cazurile declarate, pentru versiunile și dispozitivele testate, au trecut. Nu promite toate facturile, site-urile, browserele, codările sau telefoanele reale.
Gate comun de publicare: pragurile aprobate sunt trecute; nu există defecte P0/P1 deschise; excepțiile P2 au owner și acceptare explicită; licența/PII și declarațiile de store au fost aprobate de Alexandru. Review-ul unui store nu substituie testarea funcțională.
1. pdf-batch-excel
Riscuri
PDF digital, PDF scanat fără strat de text, multipagină, diacritice, PDF criptat/deteriorat și documente cu text plasat într-o ordine neobișnuită pot da rezultate diferite. pdfplumber spune că funcționează cel mai bine pe PDF-uri generate digital, nu pe scanări. 1
Pentru scanările fără text, planul trebuie să verifice explicit că produsul raportează needs_ocr, nu un ok înșelător. Nu presupun că produsul implementează OCR.
Un PDF nevalid sau foarte mare poate provoca excepții, blocare ori consum excesiv de resurse; parserul trebuie tratat ca procesare de input neîncredere.
Hot-folder-ul poate vedea fișierul cât încă se copiază, poate procesa același eveniment de două ori sau poate suprascrie un rezultat cu același nume.
Textul extras dintr-un PDF poate ajunge în XLSX ca formulă, nu ca text. OWASP avertizează că celulele care încep cu =, +, -, @ și anumite caractere de control pot fi interpretate de aplicații de spreadsheet; simpla încapsulare în ghilimele nu este întotdeauna suficientă. 1
Blocaj de contract: din descriere nu reiese schema exactă XLSX și ce înseamnă „corect” pentru rânduri/celule. Alexandru și ZCode trebuie să fixeze întâi coloanele, normalizările permise și semantica fiecărui status.
Corpus
Set real local, cu permisiune: propun minimum 30 PDF-uri cu text digital, de la cel puțin 6 furnizori (minimum 5 per furnizor), cu cel puțin 10 documente multipagină și cel puțin 10 cu diacritice românești. Ground truth-ul se face manual și se păstrează controlat local; nimic brut în repo public.
Scanări/OCR: minimum 10 PDF-uri scanate, cu cel puțin 3 layout-uri/furnizori, pentru testarea clasificării needs_ocr. Imaginile publice se pot împacheta local într-un PDF sintetic numai pentru traseul „PDF-imagine”; asta nu le transformă în probe ale structurii unor PDF-uri native reale.
Candidatul MIDD: articolul descrie 630 de facturi scanate PDF, patru layout-uri și licență CC BY 4.0. 5 Însă înregistrarea Zenodo listează doar IOB.rar, de aproximativ 1,1 MB, nu fișierele PDF brute descrise în articol. 1 Nu îl folosim drept corpus de PDF-uri până când ZCode nu inspectează arhiva și nu confirmă conținutul, proveniența și riscul PII.
Imagini reale portugheze: Zenodo are 813 imagini de facturi și bonuri de la o companie privată, CC BY 4.0, cu câmpuri precum adresa și identificatorii fiscali ai părților. Sunt imagini, nu PDF-uri, iar licența nu elimină riscul de PII; numai utilizare locală, după examinare de confidențialitate, fără upload în repo public. 1
FATURA: 10.000 de imagini JPG generate din 50 de template-uri, CC BY 4.0. E util pentru diversitate sintetică de layout și comparații OCR, dar nu dovedește performanță pe facturi reale și nu testează parserul de PDF nativ. 1
Cazuri criptate, deteriorate, cu pagini multiple, duplicate de nume și date de formulă se generează sintetic. Nu se folosesc facturi reale criptate pentru acestea.
Metodă
ZCode rulează suita existentă nemodificată, apoi testează fiecare clasă de intrare cu un manifest și un expected-output controlat.
Pentru PDF-uri reale se compară XLSX-ul cu un golden set verificat manual; se separă testele pe PDF digital de cele pe scanări.
Pentru qpdf --check se poate valida sintaxa/structura PDF-urilor de fixture, dar documentația precizează că verificarea este parțială și nu stabilește corectitudinea semantică a paginii. 3
PyMuPDF poate servi drept comparație de extragere independentă de pdfplumber; nu este un oracle al „adevărului” și nu înlocuiește golden set-ul. 1
Rulare locală: python -m pytest -q, dacă acesta este task-ul real din repo; apoi comenzile CLI/watcher preluate din README-ul proiectului. Comenzile exacte și versiunile încă trebuie verificate.
Audit de dependențe cu pip-audit și analiză statică Python cu Bandit. Primul caută vulnerabilități cunoscute ale dependențelor, iar al doilea probleme comune în cod; niciunul nu certifică securitatea aplicației. 1 1
Bară de acceptanță propusă
Contractul XLSX și normalizările sunt aprobate înainte de evaluarea datelor reale.
30/30 PDF-uri digitale din corpusul aprobat produc statusul așteptat și corespund integral golden set-ului pentru câmpurile/valorile convenite. Pentru facturi, câmpurile critice din schema aprobată — de exemplu număr, dată și total, dacă sunt în scope — au 100% potrivire exactă pe acest set; nu se compensează o valoare greșită printr-o medie bună pe alte câmpuri.
10/10 scanări sunt clasificate needs_ocr; 5/5 criptate și 5/5 deteriorate ajung în error conform contractului, fără crash sau blocare. Pentru fiecare input există exact o înregistrare finală în errors.csv; niciun fișier nu dispare și nu este numărat de două ori.
Cel puțin 10 cazuri multipagină păstrează toate paginile/rândurile incluse în contract; Unicode/diacriticele din câmpurile etalon rămân exacte.
Testul hot-folder rulează 100 operații de fișier în 3 repetări: fără rezultate pierdute/duplicate, procesare a copiei parțiale sau suprascriere neintenționată.
10 valori adversariale care ar putea deveni formule în XLSX rămân text literal la deschidere în Excel sau LibreOffice; niciuna nu devine formulă activă.
Zero P0/P1 deschise; nicio vulnerabilitate critic��/nivel înalt fără remediere ori excepție explicit acceptată.
Ce rulez local (ZCode)
Suita curentă, apoi matricea de fixtures și corpusul real aprobat, pe commit/build identificat.
Teste separate pentru PDF digital, scanări, multipagină, diacritice, criptare, deteriorare și watcher.
Auditul XLSX pentru formule și raport pip-audit/Bandit.
Livrez Arena loguri și sumar fără date brute, plus manifestul și hash-urile; facturile rămân local.
Ce faci tu (Arena)
După ce repo-ul sau build-ul este disponibil în mod read-only, verific independent scripturile și reproduc un eșantion din testele aprobate, comparând output-ul cu golden set-ul.
Revizuiesc dacă manifestul separă corect PDF digital/scanat/sintetic și dacă raportul de test nu dezvăluie PII.
În această sesiune nu am rulat produsul și nu pot confirma niciunul dintre rezultatele raportate.
Riscul rezidual care rămâne

Un set de 30–40 de documente nu acoperă toate fonturile, furnizorii, scanerele, rotațiile, formularele sau structurile PDF viitoare. MIDD rămâne un candidat blocat până la confirmarea arhivei brute; imaginile portugheze pot să nu reprezinte documente românești. Nu se poate afirma „citește toate facturile”.

2. Table Exporter — extensie Chrome MV3
Riscuri
Un <table> static este diferit de un grid construit în DOM, SPA încărcat asincron, tabel virtualizat, tabel cu rowspan/colspan, iframe sau shadow DOM.
La un tabel virtualizat, pagina poate păstra în DOM numai rândurile vizibile; exportul lor fără avertisment ar arăta complet, dar ar fi incomplet.
Cross-origin iframe-ul și closed shadow DOM pot fi inaccesibile; trebuie fie declarate suportate cu permisiuni potrivite, fie raportate clar ca nesuportate.
Celulele pot conține diacritice, newline-uri, text ascuns sau șiruri care devin formule în CSV/XLSX.
Un export de pagină poate conține date private. Extensia nu trebuie să transmită ori să păstreze rândurile în afara funcției descrise.
Corpus
24 fixtures locale deterministe: tabel simplu, mai multe tabele, thead absent, rowspan/colspan, nested table, Unicode românesc, celule goale/duplicate, tabel ascuns, DOM care se schimbă după click, scroll virtualizat, iframe same-origin/cross-origin și open/closed shadow DOM. Cazurile nesuportate trebuie să aibă rezultat așteptat explicit, nu să fie tratate ca succes.
Minimum 12 pagini live, din cel puțin 8 domenii, fiecare cu URL, tabelul ales, limbă/profil, timestamp și 10 celule-etalon. Puncte de pornire concrete: pagina interactivă Eurostat demo_pjan și tabelul static de populație de pe Wikipedia. Sunt puncte de pornire pentru revalidare, nu pagini testate acum; conținutul și structura lor se schimbă. Eurostat demo_pjan 1
Paginile live nu înlocuiesc fixtures; păstrăm snapshots numai dacă licența și condițiile site-ului permit și fără cookies/session data.
Metodă
E2E pe extensia construită și încărcată în Chrome, cu pași de utilizator: instalare/test profile → tab → detectare → selectarea tabelului → export → verificarea fișierului descărcat. Documentația Chrome descrie E2E pe extensia încărcată în browser și indică Puppeteer/Playwright/Selenium ca opțiuni. 1
Se includ latențe/rerender-uri SPA, service-worker restart, permisiune refuzată, zero tabele și tabele virtualizate.
Se auditează manifest.json: activeTab și permisiuni opționale, acolo unde designul le permite, în locul unor host permissions mai largi. 1
Exporturile se verifică în formatul real livrat. CSV-ul se verifică separat pentru formula injection conform OWASP. 1
Bară de acceptanță propusă
24/24 fixtures locale: valorile, ordinea și numărul de rânduri/coloane corespund exact pentru funcțiile declarate suportate.
12/12 pagini live au rezultat corect pentru toate cele 10 celule-etalon sau afișează explicit „parțial/nesuportat”; nu acceptăm export parțial etichetat drept complet. Prag propus pentru celule-etalon în fluxurile suportate: ≥98%, dar zero erori în celulele marcate critice și zero trunchieri tăcute.
10 payload-uri de formulă se exportă fără execuție; permisiunile din manifest sunt justificate de funcția afișată.
Zero P0/P1 de extragere greșită, scurgere sau permisiune nejustificată. E2E trebuie să acopere fiecare flux de utilizator; pentru comanda exactă de test se folosește scriptul real din repo, nu unul presupus.
Ce rulez local (ZCode)
E2E Chrome pe extensia împachetată și matricea de 24 fixtures.
Parcurgerea celor 12+ pagini live în profil Chrome curat, notând doar sentinel cells și rezultatul; nu colectez în log dump-uri brute.
Raport manifest permissions și cazuri în care funcția refuză explicit suportul.
Ce faci tu (Arena)
După acces read-only la repo/build, verific independent E2E-urile, permisiunile și output-ul pentru fixtures; apoi reproduc câteva pagini publice, dacă sunt accesibile și condițiile permit.
Revizuiesc că aplicația nu declară „complet” un export de grid virtualizat dacă a citit doar rândurile prezente.
Chrome Web Store are politici de privacy/limited use și un proces de review, dar review-ul este pentru conformitate și siguranța store-ului, nu dovadă că toate paginile se exportă corect. 2 1
Riscul rezidual care rămâne

Site-urile își schimbă DOM-ul, limbile, permisiunile și variantele A/B. Nu se poate garanta extragerea corectă din toate paginile. Orice suport pentru iframe, shadow DOM sau virtualizare trebuie limitat la ce a trecut matricea și prezentat utilizatorului fără a sugera că este universal.

3. Consent Decliner — extensie Chrome MV3
Riscuri
Riscul major este click-ul greșit: „Accept all”, „Save”, „Manage preferences” sau un buton de newsletter/login nu echivalează cu respingerea.
Bannerul poate apărea târziu, se poate re-randa, poate fi în iframe, sau aceeași semnătură DOM poate fi configurată diferit pe două domenii.
Închiderea bannerului nu dovedește că opțiunile opționale au fost refuzate și nici că site-ul nu mai pornește trackere.
Corpus și selecția CMP-urilor

Cotele servesc la selectarea acoperirii, nu la promisiuni despre un site anume:

Un studiu HTTP Archive pentru top 1M din decembrie 2023 a raportat, în acel eșantion de CMP-uri, OneTrust 27,6%, Google Funding Choices 16,1% și Cookiebot 7,3%. 1
Un studiu cross-country din 2025 a găsit 115 CMP-uri; Usercentrics, CookieYes și OneTrust însumau 37,57% în corpusul acelui studiu. 1
Un crawler comercial din 2026 raportează, în propria categorie/denominator, CookieYes 21,13%, Cookiebot 7,79% și OneTrust 4,52%; nu sunt procente comparabile direct cu studiile academice. 3 1 2

Propun ca matricea v1 să acopere OneTrust, Cookiebot, Usercentrics, CookieYes, Didomi și Quantcast/InMobi Choice — numai când varianta de pe site este efectiv identificată. Un repo terț oferă ca seed-uri Reuters, BBC, Stack Overflow, Spiegel, Booking și Shopify, dar lista aceea nu confirmă CMP-ul live în prezent; fiecare URL trebuie revalidat cu profil curat. 1

Metodă
Teste locale cu 24 fixtures: etichete clare, limbile română/engleză/germană, „reject all” separat de „manage/save”, butoane cu texte ambigue, bannere late/rerender, modal fără banner, element ascuns și false-positive controls.
Teste live în profil Chrome de unică folosință: minimum 12 site-cases, cel puțin două domenii independente pentru fiecare dintre cele șase ținte. Se înregistrează starea bannerului și decizia observată; nu se păstrează cookie-uri, identificatori sau istoric de navigare.
Înainte/după click se verifică starea din interfața CMP sau, unde există, API-ul/starea de consimțământ relevantă. Nu se consideră „succes” doar dispariția bannerului.
Recomandare de siguranță: default-ul pentru CMP necunoscut, banner ambiguu sau respingere indisponibilă trebuie să fie nu face click. Înainte de release, Alexandru trebuie să fixeze și modelul de activare: click explicit al utilizatorului sau automatizare opt-in. Eu recomand activare explicită pentru o decizie cu efect pe site.
Se testează Chrome E2E cu extensia instalată, nu doar funcții/unit tests. Permisiunile și transparența sunt gate de CWS. 1 1
Bară de acceptanță propusă
24/24 fixtures trec; pentru fiecare variantă suportată, acțiunea executată este respingerea intenționată și toate scopurile opționale sunt dezactivate în starea verificabilă.
12/12 site-cases suportate trec în profil curat. Nicio acceptare accidentală.
50 controale negative — fără banner, dialog de newsletter, „agree” fără legătură cu consimțământul și pagini cu elemente ambigue — au zero click-uri.
Necunoscut/ambiguu = no-click 100% în fixtures și manual. Dacă pagina nu oferă respingere clară, produsul raportează că nu a acționat și lasă decizia utilizatorului.
Zero P0/P1 de misclick, selectare greșită sau transmitere de browsing data. Nu se afirmă că produsul asigură conformitatea juridică a site-ului ori că blocarea de trackere funcționează.
Ce rulez local (ZCode)
E2E pe fixtures, apoi pe profil Chrome de unică folosință pentru corpusul live; fiecare site pornește cu consimțământ curat.
Raportez pentru fiecare caz: CMP identificat, variantă/limbă, acțiunea așteptată, acțiunea observată și motivul pentru no-click; fără valori de cookie în log.
Verific că trigger-ul și manifestul corespund scopului pe care îl va vedea utilizatorul în store.
Ce faci tu (Arena)
După ce build-ul/repo-ul este disponibil, verific separat fixture-urile de false-positive și red flags pentru butoane de acceptare.
Reproduc un eșantion de flows și verific că un rezultat nesigur devine no-click, nu fallback la alt buton.
Revizuiesc declarațiile/politicile CWS; acestea cer limitarea folosirii datelor la scopul declarat, iar review-ul nu substituie testarea pe site-uri. 1 2
Riscul rezidual care rămâne

Există un „long tail” de CMP-uri, configurări proprii, A/B, geolocație și limbi. Chiar și o decizie de respingere corectă în UI nu dovedește că site-ul oprește toate trackerele; asta depinde și de implementarea site-ului. Suportul rămâne cel mult pentru combinațiile site/variantă/CMP verificate, iar site-urile se pot schimba după test.

4. CSV Viewer — Android Kotlin/Compose
Riscuri
CSV este un format cu variații de delimiter și quoting; RFC 4180 este referință pentru quoting, ghilimele și newlines, nu acoperă toate dialectele reale. Portalul european de date explică explicit diferența dintre separatorul virgulă, ; folosit în unele locale și TSV cu tab. 1 1
Codare greșită poate strica diacriticele; rânduri malformate pot deplasa coloane; parsarea întregului fișier în memorie poate duce la freeze/OOM.
Viewer-ul nu trebuie să evalueze formule — trebuie să afișeze valoarea ca text.
SAF folosește URI-uri și granturi de acces; fișierul poate fi mutat, șters sau grantul poate deveni invalid. Documentația Android precizează că grantul persistent nu păstrează accesul dacă documentul este mutat sau șters. 1 2
Corpus

Candidați publici pentru testare, încă nedescărcați și neverificați local:

data.gov.ro — „Parc auto COMBUSTIBIL la 31.12.2025”, CSV, metadate cu licență OGL-ROU-1.0 și dimensiune 23.920.408 bytes. Pagina notează verificarea linkului la 15 ianuarie 2026; linkul și checksum-ul trebuie reverificate înainte de fixarea corpusului. 1
OurAirports — airports.csv, 12.741.155 bytes la 6 octombrie 2026, declarat public domain; sursa avertizează că datele nu au garanție de acuratețe. Potrivit pentru volum/parsing, nu pentru validare de domeniu. 1
UCI Wine Quality — date reale despre probe de vin, licență CC BY 4.0; fișierele red/white sunt candidați pentru un CSV cu separator ;, care trebuie confirmat pe fișierul exact la pinning. 1 2
Eurostat — demo_pjan ca tabel real și TSV/SDMX-CSV pentru acoperire cu tab/delimitere oficial documentată. Eurostat indică și condițiile sale de reutilizare; trebuie păstrate atribuirea și orice condiții specifice setului. 1 1
Localități România, geo-spatial.org — metadatele descriu variante CSV UTF-8, ISO-8859-2 și plain; setul reflectă situația din 2008, potrivit pentru test de parser/diacritice, nu pentru actualitatea datelor. Fișierul concret trebuie verificat înainte de includere. 1
Pentru UTF-16LE/BE cu BOM, quoting malformat, newline în câmp, ragged rows, BOM UTF-8 și payload-uri de formulă: fixtures sintetice deterministe. csv-spectrum oferă fișiere cu JSON etalon și are licență BSD-2-Clause, dar nu înlocuiește testele cu fișierele reale de mai sus. 2 3
Metodă
Matrice de fixtures: UTF-8 fără BOM, UTF-8 BOM, ISO-8859-2, UTF-16LE/BE BOM; delimitatori ,, ;, tab; quotes doubled, quoted newline, newline CRLF/LF, headers duplicate, rânduri neregulate și fișier gol.
Pentru fiecare fișier există expected record count, column count și celule-etalon la început/mijloc/final. Pentru fișierul mare se verifică și sampling din rânduri aleatorii.
Trasee SAF: Downloads/document provider, URI cloud dacă providerul este disponibil în mediul de test, anularea picker-ului, acces revocat/fișier șters, force-stop și redeschidere după restart. Verificăm acces prin URI, nu presupunem un path filesystem.
Paging/lazy loading pentru afișarea incrementală; Android recomandă încărcarea paginată/lazy pentru liste mari pentru a reduce memoria și timpul inițial. 4
Pentru Play, se verifică pre-launch report și Data safety. Google precizează că pre-launch report nu garantează identificarea tuturor problemelor; Data safety trebuie să reflecte exact colectarea și procesarea, inclusiv SDK-uri terțe. 1 2 1
Bară de acceptanță propusă

Pragurile de performanță sunt propunere, nu rezultate; trebuie înghețate după declararea minSdk, dispozitivului minim și dimensiunii maxime suportate.

100% fixtures deterministe: celule, delimitator și codare exacte; cazurile malformate au eroare/avertizare explicită, fără crash și fără deplasare silențioasă a coloanelor.
Cel puțin 4 lucrări SAF trec: selectare și deschidere, force-stop/reopen cu grantul prevăzut, anulare picker și fișier/grant indisponibil, care produce mesaj recuperabil, nu crash.
Prag provizoriu: fișier real de 25 MiB pe cel mai slab telefon fizic suportat — ecran inițial în cel mult 5 secunde, fără ANR/OOM, rândurile inițiale și finale accesibile și corecte. Fișier sintetic de 50 MiB: ecran inițial în cel mult 10 secunde, memorie PSS sub 256 MiB pe dispozitivul baseline propus cu 4 GB RAM și scroll până la final în cel mult 60 secunde. 100 MiB rămâne stress/stretch până este aprobată o promisiune de suport.
Trei deschideri repetate și un scroll complet fără ANR/OOM; nu se declară suport peste plafonul efectiv măsurat.
Payload-urile =, +, -, @ și newline/tab se afișează ca text literal; viewer-ul nu evaluează formule și nu transmite datele fișierului în rețea.
Ce rulez local (ZCode)
Confirm task-urile reale din repo (./gradlew tasks, apoi unit/instrumentation/UI tests și lint, dacă există); nu presupun că numele task-urilor sunt standard.
Rulez corpusul pe emulatorul deja folosit și cel puțin un telefon fizic conform minSdk; capturez versiunea Android, modelul, RAM-ul, timpul inițial și PSS.
Verific SAF după force-stop/restart și revocarea accesului; țin fișierele de test pe dispozitiv local, nu le trimit în loguri.
Ce faci tu (Arena)
După acces la APK/repo și sumarul local, reproduc fixtures-urile de codare/delimitator și revizuiesc traseul SAF și scorurile de memorie/performance.
Verific manifestul pentru permisiuni largi inutile și compar Data safety cu comportamentul observabil. În acest moment, nici build-ul Android, nici proba pe emulator nu sunt reproduse de Arena.
Riscul rezidual care rămâne

Provider-ele SAF se comportă diferit, iar anumite URI-uri expiră sau depind de conectivitate. CSV-urile reale pot avea dialecte și inconsistențe neprevăzute. Un test pe un singur emulator nu garantează comportamentul pe dispozitive Android reale sau fișiere mai mari decât plafonul aprobat.

Ordinea de execuție și blocajele de publicare
Blocaje înainte de publicare
Toate produsele: acces la repo/build identificat, baseline reproductibil, criterii aprobate de Alexandru și loguri fără secrete/PII.
PDF: contract XLSX/status înghețat; proveniență și aprobare PII pentru setul local; MIDD nu este acceptat drept PDF corpus până la inspectarea arhivei; teste pe multipagină/diacritice/watcher și celule de formulă.
Table Exporter: matrice de suport pentru griduri virtualizate/iframes/shadow DOM; E2E pe extensia instalată; justificarea permisiunilor și testul de formula injection.
Consent Decliner: Alexandru aprobă explicit modul de activare; unknown/ambiguous = no-click; minimum de CMP-uri și false-positive cases trece fără misclick.
CSV Viewer: minSdk, dispozitiv baseline și limita de dimensiune sunt fixate; SAF, encoding și malformed fixtures trec; raportul de store descrie exact datele procesate.
Ce poate fi făcut în paralel după aprobarea planului
ZCode poate rula suitele existente nemodificate, inventaria testele curente și pregăti fixtures sintetice/manifeste. Pregătirea unui corpus real se face numai după verificarea licenței și PII. Nu se adaugă teste în cod, nu se schimbă produsul și nu se deschide PR fără aprobarea de scope.
Arena poate revizui separat sursele publice, permisiunile și raportul de testare. Pentru reproducerea efectivă a produselor, Arena are nevoie de repo/build sau artefact reproductibil.
Identificarea site-urilor live și colectarea metadatelor poate începe în paralel; nu se presupune că un banner/CMP văzut în trecut este încă prezent.
Următorii pași și owner
Alexandru — acum: aprobă sau ajustează pragurile, schema XLSX, modul de activare Consent Decliner, dispozitivul minim Android și politica de corpus/PII. Până atunci, publicarea este blocată.
ZCode — după aprobarea planului: furnizează commit/build și scripturile reale de testare; rulează baseline-ul nemodificat și pregătește manifestul de corpus fără PII.
Arena — după ce există artefacte: reproduce independent matricea agreată pe fixtures și pe eșantionul permis; raportează rezultatele cu stările verificat-Arena, verificat-ZCode, neverificat, blocat.
Alexandru — final: decide publicarea numai după trecerea gates și acceptarea riscurilor reziduale. „100%” se poate afirma doar pentru setul finit și versiunea declarate, nu pentru lumea deschisă.