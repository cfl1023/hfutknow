# -*- coding: utf-8 -*-
"""一次性重建 items.json 里的逛逛条目：带版块分组、feed 标记（兼容新前端）。"""
import sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline import guang, common

ITEMS = common.DATA_DIR / "items.json"
doc = json.loads(ITEMS.read_text(encoding="utf-8"))
before = len(doc["items"])
keep = [i for i in doc["items"] if i.get("sourceId") not in ("gg-forum", "gg-activity")]
removed = before - len(keep)

op = guang._opener()
tk = guang._token(op)
posts = guang._items_from_topics(tk, op)
acts = []
try:
    res = guang._get(op, tk, "/community/ekActivity/list?pageNo=1&pageSize=50").get("result") or {}
    for a in res.get("records") or []:
        item = guang._activity_item(a)
        if item:
            acts.append(item)
except Exception as exc:
    print("acts fail", exc)

import time
t0 = time.time()
guang.enrich(posts, op, tk, max_new=400)
print("enrich took %.1fs" % (time.time() - t0))

doc["items"] = keep + acts + posts
ITEMS.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
from collections import Counter
print("before", before, "removed", removed, "now", len(doc["items"]))
print("feed on:", Counter(i.get("feed") for i in posts))
print("groups:", Counter((i.get("community") or {}).get("group") for i in posts))
print("with body:", sum(1 for i in posts if len(i.get("content") or []) > 1))
print("with author:", sum(1 for i in posts if i.get("author")))
