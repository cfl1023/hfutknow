# -*- coding: utf-8 -*-
"""测扩词效果（绕过节流，直接调内部函数）。"""
import sys
sys.path.insert(0, ".")
from pipeline import bili

cookie, key = bili._prepare()
for kw in ["合工大 讲座", "合肥工业大学 竞赛", "合肥工业大学 社团", "合工大 校园活动", "合肥工业大学 保研"]:
    params = {"search_type": "video", "keyword": kw, "page": 1, "order": "pubdate"}
    url = "https://api.bilibili.com/x/web-interface/wbi/search/type?" + bili._sign(params, key)
    try:
        data = bili._get_json(url, cookie)
        vids = bili._parse(data, kw)
        print(kw, "->", len(vids))
        for v in vids[:3]:
            print("   ", v["title"][:44], v["published"].strftime("%m-%d"))
    except Exception as e:
        print(kw, "ERR", str(e)[:80])
