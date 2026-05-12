// Design-catalog viewer.
// Pure static; loads catalog.json and renders a filterable grid + detail drawer.
// All DOM is built with createElement / textContent — no innerHTML.

const state = {
  entries: [],
  search: "",
  activeTags: new Set(),
  activeSlug: null,
  activeTab: "snippet",
  tabContent: { snippet: "", motion: "", meta: "" },
};

const els = {
  grid: document.getElementById("dc-grid"),
  search: document.getElementById("dc-search"),
  tagbar: document.getElementById("dc-tagbar"),
  detail: document.getElementById("dc-detail"),
  detailName: document.getElementById("dc-detail-name"),
  detailDesc: document.getElementById("dc-detail-desc"),
  detailChips: document.getElementById("dc-detail-chips"),
  detailPreview: document.getElementById("dc-detail-preview"),
  detailClose: document.getElementById("dc-detail-close"),
  detailBackdrop: document.getElementById("dc-detail-backdrop"),
  tabs: document.getElementById("dc-tabs"),
  tabContent: document.getElementById("dc-tab-content"),
  toast: document.getElementById("dc-toast"),
};

init().catch((err) => {
  console.error(err);
  showFatal(err.message);
});

function showFatal(message) {
  clearChildren(els.grid);
  const div = document.createElement("div");
  div.className = "dc-empty";
  const line1 = document.createElement("div");
  line1.textContent = `Could not load catalog.json — ${message}.`;
  const line2 = document.createElement("div");
  line2.textContent = "Serve via 'python3 -m http.server 8000' from the repo root, then open /design-catalog/.";
  div.appendChild(line1);
  div.appendChild(line2);
  els.grid.appendChild(div);
}

async function init() {
  const res = await fetch("./catalog.json", { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  state.entries = data.entries || [];

  renderTagbar();
  renderGrid();

  els.search.addEventListener("input", (e) => {
    state.search = e.target.value.trim().toLowerCase();
    renderGrid();
  });

  els.detailClose.addEventListener("click", closeDetail);
  els.detailBackdrop.addEventListener("click", closeDetail);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && state.activeSlug) closeDetail();
  });

  document.querySelectorAll(".dc-btn[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => onAction(btn.dataset.action));
  });

  window.addEventListener("hashchange", routeFromHash);
  routeFromHash();
}

function renderTagbar() {
  const tagSet = new Set();
  for (const e of state.entries) (e.tags || []).forEach((t) => tagSet.add(t));
  const tags = [...tagSet].sort();
  clearChildren(els.tagbar);
  if (!tags.length) {
    els.tagbar.hidden = true;
    return;
  }
  els.tagbar.hidden = false;
  for (const t of tags) {
    const chip = document.createElement("span");
    chip.className = "dc-chip";
    chip.dataset.tag = t;
    chip.textContent = t;
    chip.addEventListener("click", () => toggleTag(t));
    els.tagbar.appendChild(chip);
  }
}

function toggleTag(tag) {
  if (state.activeTags.has(tag)) state.activeTags.delete(tag);
  else state.activeTags.add(tag);
  els.tagbar.querySelectorAll(".dc-chip").forEach((chip) => {
    chip.classList.toggle("is-active", state.activeTags.has(chip.dataset.tag));
  });
  renderGrid();
}

function filterEntries() {
  return state.entries.filter((e) => {
    if (state.activeTags.size) {
      const tags = new Set(e.tags || []);
      for (const t of state.activeTags) if (!tags.has(t)) return false;
    }
    if (state.search) {
      const hay = `${e.name} ${e.description} ${(e.tags || []).join(" ")}`.toLowerCase();
      if (!hay.includes(state.search)) return false;
    }
    return true;
  });
}

function renderGrid() {
  clearChildren(els.grid);
  const filtered = filterEntries();
  if (!filtered.length) {
    const empty = document.createElement("div");
    empty.className = "dc-empty";
    empty.textContent = "No entries match.";
    els.grid.appendChild(empty);
    return;
  }
  for (const e of filtered) els.grid.appendChild(buildCard(e));
}

function buildCard(e) {
  const card = document.createElement("article");
  card.className = "dc-card";
  card.dataset.slug = e.slug;
  card.addEventListener("click", () => {
    window.location.hash = `#${e.slug}`;
  });

  const thumb = document.createElement("div");
  thumb.className = "dc-card__thumb";
  const iframe = document.createElement("iframe");
  iframe.src = `${e.path}/${e.files.preview}`;
  iframe.setAttribute("sandbox", "allow-scripts allow-same-origin");
  iframe.loading = "lazy";
  iframe.title = `${e.name} preview`;
  thumb.appendChild(iframe);

  const body = document.createElement("div");
  body.className = "dc-card__body";

  const name = document.createElement("h3");
  name.className = "dc-card__name";
  name.textContent = e.name;

  const desc = document.createElement("p");
  desc.className = "dc-card__desc";
  desc.textContent = e.description;

  const meta = document.createElement("div");
  meta.className = "dc-card__meta";
  for (const t of e.tags || []) meta.appendChild(buildChip(t));
  for (const d of e.dependencies || []) meta.appendChild(buildChip(d, "dc-chip--dep"));

  body.appendChild(name);
  body.appendChild(desc);
  body.appendChild(meta);

  card.appendChild(thumb);
  card.appendChild(body);
  return card;
}

