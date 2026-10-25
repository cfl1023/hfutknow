# -*- coding: utf-8 -*-
"""看原始返回，判断是被风控还是 _parse 过滤掉了。"""
import sys
sys.path.insert(0, ".")
from pipeline import bili

cookie, key = bili._prepare()
params = {"search_type": "video", "keyword": "合肥工业大学", "page": 1, "order": "pubdate"}
url = "https://api.bilibili.com/x/web-interface/wbi/search/type?" + bili._sign(params, key)
data = bili._get_json(url, cookie)
print("code:", data.get("code"), data.get("message"))
res = (data.get("data") or {}).get("result") or []
print("raw results:", len(res))
for v in res[:5]:
    print("   ", bili._clean(v.get("title", ""))[:44], v.get("pubdate"))
