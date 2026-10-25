# -*- coding: utf-8 -*-
"""用 CAS 会话探测：第二课堂活动列表 / 教务 / 逛逛社区 三个后端。"""
import http.cookiejar
import json
import re
import ssl
import urllib.error
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


def cas_login(service: str) -> str:
    login_url = "https://cas.hfut.edu.cn/cas/login?service=" + urllib.parse.quote(service)
    html = op.open(login_url, timeout=20).read().decode("utf-8", "ignore")
    execution = (re.search(r'name="execution" value="([^"]+)"', html) or [None, ""])[1]
    form = urllib.parse.urlencode({"username": user, "password": pwd, "execution": execution,
                                   "_eventId": "submit", "submit": "登录"}).encode()
    req = urllib.request.Request(login_url, data=form, method="POST",
                                 headers={**UA, "Content-Type": "application/x-www-form-urlencoded",
                                          "Referer": login_url})
    r = op.open(req, timeout=25)
    return r.geturl()


def try_get(url: str, label: str, size: int = 600):
    try:
        r = op.open(url, timeout=20)
        body = r.read(size * 4).decode("utf-8", "ignore")
        print(f"[{label}] {r.status} {r.geturl()[:80]}")
        print("   ", body[:size].replace("\n", " ")[:size])
        return body
    except urllib.error.HTTPError as e:
        print(f"[{label}] HTTP {e.code} {e.read(150).decode('utf-8','ignore')[:120]}")
    except Exception as e:
        print(f"[{label}] ERR {str(e)[:90]}")
    return ""


print("== CAS -> dekt ==")
u = cas_login("https://dekt.hfut.edu.cn/scReports/activity/list")
print("landed:", u[:100])
try_get("https://dekt.hfut.edu.cn/scReports/activity/list", "dekt-activity")

print("== CAS -> eams ==")
u2 = cas_login("http://jxglstu.hfut.edu.cn/eams5-student/neusoft-sso/login")
print("landed:", u2[:100])

print("== community api with cookies ==")
try:
    req = urllib.request.Request("https://community.hfut.edu.cn/api/community/community/list",
                                 data=json.dumps({"pageNum": 1, "pageSize": 3}).encode(),
                                 headers={**UA, "Content-Type": "application/json"}, method="POST")
    r = op.open(req, timeout=15)
    print("community:", r.status, r.read(300).decode("utf-8", "ignore"))
except Exception as e:
    print("community ERR", str(e)[:90])
