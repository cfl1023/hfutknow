# -*- coding: utf-8 -*-
"""xggzptapp 公告平台：找列表接口或直接抽页面数据。"""
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
page = r.read().decode("utf-8", "ignore")
print("page len", len(page))

# 1) 页面里直接有公告标题？
titles = re.findall(r'title[=:]\s*["\u201c]([^"\u201d]{8,60})["\u201d]', page)
print("titles found:", len(titles))
for t in titles[:8]:
    print("   ", t)

# 2) 所有 ajax 目标
for m in re.findall(r'\$\.(?:post|get|ajax)[^;]{0,200}', page)[:6]:
    print("AJAX:", re.sub(r"\s+", " ", m)[:180])

# 3) iframe
print("iframes:", re.findall(r'<iframe[^>]+src="([^"]+)"', page)[:6])

# 4) 常见公告接口名
base = "https://stu.hfut.edu.cn/xsfw/sys/xggzptapp/"
for ep in ["*default/gglist.do", "*default/list.do", "gg/index.do", "*default/getGg.do",
           "*default/gglb.do", "*default/index.do"]:
    try:
        rr = op.open(base + ep, timeout=12)
        b = rr.read(220).decode("utf-8", "ignore")
        print("[", rr.status, "]", ep, "|", re.sub(r"\s+", " ", b)[:150])
    except Exception as e:
        print("[x]", ep, str(e)[:50])
