# Lectii de testare — NISHIAI (se actualizeaza la finalul fiecarei sesiuni de testare)

> **Procesul recursiv (obligatoriu, 3 pasi la final de sesiune de testare):**
> 1. ce a mers prost sau a surprins → **o linie noua aici**, cu declansatorul („cand X → atunci Y");
> 2. ce poate fi verificat mecanic → **adauga verificarea in `test_preflight.py`**, nu doar text;
> 3. commit + push (Arena si magazinele de cod vad aceeasi realitate).
> O lectie care exista doar in memorie/poveste nu opreste nimic — doar ce e in preflight sau in cod se re-verifica singur.

## Mediu (E1-E8)

- **E1 · Cand pornim unelte binare pe cai scrise de utilizator → Application Control le poate bloca** (CfT `chrome.dll` 0x11C7 din 7 oct; fontTools `iup.pyd`; llvmlite). Ruleaza `test_preflight.py` INAINTE de sesiune. Alternativa verificata: Edge (semnat, in Program Files). Pentru .pyd cu fallback pure-Python: redenumire `.pyd.disabled`.
- **E2 · Cand testam content script-uri → headless (old si new) pe Edge NU injecteaza; foloseste fereastra normala (headful).** Verificat 7 oct: headful injecteaza, ambele headless nu.
- **E3 · Cand masori comportamentul content script-ului → markerul lui (`window.__consentDeclinerClicked` etc.) e in LUMEA IZOLATA, invizibil din main-world.** Masoara doar efecte in main-world: handler-ele onclick ale paginii (`window.__rejectClicked`), disparitia elementelor din DOM.
- **E4 · Cand vrei sa verifici/locuiesti `chrome.storage` → NU exista in main-world-ul paginii** (doar in SW si lumea izolata). Gate-ul de storage se verifica din service worker-ul extensiei prin CDP, nu prin injectare in pagina.
- **E5 · Service worker-ul MV3 apare leneș pe profil proaspat** → naviga mai intai (evenimentele il trezesc), apoi retry ~15s pe /json/list; selecteaza SW-ul EXTENSIEI tale (dupa numele fisierului, ex. `/bg.js`), niciodata primul SW din lista (Edge are built-in-uri cu SW proprii).
- **E6 · WebSocket CDP → adauga mereu `--remote-allow-origins=*`** in instanta de test (altfel handshake 403).
- **E7 · Procesele browser de test supraviețuiesc uciderii launcher-ului (Edge/Chrome fork-uiesc)** → curatenie doar cu filtru `Win32_Process -Filter "Name='msedge.exe' or Name='chrome.exe'"` + match pe CommandLine-ul profilului de test. ATENTIE: filtrul PowerShell trebuie sa aiba filtre de nume — pattern-ul aplicat neordonat se potriveste pe propriul sau command line si se auto-ucide (session moarta, procese ramase).
- **E8 · `wmic` NU mai exista pe Win11 24H2** → `Get-CimInstance Win32_Process`.

## Flux de test (F1-F4)

- **F1 · Profil de test proaspat → inainte de `rm -rf` omoara procesele care il tin** (lockfile „Device or resource busy" = proces viu). Profilurile nu se comit in repo.
- **F2 · La fiecare verificare, intreaba: ce vad daca sunt GREȘIT?** Lecția 7 oct: primul „default OFF" raportat a trecut din greșita cauza (scriptul nici nu rulase din cauza E4, nu pentru că poarta funcționa). Măsoara ambele ture (OFF și ON), nu doar cea care intereseaza.
- **F3 · Suportul de test e parte din produs**: `test_activation.py` (edge|cft), `test_e2e.py`, `test_exporter.py`, `test_preflight.py` — se comit, se ruleaza dupa fiecare schimbare de produs, nu „cand se poate".
- **F4 · Canale externe (chat Arena, browser IAB)**: nu tasta automat intr-o fereastra activa pe desktopul utilizatorului (tastele lui ajung in compozitor); bannerul „This chat changed… Refresh" = pagina stale, refresh-ul ȘTERGE draft-ul; panoul „Was this task successful?" se închide pe coordonate („Keep working").

## Istorie
- 2026-10-07: prima completare — din rundele CfT-blocked / Edge headless / headful (E1-E8, F1-F4). Preflight creat.
