# -*- coding: utf-8 -*-
"""加「逛逛」页：路由 #/guang、按版块分组、导航入口、主页快捷链接。"""
import io, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "site" / "app.js"
HTML = ROOT / "site" / "index.html"
CSS = ROOT / "site" / "style.css"

app = APP.read_text(encoding="utf-8")
html = HTML.read_text(encoding="utf-8")
css = CSS.read_text(encoding="utf-8")

# ---- app.js ----
a1 = "    if (bili) list = list.filter((i) => i.sourceType === 'bili');\n"
assert a1 in app, "anchor1"
app = app.replace(a1, a1 + "    if (!sourceId && !bili) list = list.filter((i) => i.feed !== false);\n")

a2 = "    else if (path === 'bili') renderBrowse({ bili: true });\n"
assert a2 in app, "anchor2"
app = app.replace(a2, a2 + "    else if (head === 'guang') renderGuang(params.get('g') || '');\n")

a3 = "      : head === 'competitions' ? 'competitions' : head === 'prefs' ? 'prefs'"
assert a3 in app, "anchor3"
app = app.replace(a3, "      : head === 'competitions' ? 'competitions' : head === 'guang' ? 'guang' : head === 'prefs' ? 'prefs'")

a4 = "        else if (path === 'bili') renderBrowse({ bili: true });\n"
if a4 in app:
    app = app.replace(a4, a4 + "        else if (path === 'guang') renderGuang(params.get('g') || '');\n")
else:
    print("WARN anchor4 missing")

a5 = '<a href="#/people">👤 ${L.nav.people}</a></p>'
assert a5 in app, "anchor5"
app = app.replace(a5, '<a href="#/people">👤 ${L.nav.people}</a><a href="#/guang">👥 逛逛</a></p>')

RENDER = r'''
  const GG_ORDER = ['mate', 'academics', 'growth', 'skills', 'life', 'scenery',
                    'culture', 'ideology', 'practice', 'memory'];
  const GG_LABEL = {
    mate: ['校园搭子', 'Buddy'], academics: ['学风学业', 'Study'],
    growth: ['成长分享', 'Growth'], skills: ['综合素质', 'Skills'],
    life: ['生活随拍', 'Daily'], scenery: ['校园风光', 'Campus'],
    culture: ['传统文化', 'Culture'], ideology: ['思想教育', 'Civic'],
    practice: ['社会实践', 'Practice'], memory: ['校园记忆', 'Memories'],
  };

  function renderGuang(active) {
    const en = S.lang === 'en';
    const posts = (S.items || []).filter((i) => i.sourceId === 'gg-forum');
    const groups = {};
    posts.forEach((p) => {
      const key = (p.community && p.community.group) || 'growth';
      (groups[key] = groups[key] || []).push(p);
    });
    const keys = GG_ORDER.filter((k) => (groups[k] || []).length);
    const chips = [{ k: '', n: posts.length, t: en ? 'All' : '全部' }]
      .concat(keys.map((k) => ({ k, n: groups[k].length, t: GG_LABEL[k][en ? 1 : 0] })));
    let out = `<section class="hero" style="padding-bottom:8px">
      <h1 style="font-size:30px">${en ? 'Community · Hooting Lake' : '逛逛 · 斛兵塘'}</h1>
      <p>${en ? 'Posts from the campus community app, grouped by section.' : '学校社区 App 里的帖子，按版块分好。发帖量不大，胜在是真人真事。'}</p>
      <div class="chip-row">${chips.map((c) => `<a class="chip${active === c.k ? ' active' : ''}" href="#/guang${c.k ? '?g=' + c.k : ''}">${esc(c.t)}<span class="n">${c.n}</span></a>`).join('')}</div>
    </section>`;
    const use = active && groups[active] ? [active] : keys;
    use.forEach((k) => {
      const list = groups[k].slice().sort((a, b) => String(b.publishedAt || '').localeCompare(String(a.publishedAt || '')));
      out += `<section class="gg-group"><h2>${esc(GG_LABEL[k][en ? 1 : 0])}<span>${list.length}${en ? '' : ' 条'}</span></h2>${gridHTML(list, S.limit)}</section>`;
    });
    if (!posts.length) out += emptyHTML();
    document.title = (en ? 'Community' : '逛逛') + ' · ' + (en ? S.site.enName : S.site.name);
    app().innerHTML = out;
  }

'''

a6 = "  function renderSources() {"
assert a6 in app, "anchor6"
app = app.replace(a6, RENDER + a6, 1)

# ---- index.html ----
h1 = '<a href="#/competitions" data-nav="competitions">竞赛</a>'
assert h1 in html, "html1"
html = html.replace(h1, h1 + '\n      <a href="#/guang" data-nav="guang">逛逛</a>')

h2 = '<a href="#/sources" data-tab="sources"><svg viewBox="0 0 24 24"><path d="M4 6h16M4 12h16M4 18h10"/></svg><span>来源</span></a>'
assert h2 in html, "html2"
html = html.replace(
    h2,
    '<a href="#/guang" data-tab="guang"><svg viewBox="0 0 24 24"><circle cx="9" cy="9" r="3"/><circle cx="16.5" cy="10.5" r="2.3"/>'
    '<path d="M3.5 19c0-2.6 2.5-4.4 5.5-4.4s5.5 1.8 5.5 4.4M15.2 15.2c2.4.2 4.3 1.6 4.3 3.8"/></svg><span>逛逛</span></a>')

# ---- CSS ----
css += """
/* ---- 逛逛（斛兵塘）---- */
.gg-group{margin-top:26px}
.gg-group h2{display:flex;align-items:baseline;gap:8px;font-size:16px;font-weight:650;margin:0 0 10px}
.gg-group h2 span{font-size:12px;font-weight:400;color:var(--muted)}
"""

APP.write_text(app, encoding="utf-8")
HTML.write_text(html, encoding="utf-8")
CSS.write_text(css, encoding="utf-8")
print("patched app.js / index.html / style.css")
