# -*- coding: utf-8 -*-
"""看活动的报名人数相关字段。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import guang  # noqa: E402

op = guang._opener()
tk = guang._token(op)
res = guang._get(op, tk, "/community/ekActivity/list?pageNo=1&pageSize=50").get("result") or {}
for a in (res.get("records") or [])[:6]:
    print(a.get("name")[:22], "| applyNum", a.get("applyNum"), "personApply", a.get("personApplyNum"),
          "teamApply", a.get("teamApplyNum"), "people", a.get("peopleNum"), "status", a.get("applyStatus"))
