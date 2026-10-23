# -*- coding: utf-8 -*-
"""信息源抓取适配器：RSS / 官网列表页 / 微信公众号文章。"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Any
from urllib.parse import urljoin

from lxml import html as lxml_html

from .common import http_get, strip_tags

NAV_WORDS = {
    "首页", "上一页", "下一页", "更多", "返回", "登录", "注册", "English", "联系我们",
    "网站地图", "友情链接", "设为首页", "加入收藏", "机构设置", "师资队伍", "人才培养",
    "科学研究", "招生就业", "党建工作", "学生工作", "信息公开", "搜索结果", "全站搜索",
}

LEAD_DATE = re.compile(r"^\s*(?:20\d{2}[-/.年]\d{1,2}[-/.月]\d{1,2}日?|\d{1,2}[-/月]\d{1,2}日?)\s*")
TRAIL_DATE = re.compile(r"\s*(?:20\d{2}[-/.]\d{1,2}[-/.]\d{1,2}|\d{1,2}[-/月]\d{1,2}日?)\s*$")
SITE_SUFFIX = re.compile(r"\s*[-–—|｜_]\s*合肥工业大学.*$")
PUB_LINE = re.compile(r"^(?:发布(?:时间|日期)|来源|浏览(?:次数)?|作者|编辑|审核)[:：].{0,40}$")


def clean_title(raw: str) -> str:
    """去掉标题里混进来的日期和列表页附带的一句摘要。"""
    text = " ".join(raw.split())
    text = LEAD_DATE.sub("", text)
    text = SITE_SUFFIX.sub("", text)
    text = TRAIL_DATE.sub("", text)
    if len(text) > 34:
        parts = text.split()
        if len(parts) > 1:
            for part in parts:
                if len(part) >= 8:
                    text = part
                    break
    return text.strip()

DATE_PATTERNS = [
    re.compile(r"(20\d{2})[-/.年](\d{1,2})[-/.月](\d{1,2})"),
    re.compile(r"(?<!\d)(\d{1,2})[-/月](\d{1,2})(?!\d)"),
]


def parse_date(text: str, now: datetime | None = None) -> str | None:
    """从一段文本里找日期，返回 ISO 时间；找不到返回 None。"""
    now = now or datetime.now()
    m = DATE_PATTERNS[0].search(text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return datetime(y, mo, d, 9, 0).isoformat()
        except ValueError:
            return None
    m = DATE_PATTERNS[1].search(text)
    if m:
        mo, d = int(m.group(1)), int(m.group(2))
        try:
            dt = datetime(now.year, mo, d, 9, 0)
        except ValueError:
            return None
        if dt > now + timedelta(days=2):
            dt = dt.replace(year=now.year - 1)
        return dt.isoformat()
    return None


def fetch_source(source: dict[str, Any], limit: int = 12) -> list[dict[str, Any]]:
    feed = source.get("feed") or {}
    kind = feed.get("kind")
    if kind == "rss":
        return fetch_rss(feed["url"], limit)
    if kind == "html_list":
        return fetch_html_list(feed, limit)
    if kind == "wechat":
        urls = feed.get("articles") or []
        return [fetch_wechat_article(u) for u in urls[:limit] if u]
    return []


def fetch_rss(url: str, limit: int = 12) -> list[dict[str, Any]]:
    text, _ = http_get(url)
    root = ET.fromstring(text.encode("utf-8"))
    out: list[dict[str, Any]] = []
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    for node in root.iter():
        tag = node.tag.split("}")[-1]
        if tag not in ("item", "entry"):
            continue
        title = _child_text(node, "title")
        link = _child_text(node, "link")
        if not link:
            el = node.find("atom:link", ns)
            link = el.get("href") if el is not None else ""
        date = _child_text(node, "pubDate") or _child_text(node, "updated") or _child_text(node, "published")
        published = None
        if date:
            try:
                from email.utils import parsedate_to_datetime
                published = parsedate_to_datetime(date).isoformat()
            except (TypeError, ValueError):
                published = parse_date(date)
        if title and link:
            out.append({"title": " ".join(title.split()), "url": link, "published_at": published})
        if len(out) >= limit:
            break
    return out


def _child_text(node: ET.Element, name: str) -> str:
    for child in node:
        if child.tag.split("}")[-1] == name:
            return (child.text or "").strip()
    return ""


def fetch_html_list(feed: dict[str, Any], limit: int = 12) -> list[dict[str, Any]]:
    url = feed["url"]
    text, final_url = http_get(url)
    doc = lxml_html.fromstring(text)
    doc.make_links_absolute(final_url)
    items: list[dict[str, Any]] = []

    item_xpath = feed.get("item_xpath")
    if item_xpath:
        for node in doc.xpath(item_xpath)[:limit * 2]:
            link_nodes = node.xpath(".//a[@href]")
            if not link_nodes:
                continue
            a = link_nodes[0]
            title = clean_title(a.get("title") or a.text_content() or "")
            node_text = " ".join(node.text_content().split())[:300]
            items.append({"title": title, "url": a.get("href"), "published_at": parse_date(node_text)})
    else:
        seen: set[str] = set()
        for a in doc.iter("a"):
            href = a.get("href")
            if not href or href.startswith(("javascript:", "#", "mailto:")):
                continue
            href = urljoin(final_url, href)
            if href in seen:
                continue
            title = clean_title(a.get("title") or a.text_content() or "")
            if len(title) < 6 or title in NAV_WORDS:
                continue
            seen.add(href)
            parent = a.getparent()
            context = " ".join(parent.text_content().split())[:240] if parent is not None else title
            published = parse_date(context)
            score = 0
            if published:
                score += 3
            if re.search(r"/info/|/content/|/detail|/article|/20\d{2}/|\.htm", href):
                score += 2
            if len(title) >= 12:
                score += 1
            if "/list.htm" in href or href.rstrip("/").endswith("index.htm"):
                score -= 2
            items.append({"title": title, "url": href, "published_at": published, "_score": score})

    if items and "_score" in items[0]:
        items.sort(key=lambda x: -x["_score"])
        items = [i for i in items if i["_score"] >= 3] or items[:limit]
    for it in items:
        it.pop("_score", None)
    # 去重 + 截断
    out, seen2 = [], set()
    for it in items:
        if it["url"] in seen2:
            continue
        seen2.add(it["url"])
        out.append(it)
        if len(out) >= limit:
            break
    return out


JUNK_LINES = ("您的位置", "当前位置", "关闭此页", "提示信息", "版权所有", "技术支持",
              "ICP备", "扫一扫", "点击查看", "上一篇", "下一篇", "相关附件")


def _body_score(node) -> float:
    total = len("".join(node.text_content().split()))
    if total < 120:
        return 0.0
    ptext = sum(len("".join(p.text_content().split())) for p in node.xpath(".//p"))
    links = sum(len("".join(a.text_content().split())) for a in node.xpath(".//a"))
    effective = ptext - links * 0.6
    if effective <= 0:
        return 0.0
    return effective * (effective / total)


def _clean_body(text: str) -> str:
    out = []
    for line in text.split("\n"):
        line = line.strip()
        if len(line) < 6:
            continue
        if any(j in line for j in JUNK_LINES) and len(line) < 60:
            continue
        if PUB_LINE.match(line):
            continue
        line = re.sub(r"(发布者|发布时间|发布单位|来源|编辑|审核|浏览次数)[:：]\s*\S{0,20}", "", line).strip()
        if len(line) < 6:
            continue
        out.append(line)
    return "\n".join(out)[:4000]


def fetch_article(url: str) -> dict[str, Any]:
    """抓单篇文章：标题 + 正文 HTML + 纯文本。"""
    text, final_url = http_get(url)
    doc = lxml_html.fromstring(text)
    doc.make_links_absolute(final_url)
    for bad in doc.xpath("//script|//style|//nav|//header|//footer"):
        bad.drop_tree()

    title = ""
    for xp in ("//h1", "//*[contains(@class,'title')]", "//title"):
        nodes = doc.xpath(xp)
        if nodes:
            title = clean_title(nodes[0].text_content())
            if title:
                break

    best, best_score = None, 0.0
    for node in doc.iter("div", "article", "section", "td"):
        score = _body_score(node)
        if score > best_score:
            best, best_score = node, score
    content_html = lxml_html.tostring(best, encoding="unicode") if best is not None else ""
    body = _clean_body(strip_tags(content_html)) if content_html else ""

    published = None
    m = re.search(r"发布时间[:：]\s*(20\d{2}[-/.]\d{1,2}[-/.]\d{1,2})", text)
    if m:
        published = parse_date(m.group(1))

    return {
        "title": title,
        "url": final_url,
        "html": content_html,
        "text": body,
        "published_at": published,
        "restricted": "仅允许校内" in text,
    }


def fetch_wechat_article(url: str) -> dict[str, Any]:
    """公众号文章（mp.weixin.qq.com）。"""
    text, final_url = http_get(url)
    doc = lxml_html.fromstring(text)
    title = ""
    for xp in ("//*[@id='activity-name']", "//meta[@property='og:title']/@content", "//h1"):
        nodes = doc.xpath(xp)
        if nodes:
            node = nodes[0]
            title = node if isinstance(node, str) else node.text_content()
            title = " ".join(title.split())
            if title:
                break
    body_nodes = doc.xpath("//*[@id='js_content']")
    content = lxml_html.tostring(body_nodes[0], encoding="unicode") if body_nodes else ""
    account = ""
    nodes = doc.xpath("//*[@id='js_name']")
    if nodes:
        account = " ".join(nodes[0].text_content().split())
    publish = ""
    m = re.search(r"var\s+ct\s*=\s*[\"'](\d{10})[\"']", text)
    if m:
        publish = datetime.fromtimestamp(int(m.group(1))).isoformat()
    return {
        "title": title,
        "url": final_url,
        "html": content,
        "text": strip_tags(content),
        "account": account,
        "published_at": publish or None,
    }
