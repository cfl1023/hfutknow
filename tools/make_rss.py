# -*- coding: utf-8 -*-
"""把 items.json 导出成 RSS，方便订阅。"""
from __future__ import annotations

import html
from datetime import datetime
from pathlib import Path
from email.utils import format_datetime

import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data"


def main() -> None:
    payload = json.loads((DATA / "items.json").read_text(encoding="utf-8"))
    site = payload.get("site", {})
    items = sorted(payload["items"], key=lambda x: x.get("publishedAt", ""), reverse=True)[:80]
    base = site.get("url", "https://example.com").rstrip("/")

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{html.escape(site.get('name', '校园知道'))}</title>",
        f"    <link>{base}</link>",
        f"    <description>{html.escape(site.get('description', ''))}</description>",
        "    <language>zh-CN</language>",
        f"    <lastBuildDate>{format_datetime(datetime.now().astimezone())}</lastBuildDate>",
        f'    <atom:link href="{base}/data/feed.xml" rel="self" type="application/rss+xml"/>',
    ]
    for it in items:
        try:
            pub = format_datetime(datetime.fromisoformat(it["publishedAt"]).astimezone())
        except ValueError:
            pub = format_datetime(datetime.now().astimezone())
        out += [
            "    <item>",
            f"      <title>{html.escape(it['title'])}</title>",
            f"      <link>{html.escape(it.get('url', base))}</link>",
            f"      <guid isPermaLink=\"false\">{html.escape(it['id'])}</guid>",
            f"      <pubDate>{pub}</pubDate>",
            f"      <category>{html.escape(it.get('category', ''))}</category>",
            f"      <description>{html.escape(it.get('summary', ''))}</description>",
            "    </item>",
        ]
    out += ["  </channel>", "</rss>"]
    (DATA / "feed.xml").write_text("\n".join(out), encoding="utf-8")
    print(f"feed.xml: {len(items)} 条")


if __name__ == "__main__":
    main()
