# -*- coding: utf-8 -*-
"""打印逛逛页面卡片要素，人工核对。"""
import os
import re

s = open(os.path.join(os.environ["TEMP"], "v_guang.html"), encoding="utf-8", errors="ignore").read()
cards = re.findall(r'<a class="card[^"]*" href="#/i/(gg-[^"]+)".*?<h3>(.*?)</h3>\s*<p class="sum">(.*?)</p>', s, re.S)
print("cards", len(cards))
for cid, title, summ in cards[:8]:
    t = re.sub(r"<[^>]+>", "", title)
    sm = re.sub(r"<[^>]+>", "", summ)
    print(f"- {cid} | {t[:26]} | {sm[:60]}")
