# -*- coding: utf-8 -*-
"""列全所有 /community/ 接口，人工挑帖子流。"""
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
hashes = {}
for mp in maps:
    try:
        for k, v in json.loads(mp).items():
            if isinstance(v, str) and re.fullmatch(r"[a-f0-9]{8}", v):
                hashes[k] = v
    except json.JSONDecodeError:
        pass
urls = [f"{BASE}/static/js/{c}.{h}.js" for c, h in hashes.items()]

paths = set()
for u in urls:
    try:
        js = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=15).read().decode("utf-8", "ignore")
    except Exception:
        continue
    paths |= set(re.findall(r'["\'](/community/[A-Za-z]+/[A-Za-z]+)["\']', js))

groups = {}
for p in sorted(paths):
    mod = p.split("/")[2]
    groups.setdefault(mod, []).append(p.split("/")[3])
for mod, eps in sorted(groups.items(), key=lambda kv: -len(kv[1])):
    print(f"{mod:28} x{len(eps):3}  {', '.join(eps[:6])}")
