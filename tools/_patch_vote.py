# -*- coding: utf-8 -*-
"""个性化投票：每张卡片 👍推荐 / 👎不感兴趣，本地学习关键词并影响排序。"""
from pathlib import Path

p = Path("site/app.js")
s = p.read_text(encoding="utf-8")

# ---------- 1) i18n ----------
s = s.replace("      newBadge: '新',",
              "      newBadge: '新',\n"
              "      voteUp: '推荐', voteDown: '不感兴趣', votedUp: '已推荐', votedDown: '已屏蔽',\n"
              "      prefsTitle: '我的偏好', prefsHint: '你在卡片上点的 👍/ 会被记下来：命中的词加分，屏蔽的词降权。只存在这台设备上，不上传。',\n"
              "      prefsUp: '推荐过', prefsDown: '屏蔽过', prefsTokens: '学到的关键词（数字=权重）', prefsClear: '清空全部偏好', prefsEmpty: '还没有点过任何 👍/。去列表里点几下，排序就会变成你的口味。',\n", 1)
s = s.replace("      newBadge: 'NEW',",
              "      newBadge: 'NEW',\n"
              "      voteUp: 'Like', voteDown: 'Not interested', votedUp: 'Liked', votedDown: 'Hidden',\n"
              "      prefsTitle: 'My preferences', prefsHint: 'Your 👍/👎 taps are learned locally: matching words boost, blocked words demote. Stored on this device only.',\n"
              "      prefsUp: 'liked', prefsDown: 'hidden', prefsTokens: 'Learned keywords (weight)', prefsClear: 'Clear all', prefsEmpty: 'No votes yet. Tap 👍/👎 on cards to tune the ranking.',\n", 1)

# ---------- 2) prefs 存取 + 权重 ----------
anchor = "  function relevance(item) {"
prefs_fns = '''  const PREFS_KEY = 'ck-prefs-v1';
  function loadPrefs() {
    try { S.prefs = JSON.parse(localStorage.getItem(PREFS_KEY)) || { up: {}, down: {} }; }
    catch (e) { S.prefs = { up: {}, down: {} }; }
    if (!S.prefs.up) S.prefs.up = {};
    if (!S.prefs.down) S.prefs.down = {};
    S.tw = tokenWeights();
  }
  function savePrefs() {
    try { localStorage.setItem(PREFS_KEY, JSON.stringify(S.prefs)); } catch (e) {}
    S.tw = tokenWeights();
  }
  function itemTokens(item) {
    const P = S.profile || {};
    const toks = new Set();
    (item.tags || []).forEach((t) => { if (t && t.length >= 2) toks.add(t); });
    if (item.category) toks.add(catName(item.category));
    const sn = (item.sourceName || '').replace(/^B站 · |^贴吧 · |^互联网 · /, '');
    if (sn.length >= 3) toks.add(sn.slice(0, 10));
    const hay = `${item.title} ${item.summary || ''}`;
    (P.keywords || []).forEach((k) => { if (hay.includes(k)) toks.add(k); });
    if (item.competition && item.competition.name) toks.add(item.competition.name);
    return Array.from(toks).slice(0, 8);
  }
  function tokenWeights() {
    const w = {};
    Object.values(S.prefs.up).forEach((ts) => ts.forEach((t) => { w[t] = (w[t] || 0) + 1; }));
    Object.values(S.prefs.down).forEach((ts) => ts.forEach((t) => { w[t] = (w[t] || 0) - 1.5; }));
    return w;
  }
  function toggleVote(id, dir) {
    const item = S.items.find((i) => i.id === id);
    if (!item) return;
    const other = dir === 'up' ? 'down' : 'up';
    if (S.prefs[dir][id]) { delete S.prefs[dir][id]; }
    else { S.prefs[dir][id] = itemTokens(item); delete S.prefs[other][id]; }
    savePrefs();
    if (S.drawerOpen && S.drawerId === id) openDrawer(id, true);
    route();
  }

'''
assert anchor in s
s = s.replace(anchor, prefs_fns + anchor, 1)

