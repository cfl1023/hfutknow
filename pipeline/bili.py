# -*- coding: utf-8 -*-
"""B 站渠道：用 wbi 签名调公开搜索接口，把「真人学生内容」接进信息流。

只做 B 站——贴吧 403、小红书/抖音要登录或签名、微博有访客墙，
在服务器上无凭据抓不到（见 README「信息渠道」一节）。
约每 3 小时刷一次，避免同一个 IP 高频打接口被风控。
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Any

from . import common

STATE_FILE = common.DATA_DIR / "bili_state.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
MIN_INTERVAL_MIN = 180
CAMPUS_WORDS = ("合肥工业大学", "合工大", "宣城校区", "翡翠湖", "HFUT")

MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52,
]


def _state() -> dict[str, Any]:
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _due() -> bool:
    last = _state().get("lastFetch") or ""
    if not last:
        return True
    try:
        return datetime.now() - datetime.fromisoformat(last) > timedelta(minutes=MIN_INTERVAL_MIN)
    except ValueError:
        return True


def _save_state() -> None:
    STATE_FILE.write_text(json.dumps({"lastFetch": datetime.now().isoformat(timespec="minutes")},
                                     ensure_ascii=False), encoding="utf-8")


def _get_json(url: str, cookie: str = "") -> dict:
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Referer": "https://www.bilibili.com/",
        "Accept": "application/json, text/plain, */*", "Cookie": cookie,
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def _prepare() -> tuple[str, str]:
    """拿 buvid3 cookie 和 wbi 密钥。"""
    cookie = ""
    try:
        spi = _get_json("https://api.bilibili.com/x/frontend/finger/spi")
        b3 = (spi.get("data") or {}).get("b_3") or ""
        cookie = f"buvid3={b3}" if b3 else ""
    except Exception:
        pass
    nav = _get_json("https://api.bilibili.com/x/web-interface/nav", cookie)
    wbi = (nav.get("data") or {}).get("wbi_img") or {}
    img = (wbi.get("img_url") or "").rsplit("/", 1)[-1].split(".")[0]
    sub = (wbi.get("sub_url") or "").rsplit("/", 1)[-1].split(".")[0]
    if not img or not sub:
        raise RuntimeError("拿不到 wbi 密钥（可能被风控）")
    raw = img + sub
    key = "".join(raw[i] for i in MIXIN_KEY_ENC_TAB)[:32]
    return cookie, key


def _sign(params: dict, key: str) -> str:
    params = dict(params)
    params["wts"] = int(time.time())
    items = sorted(params.items())
    q = urllib.parse.urlencode([(k, "".join(c for c in str(v) if c not in "!'()*")) for k, v in items])
    return q + "&w_rid=" + hashlib.md5((q + key).encode()).hexdigest()


def _clean(s: str) -> str:
    return html.unescape(re.sub(r"</?em[^>]*>", "", s or "")).strip()


def _parse(data: dict, kw: str, limit: int = 20, days: int = 30) -> list[dict[str, Any]]:
    cutoff = datetime.now() - timedelta(days=days)
    out: list[dict[str, Any]] = []
    for v in (data.get("data") or {}).get("result") or []:
        try:
            pub = datetime.fromtimestamp(int(v.get("pubdate") or 0))
        except (TypeError, ValueError):
            continue
        if pub < cutoff or not v.get("bvid"):
            continue
        title = _clean(v.get("title") or "")
        desc = _clean(v.get("description") or "")
        author = _clean(v.get("author") or "")
        hay = f"{title} {desc} {author}"
        if not title or not any(w in hay for w in CAMPUS_WORDS):
            continue
        out.append({"bvid": v["bvid"], "title": title, "author": author,
                    "published": pub, "play": v.get("play") or 0, "desc": desc})
        if len(out) >= limit:
            break
    return out


def fetch_items(keywords: list[str]) -> list[dict[str, Any]]:
    """把最近视频变成站点条目；未到刷新间隔时返回空列表。"""
    if not keywords or not _due():
        return []
    try:
        cookie, key = _prepare()
    except Exception as exc:
        print(f"  × B站: {exc}")
        return []
    items: list[dict[str, Any]] = []
    for kw in keywords:
        try:
            url = ("https://api.bilibili.com/x/web-interface/wbi/search/type?"
                   + _sign({"search_type": "video", "keyword": kw, "page": 1, "order": "pubdate"}, key))
            data = _get_json(url, cookie)
            if data.get("code") != 0:
                raise RuntimeError(f"code={data.get('code')} {data.get('message')}")
            videos = _parse(data, kw)
        except Exception as exc:
            print(f"  × B站「{kw}」: {exc}")
            continue
        sid = "bili-" + hashlib.sha1(kw.encode("utf-8")).hexdigest()[:8]
        for v in videos:
            desc = v["desc"] or f"{v['author']} 发布的 B 站视频"
            items.append({
                "id": "bili-" + v["bvid"],
                "title": v["title"],
                "sourceId": sid,
                "sourceName": f"B站 · {kw}",
                "sourceType": "bili",
                "url": f"https://www.bilibili.com/video/{v['bvid']}",
                "publishedAt": v["published"].isoformat(timespec="minutes"),
                "dateEstimated": False,
                "intent": "information",
                "category": "life",
                "summary": desc[:160],
                "event": None,
                "requiresSignup": False,
                "tags": [v["author"]] if v["author"] else [],
                "competition": None,
                "content": [f"<p>{desc}</p>"],
                "bili": {"author": v["author"], "play": v["play"]},
                "demo": False,
            })
        print(f"  ✓ B站「{kw}」: {len(videos)} 条")
    if items:
        _save_state()
    return items
