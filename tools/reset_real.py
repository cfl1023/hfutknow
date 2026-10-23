# -*- coding: utf-8 -*-
"""清掉已抓取的真实条目（保留演示数据），方便重抓。"""
import json
from pathlib import Path

p = Path("site/data/items.json")
d = json.loads(p.read_text(encoding="utf-8"))
before = len(d["items"])
d["items"] = [i for i in d["items"] if i.get("demo")]
p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"removed {before - len(d['items'])}, left {len(d['items'])}")
