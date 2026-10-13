# Fluxul de producție — roluri fixe

Regula: fiecare unealtă are un singur rol. O unealtă nouă intră doar dacă înlocuiește una.
Metrica săptămânală: produse listate și venit, nu workflow-uri construite.

| Rol | Cine | Note |
|---|---|---|
| Cercetare nișă / concurență | Gemini Deep Research (Google AI Pro); Manus Free (300 credite/zi, 1 sarcină, 2 automatizări programate) | doar pagini publice |
| Spec, brief, verificare finală | Claude | issue cu criterii de acceptanță |
| Execuție cod (produse vândute) | Claude, Codex (ChatGPT Plus), Jules (Google AI Pro) | Arena NU pentru cod vândut |
| Execuție cod (public, nevândut) | + Arena Agent Mode (gratuit) | doar repo-uri publice, fără date personale |
| Asistent local în editor | Copilot Free: 2.000 completări + 50 chat/lună, CLI inclus; agentul din cloud nu | |
| Verificare încrucișată | agentul care n-a scris codul | |
| Imagini / video promo | Gemini (Flow, Nano Banana), ChatGPT (imagini) | licență verificată |
| Texte de listare EN/RO | Claude; metadate în masă: Ollama local | |
| AI la rulare în produse | Cloudflare Workers AI: 10.000 neuroni/zi gratuit (~2,4M tokeni intrare sau ~287k ieșire pe llama-3.1-8b) | backend fără cost fix |
| Build, teste, capturi | GitHub Actions (public = minute nelimitate); `store/*.py` | |
| Porți umane | Alexandru: conturi, KYC, „publică”, prețuri, declarații AI | |

Magistrala: GitHub (issue = brief, PR = livrare); Google Drive pentru conținutul din aplicațiile de chat.
