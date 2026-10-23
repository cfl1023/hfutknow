# -*- coding: utf-8 -*-
"""抓取集成电路学院师资名单，并读取每位老师主页的研究方向/主讲课程。"""
from __future__ import annotations

import json
import re
import ssl
import urllib.request
from datetime import datetime
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

BAD_VALUES = ("论文成果", "科研项目", "获奖信息", "教师风采", "返回", "首页", "招生", "人才培养",
              "科学研究", "党建工作", "学生工作", "版权所有", "资料下载", "联系方式")

FIELD_PATTERNS = {
    "research": [r"研究方向[:：]?\s*([^\n]{2,160})", r"研究领域[:：]?\s*([^\n]{2,160})"],
    "courses": [r"(?:主讲|讲授|教授)课程[:：]?\s*([^\n]{2,160})", r"课程名称[:：]?\s*([^\n]{2,120})"],
}


def get(url: str) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
        raw = r.read(900000)
    for enc in ("utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore")


def parse_list(url: str, kind: str) -> list[dict]:
    doc = lh.fromstring(get(url))
    out: list[dict] = []
    for group in doc.xpath("//div[contains(@class,'teacher-group')]"):
        titles = group.xpath(".//div[contains(@class,'teacher-group-title')]")
        title = " ".join(titles[0].text_content().split()) if titles else ""
        for a in group.xpath(".//ul[contains(@class,'teacher-name-list')]//a[@href]"):
            name = " ".join(a.text_content().split())
            if not name or len(name) > 12:
                continue
            out.append({"name": name, "title": title or kind, "college": COLLEGE["name"],
                        "collegeId": COLLEGE["id"], "url": urljoin(url, a.get("href"))})
    return out


def enrich(person: dict) -> None:
    try:
        html = get(person["url"].replace("http://", "https://"))
    except Exception:
        return
    doc = lh.fromstring(html)
    text = "\n".join(line.strip() for line in doc.xpath("//body")[0].text_content().split("\n") if line.strip())
    for key, pats in FIELD_PATTERNS.items():
        for pat in pats:
            m = re.search(pat, text)
            if m:
                val = " ".join(m.group(1).split())[:120]
                if 8 < len(val) < 120 and not any(bad in val for bad in BAD_VALUES):
                    person[key] = val
                    break
    if not person.get("research"):
        for kw in ("微电子", "集成电路", "半导体", "器件", "电路"):
            if kw in text:
                person["research"] = f"（主页关键词：{kw}）"
                break


def main() -> None:
    people: list[dict] = []
    seen: set[str] = set()
    for kind, url in PAGES.items():
        try:
            rows = parse_list(url, kind)
        except Exception as exc:
            print(f"{kind} 抓取失败：{exc}")
            continue
        for r in rows:
            if r["name"] in seen or "行政" in r["title"]:
                continue
            seen.add(r["name"])
            enrich(r)
            people.append(r)
        print(f"{kind}: {len(rows)}")

    payload = {
        "generatedAt": datetime.now().isoformat(timespec="minutes"),
        "college": COLLEGE,
        "people": people,
        "groups": ["教授", "副教授", "研究员", "副研究员", "讲师", "兼职"],
    }
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "people.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    got = sum(1 for p in people if p.get("research") or p.get("courses"))
    print(f"people={len(people)} 有研究方向/课程={got}")


if __name__ == "__main__":
    main()
