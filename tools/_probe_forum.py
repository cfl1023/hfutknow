# -*- coding: utf-8 -*-
"""探测社区帖子流接口：从前端 JS 里挖 forum/post 路径，带 token 逐个试。"""
import json
import ssl
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, ".")
from pipeline import guang

op = guang._opener()
tk = guang._token(op)
print("token ok")

# 1) 从 vendor/app js 里挖 forum/post/feed 相关接口
paths = set()
for js in ["/static/js/app.bd968d6f.js"]:
    req = urllib.request.Request("https://community.hfut.edu.cn" + js,
                                 headers={"User-Agent": guang.UA})
    t = guang.urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
    for m in re.findall(r'["\'](/community/[a-zA-Z]+/[a-zA-Z]+)["\']', t):
        if any(k in m.lower() for k in ("forum", "post", "feed", "topic", "dynamic", "moment")):
            paths.add(m)
print("candidate paths:", sorted(paths)[:20])
