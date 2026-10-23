# -*- coding: utf-8 -*-
"""抓取集成电路学院师资名单，生成 site/data/people.json。"""
from __future__ import annotations

import json
import re
import ssl
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

from lxml import html as lh

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "site" / "data"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

COLLEGE = {"id": "ic", "name": "集成电路创新学院", "short": "集成电路"}
PAGES = {"全职": "https://ic.hfut.edu.cn/szll/qz1.htm",
         "兼职": "https://ic.hfut.edu.cn/szll/jz.htm"}


def get(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
        raw = r.read(800000)
    for enc in ("utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore")


def parse_page(url: str, kind: str) -> list[dict]:
    doc = lh.fromstring(get(url))
    out: list[dict] = []
    for group in doc.xpath("//div[contains(@class,'teacher-group')]"):
        titles = group.xpath(".//div[contains(@class,'teacher-group-title')]")
        title = " ".join(titles[0].text_content().split()) if titles else ""
        for a in group.xpath(".//ul[contains(@class,'teacher-name-list')]//a[@href]"):
            name = " ".join(a.text_content().split())
            if not name or len(name) > 12:
                continue
            out.append({
                "name": name,
                "title": title or kind,
                "college": COLLEGE["name"],
                "collegeId": COLLEGE["id"],
                "url": urljoin(url, a.get("href")),
                "kind": kind,
            })
    return out


def main() -> None:
    people: list[dict] = []
    seen: set[str] = set()
    for kind, url in PAGES.items():
        try:
            rows = parse_page(url, kind)
        except Exception as exc:
            print(f"{kind} 抓取失败：{exc}")
            continue
        for r in rows:
            if r["name"] in seen:
                continue
            seen.add(r["name"])
            people.append(r)
        print(f"{kind}: {len(rows)}")

    payload = {
        "generatedAt": __import__("datetime").datetime.now().isoformat(timespec="minutes"),
        "college": COLLEGE,
        "people": people,
        "groups": ["教授", "副教授", "讲师", "研究员", "副研究员", "兼职"],
    }
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "people.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"people={len(people)} -> {DATA / 'people.json'}")


if __name__ == "__main__":
    main()
