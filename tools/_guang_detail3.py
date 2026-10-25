# -*- coding: utf-8 -*-
"""试 getDetailsById 拿帖子正文。"""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import guang

items = json.loads((Path(__file__).resolve().parents[1] / "site/data/items.json").read_text(encoding="utf-8"))["items"]
gg = [i for i in items if i.get("sourceId") == "gg-forum"][:2]
op = guang._opener()
tk = guang._token(op)
for i in gg:
    pid = i["id"][3:]
    for q in ["/community/forumTopic/getDetailsById?id=" + pid,
              "/community/forumTopic/getDetailsById?topicId=" + pid]:
        r = guang._get(op, tk, q)
        res = r.get("result")
        print("==", q[-40:], "success", r.get("success"), type(res).__name__, str(r.get("message"))[:40])
        if isinstance(res, dict):
            for k, v in res.items():
                sv = str(v).replace("\n", "\\n")
                print("   %-16s %s" % (k, sv[:160]))
            break
