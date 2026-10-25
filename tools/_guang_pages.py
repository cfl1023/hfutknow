# -*- coding: utf-8 -*-
"""看 pageQuery 各页的时间分布与 total 变化。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import guang  # noqa: E402

op = guang._opener()
tk = guang._token(op)
for page in (1, 2, 3, 4):
    r = guang._get(op, tk, f"/community/forumTopic/pageQuery?pageNo={page}&pageSize=100")
    res = r.get("result") or {}
    recs = res.get("records") or []
    times = sorted((x.get("createTime") or "")[:10] for x in recs)
    print(f"page {page}: total {res.get('total')} n {len(recs)} oldest {times[0] if times else '-'} newest {times[-1] if times else '-'}")
