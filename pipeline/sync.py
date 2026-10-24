# -*- coding: utf-8 -*-
"""同步：抓取已启用的信息源，分类、摘要、去重后写入 site/data/。

用法：
    python -m pipeline.sync                 # 抓所有启用的源
    python -m pipeline.sync --only hfut-jwc # 只抓教务处
    python -m pipeline.sync --dry-run       # 只看抓到了什么，不写文件
    python -m pipeline.sync --enrich        # 逐篇打开正文（慢）
    python -m pipeline.sync --drop-demo     # 清掉演示数据，只留真实抓取
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import datetime, timedelta
from typing import Any

from . import classify, common, fetchers, summarize

CAT_INTENT = {c["id"]: c["intent"] for c in common.load_config()["categories"]}


def make_id(url: str) -> str:
    return "web-" + hashlib.sha1(url.encode("utf-8")).hexdigest()[:16]


def build_item(src: dict[str, Any], entry: dict[str, Any], cfg: dict[str, Any], enrich: bool) -> dict[str, Any] | None:
    url = entry["url"]
    title = entry.get("title") or ""
    text = ""
    published = entry.get("published_at")

    if enrich:
        try:
            art = fetchers.fetch_article(url)
            if art.get("restricted"):
                print(f"    - 校内可见，跳过：{title[:30]}")
                return None
            text = art.get("text") or ""
            title = art.get("title") or title
            published = art.get("published_at") or published
        except Exception as exc:  # 单篇失败不影响整批
            print(f"    ! 正文抓取失败 {url}: {exc}")

    intent, category = classify.classify(title, text)
    event = classify.extract_event(f"{title} {text}")
    summary = summarize.make_summary(title, text, event, cfg) or title

    content: list[str] = []
    if text:
        paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 10][:8]
        content = [f"<p>{p}</p>" for p in paragraphs]
    if not content:
        content = [f"<p>{summary}</p>"]

    # 没有日期的条目：发布日期用「抓取时刻减 7 天」近似，并打 estimated 标记，
    # 避免无日期内容被当成“刚刚发布”永远钉在列表顶部。
    estimated = not published
    fallback = datetime.now() - timedelta(days=7)

    return {
        "id": make_id(url),
        "title": title.strip(),
        "sourceId": src["id"],
        "sourceName": src["name"],
        "sourceType": src["type"],
        "url": url,
        "publishedAt": published or fallback.isoformat(timespec="minutes"),
        "dateEstimated": estimated,
        "intent": intent,
        "category": category,
        "summary": summary,
        "event": event,
        "requiresSignup": classify.needs_signup(f"{title} {text}"),
        "tags": classify.keywords(title),
        "content": content,
        "demo": False,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="抓取校园信息源并写入站点数据")
    ap.add_argument("--limit", type=int, default=12, help="每个源最多取几条")
    ap.add_argument("--only", default="", help="只抓这些来源 id，逗号分隔")
    ap.add_argument("--enrich", action="store_true", help="逐篇抓正文（慢，但摘要更准）")
    ap.add_argument("--fast", action="store_true", help="只抓列表不抓正文（最快，用于高频更新）")
    ap.add_argument("--dry-run", action="store_true", help="不写文件")
    ap.add_argument("--drop-demo", action="store_true", help="删除演示数据")
    args = ap.parse_args(argv)

    cfg = common.load_config()
    payload = common.load_items()
    items: list[dict[str, Any]] = payload.get("items", [])

    if args.drop_demo:
        before = len(items)
        items = [i for i in items if not i.get("demo")]
        print(f"已移除演示数据 {before - len(items)} 条")

    existing_urls = {i["url"] for i in items if i.get("url")}
    only = {x.strip() for x in args.only.split(",") if x.strip()}
    sources = [s for s in cfg["sources"] if (s.get("feed") or {}).get("enabled")]
    if only:
        sources = [s for s in sources if s["id"] in only]

    enrich = args.enrich and not args.fast
    if args.fast:
        print(f"快速模式：不抓正文，逐页只读列表，每源上限 {args.limit} 条")
    print(f"待抓取来源 {len(sources)} 个")
    total_new = 0

    from concurrent.futures import ThreadPoolExecutor, as_completed

    def fetch_one(src: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            return fetchers.fetch_source(src, args.limit)
        except Exception as exc:
            print(f"  × {src['name']}: {exc}")
            return []

    def build_one(src: dict[str, Any], entry: dict[str, Any]):
        if not entry.get("url") or entry["url"] in existing_urls:
            return None
        try:
            return build_item(src, entry, cfg, enrich)
        except Exception as exc:
            print(f"    ! 处理失败 {entry.get('url')}: {exc}")
            return None

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch_one, src): src for src in sources}
        fetched: list[tuple[dict, list[dict]]] = []
        for fut in as_completed(futures):
            src = futures[fut]
            fetched.append((src, fut.result()))
            print(f"  ✓ {src['name']}: 抓到 {len(fetched[-1][1])} 条")

    for src, entries in fetched:
        kept = 0
        with ThreadPoolExecutor(max_workers=6) as pool:
            results = list(pool.map(lambda e: build_one(src, e), entries))
        for item in results:
            if item is None:
                continue
            existing_urls.add(item["url"])
            items.append(item)
            kept += 1
        total_new += kept
        if kept:
            print(f"  + {src['name']}: 新增 {kept} 条")

    items.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)
    payload["items"] = items
    payload["generatedAt"] = datetime.now().isoformat(timespec="minutes")
    payload["categories"] = cfg["categories"]
    payload["site"] = cfg["site"]
    if any(not i.get("demo") for i in items):
        payload["demo"] = False

    # 来源计数
    counts: dict[str, int] = {}
    for it in items:
        counts[it["sourceId"]] = counts.get(it["sourceId"], 0) + 1
    sources_out = [{**s, "count": counts.get(s["id"], 0)} for s in cfg["sources"]]

    if args.dry_run:
        print(f"\n[dry-run] 新增 {total_new} 条，未写入文件")
        return 0

    common.save_items(payload)
    common.save_sources(sources_out)
    print(f"\n完成：新增 {total_new} 条，总计 {len(items)} 条 → {common.DATA_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
