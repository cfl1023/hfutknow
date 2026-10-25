# -*- coding: utf-8 -*-
"""抓逛逛首页 HTML，找 JS bundle 地址。"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import common  # noqa: E402

text, final = common.http_get("https://community.hfut.edu.cn/", timeout=25, retries=1)
print("bytes", len(text), "final", final)
for m in re.findall(r'<script[^>]+src="([^"]+)"', text):
    print("script:", m)
for m in re.findall(r'href="([^"]+\.(?:js|css))"', text)[:10]:
    print("asset:", m)
