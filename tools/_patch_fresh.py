# -*- coding: utf-8 -*-
"""让「更新」这件事可见：相对时间自动走、24 小时新增计数、只在真有新数据时重绘。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "site" / "app.js"
s = p.read_text(encoding="utf-8")

# 1) i18n 新增两条
s = s.replace("  updated: '更新于',",
              "  updated: '更新于',\n  freshSync: '数据 {age}同步',\n  freshNew: '24 小时内新增 {n} 条',", 1)
s = s.replace("  updated: 'Updated',",
              "  updated: 'Updated',\n  freshSync: 'synced {age}',\n  freshNew: '{n} new in 24h',", 1)

# 2) 注入两个工具函数（放在 t() 之后）
anchor = "  /* ---------------- chrome ---------------- */"
helpers = """  /* ---------------- freshness ---------------- */
  function relAgeText(iso) {
    if (!iso) return '';
    const L = t();
    const m = Math.max(0, Math.round((Date.now() - new Date(iso).getTime()) / 60000));
    if (m < 1) return L.relNow;
    if (m < 60) return L.relMin.replace('{n}', m);
    const h = Math.floor(m / 60);
    if (h < 24) return L.relHour.replace('{n}', h);
    const d = Math.floor(h / 24);
    return d === 1 ? L.relDay : L.relDays.replace('{n}', d);
  }

  function newIn(hours) {
    const cut = Date.now() - hours * 36e5;
    return (S.items || []).filter((i) => i.publishedAt && new Date(i.publishedAt).getTime() >= cut).length;
  }

  function freshLineHTML() {
    const L = t();
    const age = `<b>${esc(relAgeText(S.generatedAt))}</b>`;
    const n = `<b>${newIn(24)}</b>`;
    return `<span>${L.freshSync.replace('{age}', age)}</span><span>${L.freshNew.replace('{n}', n)}</span>`
      + `<span>最新一条 ${esc(relAgeText((S.items[0] || {}).publishedAt || ''))}</span>`;
  }

  /* ---------------- chrome ---------------- */"""
assert anchor in s
s = s.replace(anchor, helpers, 1)

# 3) 首页 hero 相加一行活的“更新状态”
old_stats = """          <div class="stat"><b>${(S.generatedAt || '').slice(11, 16)}</b><span>${L.updated}</span></div>
        </div>"""
new_stats = """          <div class="stat"><b>${(S.generatedAt || '').slice(11, 16)}</b><span>${L.updated}</span></div>
        </div>
        <p class="fresh-line" data-fresh>${freshLineHTML()}</p>"""
assert old_stats in s
s = s.replace(old_stats, new_stats, 1)

# 4) refreshData 只在真变化时返回数量
old_ref = """  async function refreshData() {
    if (window.__CK_DATA__) return false;"""
new_ref = """  async function refreshData() {
    if (window.__CK_DATA__) return 0;"""
s = s.replace(old_ref, new_ref, 1)

old_body = """      if (!a.ok) return false;
      const payload = await a.json();
      const srcPayload = await b.json();
      S.items = payload.items || [];"""
new_body = """      if (!a.ok) return 0;
      const payload = await a.json();
      const srcPayload = await b.json();
      const prevGen = S.generatedAt;
      const prevLen = (S.items || []).length;
      S.items = payload.items || [];"""
s = s.replace(old_body, new_body, 1)

old_tail = """      applyLang();
      return true;
    } catch (e) {
      return false;
    }
  }"""
new_tail = """      applyLang();
      if (S.generatedAt === prevGen) return 0;
      return Math.max(1, S.items.length - prevLen);
    } catch (e) {
      return 0;
    }
  }"""
s = s.replace(old_tail, new_tail, 1)

# 5) 轮询：有新数据才重绘；另外每 30 秒走一下相对时间
s = s.replace("""      const updated = await refreshData();
      if (updated) {""",
              """      const updated = await refreshData();
      if (updated > 0) {""", 1)
s = s.replace("""      if (await refreshData()) route();""",
              """      if (await refreshData() > 0) route();""", 1)

s = s.replace("""    }, 60 * 1000);
  }""",
              """    }, 60 * 1000);
    // 相对时间（「12 分钟前」）自己往前走，不用刷新页面
    setInterval(() => {
      const el = document.querySelector('[data-fresh]');
      if (el && !window.__CK_DATA__) el.innerHTML = freshLineHTML();
    }, 30 * 1000);
  }""", 1)

p.write_text(s, encoding="utf-8")
print("app.js patched", len(s))

# 6) CSS
c = ROOT / "site" / "style.css"
cs = c.read_text(encoding="utf-8")
if ".fresh-line" not in cs:
    cs += """
/* ---------------------------------------------------------------- 更新状态 */
.fresh-line { display: flex; flex-wrap: wrap; gap: 14px; margin: 10px 0 0; font-size: 12.5px; color: var(--text-3); }
.fresh-line b { color: var(--text-1); font-weight: 600; }
.fresh-line span + span::before { content: '·'; margin-right: 12px; color: var(--line); }
@media (color-scheme: dark) { .fresh-line { color: var(--text-4); } }
"""
    c.write_text(cs, encoding="utf-8")
    print("style appended")
else:
    print("style already has .fresh-line")
