// Table Exporter popup — collects tables from the active tab and exports CSV.
let pageTables = [];
let pageHost = "";

function toCSV(rows) {
  return rows
    .map((row) => row.map((cell) => `"${String(cell ?? "").replace(/"/g, '""')}"`).join(","))
    .join("\r\n");
}

// Exposed for automated testing.
window.__buildCSV = toCSV;

async function getTargetTabId() {
  const params = new URLSearchParams(location.search);
  if (params.has("src")) return Number(params.get("src")); // test hook
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab ? tab.id : null;
}

async function scan() {
  const status = document.getElementById("status");
  const params = new URLSearchParams(location.search);
  if (params.has("tables")) {
    // test hook: injecteaza tabele fara executeScript (fara user gesture in tab)
    pageTables = JSON.parse(params.get("tables"));
    pageHost = params.get("host") || "test.local";
    const n = pageTables.length;
    status.textContent = `Found ${n} table${n > 1 ? "s" : ""} on ${pageHost}.`;
    document.getElementById("download").disabled = !n;
    document.getElementById("copy").disabled = !n;
    return;
  }
  const tabId = await getTargetTabId();
  if (tabId == null) {
    status.textContent = "No active tab (browser pages can't be scanned).";
    return;
  }
  const [res] = await chrome.scripting.executeScript({
    target: { tabId },
    func: () => {
      const tables = [...document.querySelectorAll("table")];
      return {
        host: location.hostname,
        tables: tables.map((t) =>
          [...t.rows].map((tr) => [...tr.cells].map((td) => (td.innerText ?? "").replace(/\s+/g, " ").trim()))
        ),
      };
    },
  });
  pageTables = res.result.tables;
  pageHost = res.result.host;
  const n = pageTables.length;
  status.textContent = n
    ? `Found ${n} table${n > 1 ? "s" : ""} on ${pageHost}.`
    : `No tables found on ${pageHost}.`;
  document.getElementById("download").disabled = !n;
  document.getElementById("copy").disabled = !n;
}

function allRows() {
  const rows = [];
  pageTables.forEach((table, i) => {
    if (i > 0) rows.push([]);
    rows.push(...table);
  });
  return rows;
}

document.getElementById("download").addEventListener("click", () => {
  const csv = "\uFEFF" + toCSV(allRows());
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `tables-${pageHost || "page"}.csv`;
  a.click();
});

document.getElementById("copy").addEventListener("click", async () => {
  await navigator.clipboard.writeText(toCSV(allRows()));
  document.getElementById("copy").textContent = "Copied!";
  setTimeout(() => (document.getElementById("copy").textContent = "Copy to clipboard"), 1500);
});

scan();
