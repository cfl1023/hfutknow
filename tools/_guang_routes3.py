# -*- coding: utf-8 -*-
"""列出逛逛 bundle 里与帖子/详情相关的路由名。"""
import re
from pathlib import Path

t = (Path(__file__).resolve().parents[1] / "site" / "data" / "_community_app.js").read_text(
    encoding="utf-8", errors="ignore")
paths = sorted(set(re.findall(r'path\s*:\s*"([^"]{2,60})"', t)))
print("total paths", len(paths))
hit = [p for p in paths if re.search(r"topic|forum|post|dynamic|circle", p, re.I)]
print("topic-ish:", hit[:20])
# 看路由定义附近是否有 id 参数
for p in hit[:6]:
    i = t.find('path:"' + p + '"')
    print("---", p, t[i:i + 160].replace("\n", " "))
