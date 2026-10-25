# -*- coding: utf-8 -*-
"""探测 stu.hfut.edu.cn 学生服务平台：找公告/消息接口。"""
import http.cookiejar
import json
import re
import ssl
import urllib.parse
import urllib.request
from pathlib import Path

CRED = Path.home() / ".hfutknow_creds.json"
user, pwd = (lambda d: (d["user"], d["pwd"]))(json.loads(CRED.read_text(encoding="utf-8")))

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), urllib.request.HTTPSHandler(context=ctx))
op.addheaders = list(UA.items())

SERVICE = "https://stu.hfut.edu.cn/"
login_url = "https://cas.hfut.edu.cn/cas/login?service=" + urllib.parse.quote(SERVICE)
html = op.open(login_url, timeout=20).read().decode("utf-8", "ignore")
execution = (re.search(r'name="execution" value="([^"]+)"', html) or [None, ""])[1]
form = urllib.parse.urlencode({"username": user, "password": pwd, "execution": execution,
                               "_eventId": "submit", "submit": "登录"}).encode()
req = urllib.request.Request(login_url, data=form, method="POST",
                             headers={**UA, "Content-Type": "application/x-www-form-urlencoded",
                                      "Referer": login_url})
r = op.open(req, timeout=25)
print("landed:", r.geturl()[:100])
body = r.read().decode("utf-8", "ignore")
print("portal len:", len(body))

# 找 iframe / 应用入口 / 接口线索
for m in re.findall(r'(?:src|href)="([^"]{5,120})"', body):
    if any(k in m for k in ("gz", "gg", "notice", "message", "xx", "app", "sys")):
        print("  link:", m[:110])

# 常见低代码平台公告端点试一圈
cands = [
    "https://stu.hfut.edu.cn/xsfw/sys/ek_notify/publist.do",
    "https://stu.hfut.edu.cn/xsfw/sys/ek_notify/list.do",
    "https://stu.hfut.edu.cn/xsfw/sys/xggzptapp/*default/index.do",
    "https://stu.hfut.edu.cn/xsfw/sys/emessage/pub/list.do",
]
for u in cands:
    try:
        rr = op.open(u, timeout=15)
        b2 = rr.read(500).decode("utf-8", "ignore")
        print("[", rr.status, "]", u[:80], "|", re.sub(r"\s+", " ", b2[:160]))
    except Exception as e:
        print("[ERR]", u[:80], str(e)[:60])
