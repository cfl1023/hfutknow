# -*- coding: utf-8 -*-
"""逛逛/社区源：CAS 免登 → community token → 活动 + 斛兵塘帖子（按版块分类）。

凭据只从本机 ~/.hfutknow_creds.json 读取，绝不进仓库。
只在「本机更新」里跑（GitHub 上没有你的密码，也不该有）。
"""
from __future__ import annotations

import http.cookiejar
import json
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from . import common

CRED = Path.home() / ".hfutknow_creds.json"
STATE = common.DATA_DIR / "guang_state.json"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
SERVICE = "https://community.hfut.edu.cn/login"
API = "https://community.hfut.edu.cn/api"
MIN_INTERVAL_MIN = 30

MODULE_CAT = {
    "科技创新": "skills", "公益服务": "recruitment", "思想成长": "campus",
    "社会实践": "recruitment", "志愿精神": "recruitment", "工作技能": "skills",
    "文体活动": "arts", "讲座交流": "lectures", "创业实践": "careers",
}

# 帖子版块 → (分组 key, 分组名)。版块是学校二课堂/社区运营的话题栏目，
# 名字本身看不出主题，所以显式映射；未收录的按关键词兜底。
COL_GROUP = {
    "微言微语微成长": ("growth", "成长分享"),
    "综合素质拓展": ("skills", "综合素质"),
    "斛兵春色正喜人": ("scenery", "校园风光"),
    "校园采风": ("scenery", "校园风光"),
    "拾光而行  心灵绿洲": ("life", "生活随拍"),
    "学业发展强化": ("academics", "学风学业"),
    "传统文化探寻": ("culture", "传统文化"),
    "春晖言孝感恩": ("culture", "传统文化"),
    "明月相约、感恩团圆": ("culture", "传统文化"),
    "思想素质提升": ("ideology", "思想教育"),
    "国家网络安全宣传周": ("ideology", "思想教育"),
    "返乡社会实践": ("practice", "社会实践"),
    "寻找你的校园搭子": ("mate", "校园搭子"),
    "毕业季留言活动": ("memory", "校园记忆"),
    "2024级新生讨论": ("memory", "校园记忆"),
    "军训进行时": ("memory", "校园记忆"),
}
GROUP_ORDER = ["mate", "academics", "growth", "skills", "life", "scenery",
               "culture", "ideology", "practice", "memory"]
GROUP_CAT = {"mate": "recruitment", "academics": "academics", "growth": "campus",
             "skills": "skills", "life": "life", "scenery": "arts",
             "culture": "arts", "ideology": "campus", "practice": "campus",
             "memory": "campus"}
FALLBACK_GROUP = [
    (r"搭子|组队|找舍友|羽毛球|球友", ("mate", "校园搭子")),
    (r"保研|考研|推免|期末|复习|课程|考试|学习", ("academics", "学风学业")),
    (r"花|春|秋|雪|夕阳|晚霞|风景|校园", ("scenery", "校园风光")),
    (r"传统|年味|中秋|端午|春节", ("culture", "传统文化")),
    (r"实践|志愿|返乡", ("practice", "社会实践")),
    (r"毕业|新生|军训", ("memory", "校园记忆")),
]
SUB_RULES = [
    (r"组队|搭子|求组队|找舍友|招新|招募|队友", "组队"),
    (r"二手|闲置|求购|出售|收.{0,6}(自行车|书|电脑|车)", "二手"),
    (r"保研|考研|推免|夏令营|复试", "保研考研"),
    (r"实习|兼职|招聘|宣讲", "招聘"),
    (r"比赛|竞赛|大赛", "竞赛"),
    (r"求|请问|求助|有没有|怎么|学长学姐|有经验", "求助"),
]
SUB_CAT = {"组队": "recruitment", "二手": "life", "保研考研": "academics",
           "招聘": "careers", "竞赛": "skills"}
