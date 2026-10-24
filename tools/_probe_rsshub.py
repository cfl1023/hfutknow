# -*- coding: utf-8 -*-
import urllib.request

UA_PC = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
         "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

urls = [
    ("rsshub-tieba", "https://rsshub.app/tieba/forum/%E5%90%88%E8%82%A5%E5%B7%A5%E4%B8%9A%E5%A4%A7%E5%AD%A6"),
    ("rsshub-tieba2", "https://rsshub.rssforever.com/tieba/forum/%E5%90%88%E8%82%A5%E5%B7%A5%E4%B8%9A%E5%A4%A7%E5%AD%A6"),
]
for name, url in urls:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA_PC})
        with urllib.request.urlopen(req, timeout=25) as r:
            body = r.read().decode("utf-8", "ignore")
            print(f"== {name} {r.status} {len(body)}B items={body.count('<item>')}")
            import re
            for m in re.findall(r"<title><!\[CDATA\[(.*?)\]\]></title>", body)[:5]:
                print("   ", m[:60])
    except Exception as e:
        print(f"== {name} ERR {type(e).__name__}: {e}")
