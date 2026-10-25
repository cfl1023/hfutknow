# -*- coding: utf-8 -*-
import pathlib
import re

s = pathlib.Path("site/app.js").read_text(encoding="utf-8")
for key in ("freshSync", "freshNew", "crawlLine", "srcCrawl", "srcErr", "freshLineHTML", "syncCrawlLine", "sourceCrawlHTML"):
    print(key, s.count(key))
for n, line in enumerate(s.splitlines(), 1):
    if "freshSync" in line or "crawlLine" in line:
        print(n, line.strip()[:120])
