# -*- coding: utf-8 -*-
"""在 chunk 里找 uniPagesPostList 的调用上下文，拿到真实 URL。"""
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

for u in urls:
    try:
        js = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=15).read().decode("utf-8", "ignore")
    except Exception:
        continue
    for m in re.finditer(r'uniPagesPostList', js):
        i = m.start()
        seg = js[max(0, i - 260):i + 120]
        if "url" in seg or "getAction" in seg or "postAction" in seg:
            print("###", u.split("/")[-1][:20])
            print(re.sub(r"\s+", " ", seg))
            print()
            break
