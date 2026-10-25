# -*- coding: utf-8 -*-
"""从逛逛前端 JS 里找帖子详情接口。"""
import re, sys, ssl, urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
op = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
op.addheaders = [("User-Agent", UA)]

html = op.open("https://community.hfut.edu.cn/", timeout=20).read().decode("utf-8", "ignore")
js = re.findall(r'src="([^"]+\.js)"', html)
print("js:", js)
for u in js:
    if u.startswith("/"):
        u = "https://community.hfut.edu.cn" + u
    try:
        body = op.open(u, timeout=40).read().decode("utf-8", "ignore")
    except Exception as exc:
        print(u, "ERR", exc); continue
    hits = sorted(set(re.findall(r'/community/[a-zA-Z]+/[a-zA-Z]+\??[a-zA-Z0-9_=&{}].{0,20}', body)))
    print("==", u, len(body), "hits", len(hits))
    for h in hits:
        if "forum" in h.lower() or "topic" in h.lower() or "detail" in h.lower():
            print("   ", h[:120])
