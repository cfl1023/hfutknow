# -*- coding: utf-8 -*-
"""扩词为什么 0：看原始返回和过滤前后数量。"""
import sys
sys.path.insert(0, ".")
from pipeline import bili

cookie, key = bili._prepare()
for kw in ["合工大 讲座", "合肥工业大学 竞赛"]:
    params = {"search_type": "video", "keyword": kw, "page": 1, "order": "pubdate"}
    url = "https://api.bilibili.com/x/web-interface/wbi/search/type?" + bili._sign(params, key)
    data = bili._get_json(url, cookie)
    res = (data.get("data") or {}).get("result") or []
    print(kw, "code:", data.get("code"), "raw:", len(res))
    for v in res[:4]:
        t = bili._clean(v.get("title", ""))
        import datetime
        pd = datetime.datetime.fromtimestamp(v.get("pubdate") or 0)
        print("   ", t[:40], pd.strftime("%m-%d"), "| 含校名:", any(w in t for w in bili.CAMPUS_WORDS))
