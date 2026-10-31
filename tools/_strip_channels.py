# -*- coding: utf-8 -*-
"""按用户要求撤下贴吧/逛逛/B站/互联网搜索：站点只保留官网 + 公众号。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC = ROOT / "pipeline" / "sync.py"
APP = ROOT / "site" / "app.js"
HTML = ROOT / "site" / "index.html"
LUP = ROOT / "tools" / "local_update.ps1"


def rw(p, fn):
    s = p.read_text(encoding="utf-8")
    n = fn(s)
    if n == s:
        print(f"!! no change: {p.name}")
    p.write_text(n, encoding="utf-8")
    print(f"ok {p.name}")


# ---------- sync.py ----------
def sync_fn(s):
    s = s.replace(
        "from . import bili, classify, common, competitions, fetchers, guang, summarize, websearch",
        "from . import classify, common, competitions, fetchers, summarize",
    )
    start = s.index("    # B 站：真人学生视频")
    end = s.index("    items.sort(key=lambda x: x.get(\"publishedAt\", \"\"), reverse=True)")
    s = s[:start] + "    # 只保留官网 + 公众号：贴吧 / 逛逛 / B站 / 互联网搜索已按用户要求撤下\n\n" + s[end:]
    start = s.index("    if counts.get(\"gg-activity\"):")
    end = s.index("    if args.dry_run:")
    s = s[:start] + s[end:]
    s = s.replace("        \"biliNew\": bili_new,\n", "")
    return s


# ---------- app.js ----------
def app_fn(s):
    s = s.replace(": head === 'competitions' ? 'competitions' : head === 'guang' ? 'guang' : head === 'prefs' ? 'prefs'",
                  ": head === 'competitions' ? 'competitions' : head === 'prefs' ? 'prefs'")
    s = s.replace("    else if (path === 'bili') renderBrowse({ bili: true });\n", "")
    s = s.replace("        else if (path === 'guang') renderGuang(params.get('g') || '');\n", "")
    # B站 chip
    s = re.sub(r"    const nb = S\.items\.filter\(\(i\) => i\.sourceType === 'bili'\)\.length;\n"
               r"    if \(nb\) out \+= `<a class=\"chip chip-bili[^\n]*\n", "", s)
    # typeLabel
    s = s.replace("return type === 'wechat' ? L.wechat : type === 'bili' ? 'B站' : L.official;",
                  "return type === 'wechat' ? L.wechat : L.official;")
    # ggBadges
    start = s.index("  function ggBadges(item) {")
    end = s.index("  function cardHTML(item) {")
    s = s[:start] + s[end:]
    s = s.replace("        ${ggBadges(item)}\n", "")
    # 逛逛整块
    start = s.index("  const GG_ORDER = [")
    end = s.index("  function renderSources() {")
    s = s[:start] + s[end:]
    # quick link
    s = s.replace('<a href="#/guang">👥 逛逛</a>', "")
    return s


# ---------- index.html ----------
def html_fn(s):
    s = re.sub(r'\n *<a href="#/guang" data-nav="guang">逛逛</a>', "", s)
    s = re.sub(r'\n *<a href="#/guang" data-tab="guang">.*?</a>', "", s, flags=re.S)
    return s


# ---------- local_update.ps1 ----------
def lup_fn(s):
    return re.sub(r"\n *& \$py tools/ingest_corpus\.py \*>> \$log", "", s)


rw(SYNC, sync_fn)
rw(APP, app_fn)
rw(HTML, html_fn)
rw(LUP, lup_fn)

# ---------- 数据清理 ----------
KEEP = {"official", "wechat"}
items_p = ROOT / "site" / "data" / "items.json"
data = json.loads(items_p.read_text(encoding="utf-8"))
before = len(data["items"])
data["items"] = [i for i in data["items"] if i.get("sourceType") in KEEP]
items_p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"items {before} -> {len(data['items'])}")

src_p = ROOT / "site" / "data" / "sources.json"
srcs = json.loads(src_p.read_text(encoding="utf-8"))
lst = srcs if isinstance(srcs, list) else srcs.get("sources", [])
kept = [s for s in lst if s.get("type") in KEEP]
src_p.write_text(json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"sources {len(lst)} -> {len(kept)}")

for f in ["_guang_detail_cache.json", "guang_state.json", "web_state.json", "bili_state.json",
          "junk_urls.txt"]:
    p = ROOT / "site" / "data" / f
    if p.exists():
        p.unlink()
        print("rm", f)
