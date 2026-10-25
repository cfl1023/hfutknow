# -*- coding: utf-8 -*-
"""补齐 I18N 的 freshSync/freshNew/crawlLine/srcCrawl/srcErr（中英各一份）。"""
import pathlib
import re

p = pathlib.Path("site/app.js")
s = p.read_text(encoding="utf-8")

ZH = {
    "freshSync": "数据 {age}同步",
    "freshNew": "24 小时内新增 {n} 条",
    "crawlLine": "上次抓取 {age} · {ok}/{all} 源成功 · 本轮新增 {n} 条",
    "srcCrawl": "最近抓取 {age}：列表 {got} 条，新增 {n}",
    "srcErr": "最近抓取失败：{err}",
}
EN = {
    "freshSync": "Synced {age} ago",
    "freshNew": "{n} new in 24h",
    "crawlLine": "Last crawl {age} · {ok}/{all} sources ok · {n} new",
    "srcCrawl": "Crawled {age}: {got} listed, {n} new",
    "srcErr": "Last crawl failed: {err}",
}

# 已有则跳过
if "freshSync:" in s:
    print("keys already present")
else:
    lines = s.splitlines()
    out = []
    en_start = None
    for i, line in enumerate(lines):
        if re.match(r"\s*en:\s*\{", line):
            en_start = i
            break
    for i, line in enumerate(lines):
        out.append(line)
        if re.search(r"\bupdated:\s*['\"]", line):
            table = EN if (en_start is not None and i > en_start) else ZH
            for k, v in table.items():
                out.append(f"      {k}: '{v}',")
    s2 = "\n".join(out)
    p.write_text(s2, encoding="utf-8")
    print("inserted", s2.count("freshSync:"), "dicts; en_start", en_start)
