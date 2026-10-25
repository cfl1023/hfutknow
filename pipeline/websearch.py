# -*- coding: utf-8 -*-
"""互联网搜索渠道：Bing HTML 搜索（云端 IP 可达），把校外渠道的消息接进来。

策略：按关键词搜近一周，命中的结果按域名打渠道标签（贴吧/知乎/微博/B站/小红书/新闻），
标题+摘要入库，链接直达原文。本机网络对 bing 不稳，但 GitHub Actions 的海外 IP 可用；
抓不到就静默跳过，不影响主流程。
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Any

from . import common

STATE_FILE = common.DATA_DIR / "web_state.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
MIN_INTERVAL_MIN = 120

QUERIES = [
    "合肥工业大学 讲座 OR 论坛",
    "合肥工业大学 竞赛 OR 报名",
    "合工大 社团 OR 活动",
    "合肥工业大学 保研 OR 奖学金",
    "site:tieba.baidu.com 合肥工业大学",
    "site:zhihu.com 合肥工业大学",
]

CHANNEL = {
    "tieba.baidu.com": "贴吧",
    "zhihu.com": "知乎",
    "weibo.com": "微博",
    "bilibili.com": "B站",
    "xiaohongshu.com": "小红书",
    "douyin.com": "抖音",
    "thepaper.cn": "澎湃",
    "sohu.com": "搜狐",
    "163.com": "网易",
    "qq.com": "腾讯",
}

CAMPUS_RE = re.compile(r"合肥工业|合工大|HFUT|斛兵|翡翠湖")
# 官网已有专门抓取，搜索结果里再出现就是重复
SKIP_HOSTS = ("hfut.edu.cn", "bing.com", "microsoft.com")


def _due() -> bool:
    try:
        last = json.loads(STATE_FILE.read_text(encoding="utf-8")).get("lastFetch") or ""
        return datetime.now() - datetime.fromisoformat(last) > timedelta(minutes=MIN_INTERVAL_MIN)
    except Exception:
        return True


def _save() -> None:
    STATE_FILE.write_text(json.dumps({"lastFetch": datetime.now().isoformat(timespec="minutes")}),
                          encoding="utf-8")


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read(600000).decode("utf-8", "ignore")


def _channel(href: str) -> str:
    try:
        host = urllib.parse.urlparse(href).netloc
    except ValueError:
        return ""
    for k, v in CHANNEL.items():
        if k in host:
            return v
    return ""


def _search(q: str) -> list[dict[str, Any]]:
    url = "https://www.bing.com/search?q=" + urllib.parse.quote(q) + "&setlang=zh-hans&count=20"
    page = _get(url)
    out: list[dict[str, Any]] = []
    for m in re.finditer(r'<li class="b_algo".*?<h2><a[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?(?:<p[^>]*>(.*?)</p>)?',
                         page, re.S):
        href, title, desc = m.group(1), re.sub(r"<[^>]+>", "", m.group(2) or ""), re.sub(r"<[^>]+>", "", m.group(3) or "")
        title = html.unescape(title).strip()
        desc = html.unescape(desc).strip()
        if not title or not CAMPUS_RE.search(title + desc):
            continue
        if any(h in href for h in SKIP_HOSTS):
            continue
        ch = _channel(href)
        out.append({"title": title[:100], "url": href, "desc": desc[:160], "channel": ch})
    return out


def fetch_items(queries: list[str] | None = None) -> list[dict[str, Any]]:
    if not _due():
        return []
    items: list[dict[str, Any]] = []
    now = datetime.now().isoformat(timespec="minutes")
    got_any = False
    for q in (queries or QUERIES):
        try:
            rows = _search(q)
            got_any = True
        except Exception as exc:
            print(f"  × 互联网搜索「{q[:18]}」: {str(exc)[:60]}")
            continue
        for r in rows:
            sid = "web-" + hashlib.sha1(r["url"].encode()).hexdigest()[:16]
            ch = r["channel"] or "网页"
            items.append({
                "id": sid,
                "title": r["title"],
                "sourceId": "net-" + (r["channel"] or "web"),
                "sourceName": f"互联网 · {ch}",
                "sourceType": "net",
                "url": r["url"],
                "publishedAt": now,
                "dateEstimated": True,
                "intent": "information",
                "category": "campus",
                "summary": r["desc"] or r["title"],
                "event": None,
                "requiresSignup": bool(re.search(r"报名|截止", r["title"] + r["desc"])),
                "tags": [ch],
                "competition": None,
                "content": [f"<p>{html.escape(r['desc'] or r['title'])}</p>"],
                "demo": False,
            })
        print(f"  ✓ 互联网搜索「{q[:18]}」: {len(rows)} 条")
    if got_any:
        _save()
    return items
