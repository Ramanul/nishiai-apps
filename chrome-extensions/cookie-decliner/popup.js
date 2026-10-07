// Consent Decliner popup — on/off state (v1.0)
const stateEl = document.getElementById("state");

chrome.storage.sync.get({ enabled: true, clicked: 0 }, ({ enabled, clicked }) => {
  document.getElementById("enabled").checked = enabled;
  stateEl.textContent = clicked ? `Rejected ${clicked} banner${clicked > 1 ? "s" : ""} so far.` : "No banners rejected yet.";
});

document.getElementById("enabled").addEventListener("change", async (e) => {
  await chrome.storage.sync.set({ enabled: e.target.checked });
});

document.getElementById("reset").addEventListener("click", async () => {
  await chrome.storage.sync.set({ clicked: 0 });
  stateEl.textContent = "Counter reset.";
});
