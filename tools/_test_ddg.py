# -*- coding: utf-8 -*-
"""测 DuckDuckGo html 端点能不能当互联网搜索源。"""
import re
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

for q in ["合肥工业大学 讲座", "合工大 竞赛 报名", "site:tieba.baidu.com 合肥工业大学"]:
    url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(q)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Content-Type": "application/x-www-form-urlencoded"})
    try:
        raw = urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")
        links = re.findall(r'class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>', raw)
        print("==", q, "->", len(links))
        for href, t in links[:4]:
            t = re.sub(r"<[^>]+>", "", t)
            print("   ", t[:44], "|", href[:70])
    except Exception as e:
        print("==", q, "ERR", str(e)[:90])
