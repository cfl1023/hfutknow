# -*- coding: utf-8 -*-
"""从所有前端 chunk 里挖论坛/帖子接口，带 token 试。"""
import json
import re
import ssl
import sys
import urllib.request

sys.path.insert(0, ".")
from pipeline import guang

UA = {"User-Agent": guang.UA}
BASE = "https://community.hfut.edu.cn"

runtime = urllib.request.urlopen(urllib.request.Request(BASE + "/static/js/runtime.457e015c.js", headers=UA), timeout=20).read().decode("utf-8", "ignore")
chunks = set(re.findall(r'"(chunk-[a-z0-9]+\.[a-z0-9]+\.js)"', runtime))
print("chunks:", len(chunks))

paths = set()
for name in list(chunks)[:60]:
    try:
        t = urllib.request.urlopen(urllib.request.Request(BASE + "/static/js/" + name, headers=UA), timeout=15).read().decode("utf-8", "ignore")
    except Exception:
        continue
    for m in re.findall(r'["\'](/community/[A-Za-z]+/[A-Za-z]+)["\']', t):
        if any(k in m.lower() for k in ("forum", "post", "feed", "topic", "dynamic", "moment", "comment", "reply")):
            paths.add(m)

print("forum-ish endpoints:")
for p in sorted(paths):
    print("   ", p)
