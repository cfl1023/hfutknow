# -*- coding: utf-8 -*-
"""校验：主页不出现 feed=false 的逛逛旧帖；逛逛页出现。"""
import json, sys, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
items = json.loads((ROOT / "site" / "data" / "items.json").read_text(encoding="utf-8"))["items"]
hidden = [i for i in items if i.get("feed") is False]
print("feed=false:", len(hidden))
samples = [i["title"][:10] for i in hidden[:6]]
print("samples:", samples)
home = open(sys.argv[1], encoding="utf-8", errors="ignore").read()
guang = open(sys.argv[2], encoding="utf-8", errors="ignore").read()
print("home hits:", [t for t in samples if t in home])
print("guang hits:", [t for t in samples if t in guang])
print("home cards:", home.count('class="card'))
print("guang cards:", guang.count('class="card'))
