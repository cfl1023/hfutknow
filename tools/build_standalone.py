# -*- coding: utf-8 -*-
"""打包成单个 HTML 文件：双击即可打开，不需要服务器。

输出：dist/工大知道.html
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OUT = ROOT / "dist"


def main() -> None:
    html = (SITE / "index.html").read_text(encoding="utf-8")
    css = (SITE / "style.css").read_text(encoding="utf-8")
    js = (SITE / "app.js").read_text(encoding="utf-8")
    items = json.loads((SITE / "data" / "items.json").read_text(encoding="utf-8"))
    sources = json.loads((SITE / "data" / "sources.json").read_text(encoding="utf-8"))
    people_path = SITE / "data" / "people.json"
    people = json.loads(people_path.read_text(encoding="utf-8")) if people_path.exists() else None
    plans_path = SITE / "data" / "plans.json"
    plans = json.loads(plans_path.read_text(encoding="utf-8")) if plans_path.exists() else None
    comp_path = SITE / "data" / "competitions.json"
    comps = json.loads(comp_path.read_text(encoding="utf-8")) if comp_path.exists() else None
    crawl_path = SITE / "data" / "crawl_report.json"
    crawl = json.loads(crawl_path.read_text(encoding="utf-8")).get("latest") if crawl_path.exists() else None

    html = html.replace('<link rel="stylesheet" href="style.css">', f"<style>\n{css}\n</style>")
    html = html.replace('<link rel="manifest" href="manifest.webmanifest">\n', "")
    html = html.replace('<link rel="icon" href="assets/icon.svg" type="image/svg+xml">\n', "")

    data_js = (
        "<script>window.__CK_DATA__="
        + json.dumps({"items": items, "sources": sources, "people": people, "plans": plans, "competitions": comps, "crawl": crawl}, ensure_ascii=False, separators=(",", ":"))
        + ";</script>\n"
    )
    html = html.replace('<script src="app.js"></script>', data_js + f"<script>\n{js}\n</script>")

    OUT.mkdir(parents=True, exist_ok=True)
    target = OUT / "工大知道.html"
    target.write_text(html, encoding="utf-8")
    # 方便直接双击：工作区根目录 + 桌面 + 下载
    import os
    home = os.path.expanduser("~")
    outs = [ROOT.parent / "工大知道.html",
            Path(home) / "Desktop" / "工大知道.html",
            Path(home) / "Downloads" / "工大知道.html"]
    for dst in outs:
        try:
            if dst.parent.is_dir():
                dst.write_bytes(target.read_bytes())
        except OSError as exc:
            print(f"跳过 {dst}: {exc}")
    print(f"{target}  ({target.stat().st_size / 1024 / 1024:.1f} MB, {len(items['items'])} 条)")
    print("已复制到 " + ", ".join(str(d) for d in outs))


if __name__ == "__main__":
    main()
