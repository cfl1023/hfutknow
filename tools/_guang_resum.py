# -*- coding: utf-8 -*-
"""用缓存重新给逛逛帖子写摘要（不联网）。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline import guang  # noqa: E402

items_p = ROOT / "site" / "data" / "items.json"
doc = json.loads(items_p.read_text(encoding="utf-8"))
posts = [i for i in doc["items"] if i.get("sourceId") == "gg-forum"]
cache = guang._load_cache()
n = 0
for it in posts:
    d = cache.get(str(it.get("id", ""))[3:])
    if not d or not d.get("c"):
        continue
    paras = [p.strip() for p in __import__("re").split(r"\n+", d["c"]) if p.strip()]
    head = paras[0][:78] if paras else ""
    who = d.get("a") or ""
    if who:
        it["author"] = who
        if d.get("d"):
            it["author"] = who + " · " + d["d"]
    if head:
        it["summary"] = f"{head}｜{it.get('author','')} · 浏览 {it.get('views', 0)} · 评论 {d.get('cm', 0)}"
        n += 1
items_p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
print("updated summaries:", n, "of", len(posts))
print("sample:", posts[0]["summary"][:90])
