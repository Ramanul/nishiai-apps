# Table Exporter — Chrome Web Store listing

Câmpurile de mai jos se copiază în Developer Dashboard. Pachetul: `store/dist/table-exporter-<versiune>.zip`
(generat cu `python store/build_packages.py`, fără câmpul `key`).

## Store listing (English, default)

**Name** (max 75): Table Exporter — tables to CSV

**Summary** (max 132):
Export every table on the current page to a clean, formula-safe CSV in one click. Runs 100% locally, no account, no tracking.

**Description:**

Table Exporter turns the tables on any web page into a CSV file you can open in Excel, Google Sheets or LibreOffice.

How it works
1. Open a page that contains tables.
2. Click the Table Exporter icon. It counts the tables on the page.
3. Click "Download CSV" or "Copy to clipboard".

What you get
- All tables on the page in one file, separated by an empty row.
- Spreadsheet-safe output: cells that would run as formulas (starting with =, +, -, @) are kept as plain text.
- UTF-8 with BOM, so diacritics and non-Latin characters open correctly in Excel.

Privacy
- Runs entirely in your browser. No data is sent anywhere, no analytics, no account.
- The extension reads a page only after you click its icon on that page.

Limits
- Exports HTML tables (`<table>`). Grids built from other elements are not detected.
- Browser pages (chrome://, the Web Store) cannot be scanned.

**Category:** Productivity → Tools
**Language:** English

## Store listing (Română)

**Rezumat:**
Exportă într-un singur clic toate tabelele de pe pagină într-un CSV curat, sigur pentru Excel. Rulează local, fără cont, fără urmărire.

**Descriere:**
Table Exporter transformă tabelele de pe orice pagină web într-un fișier CSV pe care îl deschizi în Excel, Google Sheets sau LibreOffice. Deschizi pagina, apeși pe iconiță, alegi „Download CSV” sau „Copy to clipboard”. Toate tabelele ajung într-un singur fișier; celulele care ar porni ca formule (încep cu =, +, -, @) rămân text simplu; diacriticele se deschid corect. Nimic nu pleacă din browser: fără analize, fără cont. Limite: exportă doar tabele HTML (`<table>`); paginile interne ale browserului nu pot fi citite.

## Privacy practices tab

**Single purpose:** Exports the HTML tables of the page the user is viewing to a CSV file or the clipboard.

**Permission justification:**
- `activeTab` — grants temporary access only to the tab where the user clicks the extension icon, to read its tables.
- `scripting` — injects one function into that tab, after the click, which reads `<table>` elements and returns their text.

**Remote code:** No, the extension does not use remote code.

**Data usage:** The extension does not collect or transmit any user data. All processing happens locally.
Certify: no sale of data, no use unrelated to the single purpose, no use for creditworthiness.

**Privacy policy URL:** https://github.com/Ramanul/nishiai-apps/blob/main/store/table-exporter/PRIVACY.md

## Assets

- Icon 128×128: `chrome-extensions/table-exporter/icons/icon128.png`
- Screenshots 1280×800: `store/assets/table-exporter/screenshot-*.png`
- Small promo tile 440×280: `store/assets/table-exporter/promo-440x280.png`
