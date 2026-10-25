# -*- coding: utf-8 -*-
"""最后一轮定向探测：POST + 常见公告查询参数。"""
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

# WIS_CONFIG 里有什么
for m in re.findall(r'WIS_CONFIG[^;]{0,200}', page)[:4]:
    print("CFG:", re.sub(r"\s+", " ", m)[:190])
appId = (re.search(r'APPID\s*[:=]\s*["\']([^"\']+)', page) or [None, ""])[1]
print("APPID:", appId)

base = "https://stu.hfut.edu.cn/xsfw"
tries = [
    ("POST", f"{base}/sys/xggzptapp/*default/gglist.do", {"pageNum": 1, "pageSize": 10}),
    ("POST", f"{base}/sys/xggzptapp/*default/index.do", {"pageNum": 1}),
    ("POST", f"{base}/sys/xgutilapp/indexmenu/getAppConfig.do?appId={appId}&appName=xggzptapp", {}),
    ("GET", f"{base}/sys/xggzptapp/*default/index.do?min=1", None),
]
for method, url, data in tries:
    try:
        d = urllib.parse.urlencode(data).encode() if data is not None else None
        req = urllib.request.Request(url, data=d, method=method,
                                     headers={**UA, "Content-Type": "application/x-www-form-urlencoded",
                                              "X-Requested-With": "XMLHttpRequest", "Referer": r.geturl()})
        rr = op.open(req, timeout=15)
        b = rr.read(400).decode("utf-8", "ignore")
        print("[", rr.status, "]", method, url.split("/sys/")[-1][:60], "|", re.sub(r"\s+", " ", b)[:220])
    except Exception as e:
        print("[x]", method, url.split("/sys/")[-1][:60], str(e)[:60])