function buildChip(text, extraClass = "") {
  const chip = document.createElement("span");
  chip.className = "dc-chip" + (extraClass ? ` ${extraClass}` : "");
  chip.textContent = text;
  return chip;
}

function routeFromHash() {
  const slug = window.location.hash.replace(/^#/, "");
  if (!slug) {
    closeDetail();
    return;
  }
  const entry = state.entries.find((e) => e.slug === slug);
  if (entry) openDetail(entry);
}

async function openDetail(entry) {
  state.activeSlug = entry.slug;
  els.detailName.textContent = entry.name;
  els.detailDesc.textContent = entry.description;

  clearChildren(els.detailChips);
  for (const t of entry.tags || []) els.detailChips.appendChild(buildChip(t));
  for (const d of entry.dependencies || [])
    els.detailChips.appendChild(buildChip(d, "dc-chip--dep"));

  els.detailPreview.src = `${entry.path}/${entry.files.preview}`;

  // Build tabs based on which files this entry exposes.
  const tabs = [{ key: "snippet", label: "Snippet" }];
  if (entry.files.motion) tabs.push({ key: "motion", label: "Motion" });
  tabs.push({ key: "meta", label: "Meta" });

  clearChildren(els.tabs);
  for (const t of tabs) {
    const btn = document.createElement("button");
    btn.className = "dc-tab";
    btn.dataset.tab = t.key;
    btn.textContent = t.label;
    btn.addEventListener("click", () => activateTab(t.key));
    els.tabs.appendChild(btn);
  }

  state.tabContent = { snippet: "", motion: "", meta: JSON.stringify(entry, null, 2) };
  await Promise.all([
    fetchText(`${entry.path}/${entry.files.snippet}`).then((t) => (state.tabContent.snippet = t)),
    entry.files.motion
      ? fetchText(`${entry.path}/${entry.files.motion}`).then((t) => (state.tabContent.motion = t))
      : Promise.resolve(),
  ]);

  activateTab("snippet");

  els.detail.hidden = false;
  els.detail.setAttribute("aria-hidden", "false");
}

function activateTab(key) {
  state.activeTab = key;
  els.tabs.querySelectorAll(".dc-tab").forEach((b) => {
    b.classList.toggle("is-active", b.dataset.tab === key);
  });
  els.tabContent.textContent = state.tabContent[key] || "";
  // Reset scroll so the user lands at the top of the newly-activated tab
  // instead of staying scrolled into the previous tab's content.
  const pre = els.tabContent.parentElement;
  if (pre) pre.scrollTop = 0;
}

function closeDetail() {
  state.activeSlug = null;
  els.detail.hidden = true;
  els.detail.setAttribute("aria-hidden", "true");
  els.detailPreview.src = "about:blank";
  if (window.location.hash) {
    history.replaceState(null, "", window.location.pathname + window.location.search);
  }
}

async function fetchText(url) {
  const res = await fetch(url, { cache: "no-store" });
  if (!res.ok) throw new Error(`HTTP ${res.status} for ${url}`);
  return res.text();
}

function onAction(action) {
  const entry = state.entries.find((e) => e.slug === state.activeSlug);
  if (!entry) return;

  if (action === "copy-snippet") {
    const tab = state.activeTab === "motion" ? "motion" : "snippet";
    const text = state.tabContent[tab] || "";
    copy(text, `Copied ${tab}`);
  } else if (action === "copy-prompt") {
    copy(buildAiPrompt(entry), "Copied AI prompt");
  }
}

function buildAiPrompt(entry) {
  const motion = entry.files.motion ? ` and ${entry.files.motion}` : "";
  return `Reuse the ${entry.name.toLowerCase()} from design-catalog/${entry.slug}/. Read ${entry.files.snippet}${motion}, then adapt the styles, knobs, and motion to fit <describe target>.`;
}

async function copy(text, label) {
  // Try the modern API first; some focus/permission states throw, so fall
  // back to the textarea + execCommand trick before declaring failure.
  try {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      toast(label);
      return;
    }
  } catch (_) {
    // fall through to legacy path
  }
  if (legacyCopy(text)) {
    toast(label);
  } else {
    toast("Copy failed");
  }
}

function legacyCopy(text) {
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.setAttribute("readonly", "");
  ta.style.position = "fixed";
  ta.style.top = "0";
  ta.style.left = "0";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.select();
  let ok = false;
  try { ok = document.execCommand("copy"); } catch (_) { ok = false; }
  document.body.removeChild(ta);
  return ok;
}

let toastTimer = null;
function toast(msg) {
  els.toast.textContent = msg;
  els.toast.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (els.toast.hidden = true), 1600);
}

function clearChildren(node) {
  while (node.firstChild) node.removeChild(node.firstChild);
}
