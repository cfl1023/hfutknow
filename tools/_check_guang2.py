# -*- coding: utf-8 -*-
"""看 dump 是否完整 + 逐组数卡片。"""
import os
import re

p = os.path.join(os.environ["TEMP"], "v_guang.html")
q = open(p, encoding="utf-8", errors="ignore").read()
print("bytes", os.path.getsize(p), "ends </html>", q.rstrip().endswith("</html>"))
parts = re.split(r'<section class="gg-group">', q)
for blk in parts[1:]:
    name = re.search(r"<h2>(.*?)<span>", blk)
    n = re.search(r"<h2>.*?<span>(\d+) 条", blk)
    cards = blk.count('<a class="card"')
    print((name.group(1) if name else "?"), "declared", n.group(1) if n else "?", "cards", cards)
