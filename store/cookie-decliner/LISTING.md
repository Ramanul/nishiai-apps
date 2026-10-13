# Consent Decliner — Chrome Web Store listing

Pachetul: `store/dist/cookie-decliner-<versiune>.zip` (fără câmpul `key`).

**Poartă înainte de trimitere** (din `docs/VERIFICARE-PLAN.md`): extensia are testare minimală.
Se trimite după rularea matricei pe site-uri reale cu CMP-urile declarate (OneTrust, Cookiebot,
Quantcast, Didomi, Sourcepoint). Permisiunea pe toate site-urile (`<all_urls>`) aduce o revizuire
manuală mai lungă la Google.

## Store listing (English, default)

**Name** (max 75): Consent Decliner — auto-reject cookie banners

**Summary** (max 132):
Clicks "Reject all" on cookie consent banners when the site offers it. Off by default, never accepts, works locally.

**Description:**

Consent Decliner saves you the clicks on cookie banners by choosing the site's own "Reject all" or
"Necessary only" option for you.

How it works
- Turn it on from the extension popup (it is off until you enable it).
- On each page, it looks for a visible reject button inside the consent banner and clicks it once.
- It never clicks "Accept" and never changes site settings beyond that reject choice.

Coverage
Common consent platforms (OneTrust, Cookiebot, Quantcast, Didomi, Sourcepoint) plus generic
"Reject all / Deny / Refuse / Necessary only" buttons.

Privacy
- Runs entirely in your browser. No data is sent anywhere, no analytics, no account.
- It stores only your on/off choice and a local counter of banners handled.

Limits
- If a banner has no reject option on its first layer, the extension leaves it for you.
- Some sites change their banners often; a missed banner is not reported anywhere.

**Category:** Privacy & Security
**Language:** English

## Store listing (Română)

**Rezumat:**
Apasă „Respinge tot” pe bannerele de cookie-uri când site-ul oferă opțiunea. Oprită implicit, nu acceptă niciodată, rulează local.

**Descriere:**
Consent Decliner alege pentru tine opțiunea „Respinge tot” sau „Doar necesare” din bannerul de cookie-uri al
site-ului. O pornești din fereastra extensiei; caută butonul de respingere vizibil și îl apasă o singură dată pe
pagină. Nu apasă niciodată „Accept”. Nimic nu pleacă din browser: păstrează doar starea pornit/oprit și un
contor local.

## Privacy practices tab

**Single purpose:** Rejects non-essential cookies on consent banners by clicking the site's own reject option.

**Permission justification:**
- `storage` — remembers whether the user turned the extension on, and a local count of banners handled.
- Host permissions `<all_urls>` and the content script on all sites — consent banners can appear on any site the
  user visits; the script only looks for the banner's reject button and clicks it when the user has enabled the extension.

**Remote code:** No.

**Data usage:** The extension does not collect or transmit any user data.

**Privacy policy URL:** https://github.com/Ramanul/nishiai-apps/blob/main/store/cookie-decliner/PRIVACY.md
