# -*- coding: utf-8 -*-
"""统一时间戳为 UTC + Z：改 sync.py 写入方式，并迁移现有 json。"""
import json
import pathlib
import re

root = pathlib.Path(".")
site = root / "site" / "data"

# 1) sync.py：generatedAt / crawl at 用 UTC Z
p = root / "pipeline" / "sync.py"
s = p.read_text(encoding="utf-8")
if "import time" in s and "timezone" not in s.split("import json")[0]:
    s = s.replace("import json", "import json\nfrom datetime import datetime, timezone", 1)
s = re.sub(r"datetime\.now\(\)\.isoformat\(timespec=\"minutes\"\)", 'datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")', s)
s = re.sub(r"datetime\.now\(\)\.strftime\(\"%Y-%m-%dT%H:%M\"\)", 'datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")', s)
p.write_text(s, encoding="utf-8")
print("sync.py utc:", s.count('%Y-%m-%dT%H:%MZ'))

# 2) 迁移 items.json generatedAt
items_p = site / "items.json"
data = json.loads(items_p.read_text(encoding="utf-8"))
g = data.get("generatedAt", "")
if g and not re.search(r"[zZ]$", g):
    data["generatedAt"] = g + "Z"
    items_p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("items.generatedAt ->", data["generatedAt"])

# 3) 迁移 crawl_report.json 的 at 字段
cp = site / "crawl_report.json"
if cp.exists():
    cr = json.loads(cp.read_text(encoding="utf-8"))

    def fix(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k == "at" and isinstance(v, str) and not re.search(r"[zZ]$", v):
                    d[k] = v + "Z"
                else:
                    fix(v)
        elif isinstance(d, list):
            for v in d:
                fix(v)

    fix(cr)
    cp.write_text(json.dumps(cr, ensure_ascii=False, indent=1), encoding="utf-8")
    print("crawl at ->", cr.get("latest", {}).get("at"))
