# -*- coding: utf-8 -*-
"""修正 moreBtn 里误用 head 的分支，并确认 router 有 guang 路由。"""
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "site" / "app.js"
s = p.read_text(encoding="utf-8")
bad = "    else if (head === 'guang') renderGuang(params.get('g') || '');\n"
good = "        else if (path === 'guang') renderGuang(params.get('g') || '');\n"
print("bad count", s.count(bad))
s = s.replace(bad, good)
p.write_text(s, encoding="utf-8")
for ln in s.splitlines():
    if "guang" in ln:
        print(repr(ln))
