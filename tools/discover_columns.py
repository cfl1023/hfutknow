# -*- coding: utf-8 -*-
"""为每个已启用官网发现新闻/通知类栏目页，输出可直接粘贴进 build_config 的 COLUMN_URLS。"""
from __future__ import annotations

import re
import ssl
import urllib.request
from urllib.parse import urljoin

from lxml import html as lh

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

KEYS = ("通知", "公告", "新闻", "动态", "学术", "活动", "党建", "招生", "就业", "讲座", "比赛", "竞赛", "公示")

HOSTS = ["www", "news", "jwc", "kyy", "lib", "xgb", "xcb", "cwc", "rsc", "yjsy", "ic", "ci", "civil",
         "jxjy", "jjc", "tzb", "jjh", "me", "tiyu", "mks", "xyy", "dektjy", "wdzxy", "hgxy", "wlxy",
         "jjxy", "wfxy", "rjxy", "jxxy", "tuanwei", "wgyxy", "mse", "sjc", "bkzs", "zhaosheng"]


def get(u: str) -> str:
    req = urllib.request.Request(u, headers=UA)
    with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
        raw = r.read(500000)
    for enc in ("utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore")


for h in HOSTS:
    base = f"https://{h}.hfut.edu.cn/"
    try:
        doc = lh.fromstring(get(base))
    except Exception:
        continue
    found = []
    for a in doc.xpath("//a[@href]"):
        href = a.get("href") or ""
        if "list.htm" not in href:
            continue
        text = " ".join(a.text_content().split())
        if not text or not any(k in text for k in KEYS):
            continue
        if len(text) > 16:
            continue
        u = urljoin(base, href)
        if u not in found:
            found.append(u)
    if found:
        print(f'    "{h}": {found!r},'.replace("'", '"'))
