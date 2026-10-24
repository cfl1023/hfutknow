# -*- coding: utf-8 -*-
"""站点加入竞赛页：导航、路由、数据加载、渲染。"""
from pathlib import Path

p = Path("site/app.js")
t = p.read_text(encoding="utf-8")

# 1) 路由
t = t.replace(
    ": head === 'sources' ? 'sources' : head === 'people' ? 'people'",
    ": head === 'sources' ? 'sources' : head === 'people' ? 'people'\n      : head === 'competitions' ? 'competitions'")

old_route = "    else if (head === 'people') { renderPeople(); }"
new_route = "    else if (head === 'people') { renderPeople(); }\n    else if (head === 'competitions') { renderCompetitions(); }"
assert old_route in t
t = t.replace(old_route, new_route)

# 2) 数据加载
old_fetch = "        for (const [file, key] of [['people.json', 'peopleData'], ['plans.json', 'plansData']]) {"
new_fetch = "        for (const [file, key] of [['people.json', 'peopleData'], ['plans.json', 'plansData'], ['competitions.json', 'competitionsData']]) {"
assert old_fetch in t
t = t.replace(old_fetch, new_fetch)

old_assign = "      S.plans = (S.plansData && S.plansData.plans) || [];"
new_assign = ("      S.plans = (S.plansData && S.plansData.plans) || [];\n"
              "      S.competitions = (S.competitionsData && S.competitionsData.items) || [];")
assert old_assign in t
t = t.replace(old_assign, new_assign)

# 3) 渲染函数（插在 renderPeople 后面）
anchor = "  function renderContribute() {"
func = '''  function renderCompetitions() {
    $('#chips').hidden = true;
    const L = t();
    const comps = S.competitions || [];
    const tiers = ['三大赛', 'A类', 'B类'];
    const groups = {};
    comps.forEach((c) => { (groups[c.tier] = groups[c.tier] || []).push(c); });
    const body = comps.length
      ? tiers.filter((tr) => groups[tr]).map((tr) => `<div class="grp-title">${esc(tr)} · ${groups[tr].length}</div>
        <div class="comp-grid">${groups[tr].map((c) => `<div class="comp${c.related ? ' rel' : ''}">
          <span class="cn">${esc(c.name)}</span>
          ${c.related ? '<span class="cr">★ 与集成电路相关</span>' : ''}</div>`).join('')}</div>`).join('')
      : `<div class="empty"><b>${L.peopleEmpty}</b></div>`;
    document.title = '学科竞赛 · ' + (S.lang === 'en' ? S.site.enName : S.site.name);
    app().innerHTML = `<section class="src-head"><h1>学科竞赛</h1>
      <p>依据《合肥工业大学学科竞赛赛事列表（2026年版）》，共 ${comps.length} 项。带 ★ 的与你（集成电路）相关。</p>
      </section>${body}`;
  }

'''
assert anchor in t
t = t.replace(anchor, func + anchor)

p.write_text(t, encoding="utf-8")
print("patched competitions page")