FEED_TAGS = {"组队", "二手", "保研考研", "招聘", "求助", "竞赛"}


def _opener():
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                     urllib.request.HTTPSHandler(context=ctx))
    op.addheaders = [("User-Agent", UA), ("Accept-Language", "zh-CN,zh;q=0.9")]
    return op


def _token(op) -> str:
    if not CRED.exists():
        raise RuntimeError("无凭据文件 ~/.hfutknow_creds.json")
    cred = json.loads(CRED.read_text(encoding="utf-8"))
    login_url = "https://cas.hfut.edu.cn/cas/login?service=" + urllib.parse.quote(SERVICE)
    html = op.open(login_url, timeout=20).read().decode("utf-8", "ignore")
    m = re.search(r'name="execution" value="([^"]+)"', html)
    if not m:
        raise RuntimeError("CAS 页面无 execution token")
    form = urllib.parse.urlencode({
        "username": cred["user"], "password": cred["pwd"],
        "execution": m.group(1), "_eventId": "submit", "submit": "登录",
    }).encode()
    req = urllib.request.Request(login_url, data=form, method="POST", headers={
        "Content-Type": "application/x-www-form-urlencoded", "Referer": login_url})
    r = op.open(req, timeout=25)
    t = re.search(r"[?&]ticket=([A-Za-z0-9\-]+)", r.geturl())
    if not t:
        raise RuntimeError("CAS 未发 ticket（可能密码变更或需人工验证）")
    vreq = urllib.request.Request(
        f"{API}/sys/cas/client/validateLogin?ticket={t.group(1)}&service={urllib.parse.quote(SERVICE)}",
        headers={"X-Requested-With": "XMLHttpRequest"})
    data = json.loads(op.open(vreq, timeout=20).read().decode("utf-8", "ignore"))
    tk = (data.get("result") or {}).get("token") or ""
    if not tk:
        raise RuntimeError("validateLogin 无 token: " + str(data.get("message")))
    return tk


def _due() -> bool:
    try:
        last = json.loads(STATE.read_text(encoding="utf-8")).get("lastFetch") or ""
        return datetime.now() - datetime.fromisoformat(last) > timedelta(minutes=MIN_INTERVAL_MIN)
    except Exception:
        return True


def _get(op, tk: str, path: str) -> dict:
    req = urllib.request.Request(API + path, headers={"X-Access-Token": tk,
                                                     "X-Requested-With": "XMLHttpRequest"})
    with op.open(req, timeout=20) as r:
        return json.loads(r.read(800000).decode("utf-8", "ignore"))


def _group_of(col: str) -> tuple[str, str]:
    if col in COL_GROUP:
        return COL_GROUP[col]
    for pat, g in FALLBACK_GROUP:
        if re.search(pat, col or ""):
            return g
    return ("growth", "成长分享")


def _subtags(title: str) -> list[str]:
    out = []
    for pat, tag in SUB_RULES:
        if re.search(pat, title or ""):
            out.append(tag)
    return out


def _cat_of(group_key: str, subs: list[str]) -> str:
    for s in subs:
        if s in SUB_CAT:
            return SUB_CAT[s]
    return GROUP_CAT.get(group_key, "campus")


