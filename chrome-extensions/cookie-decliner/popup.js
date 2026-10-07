// Consent Decliner popup — on/off state (v1.1)
const stateEl = document.getElementById("state");

chrome.storage.local.get({ enabled: false, clicked: 0 }, ({ enabled, clicked }) => {
  document.getElementById("enabled").checked = enabled;
  stateEl.textContent = clicked ? `Rejected ${clicked} banner${clicked > 1 ? "s" : ""} so far.` : "No banners rejected yet.";
});

document.getElementById("enabled").addEventListener("change", async (e) => {
  await chrome.storage.local.set({ enabled: e.target.checked });
});

document.getElementById("reset").addEventListener("click", async () => {
  await chrome.storage.local.set({ clicked: 0 });
  stateEl.textContent = "Counter reset.";
});
