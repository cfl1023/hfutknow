# -*- coding: utf-8 -*-
"""试探 pageQuery 的排序参数，看能否拿到最新帖子。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import guang  # noqa: E402

op = guang._opener()
tk = guang._token(op)
paths = [
    "/community/forumTopic/pageQuery?pageNo=1&pageSize=10",
    "/community/forumTopic/pageQuery?pageNo=1&pageSize=10&orderBy=createTime&sort=desc",
    "/community/forumTopic/pageQuery?pageNo=1&pageSize=10&column=createTime&order=desc",
    "/community/forumTopic/pageQuery?pageNo=1&pageSize=10&sort=createTime&order=desc",
    "/community/forumTopic/pageQueryHome?pageNo=1&pageSize=10",
]
for p in paths:
    try:
        r = guang._get(op, tk, p)
        res = r.get("result") or {}
        recs = res.get("records") or []
        print("==", p[-58:], "total", res.get("total"), "n", len(recs))
        for x in recs[:3]:
            print("    ", (x.get("createTime") or "")[:10], (x.get("title") or "")[:22])
    except Exception as exc:
        print("×", p[-40:], exc)
