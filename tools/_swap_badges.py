# -*- coding: utf-8 -*-
"""把卡片里的内联 badge 表达式换成 ggBadges(item)。"""
import re
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "site" / "app.js"
s = p.read_text(encoding="utf-8")
start = s.find("${item.sourceType === 'gg' ? (item.tags || [])")
if start < 0:
    print("pattern miss")
else:
    end = s.find(": ''}", start)
    end = end + len(": ''}")
    s = s[:start] + "${ggBadges(item)}" + s[end:]
    p.write_text(s, encoding="utf-8")
    print("cleanup ok")
