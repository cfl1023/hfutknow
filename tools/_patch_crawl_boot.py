# -*- coding: utf-8 -*-
"""boot 里加载 crawl_report.json → S.crawl，并移除 DBGTRAP。"""
import pathlib

p = pathlib.Path("site/app.js")
s = p.read_text(encoding="utf-8")

# 1) 移除调试陷阱
start = s.find("  // DBGTRAP")
if start >= 0:
    end = s.find("});\n", s.find("document.getElementById('app')", start))
    end = s.find("\n", end) + 1
    s = s[:start] + s[end:]
    print("trap removed")
else:
    print("trap absent")

# 2) 抓取报告
old_list = "['competitions.json', 'competitionsData']"
new_list = "['competitions.json', 'competitionsData'],\n            ['crawl_report.json', 'crawlData']"
if "crawl_report.json" not in s:
    s = s.replace(old_list, new_list, 1)
    print("fetch list patched")
else:
    print("fetch list present")

anchor = "S.competitions = (S.competitionsData && S.competitionsData.items) || [];"
if "S.crawl = " not in s:
    s = s.replace(anchor, anchor + "\n      S.crawl = (S.crawlData && S.crawlData.latest) || null;", 1)
    print("S.crawl assign patched")
else:
    print("S.crawl present")

p.write_text(s, encoding="utf-8")
