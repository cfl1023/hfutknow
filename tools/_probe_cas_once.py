# -*- coding: utf-8 -*-
"""一次性探测：CAS 登录能否自动化（只试一次，失败即止）。
凭据从本地文件读取，绝不写进仓库。"""
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request
from pathlib import Path

CRED = Path.home() / ".hfutknow_creds.json"
if not CRED.exists():
    print("NO_CREDS_FILE")
    sys.exit(0)

user, pwd = (lambda d: (d["user"], d["pwd"]))(json.loads(CRED.read_text(encoding="utf-8")))

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
cj = __import__("http.cookiejar", fromlist=["CookieJar"]).CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                 urllib.request.HTTPSHandler(context=ctx))
op.addheaders = list(UA.items())

SERVICE = "https://stu.hfut.edu.cn/"
login_url = "https://cas.hfut.edu.cn/cas/login?service=" + urllib.parse.quote(SERVICE)
html = op.open(login_url, timeout=20).read().decode("utf-8", "ignore")

execution = (re.search(r'name="execution" value="([^"]+)"', html) or [None, ""])[1]
captcha = bool(re.search(r"captcha|验证码|滑块", html, re.I))
print("page ok, execution:", bool(execution), "captcha_present:", captcha, "len:", len(html))

if not execution:
    print("NO_EXECUTION_TOKEN — CAS 流程与预期不符，停止")
    sys.exit(0)

form = urllib.parse.urlencode({
    "username": user, "password": pwd, "execution": execution,
    "_eventId": "submit", "submit": "登录",
}).encode()
req = urllib.request.Request(login_url, data=form, method="POST",
                             headers={**UA, "Content-Type": "application/x-www-form-urlencoded",
                                      "Referer": login_url})
try:
    r = op.open(req, timeout=20)
    body = r.read().decode("utf-8", "ignore")
    final = r.geturl()
    print("after login url:", final[:90])
    print("success:", "stu.hfut.edu.cn" in final and "login" not in final.lower())
    print("error hints:", re.findall(r"(密码[^<\n]{0,20}|账号[^<\n]{0,20}|锁定[^<\n]{0,10})", body)[:4])
except urllib.error.HTTPError as e:
    print("HTTP", e.code, str(e.read(200), "utf-8", "ignore")[:120])
