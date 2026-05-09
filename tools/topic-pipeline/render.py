#!/usr/bin/env python3
"""Render inbox.json + competitors feed.json into a single-file dashboard.html.

The dashboard embeds both data sources directly so it works opened from disk
(no server needed). Status decisions and queued YouTube-derived candidates
persist in localStorage; the Export Decisions button downloads them as a
small JSON the user can save back to data/decisions.json (apply_decisions.py
honors them on the next run).

Layout:
- Left sidebar — Inspiration (All/HN/Reddit/Lobsters/daily.dev/YouTube)
                + Status (Unreviewed/Pending/All)
- Main column — Toolbar + cards. The card style depends on what the sidebar
  selected: candidate cards for the aggregator views, YouTube cards for the
  YouTube view.

Data trust note: all string fields rendered into the dashboard come from
controlled sources (this project's own LLM judgments + yt-dlp metadata).
Every interpolation goes through the escapeHtml() helper before reaching
innerHTML; the dashboard itself runs locally on the author's machine.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def load_json(path: Path, default: dict | list) -> dict | list:
    if not path.exists():
        return default
    parsed = json.loads(path.read_text(encoding="utf-8"))
    return parsed


# Dashboard HTML - single self-contained file with embedded data
DASHBOARD_TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Topic pipeline - review dashboard</title>
  <style>
    :root {
      --bg: #0b0b0d;
      --bg-card: #141418;
      --bg-card-hover: #1a1a20;
      --bg-elevated: #1f1f25;
      --bg-sidebar: #0e0e11;
      --border: #2a2a30;
      --border-strong: #3a3a44;
      --fg: #e8e8ec;
      --fg-dim: #888892;
      --fg-muted: #5a5a64;
      --accent: #ef4a4a;
      --green: #4ade80;
      --green-dim: #1a3d24;
      --yellow: #facc15;
      --yellow-dim: #3d2f0a;
      --red: #ef4444;
      --red-dim: #3d1414;
      --blue: #60a5fa;
      --blue-dim: #14283d;
      --sidebar-w: 220px;
      --sidebar-w-collapsed: 56px;
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; padding: 0; background: var(--bg); color: var(--fg);
      font: 14px/1.45 ui-sans-serif, system-ui, -apple-system, "Helvetica Neue", sans-serif; }
    a { color: var(--blue); text-decoration: none; }
    a:hover { text-decoration: underline; }
    .layout { display: flex; min-height: 100vh; }
    aside.sidebar { width: var(--sidebar-w); flex: 0 0 auto;
      background: var(--bg-sidebar); border-right: 1px solid var(--border);
      padding: 20px 0; display: flex; flex-direction: column;
      transition: width 0.2s ease;
      position: sticky; top: 0; height: 100vh; overflow-y: auto; }
    aside.sidebar.collapsed { width: var(--sidebar-w-collapsed); }
    aside.sidebar .section { padding: 12px 14px 8px; }
    aside.sidebar .section-h { color: var(--fg-muted); font-size: 10px;
      text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 6px; padding: 0 4px; }
    aside.sidebar.collapsed .section-h, aside.sidebar.collapsed .nav-label,
    aside.sidebar.collapsed .nav-count, aside.sidebar.collapsed .brand-text { display: none; }
    .brand { padding: 0 18px 16px; border-bottom: 1px solid var(--border);
      display: flex; align-items: center; gap: 10px; }
    .brand-logo { width: 24px; height: 24px; flex: 0 0 auto;
      border-radius: 6px; background: linear-gradient(135deg, var(--accent), var(--blue)); }
    .brand-text { font-weight: 700; font-size: 13px; letter-spacing: -0.01em; }
    .sidebar-toggle { position: absolute; bottom: 14px; right: 14px;
      background: transparent; border: 1px solid var(--border);
      color: var(--fg-muted); width: 28px; height: 28px; border-radius: 4px;
      cursor: pointer; font-size: 14px; line-height: 1; }
    .sidebar-toggle:hover { color: var(--fg); border-color: var(--border-strong); }
    .nav-item { display: flex; align-items: center; gap: 10px;
      padding: 7px 10px; border-radius: 6px; cursor: pointer;
      color: var(--fg-dim); font-size: 13px; margin-bottom: 1px; }
    .nav-item:hover { background: var(--bg-card); color: var(--fg); }
    .nav-item.active { background: var(--bg-elevated); color: var(--fg); }
    .nav-icon { width: 18px; height: 18px; flex: 0 0 auto;
      display: inline-flex; align-items: center; justify-content: center;
      font-size: 11px; color: var(--fg-muted); }
    .nav-item.active .nav-icon { color: var(--blue); }
    .nav-label { flex: 1 1 auto; }
    .nav-count { color: var(--fg-muted); font-size: 11px; font-variant-numeric: tabular-nums; }
    main.content { flex: 1 1 auto; min-width: 0; }
    header.page-header { padding: 22px 32px 14px; border-bottom: 1px solid var(--border); }
    h1 { margin: 0 0 4px; font-size: 19px; font-weight: 700; letter-spacing: -0.01em; }
    .sub { color: var(--fg-dim); font-size: 12px; }
    .toolbar { position: sticky; top: 0; z-index: 10;
      background: rgba(11,11,13,0.92); backdrop-filter: blur(8px);
      border-bottom: 1px solid var(--border);
      padding: 10px 32px;
      display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
    .toolbar > div { display: flex; align-items: center; gap: 6px; }
    .toolbar label { color: var(--fg-dim); font-size: 12px; }
    .toolbar select, .toolbar input[type=text] { background: var(--bg-card);
      border: 1px solid var(--border); color: var(--fg);
      padding: 5px 10px; border-radius: 4px; font-size: 13px; }
    .toolbar input[type=text] { min-width: 220px; }
    .toolbar input[type=range] { width: 110px; }
    .toolbar button { background: var(--bg-card); border: 1px solid var(--border);
      color: var(--fg); padding: 5px 14px; border-radius: 6px;
      font: inherit; font-size: 13px; cursor: pointer; }
    .toolbar button:hover { background: var(--bg-card-hover); }
    .toolbar button.primary { background: var(--green-dim); border-color: var(--green); color: var(--green); }
    .toolbar-spacer { flex: 1 1 auto; }
    .pill { background: var(--bg-card); border: 1px solid var(--border);
      color: var(--fg); padding: 4px 10px; border-radius: 999px;
      font-size: 12px; cursor: pointer; }
    .pill:hover { background: var(--bg-card-hover); }
    .pill.active { background: var(--bg-elevated); border-color: var(--border-strong); color: var(--blue); }
    main .grid { padding: 20px 32px 80px; }
    .card { background: var(--bg-card); border: 1px solid var(--border);
      border-radius: 10px; margin-bottom: 16px; overflow: hidden; }
    .card.status-pass { opacity: 0.4; }
    .card.status-go { border-color: var(--green); }
    .card.status-later { border-color: var(--yellow); }
    .card.status-shipped { border-color: var(--blue); opacity: 0.7; }
    .card-head { padding: 16px 18px 12px; }
    .card-rank { display: inline-block; min-width: 28px;
      color: var(--fg-muted); font-variant-numeric: tabular-nums; font-weight: 600;
      margin-right: 10px; }
    .card-title { font-size: 16px; font-weight: 600; color: var(--fg); }
    .card-title:hover { color: var(--blue); cursor: pointer; }
    .card-status-badge { float: right; padding: 3px 10px; border-radius: 999px; font-size: 11px;
      letter-spacing: 0.04em; text-transform: uppercase; }
    .badge-go { background: var(--green-dim); color: var(--green); }
    .badge-pass { background: var(--red-dim); color: var(--red); }
    .badge-later { background: var(--yellow-dim); color: var(--yellow); }
    .badge-shipped { background: var(--blue-dim); color: var(--blue); }
    .video-folder-link { display: inline-block; margin-left: 8px; padding: 2px 8px;
      border: 1px solid var(--blue); border-radius: 4px;
      color: var(--blue); font-size: 11px; font-family: ui-monospace, monospace; }
    .video-folder-link:hover { background: var(--blue-dim); text-decoration: none; }
    .card-meta { margin-top: 6px; color: var(--fg-dim); font-size: 12px;
      display: flex; flex-wrap: wrap; gap: 12px; }
    .source-tag { display: inline-block; padding: 1px 7px;
      background: var(--bg-elevated); border-radius: 3px;
      font-size: 11px; color: var(--fg-dim); margin-right: 4px; }
    .source-hn { background: #4a2511; color: #fb923c; }
    .source-reddit { background: #3d1f1a; color: #ff6b3d; }
    .source-lobsters { background: #3d1f25; color: #ec4899; }
    .source-dailydev { background: #1a2d3d; color: #60a5fa; }
    .source-youtube { background: #3d141a; color: #ef4444; }
    .scores-row { display: flex; flex-wrap: wrap; gap: 16px;
      padding: 8px 18px 12px; border-bottom: 1px solid var(--border);
      align-items: center; }
    .composite { font-size: 22px; font-weight: 700; min-width: 52px; text-align: right; }
    .composite-label { color: var(--fg-muted); font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; }
    .axis { flex: 0 0 auto; min-width: 90px; }
    .axis-label { color: var(--fg-dim); font-size: 10px; text-transform: uppercase; letter-spacing: 0.06em; }
    .axis-bar { height: 4px; background: var(--bg-elevated); border-radius: 2px; margin-top: 3px; overflow: hidden; }
    .axis-fill { height: 100%; background: var(--blue); transition: width 0.2s; }
    .axis-value { color: var(--fg); font-size: 12px; font-variant-numeric: tabular-nums; margin-left: 4px; }
    .angles { padding: 12px 18px 16px; }
    .angles-h { color: var(--fg-dim); font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 8px; }
    .angle { background: var(--bg-elevated); border: 1px solid var(--border);
      border-radius: 6px; padding: 12px 14px; margin-bottom: 8px;
      display: grid; grid-template-columns: 32px 1fr auto; gap: 12px; align-items: start; }
    .angle.is-best { border-color: var(--green); }
    .angle-num { color: var(--fg-muted); font-weight: 600; }
    .angle-num.is-best { color: var(--green); }
    .angle-title { font-weight: 600; color: var(--fg); margin-bottom: 4px; }
    .angle-lens { color: var(--fg-dim); font-size: 12px; }
    .angle-scores { color: var(--fg-dim); font-size: 11px; margin-top: 4px; font-variant-numeric: tabular-nums; }
    .angle-comp { font-size: 18px; font-weight: 700; color: var(--fg); text-align: right; min-width: 44px; font-variant-numeric: tabular-nums; }
    .angle-comp small { display: block; color: var(--fg-muted); font-size: 9px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.06em; }
    .angle-actions { margin-top: 6px; display: flex; gap: 6px; }
    .angle-actions button { background: transparent; border: 1px solid var(--border);
      color: var(--fg-dim); padding: 3px 10px; border-radius: 4px;
      font-size: 11px; cursor: pointer; }
    .angle-actions button:hover { color: var(--fg); border-color: var(--border-strong); }
    .angle-actions button.go-btn:hover { color: var(--green); border-color: var(--green); }
    .card-actions { padding: 12px 18px 16px; border-top: 1px solid var(--border);
      display: flex; gap: 8px; align-items: center; }
    .card-actions button { background: transparent; border: 1px solid var(--border);
      color: var(--fg-dim); padding: 5px 12px; border-radius: 5px;
      font: inherit; font-size: 12px; cursor: pointer; }
    .card-actions button:hover { color: var(--fg); border-color: var(--border-strong); }
    .card-actions .pass-btn:hover { color: var(--red); border-color: var(--red); }
    .card-actions .later-btn:hover { color: var(--yellow); border-color: var(--yellow); }
    .card-actions .ship-btn:hover { color: var(--blue); border-color: var(--blue); }
    .card-actions .reset-btn { margin-left: auto; }
    .yt-card { background: var(--bg-card); border: 1px solid var(--border);
      border-radius: 10px; padding: 14px 16px; margin-bottom: 12px;
      display: grid; grid-template-columns: 1fr auto;
      gap: 16px; align-items: start; }
    .yt-card.queued { border-color: var(--green); }
    .yt-title { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
    .yt-title a { color: var(--fg); }
    .yt-title a:hover { color: var(--blue); }
    .yt-meta { color: var(--fg-dim); font-size: 12px; display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }
    .tier-badge { padding: 1px 6px; border-radius: 3px; font-size: 10px;
      text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; }
    .tier-B { background: var(--blue-dim); color: var(--blue); }
    .tier-C { background: var(--yellow-dim); color: var(--yellow); }
    .yt-actions { display: flex; flex-direction: column; gap: 6px; align-items: flex-end; }
    .yt-actions button { background: var(--bg-elevated); border: 1px solid var(--border);
      color: var(--fg-dim); padding: 6px 12px; border-radius: 5px;
      font: inherit; font-size: 12px; cursor: pointer; white-space: nowrap; }
    .yt-actions button:hover { color: var(--fg); border-color: var(--border-strong); }
    .yt-actions button.queued { color: var(--green); border-color: var(--green); }
    .empty { text-align: center; padding: 60px 20px; color: var(--fg-dim); }
    @media (max-width: 720px) {
      :root { --sidebar-w: 100vw; }
      aside.sidebar { position: fixed; z-index: 100; }
      aside.sidebar.collapsed { transform: translateX(-100%); width: var(--sidebar-w); }
    }
  </style>
</head>
<body>
<div class="layout">
  <aside class="sidebar" id="sidebar">
    <div class="brand">
      <div class="brand-logo"></div>
      <div class="brand-text">topic-pipeline</div>
    </div>
    <div class="section">
      <div class="section-h">Inspiration</div>
      <div id="nav-sources"></div>
    </div>
    <div class="section">
      <div class="section-h">Status</div>
      <div id="nav-status"></div>
    </div>
    <button class="sidebar-toggle" id="sidebar-toggle" title="Collapse sidebar">&lsaquo;</button>
  </aside>
  <main class="content">
    <header class="page-header">
      <h1 id="page-title">All inspiration</h1>
      <div class="sub">Generated <span id="generated-at">-</span> &middot; <span id="page-sub">-</span></div>
    </header>
    <div class="toolbar" id="toolbar"></div>
    <div class="grid" id="grid"></div>
  </main>
</div>
<script>
const INBOX = __INBOX_DATA__;
const FEED = __FEED_DATA__;
const INBOX_YT_IDS = new Set(__INBOX_YT_IDS__);

const STATUS_KEY = "topic-pipeline:decisions:v1";
const CREATE_KEY = "topic-pipeline:create-candidates:v1";
const SIDEBAR_KEY = "topic-pipeline:sidebar-collapsed:v1";

// Drop queue entries that have made it to inbox (avoid zombie "Queued"
// indicator after a successful apply_decisions run).
(function cleanQueue() {
  const queue = loadCreates();
  let changed = false;
  for (const k of Object.keys(queue)) {
    if (INBOX_YT_IDS.has(k)) { delete queue[k]; changed = true; }
  }
  if (changed) saveCreates(queue);
})();

function loadStatus() { try { return JSON.parse(localStorage.getItem(STATUS_KEY) || "{}"); } catch(e) { return {}; } }
function saveStatus(d) { localStorage.setItem(STATUS_KEY, JSON.stringify(d)); }
function loadCreates() { try { return JSON.parse(localStorage.getItem(CREATE_KEY) || "{}"); } catch(e) { return {}; } }
function saveCreates(d) { localStorage.setItem(CREATE_KEY, JSON.stringify(d)); }

function setStatus(id, status, selectedAngleIndex, videoFolder) {
  const d = loadStatus();
  d[id] = d[id] || {};
  d[id].status = status;
  d[id].updated_at = new Date().toISOString();
  if (selectedAngleIndex !== null && selectedAngleIndex !== undefined) d[id].selected_angle_index = selectedAngleIndex;
  if (videoFolder) d[id].video_folder = videoFolder;
  saveStatus(d);
  render();
}
function markShipped(id) {
  const c = (INBOX.candidates || {})[id];
  const existing = (loadStatus()[id] || {}).video_folder
    || (c && c.video_folder)
    || "";
  const slug = prompt(
    "Mark as shipped — video folder slug (e.g. 'why-text-is-hard-2026-05-07'):",
    existing
  );
  if (slug == null) return;             // cancel
  const trimmed = String(slug).trim();
  if (!trimmed) return;                  // empty input == cancel
  const folder = trimmed.startsWith("videos/") ? trimmed : "videos/" + trimmed;
  setStatus(id, "shipped", null, folder);
}
function clearStatus(id) {
  const d = loadStatus();
  delete d[id];
  saveStatus(d);
  render();
}
function effectiveStatus(c) {
  const d = loadStatus();
  return (d[c.id] && d[c.id].status) || c.user_status || null;
}
function effectiveVideoFolder(c) {
  const d = loadStatus();
  return (d[c.id] && d[c.id].video_folder) || c.video_folder || null;
}

function toggleYoutubeQueue(video) {
  const c = loadCreates();
  if (c[video.id]) { delete c[video.id]; }
  else {
    c[video.id] = {
      from_youtube: {
        video_id: video.id,
        title: video.title,
        channel: video.channel,
        channel_handle: video.channel_handle,
        channel_tier: video.channel_tier,
        channel_note: video.channel_note,
        view_count: video.view_count,
        upload_date: video.upload_date,
        duration_s: video.duration_s,
        queued_at: new Date().toISOString()
      }
    };
  }
  saveCreates(c);
  render();
}

function escapeHtml(s) {
  return String(s == null ? "" : s).replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c]));
}
function fmtViews(n) {
  if (n == null) return "-";
  if (n >= 1000000) return (n/1000000).toFixed(1).replace(/\.0$/, "") + "M views";
  if (n >= 1000) return (n/1000).toFixed(1).replace(/\.0$/, "") + "K views";
  return n + " views";
}
function daysAgo(yyyymmdd) {
  if (!yyyymmdd || yyyymmdd.length !== 8) return null;
  const y = +yyyymmdd.slice(0,4), m = +yyyymmdd.slice(4,6) - 1, d = +yyyymmdd.slice(6,8);
  const then = new Date(Date.UTC(y, m, d));
  return Math.round((Date.now() - then.getTime()) / 86400000);
}
function fmtRelative(yyyymmdd) {
  const d = daysAgo(yyyymmdd);
  if (d == null) return "-";
  if (d === 0) return "today";
  if (d === 1) return "yesterday";
  if (d < 30) return d + "d ago";
  if (d < 365) return Math.round(d/30) + "mo ago";
  return Math.round(d/365) + "y ago";
}

const STATE = {
  view: "all",
  statusFilter: "unreviewed",
  minScore: 0,
  search: "",
  candSort: "composite",
  multiSourceOnly: false,
  ytTier: "all",
  ytSort: "recent"
};

const CAND_SORTS = [
  {key: "composite", label: "Best composite"},
  {key: "recent",    label: "Most recent"},
  {key: "oldest",    label: "Oldest first"},
  {key: "demand",    label: "Demand"},
  {key: "evergreen", label: "Evergreen"}
];

function compareBy(key) {
  if (key === "recent")    return (a,b) => (b.first_seen_at||"").localeCompare(a.first_seen_at||"");
  if (key === "oldest")    return (a,b) => (a.first_seen_at||"").localeCompare(b.first_seen_at||"");
  if (key === "demand")    return (a,b) => ((b.scores||{}).demand||0) - ((a.scores||{}).demand||0);
  if (key === "evergreen") return (a,b) => ((b.scores||{}).evergreen||0) - ((a.scores||{}).evergreen||0);
  return (a,b) => (b.best_composite||0) - (a.best_composite||0);
}

function setView(v) { STATE.view = v; STATE.search = ""; render(); }
function setStatusFilter(s) { STATE.statusFilter = s; render(); }

const SOURCE_LABELS = [
  {key: "all",      label: "All",          icon: "*"},
  {key: "hn",       label: "Hacker News",  icon: "Y"},
  {key: "reddit",   label: "Reddit",       icon: "R"},
  {key: "lobsters", label: "Lobste.rs",    icon: "L"},
  {key: "dailydev", label: "daily.dev",    icon: "D"},
  {key: "youtube",  label: "YouTube",      icon: ">"}
];
const STATUS_LABELS = [
  {key: "unreviewed", label: "Unreviewed",       icon: "."},
  {key: "pending",    label: "Pending judgment", icon: "?"},
  {key: "all",        label: "All (active)",     icon: "="},
  {key: "go",         label: "Go",               icon: "+"},
  {key: "later",      label: "Later",            icon: "~"},
  {key: "pass",       label: "Pass",             icon: "x"},
  {key: "shipped",    label: "Shipped",          icon: ">"}
];

function countCandidatesBySource() {
  const cands = Object.values(INBOX.candidates || {});
  const counts = {all: cands.length, hn: 0, reddit: 0, lobsters: 0, dailydev: 0, youtube: 0};
  for (const c of cands) for (const s of (c.sources||[])) {
    if (counts[s] !== undefined) counts[s]++;
  }
  // YouTube sidebar count = videos in the feed minus those already inspired
  // (so the user sees the actual fresh-inspiration count, not the catalog total).
  counts.youtube_feed = (FEED.videos || []).filter(v => !INBOX_YT_IDS.has(v.id)).length;
  return counts;
}

function renderSidebar() {
  const counts = countCandidatesBySource();
  const navSources = SOURCE_LABELS.map(s => {
    let count;
    if (s.key === "youtube") count = counts.youtube_feed;
    else count = counts[s.key];
    const active = STATE.view === s.key ? "active" : "";
    return '<div class="nav-item ' + active + '" data-view="' + escapeHtml(s.key) + '">'
      + '<span class="nav-icon">' + escapeHtml(s.icon) + '</span>'
      + '<span class="nav-label">' + escapeHtml(s.label) + '</span>'
      + '<span class="nav-count">' + count + '</span></div>';
  }).join("");
  document.getElementById("nav-sources").innerHTML = navSources;

  const navStatus = STATUS_LABELS.map(s => {
    const active = STATE.statusFilter === s.key ? "active" : "";
    return '<div class="nav-item ' + active + '" data-status="' + escapeHtml(s.key) + '">'
      + '<span class="nav-icon">' + escapeHtml(s.icon) + '</span>'
      + '<span class="nav-label">' + escapeHtml(s.label) + '</span></div>';
  }).join("");
  document.getElementById("nav-status").innerHTML = navStatus;

  for (const el of document.querySelectorAll("#nav-sources .nav-item")) {
    el.addEventListener("click", () => setView(el.dataset.view));
  }
  for (const el of document.querySelectorAll("#nav-status .nav-item")) {
    el.addEventListener("click", () => setStatusFilter(el.dataset.status));
  }
}

function renderToolbar() {
  const tb = document.getElementById("toolbar");
  if (STATE.view === "youtube") {
    tb.innerHTML =
      '<div>'
        + '<span class="pill ' + (STATE.ytTier==='all'?'active':'') + '" data-tier="all">All</span> '
        + '<span class="pill ' + (STATE.ytTier==='B'?'active':'') + '" data-tier="B">Tier B</span> '
        + '<span class="pill ' + (STATE.ytTier==='C'?'active':'') + '" data-tier="C">Tier C</span>'
      + '</div>'
      + '<div><label for="yt-sort">Sort</label>'
        + '<select id="yt-sort">'
          + '<option value="recent" ' + (STATE.ytSort==='recent'?'selected':'') + '>Most recent</option>'
          + '<option value="views" ' + (STATE.ytSort==='views'?'selected':'') + '>View count</option>'
          + '<option value="channel" ' + (STATE.ytSort==='channel'?'selected':'') + '>Channel</option>'
        + '</select></div>'
      + '<div><input type="text" id="search" placeholder="Search title/channel..." value="' + escapeHtml(STATE.search) + '" /></div>'
      + '<div class="toolbar-spacer"></div>'
      + '<button id="export-btn" class="primary">Export decisions</button>';
    for (const el of tb.querySelectorAll(".pill[data-tier]")) {
      el.addEventListener("click", () => { STATE.ytTier = el.dataset.tier; render(); });
    }
    tb.querySelector("#yt-sort").addEventListener("change", e => { STATE.ytSort = e.target.value; render(); });
  } else {
    const sortOpts = CAND_SORTS.map(s =>
      '<option value="' + s.key + '" ' + (STATE.candSort===s.key?'selected':'') + '>'
        + escapeHtml(s.label) + '</option>'
    ).join("");
    tb.innerHTML =
      '<div><label for="cand-sort">Sort</label>'
        + '<select id="cand-sort">' + sortOpts + '</select></div>'
      + '<div><label for="score-threshold">Min score</label>'
        + '<input type="range" id="score-threshold" min="0" max="100" value="' + STATE.minScore + '" step="5">'
        + '<span id="score-threshold-value">' + STATE.minScore + '</span></div>'
      + '<div>'
        + '<span class="pill ' + (STATE.multiSourceOnly?'active':'') + '" id="multi-source-toggle">Multi-source only</span>'
      + '</div>'
      + '<div><input type="text" id="search" placeholder="Search title/lens/tag..." value="' + escapeHtml(STATE.search) + '" /></div>'
      + '<div class="toolbar-spacer"></div>'
      + '<button id="export-btn" class="primary">Export decisions</button>';
    tb.querySelector("#cand-sort").addEventListener("change", e => {
      STATE.candSort = e.target.value;
      render();
    });
    tb.querySelector("#score-threshold").addEventListener("input", e => {
      STATE.minScore = parseInt(e.target.value, 10);
      tb.querySelector("#score-threshold-value").textContent = STATE.minScore;
      render();
    });
    tb.querySelector("#multi-source-toggle").addEventListener("click", () => {
      STATE.multiSourceOnly = !STATE.multiSourceOnly;
      render();
    });
  }
  tb.querySelector("#search").addEventListener("input", e => { STATE.search = e.target.value.toLowerCase().trim(); render(); });
  tb.querySelector("#export-btn").addEventListener("click", exportDecisions);
}

function axisBar(label, value, max) {
  max = max || 20;
  const v = value || 0;
  const pct = Math.min(100, (v / max) * 100);
  return '<div class="axis">'
    + '<div class="axis-label">' + escapeHtml(label) + '<span class="axis-value">' + v + '/' + max + '</span></div>'
    + '<div class="axis-bar"><div class="axis-fill" style="width:' + pct + '%"></div></div></div>';
}
function sourceTag(s) { return '<span class="source-tag source-' + escapeHtml(s) + '">' + escapeHtml(s) + '</span>'; }

function renderCandidateCard(c, rank) {
  const status = effectiveStatus(c);
  const statusClass = status ? "status-" + status : "";
  const statusBadge = status ? '<span class="card-status-badge badge-' + status + '">' + escapeHtml(status) + '</span>' : "";
  const videoFolder = effectiveVideoFolder(c);
  const folderLink = (status === "shipped" && videoFolder)
    ? '<a class="video-folder-link" href="../../../' + escapeHtml(videoFolder) + '/" target="_blank" rel="noreferrer">' + escapeHtml(videoFolder) + '</a>'
    : "";
  const s = c.scores || {};
  const angles = c.angles || [];
  const bestIdx = c.best_angle_index;
  const pending = c.pending_judgment ? '<span class="card-status-badge badge-later">awaiting judgment</span>' : "";
  const cooldown = (s.cooldown_reason)
    ? '<div class="angles-h" style="color:#c9a227;">[Cooldown] ' + escapeHtml(s.cooldown_reason) + '</div>' : "";
  const subCaps = s.demand_sub_caps || {};
  const subCapStr = (s.demand_sub_caps)
    ? '<small style="color:var(--fg-muted)"> = breadth ' + (subCaps.aggregator_breadth||0)
      + ' &middot; cold ' + (subCaps.cold_search||0)
      + ' &middot; auto ' + (subCaps.autocomplete||0)
      + ' &middot; TierB ' + (subCaps.tier_b_hit||0) + '</small>' : "";

  const anglesHtml = angles.length === 0
    ? '<div class="angles-h">Awaiting LLM judgment</div>'
    : '<div class="angles-h">' + angles.length + ' angle' + (angles.length>1?"s":"") + ' - pick one to make the video</div>'
      + angles.map((a, i) => {
        const isBest = i === bestIdx;
        const ascores = a.scores || {};
        return '<div class="angle ' + (isBest ? "is-best" : "") + '">'
          + '<div class="angle-num ' + (isBest ? "is-best" : "") + '">' + (i+1) + (isBest?" *":"") + '</div>'
          + '<div>'
          + '<div class="angle-title">' + escapeHtml(a.title || "") + '</div>'
          + '<div class="angle-lens">Lens: ' + escapeHtml(a.lens || "-") + '</div>'
          + '<div class="angle-scores">'
            + 'Audience ' + (ascores.audience_reach||0) + '/20 &middot; '
            + 'Hook ' + (ascores.curiosity_hook||0) + '/20 &middot; '
            + 'Depth ' + (ascores.computing_depth||0) + '/20'
            + (a.is_original_article_framing ? ' &middot; <em>article framing</em>' : "")
          + '</div>'
          + (a.notes ? '<div class="angle-lens" style="margin-top:6px;font-style:italic;">' + escapeHtml(a.notes) + '</div>' : "")
          + '<div class="angle-actions">'
            + '<button class="go-btn" onclick="event.stopPropagation();window.setStatusJS(\'' + escapeHtml(c.id) + '\',\'go\',' + i + ')">Go on this angle</button>'
          + '</div></div>'
          + '<div class="angle-comp">' + (a.composite||0) + '<small>/100</small></div></div>';
      }).join("");

  return '<article class="card ' + statusClass + '" data-id="' + escapeHtml(c.id) + '">'
    + '<div class="card-head">'
      + statusBadge
      + pending
      + '<span class="card-rank">' + rank + '.</span>'
      + '<a class="card-title" href="' + escapeHtml(c.url) + '" target="_blank" rel="noreferrer">' + escapeHtml(c.title || "(untitled)") + '</a>'
      + '<div class="card-meta">'
        + '<span>' + (c.sources||[]).map(sourceTag).join(" ") + '</span>'
        + '<span>First seen ' + escapeHtml((c.first_seen_at||"").slice(0,10)) + '</span>'
        + (c.tags && c.tags.length ? '<span>Tags: ' + c.tags.slice(0,5).map(escapeHtml).join(", ") + '</span>' : "")
        + (folderLink ? '<span>' + folderLink + '</span>' : "")
      + '</div></div>'
    + '<div class="scores-row">'
      + '<div><div class="composite-label">Best composite</div><div class="composite">' + (c.best_composite || 0) + '</div></div>'
      + axisBar("Demand", s.demand||0)
      + axisBar("Evergreen", s.evergreen||0)
      + axisBar("YT comp.", s.yt_competition||0)
    + '</div>'
    + '<div class="card-meta" style="margin-top:-4px;padding:0 18px 10px;">' + subCapStr + '</div>'
    + cooldown
    + '<div class="angles">' + anglesHtml + '</div>'
    + '<div class="card-actions">'
      + '<button class="pass-btn" onclick="window.setStatusJS(\'' + escapeHtml(c.id) + '\',\'pass\')">Pass</button>'
      + '<button class="later-btn" onclick="window.setStatusJS(\'' + escapeHtml(c.id) + '\',\'later\')">Later</button>'
      + '<button class="ship-btn" onclick="window.markShippedJS(\'' + escapeHtml(c.id) + '\')">'
        + (status === "shipped" ? "Update folder" : "Mark shipped") + '</button>'
      + (status ? '<button class="reset-btn" onclick="window.clearStatusJS(\'' + escapeHtml(c.id) + '\')">Clear status</button>' : "")
    + '</div></article>';
}

function renderYoutubeCard(v) {
  const queued = !!loadCreates()[v.id];
  const ytUrl = "https://www.youtube.com/watch?v=" + encodeURIComponent(v.id);
  return '<div class="yt-card ' + (queued?'queued':'') + '">'
    + '<div>'
    + '<div class="yt-title"><a href="' + escapeHtml(ytUrl) + '" target="_blank" rel="noreferrer">' + escapeHtml(v.title) + '</a></div>'
    + '<div class="yt-meta">'
      + '<span class="tier-badge tier-' + escapeHtml(v.channel_tier) + '">Tier ' + escapeHtml(v.channel_tier) + '</span>'
      + '<strong style="color:var(--fg);">' + escapeHtml(v.channel || v.channel_handle || "?") + '</strong>'
      + '<span>' + escapeHtml(fmtViews(v.view_count)) + '</span>'
      + '<span>' + escapeHtml(fmtRelative(v.upload_date)) + '</span>'
      + (v.channel_note ? '<span style="color:var(--fg-muted);">- ' + escapeHtml(v.channel_note) + '</span>' : "")
    + '</div></div>'
    + '<div class="yt-actions">'
      + '<button class="' + (queued?'queued':'') + '" onclick="window.toggleYT(\'' + escapeHtml(v.id) + '\')">'
        + (queued ? "[+] Queued" : "Inspire from this") + '</button>'
    + '</div></div>';
}

function render() {
  renderSidebar();
  renderToolbar();
  const grid = document.getElementById("grid");
  const title = document.getElementById("page-title");
  const sub = document.getElementById("page-sub");

  if (STATE.view === "youtube") {
    title.textContent = "YouTube - Tier B & C inspiration";
    const all = FEED.videos || [];
    // Drop already-inspired videos up front so all downstream filters and
    // sorts operate on fresh inspiration only.
    let videos = all.filter(v => !INBOX_YT_IDS.has(v.id));
    const fresh = videos.length;
    const hidden = all.length - fresh;
    if (STATE.ytTier !== "all") videos = videos.filter(v => v.channel_tier === STATE.ytTier);
    if (STATE.search) {
      const q = STATE.search;
      videos = videos.filter(v =>
        (v.title||"").toLowerCase().includes(q) ||
        (v.channel||"").toLowerCase().includes(q) ||
        (v.channel_handle||"").toLowerCase().includes(q));
    }
    if (STATE.ytSort === "recent") {
      videos.sort((a,b) => (b.upload_date||"").localeCompare(a.upload_date||""));
    } else if (STATE.ytSort === "views") {
      videos.sort((a,b) => (b.view_count||0) - (a.view_count||0));
    } else if (STATE.ytSort === "channel") {
      videos.sort((a,b) => (a.channel||"").localeCompare(b.channel||""));
    }
    const hiddenNote = hidden > 0 ? " (" + hidden + " already in inbox)" : "";
    sub.textContent = videos.length + " of " + fresh + " videos" + hiddenNote;
    grid.innerHTML = videos.length === 0
      ? '<div class="empty">No videos match the current filters.</div>'
      : videos.map(renderYoutubeCard).join("");
    return;
  }

  const viewLabels = {
    all: "All inspiration", hn: "Hacker News", reddit: "Reddit",
    lobsters: "Lobste.rs", dailydev: "daily.dev"
  };
  title.textContent = viewLabels[STATE.view] || "All";

  const candidates = Object.values(INBOX.candidates || {});
  let filtered = candidates.filter(c => {
    if (STATE.view !== "all" && !((c.sources||[]).includes(STATE.view))) return false;
    const status = effectiveStatus(c);
    if (STATE.statusFilter === "unreviewed" && status) return false;
    if (STATE.statusFilter === "pending" && !c.pending_judgment) return false;
    if (STATE.statusFilter === "all" && status === "shipped") return false;
    if (["go","pass","later","shipped"].includes(STATE.statusFilter) && status !== STATE.statusFilter) return false;
    if ((c.best_composite || 0) < STATE.minScore) return false;
    if (STATE.multiSourceOnly && (c.sources||[]).length < 2) return false;
    if (STATE.search) {
      const hay = [
        c.title, ...(c.tags||[]),
        ...((c.angles||[]).flatMap(a => [a.title, a.lens]))
      ].join(" ").toLowerCase();
      if (!hay.includes(STATE.search)) return false;
    }
    return true;
  });
  filtered.sort(compareBy(STATE.candSort));

  sub.textContent = filtered.length + " of " + candidates.length + " candidates visible";
  grid.innerHTML = filtered.length === 0
    ? '<div class="empty">No candidates match the current filters.</div>'
    : filtered.map((c, i) => renderCandidateCard(c, i+1)).join("");
}

function exportDecisions() {
  const status = loadStatus();
  const creates = loadCreates();
  const payload = {
    exported_at: new Date().toISOString(),
    candidates: status,
    create_candidates: Object.values(creates)
  };
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "decisions-" + new Date().toISOString().slice(0,10) + ".json";
  a.click();
}

function applySidebarState() {
  const collapsed = localStorage.getItem(SIDEBAR_KEY) === "1";
  const sb = document.getElementById("sidebar");
  const tg = document.getElementById("sidebar-toggle");
  sb.classList.toggle("collapsed", collapsed);
  tg.textContent = collapsed ? "›" : "‹";
}
document.getElementById("sidebar-toggle").addEventListener("click", () => {
  const collapsed = localStorage.getItem(SIDEBAR_KEY) === "1";
  localStorage.setItem(SIDEBAR_KEY, collapsed ? "0" : "1");
  applySidebarState();
});

window.toggleYT = (vid) => {
  const v = (FEED.videos || []).find(x => x.id === vid);
  if (v) toggleYoutubeQueue(v);
};
window.setStatusJS = setStatus;
window.clearStatusJS = clearStatus;
window.markShippedJS = markShipped;

document.getElementById("generated-at").textContent = INBOX.last_updated || "-";
applySidebarState();
render();
</script>
</body>
</html>
"""


