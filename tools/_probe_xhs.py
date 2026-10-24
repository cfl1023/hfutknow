# -*- coding: utf-8 -*-
import json
import re
import urllib.request

UA_PC = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

url = "https://www.xiaohongshu.com/search_result?keyword=%E5%90%88%E5%B7%A5%E5%A4%A7"
req = urllib.request.Request(url, headers={"User-Agent": UA_PC, "Accept-Language": "zh-CN,zh;q=0.9"})
with urllib.request.urlopen(req, timeout=20) as r:
    t = r.read().decode("utf-8", "ignore")

i = t.find("__INITIAL_STATE__=")
j = t.find("</script>", i)
raw = t[i + len("__INITIAL_STATE__="):j].strip()
# xhs 用 undefined 占位
raw = raw.replace("undefined", "null")
try:
    d = json.loads(raw)
    print("parsed ok, top keys:", list(d.keys())[:12])
    search = d.get("search") or {}
    print("search keys:", list(search.keys())[:12])
    feeds = (search.get("feeds") or search.get("items") or [])
    print("feeds n=", len(feeds))
    for f in feeds[:5]:
        nc = f.get("noteCard") or f
        print("  -", (nc.get("displayTitle") or "")[:40], "|", (nc.get("user") or {}).get("nickname"))
except Exception as e:
    print("parse fail:", type(e).__name__, e)
    print("head:", raw[:200])
