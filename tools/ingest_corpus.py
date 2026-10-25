# -*- coding: utf-8 -*-
"""把 corpus（贴吧主题帖 + B站视频）灌进站点数据：互联网渠道的量。

用法：python tools/ingest_corpus.py
- 贴吧：近 30 天有回复的帖 → category 按关键词归类，sourceName「互联网 · 贴吧」
- B站：与合工大/合肥相关、近 90 天发布的视频（播放量>=200 或 校园相关）
- 幂等：按 tid/bvid 生成稳定 id，重复跑不会产生重复条目
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT.parent / "corpus"
ITEMS = ROOT / "site" / "data" / "items.json"

CAT_RULES = [
    ("lectures", ["讲座", "论坛", "报告", "讲堂", "公开课"]),
    ("recruitment", ["招新", "社团", "志愿者", "支教", "实践"]),
    ("skills", ["竞赛", "大赛", "挑战杯", "大创", "建模", "蓝桥", "电子设计"]),
    ("careers", ["秋招", "实习", "offer", "就业", "招聘", "选调"]),
    ("academics", ["选课", "绩点", "保研", "考研", "考试", "学分", "培养", "转专业", "推免"]),
    ("scholarships", ["奖学金", "助学金", "综测", "评优"]),
    ("life", ["食堂", "宿舍", "快递", "校车", "热水", "供暖", "外卖", "租房"]),
    ("services", ["校园卡", "报修", "网", "VPN", "办事", "盖章"]),
    ("exchange", ["交换", "留学", "访学", "出国"]),
    ("arts", ["演出", "音乐会", "电影", "展览", "运动会", "球赛", "晚会"]),
]


def classify(title: str) -> str:
    for cat, words in CAT_RULES:
        if any(w in title for w in words):
            return cat
    return "campus"


def intent_of(cat: str) -> str:
    return "activity" if cat in {"lectures", "recruitment", "skills", "careers",
                                 "exchange", "arts"} else "information"


def load_jsonl(name: str) -> list[dict]:
    p = CORPUS / name
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def tieba_items(days: int = 30) -> list[dict]:
    cutoff = datetime.now() - timedelta(days=days)
    out = []
    for r in load_jsonl("tieba_threads.jsonl"):
        if not r.get("tid"):
            continue
        # lastReplyAt 形态：null（老帖，不收）/ "09-19" / "2026-10-25" / "11小时前" / "38分钟前"
        lra = str(r.get("lastReplyAt") or "").strip()
        if not lra:
            continue
        m = re.match(r"(\d{4})-(\d{2})-(\d{2})", lra)
        recent = False
        if m:
            try:
                recent = datetime.strptime(m.group(0), "%Y-%m-%d") >= cutoff
            except ValueError:
                recent = False
        elif re.search(r"(分钟|小时)前$", lra):
            recent = True
        elif re.match(r"(\d{1,2})-(\d{1,2})$", lra):
            mo, dd = map(int, lra.split("-"))
            try:
                recent = datetime(datetime.now().year, mo, dd) >= cutoff
            except ValueError:
                recent = False
        if not recent:
            continue
        title = (r.get("title") or "").strip()
        if len(title) < 5:
            continue
        cat = classify(title)
        replies = r.get("replies")
        # 发布时间用「最近回复日期」，避免老帖全堆在今天
        pub_iso = datetime.now().isoformat(timespec="minutes")
        if m:
            pub_iso = m.group(0) + "T12:00"
        elif re.search(r"(分钟|小时)前$", lra):
            pass  # 保持 now
        elif re.match(r"(\d{1,2})-(\d{1,2})$", lra):
            mo, dd = map(int, str(lra).split("-"))
            try:
                dt_ = datetime(datetime.now().year, mo, dd, 12, 0)
                if dt_ > datetime.now():
                    dt_ = dt_.replace(year=dt_.year - 1)
                pub_iso = dt_.isoformat(timespec="minutes")
            except ValueError:
                pass
        out.append({
            "id": f"tb-{r['tid']}",
            "title": title[:100],
            "sourceId": f"tieba-{r.get('bar') or '合工大'}",
            "sourceName": f"贴吧 · {r.get('bar') or '合肥工业大学'}",
            "sourceType": "net",
            "url": f"https://tieba.baidu.com/p/{r['tid']}",
            "publishedAt": pub_iso,
            "dateEstimated": True,
            "intent": intent_of(cat),
            "category": cat,
            "summary": f"贴吧讨论（{replies or '?'} 回复）：{title[:80]}",
            "event": None,
            "requiresSignup": bool(re.search(r"报名|招募|招新", title)),
            "tags": ["贴吧"],
            "competition": None,
            "content": [f"<p>来自贴吧「{r.get('bar') or '合肥工业大学'}吧」的主题帖讨论。</p>"],
            "demo": False,
        })
    return out


def bili_items(days: int = 90, min_play: int = 300) -> list[dict]:
    cutoff = datetime.now() - timedelta(days=days)
    rel = re.compile(r"合肥工业|合工大|HFUT|斛兵|翡翠湖|宣城校区")
    out = []
    for r in load_jsonl("bili_videos.jsonl"):
        if not r.get("bvid"):
            continue
        try:
            pub = datetime.fromtimestamp(int(r.get("pubdate") or 0))
        except (TypeError, ValueError):
            continue
        if pub < cutoff:
            continue
        hay = f"{r.get('title','')} {r.get('tag','')} {r.get('desc','')}"
        if not rel.search(hay):
            continue
        if int(r.get("play") or 0) < min_play:
            continue
        title = (r.get("title") or "").strip()
        if len(title) < 5:
            continue
        cat = classify(title)
        out.append({
            "id": f"bl-{r['bvid']}",
            "title": title[:100],
            "sourceId": "bili-net",
            "sourceName": f"B站 · {r.get('author','')[:14]}",
            "sourceType": "net",
            "url": f"https://www.bilibili.com/video/{r['bvid']}",
            "publishedAt": pub.isoformat(timespec="minutes"),
            "dateEstimated": False,
            "intent": intent_of(cat),
            "category": cat,
            "summary": ((r.get("desc") or "").strip() or title)[:150],
            "event": None,
            "requiresSignup": False,
            "tags": ["B站"],
            "competition": None,
            "content": [f"<p>{(r.get('desc') or '').strip()[:600] or title}</p>"],
            "bili": {"author": r.get("author") or "", "play": int(r.get("play") or 0)},
            "demo": False,
        })
    return out


def main() -> None:
    payload = json.loads(ITEMS.read_text(encoding="utf-8"))
    items = payload["items"]
    known_ids = {i["id"] for i in items}
    known_urls = {i.get("url") for i in items}

    new = []
    for it in tieba_items() + bili_items():
        if it["id"] in known_ids or it["url"] in known_urls:
            continue
        known_ids.add(it["id"])
        known_urls.add(it["url"])
        new.append(it)

    items.extend(new)
    items.sort(key=lambda x: x.get("publishedAt", ""), reverse=True)
    payload["items"] = items
    payload["generatedAt"] = datetime.now().strftime("%Y-%m-%dT%H:%MZ")
    ITEMS.write_text(json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")

    from collections import Counter
    print("新增", len(new), "条 →", Counter(i['sourceName'].split(' · ')[0] for i in new))
    print("总计", len(items))


if __name__ == "__main__":
    main()
