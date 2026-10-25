# -*- coding: utf-8 -*-
"""把 config.json 里 site.profile 与顶层 profile 对齐为微电子学院，并同步 items.json。"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
cfg_p = ROOT / "config.json"
cfg = json.loads(cfg_p.read_text(encoding="utf-8"))
prof = cfg.setdefault("site", {}).setdefault("profile", {})
prof["college"] = "微电子学院"
cfg.setdefault("profile", {})["college"] = "微电子学院"
cfg_p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("config site.profile:", prof["college"])

items_p = ROOT / "site" / "data" / "items.json"
if items_p.exists():
    doc = json.loads(items_p.read_text(encoding="utf-8"))
    (doc.get("site") or {}).setdefault("profile", {})["college"] = "微电子学院"
    items_p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print("items.json profile:", doc["site"]["profile"]["college"])
