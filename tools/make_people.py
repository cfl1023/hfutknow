# -*- coding: utf-8 -*-
"""抓取师资名单：集成电路创新学院 + 微电子学院（电子科学与应用物理学院）。

输出 site/data/people.json：
    {"generatedAt", "colleges": [...], "people": [{name,title,college,collegeId,dept,url,research}]}
"""
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

BAD_VALUES = ("论文成果", "科研项目", "获奖信息", "教师风采", "返回", "首页", "招生", "人才培养",
              "科学研究", "党建工作", "学生工作", "版权所有", "资料下载", "联系方式", "栏目名称")

TITLE_RE = re.compile(r"职\s*称[:：]\s*(教授|副教授|特任教授|讲师|研究员|副研究员|高级工程师|工程师|助理研究员)")
DEPT_RE = re.compile(r"所属系[:：]\s*([^\s，。;；]{2,12})")
RESEARCH_FIELD_RE = re.compile(r"(?:研究方向|研究领域|科研方向|主要研究方向)[:：]\s*([^\n]{2,120})")

IC_COLLEGE = {"id": "ic", "name": "集成电路创新学院", "short": "集创院"}
IC_PAGES = {"全职": "https://ic.hfut.edu.cn/szll/qz1.htm",
            "兼职": "https://ic.hfut.edu.cn/szll/jz.htm"}
IC_FIELDS = {
    "research": [r"研究方向[:：]?\s*([^\n]{2,160})", r"研究领域[:：]?\s*([^\n]{2,160})"],
    "courses": [r"(?:主讲|讲授|教授)课程[:：]?\s*([^\n]{2,160})", r"课程名称[:：]?\s*([^\n]{2,120})"],
}

WDZ_COLLEGE = {"id": "wdz", "name": "微电子学院", "short": "微电子"}
WDZ_LIST = "https://wdzxy.hfut.edu.cn/11454/list.htm"
WDZ_SKIP_DEPT = ("院党政领导", "实验中心")


def get(url: str, limit: int = 900_000) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25, context=ctx) as r:
        raw = r.read(limit)
    for enc in ("utf-8", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore")


def body_text(html: str) -> str:
    doc = lh.fromstring(html)
    body = doc.xpath("//body")
    if not body:
        return ""
    return "\n".join(x.strip() for x in body[0].text_content().split("\n") if x.strip())


def parse_ic() -> list[dict]:
    out: list[dict] = []
    seen: set[str] = set()
    for kind, url in IC_PAGES.items():
        try:
            doc = lh.fromstring(get(url))
        except Exception as exc:
            print(f"  IC {kind} 列表失败：{exc}")
            continue
        for group in doc.xpath("//div[contains(@class,'teacher-group')]"):
            titles = group.xpath(".//div[contains(@class,'teacher-group-title')]")
            title = " ".join(titles[0].text_content().split()) if titles else ""
            for a in group.xpath(".//ul[contains(@class,'teacher-name-list')]//a[@href]"):
                name = " ".join(a.text_content().split())
                if not name or len(name) > 12 or name in seen:
                    continue
                seen.add(name)
                out.append({"name": name, "title": title or kind, "collegeId": "ic",
                            "college": IC_COLLEGE["name"], "dept": "",
                            "url": urljoin(url, a.get("href"))})
    for p in out:
        try:
            text = body_text(get(p["url"].replace("http://", "https://")))
        except Exception:
            continue
        m = TITLE_RE.search(text)
        if m:
            p["title"] = m.group(1)
        for key, pats in IC_FIELDS.items():
            for pat in pats:
                mm = re.search(pat, text)
                if mm:
                    val = " ".join(mm.group(1).split())[:120]
                    if 8 < len(val) < 120 and not any(bad in val for bad in BAD_VALUES):
                        p[key] = val
                        break
    return out


def parse_wdz() -> list[dict]:
    try:
        doc = lh.fromstring(get(WDZ_LIST))
    except Exception as exc:
        print(f"  微电子列表失败：{exc}")
        return []
    out: list[dict] = []
    for block in doc.xpath("//div[contains(@class,'minglu')]"):
        h2 = block.xpath(".//h2//a")
        dept = " ".join(h2[0].text_content().split()) if h2 else ""
        if any(s in dept for s in WDZ_SKIP_DEPT):
            continue
        for a in block.xpath(".//ul//li//a[@href]"):
            name = (a.get("title") or a.text_content() or "").strip()
            if not name or not re.fullmatch(r"[\u4e00-\u9fa5·]{2,6}", name):
                continue
            out.append({"name": name, "title": "", "collegeId": "wdz",
                        "college": WDZ_COLLEGE["name"], "dept": dept,
                        "url": urljoin(WDZ_LIST, a.get("href"))})
    print(f"  微电子名录：{len(out)} 人")
    return out


def enrich_wdz(p: dict) -> None:
    try:
        text = body_text(get(p["url"].replace("http://", "https://")))
    except Exception:
        return
    m = TITLE_RE.search(text)
    if m:
        p["title"] = m.group(1)
    if not p.get("dept"):
        m = DEPT_RE.search(text)
        if m:
            p["dept"] = m.group(1)
    m = RESEARCH_FIELD_RE.search(text)
    if m:
        p["research"] = " ".join(m.group(1).split())[:120]
    else:
        m = re.search(r"(?:主要)?(?:科研|研究)方向[为是]?\s*([^。；;]{4,80})", text)
        if m:
            p["research"] = " ".join(m.group(1).split())[:100]


def main() -> None:
    print("抓集成电路创新学院…")
    people = parse_ic()
    print(f"  {len(people)} 人")
    print("抓微电子学院…")
    wdz = parse_wdz()
    seen = {p["name"] for p in people}
    for p in wdz:
        if p["name"] in seen:
            continue
        seen.add(p["name"])
        enrich_wdz(p)
        people.append(p)

    for p in people:
        if not p.get("title"):
            p["title"] = "教师"
    order = {"教授": 0, "特任教授": 0, "研究员": 1, "副教授": 2, "副研究员": 2,
             "高级工程师": 3, "讲师": 4, "工程师": 4, "助理研究员": 4, "教师": 9}
    people.sort(key=lambda p: (p["collegeId"], order.get(p["title"], 8), p["name"]))

    payload = {
        "generatedAt": datetime.now().isoformat(timespec="minutes"),
        "colleges": [IC_COLLEGE, WDZ_COLLEGE],
        "groups": ["教授", "副教授", "研究员", "副研究员", "讲师", "其他"],
        "people": people,
    }
    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "people.json").write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
    from collections import Counter
    print("完成：", Counter(p["college"] for p in people))


if __name__ == "__main__":
    main()
