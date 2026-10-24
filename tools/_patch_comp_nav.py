# -*- coding: utf-8 -*-
from pathlib import Path

# 导航加「竞赛」
h = Path("site/index.html")
s = h.read_text(encoding="utf-8")
if 'data-nav="competitions"' not in s:
    s = s.replace('<a href="#/people" data-nav="people">教师</a>',
                  '<a href="#/people" data-nav="people">教师</a>\n      <a href="#/competitions" data-nav="competitions">竞赛</a>')
h.write_text(s, encoding="utf-8")

# 竞赛页样式
c = Path("site/style.css")
css = c.read_text(encoding="utf-8")
css += """
/* ---------- 竞赛 ---------- */
.comp-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 8px; padding-bottom: 30px; }
.comp { display: flex; flex-direction: column; gap: 4px; padding: 12px 14px; background: var(--surface);
  border: 1px solid var(--line); border-radius: 10px; font-size: 13.5px; }
.comp.rel { border-color: color-mix(in srgb, var(--ok) 45%, var(--line)); background: color-mix(in srgb, var(--ok-soft) 45%, var(--surface)); }
.comp .cn { font-weight: 500; }
.comp .cr { font-size: 11px; color: var(--ok); }
"""
c.write_text(css, encoding="utf-8")
print("patched nav + styles")
