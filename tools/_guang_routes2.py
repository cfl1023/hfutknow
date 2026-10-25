# -*- coding: utf-8 -*-
"""下载逛逛 bundle 并列路由。"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from pipeline import common  # noqa: E402

t, f = common.http_get("https://community.hfut.edu.cn/static/js/app.bd968d6f.js", timeout=30, retries=1)
print("bytes", len(t))
(ROOT / "site" / "data" / "_community_app.js").write_text(t, encoding="utf-8")
paths = sorted(set(re.findall(r'path\s*:\s*"([^"]{2,40})"', t)))
print("paths:", paths[:30])
for kw in ("topicDetail", "detail", "topic/"):
    hits = re.findall(kw + r'[^,;\n]{0,70}', t)[:3]
    print(kw, "→", hits)
