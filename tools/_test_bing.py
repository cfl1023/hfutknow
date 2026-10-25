# -*- coding: utf-8 -*-
"""测 Bing 能不能当互联网搜索源（本机网络）。"""
import re
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

for host, q in [
    ("www.bing.com", "合肥工业大学 讲座"),
    ("cn.bing.com", "合工大 竞赛 报名"),
    ("www.baidu.com", "site:tieba.baidu.com 合肥工业大学 讲座"),
]:
    url = f"https://{host}/search?q=" + urllib.parse.quote(q) + "&rtl=0"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})
    try:
        raw = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "ignore")
        # bing: <h2><a href=..>title</a></h2>
        links = re.findall(r'<h2[^>]*><a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', raw)
        clean = [(u, re.sub(r"<[^>]+>", "", t)) for u, t in links if "bing.com" not in u][:5]
        print("==", host, q, "->", len(links), "results")
        for u, t in clean[:4]:
            print("   ", t[:40], "|", u[:70])
    except Exception as e:
        print("==", host, q, "ERR", str(e)[:90])
