# -*- coding: utf-8 -*-
"""抓取体检报告：每次 sync 都写 site/data/crawl_report.json，页面能显示每个源的状态与上次更新时间。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "pipeline" / "sync.py"
s = p.read_text(encoding="utf-8")

s = s.replace("""import argparse
from datetime import datetime""", """import argparse
import json
import time
from datetime import datetime""", 1)

# ---- fetch_one 返回错误与耗时 ----
old = """    def fetch_one(src: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            return fetchers.fetch_source(src, args.limit)
        except Exception as exc:
            print(f"  × {src['name']}: {exc}")
            return []"""
new = """    def fetch_one(src: dict[str, Any]):
        t0 = time.time()
        try:
            got = fetchers.fetch_source(src, args.limit)
            return got, None, round(time.time() - t0, 1)
        except Exception as exc:
            print(f"  × {src['name']}: {exc}")
            return [], str(exc)[:160], round(time.time() - t0, 1)"""
assert old in s
s = s.replace(old, new, 1)

old = """    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = {pool.submit(fetch_one, src): src for src in sources}
        fetched: list[tuple[dict, list[dict]]] = []
        for fut in as_completed(futures):
            src = futures[fut]
            fetched.append((src, fut.result()))
            print(f"  ✓ {src['name']}: 抓到 {len(fetched[-1][1])} 条")"""
new = """    started = time.time()
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
                print(f"  ✓ {src['name']}: 抓到 {len(got)} 条  ({sec}s)")"""
assert old in s
s = s.replace(old, new, 1)

# ---- 记录每个源新增多少 ----
old = """        total_new += kept
        if kept:
            print(f"  + {src['name']}: 新增 {kept} 条")"""
new = """        total_new += kept
        if src["id"] in report:
            report[src["id"]]["new"] = kept
        if kept:
            print(f"  + {src['name']}: 新增 {kept} 条")"""
assert old in s
s = s.replace(old, new, 1)

# ---- 写报告 ----
old = """    common.save_items(payload)
    common.save_sources(sources_out)"""
new = """    common.save_items(payload)
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
        "at": datetime.now().isoformat(timespec="minutes"),
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
                  encoding="utf-8")"""
assert old in s
s = s.replace(old, new, 1)

p.write_text(s, encoding="utf-8")
print("sync.py patched")
