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
        name = (a.get("name") or "").strip()
        if not name:
            continue
        cat = guang.MODULE_CAT.get(a.get("moduleName") or "", "campus")
        begin = (a.get("beginTime") or "").replace(" ", "T")[:16]
        from datetime import datetime
        summary = f"{a.get('moduleName') or ''}｜主办 {a.get('sponsor') or '?'}"
        if a.get("peopleNum"):
            summary += f"｜限 {a['peopleNum']} 人"
        if a.get("applyNum"):
            summary += f"｜已报 {a['applyNum']}"
        acts.append({
            "id": "gg-" + str(a.get("id")), "title": name[:100], "sourceId": "gg-activity",
            "sourceName": "逛逛 · 校园活动", "sourceType": "gg",
            "url": "https://community.hfut.edu.cn/",
            "publishedAt": begin or datetime.now().isoformat(timespec="minutes"),
            "dateEstimated": not bool(begin), "intent": "activity", "category": cat,
            "summary": summary,
            "event": {"start": begin, "location": (a.get("theVenue") or "").strip() or None} if begin else None,
            "requiresSignup": True,
            "tags": [t for t in [a.get("moduleName"), a.get("campus_dictText")] if t],
            "competition": None, "feed": True,
            "content": [f"<p>{summary}</p>"], "demo": False,
        })
except Exception as exc:
    print("acts fail", exc)

doc["items"] = keep + acts + posts
ITEMS.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
from collections import Counter
print("before", before, "removed", removed, "now", len(doc["items"]))
print("feed on:", Counter(i.get("feed") for i in posts))
print("groups:", Counter((i.get("community") or {}).get("group") for i in posts))
