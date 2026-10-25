# -*- coding: utf-8 -*-
"""探查逛逛（community.hfut.edu.cn）帖子版块分布，用于细化分类。"""
import sys, json
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pipeline import guang

def main():
    op = guang._opener()
    tk = guang._token(op)
    if not tk:
        print("no token")
        return
    allrows, total = [], None
    for p in range(1, 4):
        r = guang._get(op, tk, "/community/forumTopic/pageQuery?pageNo=%d&pageSize=100" % p)
        res = r.get("result") or {}
        total = res.get("total")
        recs = res.get("records") or []
        print("page%d total=%s rows=%s" % (p, total, len(recs)))
        allrows += recs
        if len(recs) < 100:
            break
    cols = Counter((x.get("columnName") or "（无版块）").strip() for x in allrows)
    print("distinct columns:", len(cols), "posts:", len(allrows))
    for c, n in cols.most_common():
        print("  %-16s %s" % (c, n))
    bycol = defaultdict(list)
    for x in allrows:
        bycol[(x.get("columnName") or "（无版块）").strip()].append(x)
    out = {}
    for c, rows in bycol.items():
        print("\n=== %s (%d) ===" % (c, len(rows)))
        for x in rows[:15]:
            print("   [%s] v=%-5s c=%-4s %s" % (x.get("createTime", "")[:10], x.get("views"), x.get("commentNum"), (x.get("title") or "")[:46]))
        out[c] = [{"id": x.get("id"), "title": x.get("title"), "createTime": x.get("createTime"),
                   "views": x.get("views"), "commentNum": x.get("commentNum"),
                   "likeNum": x.get("likeNum"), "columnName": x.get("columnName")} for x in rows]
    Path("tools/_guang_posts.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\nsaved tools/_guang_posts.json")

main()
