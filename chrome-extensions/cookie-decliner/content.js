// Consent Decliner — content script (v1.0)
// Heuristic: find a visible "reject all"-type button inside consent containers and click it
// once per page. Never clicks "Accept". Known CMP coverage: OneTrust, CookieBot, Quantcast,
// Didomi, Sourcepoint + generic text matching.

(function () {
  if (window.__consentDeclinerRan) return;
  window.__consentDeclinerRan = true;

  const REJECT_TEXT =
    /^\s*(reject\s+(all)?|deny\s+(all)?|refuse\s+(all)?|decline\s+(all)?|necessary\s+(only|cookies\s+only)|only\s+necessary|use\s+necessary\s+cookies\s+only|continue\s+without\s+accepting|doar\s+necesare|resping|respinge|respinge\s+tot|respinge tot|resping\s+toate|nu\s+accept)\b/i;

  const CONTAINER_SEL = [
    "[class*='onetrust']",
    "[id*='onetrust']",
    "[id*='CybotCookiebot']",
    "[class*='CybotCookiebot']",
    "[class*='qc-cmp']",
    "[class*='qc__']",
    "[id*='didomi']",
    "[class*='didomi']",
    "[class*='sp_message']",
    "[class*='sourcepoint']",
    "[class*='cookie']",
    "[class*='consent']",
    "[class*='gdpr']",
    "[id*='cookie']",
    "[id*='consent']",
    "[role='dialog']",
  ].join(",");

  function visible(el) {
    const r = el.getBoundingClientRect();
    const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none";
  }

  function findRejectButton() {
    const containers = [...document.querySelectorAll(CONTAINER_SEL)];
    const scopes = containers.length ? containers : [document.body];
    for (const scope of scopes) {
      const candidates = [...scope.querySelectorAll("button, a[role='button'], input[type='button'], input[type='submit']")];
      const hit = candidates.find((b) => visible(b) && REJECT_TEXT.test(b.innerText || b.value || ""));
      if (hit) return hit;
    }
    return null;
  }

  function tryClick(attempt) {
    chrome.storage.sync.get({ enabled: false }, ({ enabled }) => {
      if (!enabled) return;
      const btn = findRejectButton();
      if (btn) {
        btn.click();
        window.__consentDeclinerClicked = true;
        chrome.storage.sync.get({ clicked: 0 }, ({ clicked }) =>
          chrome.storage.sync.set({ clicked: clicked + 1 })
        );
        return;
      }
      if (attempt < 6) setTimeout(() => tryClick(attempt + 1), 700); // banners mount late
    });
  }

  tryClick(0);
})();
