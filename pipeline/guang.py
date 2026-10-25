# -*- coding: utf-8 -*-
"""逛逛/社区活动源：CAS 免登 → community token → 可报名活动列表。

凭据只从本机 ~/.hfutknow_creds.json 读取，绝不进仓库。
只在「本机更新」里跑（GitHub 上没有你的密码，也不该有）。
"""
from __future__ import annotations

import http.cookiejar
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from . import common

CRED = Path.home() / ".hfutknow_creds.json"
STATE = common.DATA_DIR / "guang_state.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
SERVICE = "https://community.hfut.edu.cn/login"
API = "https://community.hfut.edu.cn/api"
MIN_INTERVAL_MIN = 30

MODULE_CAT = {
    "科技创新": "skills", "公益服务": "recruitment", "思想成长": "campus",
    "社会实践": "recruitment", "志愿精神": "recruitment", "工作技能": "skills",
    "文体活动": "arts", "讲座交流": "lectures", "创业实践": "careers",
}


def _opener():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                     urllib.request.HTTPSHandler(context=ctx))
    op.addheaders = [("User-Agent", UA), ("Accept-Language", "zh-CN,zh;q=0.9")]
    return op


def _token(op) -> str:
    if not CRED.exists():
        raise RuntimeError("无凭据文件 ~/.hfutknow_creds.json")
    cred = json.loads(CRED.read_text(encoding="utf-8"))
    login_url = "https://cas.hfut.edu.cn/cas/login?service=" + urllib.parse.quote(SERVICE)
    html = op.open(login_url, timeout=20).read().decode("utf-8", "ignore")
    m = re.search(r'name="execution" value="([^"]+)"', html)
    if not m:
        raise RuntimeError("CAS 页面无 execution token")
    form = urllib.parse.urlencode({
        "username": cred["user"], "password": cred["pwd"],
        "execution": m.group(1), "_eventId": "submit", "submit": "登录",
    }).encode()
    req = urllib.request.Request(login_url, data=form, method="POST", headers={
        "Content-Type": "application/x-www-form-urlencoded", "Referer": login_url})
    r = op.open(req, timeout=25)
    t = re.search(r"[?&]ticket=([A-Za-z0-9\-]+)", r.geturl())
    if not t:
        raise RuntimeError("CAS 未发 ticket（可能密码变更或需人工验证）")
    vreq = urllib.request.Request(
        f"{API}/sys/cas/client/validateLogin?ticket={t.group(1)}&service={urllib.parse.quote(SERVICE)}",
        headers={"X-Requested-With": "XMLHttpRequest"})
    data = json.loads(op.open(vreq, timeout=20).read().decode("utf-8", "ignore"))
    tk = (data.get("result") or {}).get("token") or ""
    if not tk:
        raise RuntimeError("validateLogin 无 token: " + str(data.get("message")))
    return tk


def _due() -> bool:
    try:
        last = json.loads(STATE.read_text(encoding="utf-8")).get("lastFetch") or ""
        return datetime.now() - datetime.fromisoformat(last) > timedelta(minutes=MIN_INTERVAL_MIN)
    except Exception:
        return True


def _get(op, tk: str, path: str) -> dict:
    req = urllib.request.Request(API + path, headers={"X-Access-Token": tk,
                                                      "X-Requested-With": "XMLHttpRequest"})
    with op.open(req, timeout=20) as r:
        return json.loads(r.read(800000).decode("utf-8", "ignore"))


def fetch_items() -> list[dict[str, Any]]:
    if not _due() or not CRED.exists():
        return []
    try:
        op = _opener()
        tk = _token(op)
        acts = _get(op, tk, "/community/ekActivity/list?pageNo=1&pageSize=50").get("result") or {}
    except Exception as exc:
        print(f"  × 逛逛/活动: {exc}")
        return []
    items: list[dict[str, Any]] = []
    for a in acts.get("records") or []:
        name = (a.get("name") or "").strip()
        if not name:
            continue
        cat = MODULE_CAT.get(a.get("moduleName") or "", "campus")
        begin = (a.get("beginTime") or "").replace(" ", "T")[:16]
        end = (a.get("endTime") or "").replace(" ", "T")[:16]
        event = {"start": begin, "location": (a.get("theVenue") or "").strip() or None} if begin else None
        summary = f"{a.get('moduleName') or ''}｜主办 {a.get('sponsor') or '?'}"
        if a.get("peopleNum"):
            summary += f"｜限 {a['peopleNum']} 人"
        if a.get("applyNum"):
            summary += f"｜已报 {a['applyNum']}"
        items.append({
            "id": "gg-" + str(a.get("id")),
            "title": name[:100],
            "sourceId": "gg-activity",
            "sourceName": "逛逛 · 校园活动",
            "sourceType": "gg",
            "url": "https://community.hfut.edu.cn/",
            "publishedAt": begin or datetime.now().isoformat(timespec="minutes"),
            "dateEstimated": not bool(begin),
            "intent": "activity",
            "category": cat,
            "summary": summary,
            "event": event,
            "requiresSignup": True,
            "tags": [t for t in [a.get("moduleName"), a.get("campus_dictText")] if t],
            "competition": None,
            "content": [f"<p>{summary}</p>"],
            "demo": False,
        })
    STATE.write_text(json.dumps({"lastFetch": datetime.now().isoformat(timespec="minutes")}),
                     encoding="utf-8")
    print(f"  ✓ 逛逛/活动: {len(items)} 条")
    return items
