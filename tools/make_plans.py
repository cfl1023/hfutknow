# -*- coding: utf-8 -*-
"""抓取微电子学院的培养方案文档列表（标题 + 官方 PDF）。"""
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

LIST = "https://wdzxy.hfut.edu.cn/11467/list.htm"


def get(u: str) -> str:
    req = urllib.request.Request(u, headers=UA)
    with urllib.request.urlopen(req, timeout=30, context=ctx) as r:
        raw = r.read(600000)
    for enc in ("utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore")


def main() -> None:
    doc = lh.fromstring(get(LIST))
    plans = []
    for a in doc.xpath("//a[@href]"):
        title = " ".join(a.text_content().split())
        if "培养方案" not in title and "教学计划" not in title:
            continue
        url = urljoin(LIST, a.get("href"))
        if not url.endswith(".htm"):
            continue
        pdf = ""
        try:
            page = lh.fromstring(get(url))
            links = [urljoin(url, x.get("href")) for x in page.xpath("//a[contains(@href,'.pdf')]")]
            pdf = links[0] if links else ""
        except Exception:
            pass
        plans.append({"title": title, "url": url, "pdf": pdf,
                      "major": re.sub(r"20\d{2}版|专业培养方案|教学计划|（.*?）|\(.*?\)", "", title).strip()})
    seen, out = set(), []
    for p in plans:
        if p["title"] in seen:
            continue
        seen.add(p["title"])
        out.append(p)
    (DATA / "plans.json").write_text(json.dumps(
        {"generatedAt": datetime.now().isoformat(timespec="minutes"), "college": "微电子学院", "plans": out},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"plans={len(out)} with_pdf={sum(1 for p in out if p['pdf'])}")


if __name__ == "__main__":
    main()
