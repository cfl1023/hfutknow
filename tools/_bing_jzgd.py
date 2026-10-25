# -*- coding: utf-8 -*-
"""Bing 搜「聚在工大」，找小程序/网页入口。"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import common  # noqa: E402

for q in ("聚在工大 合肥工业大学", "聚在工大 小程序 逛逛"):
    url = "https://www.bing.com/search?q=" + common.quote_plus(q) if hasattr(common, "quote_plus") else None
    if not url:
        from urllib.parse import quote_plus

        url = "https://www.bing.com/search?q=" + quote_plus(q)
    try:
        html, final = common.http_get(url, timeout=25, retries=1)
    except Exception as exc:
        print("fail", q, exc)
        continue
    items = re.findall(r'<h2><a href="([^"]+)"[^>]*>(.*?)</a></h2>', html)
    print("==", q, "hits", len(items))
    for href, title in items[:6]:
        t = re.sub(r"<[^>]+>", "", title)
        print("  -", t[:60], "|", href[:90])