def _items_from_topics(tk: str, op) -> list[dict[str, Any]]:
    seen, rows = set(), []
    for page in range(1, 4):
        try:
            res = (_get(op, tk, f"/community/forumTopic/pageQuery?pageNo={page}&pageSize=100")
                   .get("result") or {})
        except Exception as exc:
            print(f"  × 逛逛/帖子 第{page}页: {exc}")
            break
        recs = res.get("records") or []
        for r in recs:
            rid = str(r.get("id") or "")
            if rid and rid not in seen:
                seen.add(rid)
                rows.append(r)
        if len(recs) < 100:
            break
    now = datetime.now()
    items: list[dict[str, Any]] = []
    for t in rows:
        title = (t.get("title") or "").strip()
        if not title:
            continue
        col = (t.get("columnName") or "").strip()
        gkey, glabel = _group_of(col)
        subs = _subtags(title)
        created = (t.get("createTime") or "").replace(" ", "T")[:16]
        views = t.get("views") or 0
        comments = t.get("commentNum") or 0
        likes = t.get("likeNum") or 0
        age_ok = False
        try:
            age_ok = (now - datetime.fromisoformat(created)).days <= 400
        except Exception:
            age_ok = False
        feed = age_ok or bool(FEED_TAGS & set(subs)) or views >= 150 or comments >= 3
        summary = f"版块「{col or '斛兵塘'}」｜浏览 {views} · 评论 {comments} · 赞 {likes}"
        if subs:
            summary += "｜" + " · ".join(subs)
        items.append({
            "id": "gg-" + str(t.get("id")),
            "title": title[:100],
            "sourceId": "gg-forum",
            "sourceName": "逛逛 · " + glabel,
            "sourceType": "gg",
            "url": "https://community.hfut.edu.cn/",
            "publishedAt": created or now.isoformat(timespec="minutes"),
            "dateEstimated": not bool(created),
            "intent": "information",
            "category": _cat_of(gkey, subs),
            "summary": summary,
            "event": None,
            "requiresSignup": bool(re.search(r"组队|招募|招新", title)),
            "tags": [t for t in [col, glabel] if t] + subs,
            "competition": None,
            "community": {"col": col, "group": gkey, "label": glabel,
                          "views": views, "comments": comments, "likes": likes},
            "feed": feed,
            "content": [f"<p>{summary}</p>"],
            "demo": False,
        })
    return items


DETAIL_CACHE = common.DATA_DIR / "_guang_detail_cache.json"


