# -*- coding: utf-8 -*-
"""加「B站」入口：chip + 路由 + 过滤。"""
from pathlib import Path

p = Path("site/app.js")
t = p.read_text(encoding="utf-8")

# 1) chipsHTML 末尾加 B站 chip
old = """    S.categories.forEach((c, idx) => {
      out += `<a class="chip${idx === 0 ? ' group-start' : ''}${activeCat === c.id ? ' active' : ''}" href="#/c/${c.id}">${S.lang === 'en' ? c.en : c.zh}<span class="n">${counts[c.id] || 0}</span></a>`;
    });
    return out;"""
new = """    S.categories.forEach((c, idx) => {
      out += `<a class="chip${idx === 0 ? ' group-start' : ''}${activeCat === c.id ? ' active' : ''}" href="#/c/${c.id}">${S.lang === 'en' ? c.en : c.zh}<span class="n">${counts[c.id] || 0}</span></a>`;
    });
    const nb = S.items.filter((i) => i.sourceType === 'bili').length;
    if (nb) out += `<a class="chip chip-bili${S.route === 'bili' ? ' active' : ''}" href="#/bili">B站<span class="n">${nb}</span></a>`;
    return out;"""
assert old in t
t = t.replace(old, new)

# 2) renderBrowse 支持 bili 过滤
old2 = """  function renderBrowse({ intent = null, cat = null, sourceId = null, q = '', forYou = false }) {
    S._q = q;
    let list = S.items.slice();
    if (forYou) list = list.filter(isRelated);"""
new2 = """  function renderBrowse({ intent = null, cat = null, sourceId = null, q = '', forYou = false, bili = false }) {
    S._q = q;
    let list = S.items.slice();
    if (bili) list = list.filter((i) => i.sourceType === 'bili');
    if (forYou) list = list.filter(isRelated);"""
assert old2 in t
t = t.replace(old2, new2)

# 3) 标题与 hero
old3 = """      : forYou ? L.forYou
      : intent === 'activity' ? L.activity : intent === 'information' ? L.information : '';"""
new3 = """      : bili ? 'B站 · 真人内容'
      : forYou ? L.forYou
      : intent === 'activity' ? L.activity : intent === 'information' ? L.information : '';"""
assert old3 in t
t = t.replace(old3, new3)

old4 = """    } else {
      html += `<section class="hero" style="padding-bottom:6px"><h1 style="font-size:30px">${esc(title)}</h1>
        <p>${forYou ? L.heroSub : ''}</p></section>`;"""
new4 = """    } else {
      html += `<section class="hero" style="padding-bottom:6px"><h1 style="font-size:30px">${esc(title)}</h1>
        <p>${bili ? '从 B 站搜到的学生 / UP 主视频，按发布时间倒序。不是官方通稿。' : forYou ? L.heroSub : ''}</p></section>`;"""
assert old4 in t
t = t.replace(old4, new4)

# 4) 路由
old5 = """    else if (path === 'foryou') renderBrowse({ forYou: true });"""
new5 = """    else if (path === 'foryou') renderBrowse({ forYou: true });
    else if (path === 'bili') renderBrowse({ bili: true });"""
assert old5 in t
t = t.replace(old5, new5)

# 5) isHome 判断避免误判
old6 = "    const isHome = !cat && !sourceId && !q && (!intent || intent === 'all') && !forYou;"
new6 = "    const isHome = !cat && !sourceId && !q && !bili && (!intent || intent === 'all') && !forYou;"
assert old6 in t
t = t.replace(old6, new6)

p.write_text(t, encoding="utf-8")
print("bili route patched")
