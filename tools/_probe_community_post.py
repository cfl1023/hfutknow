# -*- coding: utf-8 -*-
"""探测 community.hfut.edu.cn 的接口能不能匿名 POST（逛逛数据源）。"""
import json
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36",
      "Content-Type": "application/json",
      "Referer": "https://community.hfut.edu.cn/"}

paths = [
    "/community/community/communityList",
    "/community/community/list",
    "/community/ekActivity/list",
    "/community/community/queryCommunitySiteList",
    "/community/forumAccount/queryTreeList",
]
for p in paths:
    url = "https://community.hfut.edu.cn/api" + p
    for method, data in (("POST", json.dumps({"pageNum": 1, "pageSize": 5}).encode()), ("GET", None)):
        try:
            req = urllib.request.Request(url, headers=UA, data=data, method=method)
            with urllib.request.urlopen(req, timeout=12) as r:
                body = r.read(400).decode("utf-8", "ignore")
            print(method, p, r.status, body[:150].replace("\n", " "))
            break
        except Exception as e:
            print(method, p, "ERR", str(e)[:70])
