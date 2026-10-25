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
import json
from datetime import datetime, timezone
import time
import hashlib
import sys
from datetime import datetime, timedelta
from typing import Any

from . import bili, classify, common, competitions, fetchers, guang, summarize, websearch

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
        "competition": competitions.detect_competition(title, text),
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
    jbk = common.DATA_DIR / "junk_urls.txt"
    if jbk.exists():
        existing_urls |= set(jbk.read_text(encoding="utf-8").split())
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

    def fetch_one(src: dict[str, Any]):
        t0 = time.time()
        try:
            got = fetchers.fetch_source(src, args.limit)
            return got, None, round(time.time() - t0, 1)
        except Exception as exc:
            print(f"  × {src['name']}: {exc}")
            return [], str(exc)[:160], round(time.time() - t0, 1)

    def build_one(src: dict[str, Any], entry: dict[str, Any]):
        if not entry.get("url") or entry["url"] in existing_urls:
            return None
        try:
            return build_item(src, entry, cfg, enrich)
        except Exception as exc:
            print(f"    ! 处理失败 {entry.get('url')}: {exc}")
            return None

    started = time.time()
    report: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch_one, src): src for src in sources}
        fetched: list[tuple[dict, list[dict]]] = []
        for fut in as_completed(futures):
            src = futures[fut]
            got, err, sec = fut.result()
            fetched.append((src, got))
            report[src["id"]] = {"id": src["id"], "name": src["name"], "ok": err is None,
                                 "got": len(got), "err": err, "sec": sec}
            if err:
                print(f"  × {src['name']}: {err}  ({sec}s)")
            else:
                print(f"  ✓ {src['name']}: 抓到 {len(got)} 条  ({sec}s)")

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
        if src["id"] in report:
            report[src["id"]]["new"] = kept
        if kept:
            print(f"  + {src['name']}: 新增 {kept} 条")

    # B 站：真人学生视频（约每 3 小时刷一次，见 pipeline/bili.py）
    bili_items = bili.fetch_items(cfg.get("biliKeywords") or ["合肥工业大学", "合工大"])
    bili_new = 0
    for it in bili_items:
        if it["url"] in existing_urls:
            continue
        existing_urls.add(it["url"])
        items.append(it)
        bili_new += 1
    if bili_new:
        print(f"  + B站: 新增 {bili_new} 条")
    total_new += bili_new

    # 逛逛/社区活动（CAS 免登，本机专属；无凭据自动跳过）
    try:
        gg_items = guang.fetch_items()
    except Exception as exc:
        print(f"  × 逛逛: {exc}")
        gg_items = []
    gg_new = 0
    gg_ids = {i["id"] for i in items}
    for it in gg_items:
        if it["id"] in gg_ids:
            continue
        gg_ids.add(it["id"])
        items.append(it)
        gg_new += 1
    if gg_new:
        print(f"  + 逛逛: 新增 {gg_new} 条")
    total_new += gg_new

    # 互联网搜索（Bing，约 2 小时一次；海外 runner 上稳定，本机可能被墙）
    try:
        web_items = websearch.fetch_items()
    except Exception as exc:
        print(f"  × 互联网搜索整体失败: {str(exc)[:80]}")
        web_items = []
    web_new = 0
    for it in web_items:
        if it["url"] in existing_urls or it["id"] in {i["id"] for i in items}:
            continue
        existing_urls.add(it["url"])
        items.append(it)
        web_new += 1
    if web_new:
        print(f"  + 互联网: 新增 {web_new} 条")
    total_new += web_new

    items.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)
    payload["items"] = items
    payload["generatedAt"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    payload["categories"] = cfg["categories"]
    payload["site"] = cfg["site"]
    if any(not i.get("demo") for i in items):
        payload["demo"] = False

    # 来源计数
    counts: dict[str, int] = {}
    for it in items:
        counts[it["sourceId"]] = counts.get(it["sourceId"], 0) + 1
    sources_out = [{**s, "count": counts.get(s["id"], 0)} for s in cfg["sources"]]
    seen = {s["id"] for s in sources_out}
    if counts.get("gg-activity"):
        sources_out.append({"id": "gg-activity", "name": "逛逛 · 校园活动", "type": "gg",
                            "url": "https://community.hfut.edu.cn/", "category": "campus",
                            "count": counts["gg-activity"],
                            "feed": {"type": "gg", "url": "", "enabled": True}})
        seen.add("gg-activity")
    for b_id, n in counts.items():
        if b_id.startswith("bili-") and b_id not in seen:
            name = next((i["sourceName"] for i in items if i["sourceId"] == b_id), "B站")
            kw = name.replace("B站 · ", "")
            sources_out.append({"id": b_id, "name": name, "type": "bili",
                                "url": f"https://search.bilibili.com/all?keyword={kw}",
                                "category": "life", "count": n,
                                "feed": {"type": "bili", "url": "", "enabled": True}})

    if args.dry_run:
        print(f"\n[dry-run] 新增 {total_new} 条，未写入文件")
        return 0

    common.save_items(payload)
    common.save_sources(sources_out)

    # 抓取体检报告（页面显示「上次抓取 / 各源状态」）
    rp = common.DATA_DIR / "crawl_report.json"
    hist: list[dict[str, Any]] = []
    try:
        if rp.exists():
            hist = json.loads(rp.read_text(encoding="utf-8")).get("history") or []
    except Exception:
        hist = []
    run = {
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "mode": "fast" if args.fast else ("enrich" if enrich else "normal"),
        "limit": args.limit,
        "seconds": round(time.time() - started, 1),
        "ok": sum(1 for v in report.values() if v["ok"]),
        "failed": sum(1 for v in report.values() if not v["ok"]),
        "sources": sorted(report.values(), key=lambda v: (-(v.get("new") or 0), v["name"])),
        "new": total_new,
        "total": len(items),
        "biliNew": bili_new,
    }
    hist = ([run] + hist)[:40]
    rp.write_text(json.dumps({"latest": run, "history": hist}, ensure_ascii=False, indent=1),
                  encoding="utf-8")
    print(f"\n完成：新增 {total_new} 条，总计 {len(items)} 条 → {common.DATA_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())