# -*- coding: utf-8 -*-
"""boot 首次加载也拉 crawl_report.json。"""
import pathlib

p = pathlib.Path("site/app.js")
s = p.read_text(encoding="utf-8")

anchor = "      S.generatedAt = payload.generatedAt || '';"
add = anchor + """
      fetch('data/crawl_report.json?t=' + Date.now(), { cache: 'no-store' })
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => { if (d && d.latest) { S.crawl = d.latest; syncCrawlLine(); } })
        .catch(() => {});"""

# 只在 boot 内（route/bind/applyLang 之前）插入一次
if "S.generatedAt = payload.generatedAt || '';\n      fetch('data/crawl_report.json" in s:
    print("boot crawl fetch already present")
else:
    if anchor in s:
        s = s.replace(anchor, add, 1)
        p.write_text(s, encoding="utf-8")
        print("boot crawl fetch added")
    else:
        print("ANCHOR MISS")