def render_inbox_md(inbox: dict, top_n: int = 25, pending_limit: int = 15) -> str:
    """A flat, scannable markdown digest of the inbox for terminal triage and
    chat pasting. Surfaces the top-N unreviewed candidates by composite plus
    a thinner list of awaiting-judgment candidates so the user can spot work
    that's still queued. Reviewed candidates (go/pass/later/shipped) are
    intentionally omitted — those decisions belong in the dashboard, not in
    a fresh-triage feed."""
    cands = list((inbox.get("candidates") or {}).values())
    unreviewed = [c for c in cands if not (c.get("user_status") or "")]
    judged = [c for c in unreviewed if not c.get("pending_judgment") and (c.get("angles") or [])]
    pending = [c for c in unreviewed if c.get("pending_judgment") or not (c.get("angles") or [])]

    judged.sort(key=lambda c: c.get("best_composite") or 0, reverse=True)
    pending.sort(key=lambda c: c.get("best_composite") or 0, reverse=True)

    last_updated = inbox.get("last_updated") or "?"
    date_part = (last_updated[:10] if isinstance(last_updated, str) else "?")

    lines: list[str] = []
    lines.append(f"# topic-pipeline inbox — {date_part}")
    lines.append("")
    lines.append(
        f"{len(unreviewed)} unreviewed ({len(judged)} judged, "
        f"{len(pending)} awaiting judgment) · {len(cands)} total"
    )
    lines.append("")
    lines.append(f"## Top {min(top_n, len(judged))} unreviewed by composite")
    lines.append("")

    if not judged:
        lines.append("_(none — every judged candidate has a status)_")
        lines.append("")

    for i, c in enumerate(judged[:top_n], start=1):
        bi = c.get("best_angle_index")
        angles = c.get("angles") or []
        best = angles[bi] if (bi is not None and 0 <= bi < len(angles)) else (angles[0] if angles else None)
        s = c.get("scores") or {}
        sources = ", ".join(c.get("sources") or []) or "-"
        first_seen = (c.get("first_seen_at") or "")[:10]
        composite = c.get("best_composite") or 0

        title = (c.get("title") or "(untitled)").replace("\n", " ").strip()
        lines.append(f"### {i}. [{composite}] {title}")
        if best:
            angle_title = (best.get("title") or "").replace("\n", " ").strip()
            angle_lens = (best.get("lens") or "").replace("\n", " ").strip()
            lines.append(f"- **Best angle:** {angle_title}  _({angle_lens or '—'})_")
            ascores = best.get("scores") or {}
            lines.append(
                f"- **Axes:** demand {s.get('demand', 0)}/20 · "
                f"evergreen {s.get('evergreen', 0)}/20 · "
                f"yt-comp {s.get('yt_competition', 0)}/20 · "
                f"audience {ascores.get('audience_reach', 0)}/20 · "
                f"hook {ascores.get('curiosity_hook', 0)}/20 · "
                f"depth {ascores.get('computing_depth', 0)}/20"
            )
        else:
            lines.append(
                f"- **Axes:** demand {s.get('demand', 0)}/20 · "
                f"evergreen {s.get('evergreen', 0)}/20 · "
                f"yt-comp {s.get('yt_competition', 0)}/20"
            )
        cooldown = s.get("cooldown_reason")
        if cooldown:
            lines.append(f"- **Cooldown:** {cooldown}")
        lines.append(f"- **Sources:** {sources}  ·  first seen {first_seen}")
        lines.append(f"- <{c.get('url') or ''}>")
        lines.append("")

    if pending:
        lines.append(f"## Awaiting judgment ({len(pending)})")
        lines.append("")
        lines.append("Score is the 3-axis floor (demand + evergreen + yt_competition / 1.2).")
        lines.append("")
        for c in pending[:pending_limit]:
            title = (c.get("title") or "(untitled)").replace("\n", " ").strip()
            sources = ",".join(c.get("sources") or []) or "-"
            composite = c.get("best_composite") or 0
            lines.append(
                f"- [{composite}*] {title}  ({sources})  "
                f"<{c.get('url') or ''}>"
            )
        if len(pending) > pending_limit:
            lines.append(f"- _… and {len(pending) - pending_limit} more_")
        lines.append("")

    return "\n".join(lines)


