# -*- coding: utf-8 -*-
"""解析 runtime 的 chunk 名→hash 两张表，拼出真实 chunk URL，挖论坛接口。"""
import json
import re
import sys
import urllib.request

sys.path.insert(0, ".")
from pipeline import guang

UA = {"User-Agent": guang.UA}
BASE = "https://community.hfut.edu.cn"
t = urllib.request.urlopen(urllib.request.Request(BASE + "/static/js/runtime.457e015c.js", headers=UA), timeout=20).read().decode("utf-8", "ignore")

maps = re.findall(r'\{"chunk[^{}]+\}', t)
names = {}
hashes = {}
for mp in maps:
    try:
        d = json.loads(mp)
    except json.JSONDecodeError:
        continue
    for k, v in d.items():
        if re.fullmatch(r"chunk-[a-z0-9]+", k):
            if isinstance(v, str) and re.fullmatch(r"[a-f0-9]{8}", v):
                hashes[k] = v
            else:
                names[k] = v

urls = [f"{BASE}/static/js/{c}.{h}.js" for c, h in hashes.items()]
print("chunk urls:", len(urls))

paths = set()
for u in urls:
    try:
        js = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=15).read().decode("utf-8", "ignore")
    except Exception:
        continue
    for m in re.findall(r'["\'](/community/[A-Za-z]+/[A-Za-z]+)["\']', js):
        low = m.lower()
        if any(k in low for k in ("forum", "post", "feed", "topic", "dynamic", "moment", "comment", "rely", "square", "discuss")):
            paths.add(m)

for p in sorted(paths):
    print("   ", p)
