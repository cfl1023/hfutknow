# -*- coding: utf-8 -*-
import json
import re
import urllib.request

UA_M = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
UA_PC = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def get(url, ua=UA_PC, referer=None):
    h = {"User-Agent": ua, "Accept-Language": "zh-CN,zh;q=0.9",
         "Accept": "application/json, text/plain, */*"}
    if referer:
        h["Referer"] = referer
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.read()


tests = []

# 1) B站搜索 API
try:
    code, raw = get("https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=%E5%90%88%E8%82%A5%E5%B7%A5%E4%B8%9A%E5%A4%A7%E5%AD%A6&page=1",
                    referer="https://www.bilibili.com")
    d = json.loads(raw.decode("utf-8", "ignore"))
    res = (d.get("data") or {}).get("result") or []
    print("bili", code, "code=", d.get("code"), "n=", len(res))
    for v in res[:4]:
        print("   ", re.sub(r"<[^>]+>", "", v.get("title", ""))[:50])
except Exception as e:
    print("bili ERR", type(e).__name__, e)

# 2) 微博 m 站搜索
try:
    code, raw = get("https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D%E5%90%88%E5%B7%A5%E5%A4%A7&page_type=searchall",
                    ua=UA_M, referer="https://m.weibo.cn")
    d = json.loads(raw.decode("utf-8", "ignore"))
    cards = (d.get("data") or {}).get("cards") or []
    print("weibo", code, "ok=", d.get("ok"), "cards=", len(cards))
    n = 0
    for c in cards:
        for m in (c.get("card_group") or [c]):
            txt = (m.get("mblog") or {}).get("text", "")
            txt = re.sub(r"<[^>]+>", "", txt)
            if txt and n < 4:
                print("   ", txt[:60]); n += 1
except Exception as e:
    print("weibo ERR", type(e).__name__, e)

# 3) 贴吧手机版
try:
    code, raw = get("https://tieba.baidu.com/mo/q/m?kw=%E5%90%88%E8%82%A5%E5%B7%A5%E4%B8%9A%E5%A4%A7%E5%AD%A6", ua=UA_M)
    t = raw.decode("utf-8", "ignore")
    print("tieba-m", code, len(t), "验证" in t)
except Exception as e:
    print("tieba-m ERR", type(e).__name__, e)

# 4) 抖音网页搜索页
try:
    code, raw = get("https://www.douyin.com/search/%E5%90%88%E5%B7%A5%E5%A4%A7", ua=UA_PC)
    print("douyin", code, len(raw))
except Exception as e:
    print("douyin ERR", type(e).__name__, e)

# 5) 小红书搜索页
try:
    code, raw = get("https://www.xiaohongshu.com/search_result?keyword=%E5%90%88%E5%B7%A5%E5%A4%A7", ua=UA_PC)
    print("xhs", code, len(raw))
except Exception as e:
    print("xhs ERR", type(e).__name__, e)
