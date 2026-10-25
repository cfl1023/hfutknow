# -*- coding: utf-8 -*-
"""打印提到「聚在工大」的贴吧帖全文。"""
import json
from pathlib import Path

p = Path(r"C:\Users\lenovo\Documents\deepseek-harness\default-workspace\corpus\tieba_threads.jsonl")
for line in p.open(encoding="utf-8", errors="ignore"):
    try:
        o = json.loads(line)
    except Exception:
        continue
    if "聚在工大" in json.dumps(o, ensure_ascii=False):
        print("===", o.get("title"))
        print("tid", o.get("tid"), "| url", o.get("url"))
        for fl in (o.get("floors") or [])[:12]:
            text = (fl.get("text") or "").replace("\n", " ")[:120]
            print("-", fl.get("author"), ":", text)
