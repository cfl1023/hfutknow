# -*- coding: utf-8 -*-
"""测 Bing News RSS：云端可用、无需 key 的互联网新闻源。"""
import re
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

for q in ["合肥工业大学", "合工大", "合肥工业大学 讲座"]:
    url = "https://www.bing.com/news/search?q=" + urllib.parse.quote(q) + "&format=rss"
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20).read()
        t = raw.decode("utf-8", "ignore")
        items = re.findall(r"<item>(.*?)</item>", t, re.S)
        print("==", q, "->", len(items), "items")
        for it in items[:4]:
            title = re.search(r"<title>(.*?)</title>", it, re.S)
            date = re.search(r"<pubDate>(.*?)</pubDate>", it)
            link = re.search(r"<link>(.*?)</link>", it)
            print("   ", (date.group(1)[:16] if date else "?"), "|", (title.group(1)[:40] if title else "?"))
            print("      ", (link.group(1)[:80] if link else "?"))
    except Exception as e:
        print("==", q, "ERR", str(e)[:90])
