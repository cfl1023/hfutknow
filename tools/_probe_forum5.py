# -*- coding: utf-8 -*-
"""在全部前端 chunk 里搜 forum/post/topic/feed 字符串（接口名可能是拼接的）。"""
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
    except Exception:
        pass
urls = [f"{BASE}/static/js/{c}.{h}.js" for c, h in hashes.items()]

hits = {}
for u in urls:
    try:
        js = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=15).read().decode("utf-8", "ignore")
    except Exception:
        continue
    for m in re.findall(r'["\']([a-zA-Z0-9_/\-]{6,60}(?:forum|Forum|post|Post|topic|Topic|feed|Feed|square|Square)[a-zA-Z0-9_/\-]{0,40})["\']', js):
        hits[m] = u.split("/")[-1][:16]
for k, v in sorted(hits.items()):
    print(f"{k:58} {v}")
