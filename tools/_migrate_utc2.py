# -*- coding: utf-8 -*-
"""把先前误加 Z 的本地时间戳（实为 CST）改成真正的 UTC。"""
import json
import pathlib
from datetime import datetime, timedelta

site = pathlib.Path("site") / "data"
CST = timedelta(hours=8)


def to_utc(s: str) -> str:
    if not (isinstance(s, str) and s.endswith("Z")):
        return s
    try:
        naive = datetime.strptime(s[:-1], "%Y-%m-%dT%H:%M")
    except ValueError:
        return s
    return (naive - CST).strftime("%Y-%m-%dT%H:%MZ")


ip = site / "items.json"
data = json.loads(ip.read_text(encoding="utf-8"))
data["generatedAt"] = to_utc(data.get("generatedAt", ""))
ip.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print("items:", data["generatedAt"])

cp = site / "crawl_report.json"
if cp.exists():
    cr = json.loads(cp.read_text(encoding="utf-8"))

    def walk(d):
        if isinstance(d, dict):
            for k, v in d.items():
                if k == "at":
                    d[k] = to_utc(v)
                else:
                    walk(v)
        elif isinstance(d, list):
            for v in d:
                walk(v)

    walk(cr)
    cp.write_text(json.dumps(cr, ensure_ascii=False, indent=1), encoding="utf-8")
    print("crawl:", cr["latest"]["at"])
