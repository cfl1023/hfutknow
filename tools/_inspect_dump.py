# -*- coding: utf-8 -*-
"""检查 dist 渲染结果：找最后一个 fresh-line / footCrawl 的实际文本。"""
import pathlib
import re

p = pathlib.Path(r"C:\Users\lenovo\AppData\Local\Temp\ck_fresh.html")
if not p.exists():
    p = pathlib.Path("dist/_dump.html")
html = p.read_text(encoding="utf-8", errors="replace")
print("len:", len(html))
for m in re.finditer(r'<p class="fresh-line"[^>]*>(.*?)</p>', html, re.S):
    txt = re.sub(r"<[^>]+>", "", m.group(1))
    print("FRESH:", " ".join(txt.split())[:160])
for m in re.finditer(r'<div id="footCrawl"[^>]*>(.*?)</div>', html, re.S):
    txt = re.sub(r"<[^>]+>", "", m.group(1))
    print("CRAWL:", " ".join(txt.split())[:160])
print("cards:", html.count('class="card"'), "| data-id:", len(re.findall(r'data-id="', html)))
