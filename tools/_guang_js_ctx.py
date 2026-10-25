# -*- coding: utf-8 -*-
"""下载逛逛前端 JS 并打印 getPublishDetailsById / pageQueryHome 的调用上下文。"""
import re, ssl, urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent", UA)]
out = Path(__file__).resolve().parent / "_app.js.txt"
if not out.exists():
    body = op.open("https://community.hfut.edu.cn/static/js/app.bd968d6f.js", timeout=60).read()
    out.write_bytes(body)
s = out.read_text(encoding="utf-8", errors="ignore")
for key in ["getPublishDetailsById", "pageQueryHome", "listHomeRecommend", "getDetailsById"]:
    print("=" * 20, key)
    for m in re.finditer(re.escape(key), s):
        a = max(0, m.start() - 260)
        print(repr(s[a:m.end() + 260]))
        print("-" * 8)
