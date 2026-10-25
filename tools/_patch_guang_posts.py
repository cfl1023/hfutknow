# -*- coding: utf-8 -*-
"""guang.py 增加帖子流：forumTopic/pageQuery → 站点条目。"""
from pathlib import Path

p = Path("pipeline/guang.py")
s = p.read_text(encoding="utf-8")

old = '''def fetch_items() -> list[dict[str, Any]]:
    if not _due() or not CRED.exists():
        return []
    try:
        op = _opener()
        tk = _token(op)
        acts = _get(op, tk, "/community/ekActivity/list?pageNo=1&pageSize=50").get("result") or {}
    except Exception as exc:
        print(f"  × 逛逛/活动: {exc}")
        return []'''
new = '''COL_CAT = {
    "搭子": "recruitment", "保研": "academics", "考研": "academics", "学习": "academics",
    "心理": "life", "绿洲": "life", "失物": "life", "闲置": "life", "表白": "campus",
    "吐槽": "campus", "摄影": "arts", "运动": "arts", "竞赛": "skills", "科创": "skills",
}


def _cat_of(col: str, title: str) -> str:
    hay = (col or "") + (title or "")
    for k, v in COL_CAT.items():
        if k in hay:
            return v
    return "campus"


def fetch_items() -> list[dict[str, Any]]:
    if not _due() or not CRED.exists():
        return []
    try:
        op = _opener()
        tk = _token(op)
        acts = _get(op, tk, "/community/ekActivity/list?pageNo=1&pageSize=50").get("result") or {}
    except Exception as exc:
        print(f"  × 逛逛/活动: {exc}")
        acts = {}
    try:
        topics = _get(op, tk, "/community/forumTopic/pageQuery?pageNo=1&pageSize=100").get("result") or {}
    except Exception as exc:
        print(f"  × 逛逛/帖子: {exc}")
        topics = {}'''
assert old in s
s = s.replace(old, new, 1)

old2 = '''    STATE.write_text(json.dumps({"lastFetch": datetime.now().isoformat(timespec="minutes")}),
                     encoding="utf-8")
    print(f"  ✓ 逛逛/活动: {len(items)} 条")
    return items'''
new2 = '''    for t in topics.get("records") or []:
        title = (t.get("title") or "").strip()
        if not title:
            continue
        col = (t.get("columnName") or "").strip()
        created = (t.get("createTime") or "").replace(" ", "T")[:16]
        summary = f"版块「{col}」｜浏览 {t.get('views') or 0} · 点赞 {t.get('likeNum') or 0} · 评论 {t.get('commentNum') or 0}"
        items.append({
            "id": "gg-" + str(t.get("id")),
            "title": title[:100],
            "sourceId": "gg-forum",
            "sourceName": f"逛逛 · {col[:12]}" if col else "逛逛 · 斛兵塘",
            "sourceType": "gg",
            "url": "https://community.hfut.edu.cn/",
            "publishedAt": created or datetime.now().isoformat(timespec="minutes"),
            "dateEstimated": not bool(created),
            "intent": "information",
            "category": _cat_of(col, title),
            "summary": summary,
            "event": None,
            "requiresSignup": bool(re.search(r"组队|招募|招新", title)),
            "tags": [col] if col else [],
            "competition": None,
            "content": [f"<p>{summary}</p>"],
            "demo": False,
        })
    STATE.write_text(json.dumps({"lastFetch": datetime.now().isoformat(timespec="minutes")}),
                     encoding="utf-8")
    print(f"  ✓ 逛逛: 活动+帖子共 {len(items)} 条")
    return items'''
assert old2 in s
s = s.replace(old2, new2, 1)
p.write_text(s, encoding="utf-8")
import ast
ast.parse(s)
print("guang patched")
