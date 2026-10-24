# -*- coding: utf-8 -*-
import io
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------- index.html: 手机底栏把「日历」换成「竞赛」 ----------
p = ROOT / "site" / "index.html"
s = p.read_text(encoding="utf-8")
old = '  <a href="#/calendar" data-tab="calendar"><svg viewBox="0 0 24 24"><path d="M12 6v6l4 2"/><circle cx="12" cy="12" r="8.5"/></svg><span>日历</span></a>\n'
new = ('  <a href="#/competitions" data-tab="competitions"><svg viewBox="0 0 24 24">'
       '<path d="M8 4h8v3a4 4 0 0 1-8 0z"/><path d="M8 5H5.5a2.5 2.5 0 0 0 0 5H8M16 5h2.5a2.5 2.5 0 0 1 0 5H16"/>'
       '<path d="M12 11v5M8.5 20h7M9.5 16.5h5l.5 3.5h-6z"/></svg><span>竞赛</span></a>\n')
assert old in s, "tabbar calendar anchor not found"
s = s.replace(old, new)
p.write_text(s, encoding="utf-8")
print("index.html tabbar patched")

# ---------- app.js ----------
p = ROOT / "site" / "app.js"
s = p.read_text(encoding="utf-8")
assert s.count("function renderPeople()") == 1

old_people_start = """  function renderPeople() {
    $('#chips').hidden = true;
    const L = t();
    const people = S.people || [];"""
new_people_start = """  function renderPeople() {
    $('#chips').hidden = true;
    const L = t();
    const { params } = parseHash();
    const colId = params.get('college') || '';
    const colleges = (S.peopleColleges && S.peopleColleges.length)
      ? S.peopleColleges : (S.colleges || []);
    const people = (S.people || []).filter((p) => !colId || p.collegeId === colId);"""
assert old_people_start in s
s = s.replace(old_people_start, new_people_start)

old_html = """    app().innerHTML = `<section class="src-head"><h1>${L.peopleTitle}</h1><p>${L.peopleSub}</p></section>${body}${planHTML}`;"""
new_html = """    const colChips = colleges.map((c) => `<button class="chip${colId === c.id ? ' on' : ''}" data-college="${esc(c.id)}">${esc(c.name)}</button>`).join('');
    app().innerHTML = `<section class="src-head"><h1>${L.peopleTitle}</h1><p>${L.peopleSub}</p></section>
      <div class="chip-row" id="peopleCols"><button class="chip${colId ? '' : ' on'}" data-college="">全部</button>${colChips}</div>
      ${body}${planHTML}`;
    const row = $('#peopleCols');
    if (row) row.addEventListener('click', (e) => {
      const b = e.target.closest('[data-college]');
      if (!b) return;
      const id = b.getAttribute('data-college');
      go(`/people${id ? '?college=' + encodeURIComponent(id) : ''}`);
    });"""
assert old_html in s
s = s.replace(old_html, new_html)

# 卡片 meta 显示学院 + 系
old_meta = """          <span class="cl">${esc(p.college)} · ${L.peopleLink} ↗</span>"""
new_meta = """          <span class="cl">${esc(p.college)}${p.dept ? ' · ' + esc(p.dept) : ''} · ${L.peopleLink} ↗</span>"""
assert old_meta in s
s = s.replace(old_meta, new_meta)

p.write_text(s, encoding="utf-8")
print("app.js people patched")