# ---------- 3) relevance 接入 ----------
old = """    const age = (Date.now() - new Date(item.publishedAt).getTime()) / 864e5;
    score += Math.max(0, 3 - age * 0.6);
    return Math.round(score * 10) / 10;
  }"""
new = """    const age = (Date.now() - new Date(item.publishedAt).getTime()) / 864e5;
    score += Math.max(0, 3 - age * 0.6);
    if (S.prefs) {
      if (S.prefs.down[item.id]) return -999;
      if (S.prefs.up[item.id]) score += 30;
      const tw = S.tw || {};
      let ts = 0;
      for (const k in tw) { if (text.includes(k)) ts += tw[k] * 3; }
      score += Math.max(-15, Math.min(12, ts));
    }
    return Math.round(score * 10) / 10;
  }"""
assert old in s
s = s.replace(old, new, 1)

# ---------- 4) 卡片投票按钮 ----------
old = """      <h3>${hl(item.title, S._q)}</h3>"""
new = """      <span class="vote-row">
        <button class="vote${S.prefs && S.prefs.up[item.id] ? ' on' : ''}" data-vote="up" data-id="${esc(item.id)}" title="${t().voteUp}" aria-label="${t().voteUp}">👍</button>
        <button class="vote${S.prefs && S.prefs.down[item.id] ? ' on' : ''}" data-vote="down" data-id="${esc(item.id)}" title="${t().voteDown}" aria-label="${t().voteDown}">👎</button>
      </span>
      <h3>${hl(item.title, S._q)}</h3>"""
assert old in s
s = s.replace(old, new, 1)

# ---------- 5) 点击处理 ----------
old = """      const close = e.target.closest('[data-close]');
      if (close) { e.preventDefault(); closeDrawer(); return; }"""
new = """      const close = e.target.closest('[data-close]');
      if (close) { e.preventDefault(); closeDrawer(); return; }

      const vote = e.target.closest('.vote');
      if (vote) { e.preventDefault(); e.stopPropagation(); toggleVote(vote.dataset.id, vote.dataset.vote); return; }"""
assert old in s
s = s.replace(old, new, 1)

# ---------- 6) 抽屉记录 id + 详情按钮 ----------
old = """  function openDrawer(id) {
    const item = S.items.find((i) => i.id === id);
    if (!item) return;"""
new = """  function openDrawer(id, keep) {
    const item = S.items.find((i) => i.id === id);
    if (!item) return;
    S.drawerId = id;
    if (!keep) S.scrollY = window.scrollY;"""
assert old in s
s = s.replace(old, new, 1)
s = s.replace("""    const drawer = $('#drawer');
    S.scrollY = window.scrollY;
    drawer.innerHTML""", """    const drawer = $('#drawer');
    drawer.innerHTML""", 1)

old = """      <div class="dt-actions">${original}</div>`;"""
new = """      <div class="dt-actions">${original}
        <button class="btn ghost${S.prefs && S.prefs.up[item.id] ? ' voted' : ''}" data-vote="up" data-id="${esc(item.id)}">👍 ${t().voteUp}</button>
        <button class="btn ghost${S.prefs && S.prefs.down[item.id] ? ' voted' : ''}" data-vote="down" data-id="${esc(item.id)}">👎 ${t().voteDown}</button>
      </div>`;"""
assert old in s
s = s.replace(old, new, 1)

# ---------- 7) 偏好页 + 路由 ----------
old = """    else if (head === 'competitions') renderCompetitions();"""
new = """    else if (head === 'competitions') renderCompetitions();
    else if (head === 'prefs') renderPrefs();"""
assert old in s
s = s.replace(old, new, 1)

