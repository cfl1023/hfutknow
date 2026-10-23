# -*- coding: utf-8 -*-
"""为一个来源发现可抓取的栏目列表页（同一站点下的 list.htm）。"""
from __future__ import annotations

import re
import ssl
import sys
import urllib.request
from urllib.parse import urljoin

from lxml import html as lh

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

KEYS = ("通知公告", "新闻", "动态", "学术", "活动", "党建", "招生", "就业", "讲座", "比赛", "竞赛")


def get(u: str) -> str:
    req = urllib.request.Request(u, headers=UA)
    with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
        raw = r.read(600000)
    for enc in ("utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore")


def main() -> None:
    for base in sys.argv[1:]:
        try:
            doc = lh.fromstring(get(base))
        except Exception as exc:
            print(f"== {base} ERR {exc}")
            continue
        print(f"== {base}")
        seen = set()
        for a in doc.xpath("//a[@href]"):
            href = a.get("href") or ""
            if "list.htm" not in href:
                continue
            text = " ".join(a.text_content().split())
            if not text or text in seen:
                continue
            if not any(k in text for k in KEYS):
                continue
            seen.add(text)
            print(f"   {text[:16]:18} {urljoin(base, href)}")


if __name__ == "__main__":
    main()
