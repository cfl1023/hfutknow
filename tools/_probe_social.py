# -*- coding: utf-8 -*-
import re
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.read()

targets = [
    ("tieba", "https://tieba.baidu.com/f?kw=%E5%90%88%E8%82%A5%E5%B7%A5%E4%B8%9A%E5%A4%A7%E5%AD%A6&ie=utf-8"),
    ("zhihu", "https://www.zhihu.com/search?type=content&q=%E5%90%88%E5%B7%A5%E5%A4%A7"),
]
for name, url in targets:
    try:
        code, raw = get(url)
        text = raw.decode("utf-8", "ignore")
        print(f"== {name} {code} {len(text)}B  login={'登录' in text} captcha={'验证' in text or '安全验证' in text}")
        titles = re.findall(r'<a[^>]+title="([^"]{8,60})"', text)[:6]
        print("   titles:", titles)
    except Exception as e:
        print(f"== {name} ERR {type(e).__name__}: {e}")