def collect_inbox_youtube_ids(inbox: dict) -> list[str]:
    """Walk inbox candidates with sources=['youtube'] and pull the YT video ID
    out of per_source[].external_id (where apply_decisions.py stashed it).
    The dashboard uses this set to suppress already-inspired videos from the
    YouTube tab so the user only sees fresh inspiration each day."""
    ids: list[str] = []
    for c in (inbox.get("candidates") or {}).values():
        if "youtube" not in (c.get("sources") or []):
            continue
        for ps in c.get("per_source") or []:
            if ps.get("source") == "youtube" and ps.get("external_id"):
                ids.append(ps["external_id"])
    return ids


def render_dashboard(inbox: dict, feed: dict) -> str:
    inbox_payload = json.dumps(inbox, ensure_ascii=False)
    feed_payload = json.dumps(feed, ensure_ascii=False)
    inbox_yt_ids_payload = json.dumps(collect_inbox_youtube_ids(inbox))
    return (DASHBOARD_TEMPLATE
            .replace("__INBOX_DATA__", inbox_payload)
            .replace("__FEED_DATA__", feed_payload)
            .replace("__INBOX_YT_IDS__", inbox_yt_ids_payload))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(Path(__file__).parent / "config.json"))
    args = ap.parse_args()

    cfg_path = Path(args.config).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base_dir = cfg_path.parent
    inbox_path = (base_dir / cfg["paths"]["inbox_json"]).resolve()
    feed_path = (base_dir / cfg["paths"]["competitors_feed"]).resolve()
    dashboard = (base_dir / cfg["paths"]["dashboard_html"]).resolve()
    inbox_md_rel = cfg["paths"].get("inbox_md")
    inbox_md_path = (base_dir / inbox_md_rel).resolve() if inbox_md_rel else None

    inbox_raw = load_json(inbox_path, {"version": 2, "last_updated": None, "candidates": {}})
    feed_raw = load_json(feed_path, {"videos": []})
    inbox = inbox_raw if isinstance(inbox_raw, dict) else {"version": 2, "last_updated": None, "candidates": {}}
    feed = feed_raw if isinstance(feed_raw, dict) else {"videos": feed_raw}

    html_text = render_dashboard(inbox, feed)
    dashboard.write_text(html_text, encoding="utf-8")
    print(f"[wrote]   {dashboard}", file=sys.stderr)

    if inbox_md_path:
        md_text = render_inbox_md(inbox)
        inbox_md_path.write_text(md_text, encoding="utf-8")
        print(f"[wrote]   {inbox_md_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
