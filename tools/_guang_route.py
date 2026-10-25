# -*- coding: utf-8 -*-
"""找出逛逛前端里帖子详情的路由格式。"""
import re
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "site" / "js" / "app.bd968d6f.js"
s = p.read_text(encoding="utf-8", errors="ignore")
paths = sorted(set(re.findall(r'path\s*:\s*"([^"]{2,60})"', s)))
print("paths:", paths[:40])
for kw in ("topicDetail", "forumTopic", "detail", "topic"):
    for m in list(re.finditer(kw, s))[:4]:
        print(kw, "…", s[max(0, m.start() - 90):m.start() + 90].replace("\n", " "))
