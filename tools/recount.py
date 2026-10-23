# -*- coding: utf-8 -*-
"""按当前 items.json 重算 sources.json 里的条数。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data"


def main() -> None:
    items = json.loads((DATA / "items.json").read_text(encoding="utf-8"))["items"]
    sources = json.loads((DATA / "sources.json").read_text(encoding="utf-8"))["sources"]
    counts: dict[str, int] = {}
    for it in items:
        counts[it["sourceId"]] = counts.get(it["sourceId"], 0) + 1
    for s in sources:
        s["count"] = counts.get(s["id"], 0)
    (DATA / "sources.json").write_text(
        json.dumps({"sources": sources}, ensure_ascii=False, indent=1), encoding="utf-8")
    filled = sum(1 for s in sources if s["count"])
    print(f"items={len(items)} sources_with_content={filled}/{len(sources)}")


if __name__ == "__main__":
    main()
