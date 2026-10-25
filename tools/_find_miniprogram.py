# -*- coding: utf-8 -*-
"""在 B站/贴吧语料里找「聚在工大 / 逛逛」小程序线索。"""
import json
from pathlib import Path

corpus = Path(r"C:\Users\lenovo\Documents\deepseek-harness\default-workspace\corpus")
hits = []
for f in ("tieba_threads.jsonl", "bili_videos.jsonl"):
    p = corpus / f
    if not p.exists():
        continue
    for line in p.open(encoding="utf-8", errors="ignore"):
        try:
            o = json.loads(line)
        except Exception:
            continue
        text = " ".join(str(o.get(k, "")) for k in ("title", "desc", "body", "content"))
        if "聚在工大" in text or ("逛逛" in text and "小程序" in text):
            hits.append((f, text[:130].replace("\n", " ")))
print("hits", len(hits))
for h in hits[:12]:
    print("-", h[0], h[1])
