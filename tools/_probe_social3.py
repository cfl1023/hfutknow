# -*- coding: utf-8 -*-
import re
import urllib.request

UA_PC = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def get(url, ua=UA_PC, referer=None):
    h = {"User-Agent": ua, "Accept-Language": "zh-CN,zh;q=0.9",
         "Accept": "text/html,application/json;q=0.9,*/*;q=0.8"}
    if referer:
        h["Referer"] = referer
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


for name, url, ref in [
    ("bili", "https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword=%E5%90%88%E5%B7%A5%E5%A4%A7", "https://www.bilibili.com"),
    ("weibo", "https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D%E5%90%88%E5%B7%A5%E5%A4%A7&page_type=searchall", "https://m.weibo.cn"),
]:
    code, raw = get(url, referer=ref)
    print(f"== {name} {code} {len(raw)}B")
    print("   ", raw[:160].decode("utf-8", "ignore").replace("\n", " "))

for name, url in [("douyin", "https://www.douyin.com/search/%E5%90%88%E5%B7%A5%E5%A4%A7"),
                  ("xhs", "https://www.xiaohongshu.com/search_result?keyword=%E5%90%88%E5%B7%A5%E5%A4%A7")]:
    code, raw = get(url)
    t = raw.decode("utf-8", "ignore")
    print(f"== {name} {code} {len(t)}B RENDER_DATA={'RENDER_DATA' in t} _ROUTER_DATA={'_ROUTER_DATA' in t} __INITIAL_STATE__={'__INITIAL_STATE__' in t}")
    # 提取 SSR JSON 是否含帖子
    for marker in ["RENDER_DATA", "_ROUTER_DATA", "__INITIAL_STATE__"]:
        i = t.find(marker)
        if i > 0:
            print("   ", marker, "ctx:", t[i:i+120].replace("\n", " "))
