# -*- coding: utf-8 -*-
"""从培养方案 PDF 里抽课程表。"""
from __future__ import annotations

import io
import re
import ssl
import urllib.request
from pathlib import Path
from urllib.parse import urljoin

from lxml import html as lh
from pypdf import PdfReader

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

PAGE = "https://wdzxy.hfut.edu.cn/2023/1226/c11467a300102/page.htm"


def get_bytes(u: str) -> bytes:
    req = urllib.request.Request(u, headers=UA)
    with urllib.request.urlopen(req, timeout=40, context=ctx) as r:
        return r.read()


def main() -> None:
    doc = lh.fromstring(get_bytes(PAGE).decode("utf-8", "ignore"))
    pdfs = [urljoin(PAGE, a.get("href")) for a in doc.xpath("//a[contains(@href,'.pdf')]")]
    print("pdfs:", pdfs[:2])
    if not pdfs:
        return
    raw = get_bytes(pdfs[0])
    print("bytes:", len(raw))
    reader = PdfReader(io.BytesIO(raw))
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    Path("_tmp_plan.txt").write_text(text, encoding="utf-8")
    print("pages:", len(reader.pages), "chars:", len(text))
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    hits = [ln for ln in lines if re.search(r"[A-Z]?\d{6,8}[A-Z]?\s+\S+", ln) and ("课" in ln or "学分" in ln)]
    print("candidate lines:", len(hits))
    for ln in hits[:15]:
        print("   ", ln[:80])


if __name__ == "__main__":
    main()
