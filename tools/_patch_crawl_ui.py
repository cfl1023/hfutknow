# -*- coding: utf-8 -*-
"""把「抓取体检」搬上页面：首页页脚 + 来源页 + 单文件版内嵌。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------- app.js ----------
p = ROOT / "site" / "app.js"
s = p.read_text(encoding="utf-8")

s = s.replace("  freshNew: '24 小时内新增 {n} 条',",
              "  freshNew: '24 小时内新增 {n} 条',\n  crawlLine: '上次抓取 {age} · {ok}/{all} 源成功 · 本轮新增 {n} 条',\n  srcCrawl: '最近抓取 {age}：列表 {got} 条，新增 {n}',\n  srcErr: '上次抓取失败：{err}',", 1)
s = s.replace("  freshNew: '{n} new in 24h',",
              "  freshNew: '{n} new in 24h',\n  crawlLine: 'last crawl {age} · {ok}/{all} sources ok · +{n}',\n  srcCrawl: 'crawled {age}: {got} entries, +{n}',\n  srcErr: 'last crawl failed: {err}',", 1)

# 载入 crawl_report（失败不影响主流程）
old = """      S.generatedAt = payload.generatedAt || S.generatedAt;"""
new = """      S.generatedAt = payload.generatedAt || S.generatedAt;
      fetch('data/crawl_report.json?t=' + Date.now(), { cache: 'no-store' })
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => { if (d) { S.crawl = d.latest || null; syncCrawlLine(); } })
        .catch(() => {});"""
assert old in s
s = s.replace(old, new, 1)

# 页脚加一行抓取状态
old = """    $('#footMeta').innerHTML = S.items.length"""
new = """    syncCrawlLine();
    $('#footMeta').innerHTML = S.items.length"""
assert old in s
s = s.replace(old, new, 1)

# 工具函数
old = """  function freshLineHTML() {"""
new = """  function syncCrawlLine() {
    const el = $('#footCrawl');
    if (!el) return;
    const L = t();
    const c = S.crawl;
    if (!c) { el.textContent = ''; return; }
    el.textContent = L.crawlLine
      .replace('{age}', relAgeText(c.at))
      .replace('{ok}', c.ok).replace('{all}', c.ok + c.failed).replace('{n}', c.new);
  }

  function freshLineHTML() {"""
assert old in s
s = s.replace(old, new, 1)

# 来源页：显示该源上次抓取情况
old = """        <p>${s ? srcTypeName(s.type) : ''}</p></section>`;"""
new = """        <p>${s ? srcTypeName(s.type) : ''}</p>
        ${sourceCrawlHTML(sourceId)}</section>`;"""
assert old in s
s = s.replace(old, new, 1)

old = """  function renderSearch(q) { renderBrowse({ q }); }"""
new = """  function sourceCrawlHTML(id) {
    const L = t();
    const c = S.crawl && S.crawl.sources ? S.crawl.sources.find((x) => x.id === id) : null;
    if (!c) return '';
    if (!c.ok) return `<p class="src-crawl bad">${L.srcErr.replace('{err}', esc(c.err || ''))}</p>`;
    return `<p class="src-crawl">${L.srcCrawl.replace('{age}', relAgeText(S.crawl.at)).replace('{got}', c.got).replace('{n}', c.new || 0)}</p>`;
  }

  function renderSearch(q) { renderBrowse({ q }); }"""
assert old in s
s = s.replace(old, new, 1)

# 每 30 秒刷新相对时间时，顺手刷新页脚那行
s = s.replace("""      if (el && !window.__CK_DATA__) el.innerHTML = freshLineHTML();""",
              """      if (el && !window.__CK_DATA__) el.innerHTML = freshLineHTML();
      syncCrawlLine();""", 1)

p.write_text(s, encoding="utf-8")
print("app.js patched")

# ---------- style.css ----------
c = ROOT / "site" / "style.css"
cs = c.read_text(encoding="utf-8")
if ".src-crawl" not in cs:
    cs += """
.src-crawl { margin: 6px 0 0; font-size: 12.5px; color: var(--text-3); }
.src-crawl.bad { color: var(--accent); }
#footCrawl { margin-top: 6px; font-size: 12px; color: var(--text-4); }
"""
    c.write_text(cs, encoding="utf-8")
    print("style appended")

# ---------- index.html：页脚占位 ----------
h = ROOT / "site" / "index.html"
hs = h.read_text(encoding="utf-8")
if 'id="footCrawl"' not in hs:
    hs = hs.replace('<div class="foot-meta" id="footMeta"></div>',
                    '<div class="foot-meta" id="footMeta"></div>\n      <div id="footCrawl"></div>', 1)
    h.write_text(hs, encoding="utf-8")
    print("index.html patched")

# ---------- 单文件版内嵌 crawl_report ----------
b = ROOT / "tools" / "build_standalone.py"
bs = b.read_text(encoding="utf-8")
print("standalone has crawl:", "crawl_report" in bs)
