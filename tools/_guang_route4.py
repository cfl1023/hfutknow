# -*- coding: utf-8 -*-
"""看 uniPagesPostDetail 路由定义。"""
from pathlib import Path

t = (Path(__file__).resolve().parents[1] / "site" / "data" / "_community_app.js").read_text(
    encoding="utf-8", errors="ignore")
i = t.find('path:"uniPagesPostDetail"')
print(t[i - 80:i + 260])
print("=== nav to detail ===")
j = t.find("uniPagesPostDetail")
while j > 0 and j < len(t):
    seg = t[max(0, j - 120):j + 60]
    if "push" in seg or "href" in seg or "to:" in seg:
        print(seg.replace("\n", " "))
        break
    j = t.find("uniPagesPostDetail", j + 10)
