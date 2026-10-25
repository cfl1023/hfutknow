# -*- coding: utf-8 -*-
"""试 uniHomeLand 帖子流接口。"""
import json
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, ".")
from pipeline import guang

op = guang._opener()
tk = guang._token(op)
print("token ok")

cands = [
    "/uniHomeLand/uniHomeLandPage/uniPagesPostList?pageNo=1&pageSize=5",
    "/uniHomeLand/uniHomeLandPage/uniPagesPostList?pageNo=1&pageSize=5&type=1",
    "/uniHomeLand/homeLandManage/homeLandContManage/homeLandContPost?pageNo=1&pageSize=5",
]
for path in cands:
    url = guang.API + path
    req = urllib.request.Request(url, headers={"X-Access-Token": tk, "X-Requested-With": "XMLHttpRequest"})
    try:
        with op.open(req, timeout=20) as r:
            body = r.read(2000).decode("utf-8", "ignore")
        print("==", path[:70])
        print("  ", body[:600].replace("\n", " "))
    except Exception as e:
        print("==", path[:70], "ERR", str(e)[:80])