def _load_cache() -> dict:
    try:
        return json.loads(DETAIL_CACHE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _fetch_detail(op, tk: str, pid: str) -> dict:
    r = _get(op, tk, "/community/forumTopic/getDetailsById?id=" + pid)
    res = r.get("result") or {}
    return {
        "c": (res.get("content") or "").strip(),
        "a": (res.get("displayName") or "").strip(),
        "d": (res.get("depart") or "").strip(),
        "cm": res.get("commentNum") or 0,
        "cs": [(c.get("content") or "").strip()[:120]
               for c in (res.get("commentList") or [])[:4] if (c.get("content") or "").strip()],
        "t": datetime.now().isoformat(timespec="minutes"),
    }


def enrich(items: list[dict[str, Any]], op, tk: str, max_new: int = 40) -> None:
    """补帖子正文/作者/学院。缓存到 data/_guang_detail_cache.json，避免每轮重复抓。"""
    cache = _load_cache()
    todo = [i for i in items
            if i.get("sourceId") == "gg-forum" and str(i.get("id", ""))[3:] not in cache]
    added = 0
    for it in todo[:max_new]:
        pid = str(it["id"])[3:]
        try:
            cache[pid] = _fetch_detail(op, tk, pid)
            added += 1
        except Exception as exc:
            print(f"  × 逛逛详情 {pid}: {exc}")
    if added:
        DETAIL_CACHE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    for it in items:
        if it.get("sourceId") != "gg-forum":
            continue
        d = cache.get(str(it.get("id", ""))[3:])
        if not d:
            continue
        if d.get("a") or d.get("d"):
            who = d.get("a") or ""
            if d.get("d"):
                who += (" · " if who else "") + d["d"]
            it["author"] = who
            it["summary"] = it.get("summary", "") + f"｜{who}"
        if d.get("c"):
            paras = [p.strip() for p in re.split(r"\n+", d["c"]) if p.strip()]
            it["content"] = [f"<p>{p}</p>" for p in paras[:8]]
            it["excerpt"] = d["c"][:110].replace("\n", " ")
            head = paras[0][:78] if paras else ""
            if head:
                it["summary"] = f"{head}｜{it.get('author','')} · 浏览 {(it.get('community') or {}).get('views', 0)} · 评论 {(it.get('community') or {}).get('comments', 0)}"
        if d.get("cs"):
            it["comments"] = d["cs"]
    if added:
        print(f"  ✓ 逛逛正文: 新增 {added} 条（缓存 {len(cache)}）")


def _loc(iso: str) -> str:
    """逛逛接口给的是北京时间（无时区），补 +08:00，免得前端当 UTC 再 +8。"""
    t = (iso or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", t):
        return t + "+08:00"
    return t


def _activity_item(a: dict) -> dict[str, Any] | None:
    name = (a.get("name") or "").strip()
    if not name:
        return None
    cat = MODULE_CAT.get(a.get("moduleName") or "", "campus")
    lec = _loc((a.get("lectureStartTime") or "").replace(" ", "T")[:16])
    begin = lec or _loc((a.get("beginTime") or "").replace(" ", "T")[:16])
    end = _loc((a.get("lectureEndTime") or a.get("endTime") or "").replace(" ", "T")[:16])
    close = (a.get("et") or a.get("mobileEndTime") or "").strip()
    venue = (a.get("theVenue") or "").strip()
    evt = {"start": begin or None, "end": end or None, "location": venue or None}
    bits = [a.get("moduleName") or "", "主办 " + (a.get("sponsor") or "?")]
    if a.get("form"):
        bits.append(str(a["form"]))
    if a.get("keynoteSpeaker"):
        bits.append("主讲 " + str(a["keynoteSpeaker"]))
    if a.get("peopleNum"):
        bits.append(f"限 {a['peopleNum']} 人")
    if a.get("applyNum"):
        bits.append(f"已报 {a['applyNum']}")
    if close:
        bits.append(f"报名截止 {close}")
    if venue:
        bits.append(venue)
    summary = "｜".join([b for b in bits if b])
    paras = [f"<p>{summary}</p>"]
    photo = (a.get("activePhoto") or "").strip()
    if photo.startswith("http"):
        paras.append(f'<p><img src="{photo}" alt="{name}" loading="lazy"></p>')
    return {
        "id": "gg-" + str(a.get("id")),
        "title": name[:100],
        "sourceId": "gg-activity",
        "sourceName": "逛逛 · 校园活动",
        "sourceType": "gg",
        "url": "https://community.hfut.edu.cn/",
        "publishedAt": begin or datetime.now().isoformat(timespec="minutes"),
        "dateEstimated": not bool(begin),
        "intent": "activity",
        "category": cat,
        "summary": summary,
        "event": evt if begin else None,
        "deadline": close or None,
        "speaker": (a.get("keynoteSpeaker") or "").strip() or None,
        "requiresSignup": True,
        "tags": [t for t in [a.get("moduleName"), a.get("campus_dictText"), a.get("form")] if t],
        "competition": None,
        "feed": True,
        "content": paras,
        "poster": photo or None,
        "demo": False,
    }


def fetch_items() -> list[dict[str, Any]]:
    if not _due() or not CRED.exists():
        return []
    op = _opener()
    tk = _token(op)
    items: list[dict[str, Any]] = []
    try:
        acts = _get(op, tk, "/community/ekActivity/list?pageNo=1&pageSize=50").get("result") or {}
    except Exception as exc:
        print(f"  × 逛逛/活动: {exc}")
        acts = {}
    for a in acts.get("records") or []:
        item = _activity_item(a)
        if item:
            items.append(item)
    items.extend(_items_from_topics(tk, op))
    try:
        enrich(items, op, tk, max_new=40)
    except Exception as exc:
        print(f"  × 逛逛正文: {exc}")
    STATE.write_text(json.dumps({"lastFetch": datetime.now().isoformat(timespec="minutes")}),
                     encoding="utf-8")
    print(f"  ✓ 逛逛: 活动+帖子共 {len(items)} 条")
    return items
