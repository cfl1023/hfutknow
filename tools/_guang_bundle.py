# -*- coding: utf-8 -*-
"""下载逛逛前端 bundle，找帖子详情路由。"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import common  # noqa: E402

url = "https://community.hfut.edu.cn/js/app.bd968d6f.js"
try:
    text, final = common.http_get(url, timeout=25, retries=1)
except Exception as exc:
    print("fail", exc)
    raise SystemExit(0)

print("bytes", len(text))
paths = sorted(set(re.findall(r'path\s*:\s*"([^"]{2,80})"', text)))
print("paths:", paths[:30])
m = re.findall(r'topicDetail[^,;]{0,60}', text)[:5]
print("topicDetail:", m)
m2 = re.findall(r'forumTopic/detail[^,;]{0,60}', text)[:5]
print("detail:", m2)
Path("site/data/_community_app.js").write_text(text, encoding="utf-8")
