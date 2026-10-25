# -*- coding: utf-8 -*-
"""检查 headless dump 的 DOM：关键标记 + 卡片数。"""
import re, sys, os
p = sys.argv[1]
s = open(p, encoding="utf-8", errors="ignore").read()
print("bytes", len(s))
for key in ["数据没能加载", "脚本错误", "Cannot read", "逛逛", "gg-group", "chip-row", "data-id="]:
    print("%-12s %d" % (key, s.count(key)))
m = re.search(r'<title>(.*?)</title>', s, re.S)
print("title:", m.group(1)[:120] if m else None)
i = s.find('id="app"')
print("app snippet:", s[i:i+400].replace("\n", " ")[:400] if i > 0 else "NO APP")
