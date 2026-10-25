# -*- coding: utf-8 -*-
"""探查逛逛帖子详情接口字段。"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import guang

items = json.loads((Path(__file__).resolve().parents[1] / "site/data/items.json").read_text(encoding="utf-8"))["items"]
gg = [i for i in items if i.get("sourceId") == "gg-forum"][:3]
op = guang._opener()
tk = guang._token(op)
for i in gg:
    pid = i["id"][3:]
    for path in ["/community/forumTopic/queryById?id=%s" % pid,
                 "/community/forumTopic/detail?id=%s" % pid]:
        try:
            r = guang._get(op, tk, path)
        except Exception as exc:
            print(path, "ERR", exc)
            continue
        res = r.get("result")
        print("==", path, "success=", r.get("success"), type(res).__name__)
        if isinstance(res, dict):
            for k, v in res.items():
                sv = str(v)
                print("   %-14s %s" % (k, sv[:90]))
        break
