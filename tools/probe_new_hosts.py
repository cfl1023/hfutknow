# -*- coding: utf-8 -*-
"""批量确认新发现的子域名身份 + 列表页可用性。"""
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

HOSTS = ["wgyxy", "mse", "zzb", "sjc", "xxh", "dzb"]


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
        title = doc.xpath("//title")[0].text_content().strip() if doc.xpath("//title") else "?"
        lists = sorted({urljoin(base, a.get("href")) for a in doc.xpath("//a[@href]")
                        if "list.htm" in (a.get("href") or "")})
        print(f"{h:8} {title[:30]:32} lists={len(lists)}")
        for u in lists[:6]:
            print(f"        {u}")
    except Exception as e:
        print(f"{h:8} ERR {str(e)[:60]}")
