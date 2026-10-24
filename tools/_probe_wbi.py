# -*- coding: utf-8 -*-
"""B站 wbi 签名搜索冒烟测试。"""
import hashlib
import json
import time
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

MIXIN_KEY_ENC_TAB = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52,
]


def get_json(url, cookie=""):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Referer": "https://www.bilibili.com/",
        "Accept": "application/json, text/plain, */*",
        "Cookie": cookie,
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8", "ignore"))


def get_cookie():
    try:
        d = get_json("https://api.bilibili.com/x/frontend/finger/spi")
        b3 = (d.get("data") or {}).get("b_3") or ""
        return f"buvid3={b3}" if b3 else ""
    except Exception as e:
        print("spi fail", e)
        return ""


def get_wbi_keys(cookie):
    d = get_json("https://api.bilibili.com/x/web-interface/nav", cookie)
    wbi = (d.get("data") or {}).get("wbi_img") or {}
    img = (wbi.get("img_url") or "").rsplit("/", 1)[-1].split(".")[0]
    sub = (wbi.get("sub_url") or "").rsplit("/", 1)[-1].split(".")[0]
    print("nav code:", d.get("code"), "img:", bool(img), "sub:", bool(sub))
    return img, sub


def mixin_key(img, sub):
    raw = img + sub
    return "".join(raw[i] for i in MIXIN_KEY_ENC_TAB)[:32]


def sign(params: dict, key: str) -> str:
    params = dict(params)
    params["wts"] = int(time.time())
    items = sorted(params.items())
    q = urllib.parse.urlencode(
        [(k, "".join(c for c in str(v) if c not in "!'()*")) for k, v in items])
    w_rid = hashlib.md5((q + key).encode()).hexdigest()
    return q + "&w_rid=" + w_rid


def main():
    cookie = get_cookie()
    print("cookie:", cookie[:30])
    img, sub = get_wbi_keys(cookie)
    if not img or not sub:
        print("no wbi keys -> blocked")
        return
    key = mixin_key(img, sub)
    q = sign({"search_type": "video", "keyword": "合肥工业大学", "page": 1}, key)
    url = "https://api.bilibili.com/x/web-interface/wbi/search/type?" + q
    d = get_json(url, cookie)
    print("code:", d.get("code"), d.get("message"))
    res = (d.get("data") or {}).get("result") or []
    print("n:", len(res))
    for v in res[:6]:
        print("  -", v.get("title", "")[:45], "|", v.get("author"), "|", v.get("pubdate"))


main()
