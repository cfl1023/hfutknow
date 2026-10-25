# -*- coding: utf-8 -*-
"""核对逛逛帖子：标题 vs 正文 vs 版块 是否一致。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = json.loads((ROOT / "site" / "data" / "items.json").read_text(encoding="utf-8"))
posts = [i for i in doc["items"] if i.get("sourceId") == "gg-forum"]
cache = json.loads((ROOT / "site" / "data" / "_guang_detail_cache.json").read_text(encoding="utf-8"))

bad = []
for p in posts:
    pid = str(p["id"])[3:]
    d = cache.get(pid)
    if not d:
        bad.append((p["id"], "no-cache", p["title"]))
        continue
    body = (d.get("c") or "").replace(" ", "")
    title = p["title"].replace(" ", "")
    if not body:
        continue
    # 标题里的实词是否出现在正文
    chars = set(re.findall(r"[\u4e00-\u9fa5]{2,}", title))
    hit = any(c in body for c in chars)
    if not hit:
        bad.append((p["id"], p["title"][:24], body[:40]))
print("posts", len(posts), "cache", len(cache), "suspect", len(bad))
for b in bad[:10]:
    print(" ", b)
