# -*- coding: utf-8 -*-
"""stu 门户：从页面/JS 里挖真实数据接口。"""
import http.cookiejar
import json
import re
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

CRED = Path.home() / ".hfutknow_creds.json"
user, pwd = (lambda d: (d["user"], d["pwd"]))(json.loads(CRED.read_text(encoding="utf-8")))
ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = list(UA.items())

login_url = "https://cas.hfut.edu.cn/cas/login?service=" + urllib.parse.quote("https://stu.hfut.edu.cn/")
html = op.open(login_url, timeout=20).read().decode("utf-8", "ignore")
execution = (re.search(r'name="execution" value="([^"]+)"', html) or [None, ""])[1]
form = urllib.parse.urlencode({"username": user, "password": pwd, "execution": execution, "_eventId": "submit"}).encode()
r = op.open(urllib.request.Request(login_url, data=form, method="POST",
                                   headers={**UA, "Content-Type": "application/x-www-form-urlencoded", "Referer": login_url}), timeout=25)
base = r.geturl().rsplit("*default", 1)[0]
page = r.read().decode("utf-8", "ignore")

# 页内所有 .do / action / url 线索
urls = set(re.findall(r'["\']([^"\']{4,120}\.do[^"\']*)["\']', page))
urls |= set(re.findall(r'url\s*[:=]\s*["\']([^"\']{4,120})["\']', page))
print("clues in page:")
for u in sorted(urls)[:30]:
    print("   ", u)

# 引用的 js 里继续挖
js_srcs = [u for u in re.findall(r'src="([^"]+\.js[^"]*)"', page) if "appcore" not in u][:6]
for js in js_srcs:
    jsu = urllib.parse.urljoin(r.geturl(), js.replace("../../", "/xsfw/sys/"))
    try:
        t = op.open(jsu, timeout=12).read().decode("utf-8", "ignore")
        hits = set(re.findall(r'["\'](/[a-zA-Z0-9_/.\-*]{4,80}\.do)["\']', t))
        if hits:
            print("in", js[:40], "->")
            for h in sorted(hits)[:15]:
                print("    ", h)
    except Exception as e:
        pass