anchor = "  function renderContribute() {"
prefs_page = '''  function renderPrefs() {
    $('#chips').hidden = true;
    const L = t();
    const up = Object.keys(S.prefs.up).length, down = Object.keys(S.prefs.down).length;
    const tw = S.tw || {};
    const toks = Object.entries(tw).sort((a, b) => b[1] - a[1]);
    const body = (up || down)
      ? `<div class="prefs-stats"><span class="tag">👍 ${L.prefsUp} ${up}</span><span class="tag">👎 ${L.prefsDown} ${down}</span></div>
        <div class="grp-title">${L.prefsTokens}</div>
        <div class="roster-chips">${toks.map(([k, v]) => `<span class="roster-chip${v > 0 ? ' rel' : ''}">${esc(k)} · ${v > 0 ? '+' : ''}${Math.round(v * 10) / 10}</span>`).join('')}</div>
        <p style="margin-top:22px"><button class="btn ghost" id="clearPrefs">${L.prefsClear}</button></p>`
      : `<div class="empty"><b>${L.prefsEmpty}</b></div>`;
    document.title = `${L.prefsTitle} · ${S.lang === 'en' ? S.site.enName : S.site.name}`;
    app().innerHTML = `<section class="src-head"><h1>${L.prefsTitle}</h1><p>${L.prefsHint}</p></section>${body}`;
    const btn = $('#clearPrefs');
    if (btn) btn.addEventListener('click', () => { S.prefs = { up: {}, down: {} }; savePrefs(); route(); });
  }

'''
assert anchor in s
s = s.replace(anchor, prefs_page + anchor, 1)

# ---------- 8) boot 加载 prefs ----------
old = "      S.profile = S.site.profile || {};"
new = "      S.profile = S.site.profile || {};\n      loadPrefs();"
assert old in s
s = s.replace(old, new, 1)

# ---------- 9) 顶栏/底栏入口 ----------
old = "      <a href=\"#/competitions\" data-nav=\"competitions\">竞赛</a>"
new = "      <a href=\"#/competitions\" data-nav=\"competitions\">竞赛</a>\n      <a href=\"#/prefs\" data-nav=\"prefs\">偏好</a>"
if old in s:
    pass
p.write_text(s, encoding="utf-8")
print("app.js patched")

# index.html 加偏好入口
h = Path("site/index.html")
t = h.read_text(encoding="utf-8")
old = '<a href="#/competitions" data-nav="competitions">竞赛</a>'
new = '<a href="#/competitions" data-nav="competitions">竞赛</a>\n      <a href="#/prefs" data-nav="prefs">偏好</a>'
if 'data-nav="prefs"' not in t and old in t:
    t = t.replace(old, new, 1)
    h.write_text(t, encoding="utf-8")
    print("index nav ok")

# ---------- 10) CSS ----------
c = Path("site/style.css")
css = c.read_text(encoding="utf-8")
css += """
/* ---- 个性化投票 ---- */
.card { position: relative; }
.vote-row { position: absolute; top: 8px; right: 8px; display: flex; gap: 2px; opacity: .45; transition: opacity .15s; }
.card:hover .vote-row, .vote-row:has(.on) { opacity: 1; }
.vote { border: 0; background: var(--surface-2); border-radius: 7px; width: 30px; height: 30px; font-size: 14px;
  cursor: pointer; line-height: 1; display: grid; place-items: center; padding: 0; }
.vote:hover { background: var(--accent-soft); }
.vote.on { background: var(--accent); filter: saturate(1.2); }
.vote[data-vote="down"].on { background: var(--muted); }
.dt-actions .btn.voted { background: var(--text); color: var(--bg); border-color: var(--text); }
.prefs-stats { display: flex; gap: 8px; margin: 0 0 18px; }
@media (max-width: 780px) {
  .vote-row { opacity: 1; top: 6px; right: 6px; }
  .vote { width: 34px; height: 34px; font-size: 16px; }
  .card h3 { padding-right: 74px; }
}
"""
c.write_text(css, encoding="utf-8")
print("css ok")

# ---------- 11) sw 版本 ----------
sw = Path("site/sw.js")
t = sw.read_text(encoding="utf-8")
t = t.replace("hfutknow-v5", "hfutknow-v6")
sw.write_text(t, encoding="utf-8")
print("sw v6")
