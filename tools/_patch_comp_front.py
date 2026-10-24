# -*- coding: utf-8 -*-
"""前端：竞赛消息打标（卡片 + 相关排序加分）。"""
from pathlib import Path

p = Path("site/app.js")
t = p.read_text(encoding="utf-8")

# relevance 里加竞赛加分（放在 scholarships 行后）
old_rel = "    if (item.category === 'lectures') score += 1;"
new_rel = ("    if (item.category === 'lectures') score += 1;\n"
           "    if (item.competition && item.competition.ic) score += 6;\n"
           "    else if (item.competition) score += 3;")
assert old_rel in t
t = t.replace(old_rel, new_rel)

# 卡片标签区加竞赛徽章
old_tags = "        ${rel ? `<span class=\"badge-related\">${t().related}</span>` : ''}"
new_tags = ("        ${rel ? `<span class=\"badge-related\">${t().related}</span>` : ''}\n"
            "        ${item.competition ? `<span class=\"badge-comp${item.competition.ic ? ' ic' : ''}\">${esc(item.competition.ic ? '★ ' + item.competition.name : item.competition.name)}</span>` : ''}")
assert old_tags in t
t = t.replace(old_tags, new_tags)

# 详情页 tags 行也加
old_dt = "        ${tags}"
new_dt = ("        ${tags}\n"
          "        ${item.competition ? `<span class=\"tag cat\" style=\"background:#3f7a5a1a;color:#3f7a5a\">竞赛：${esc(item.competition.name)}</span>` : ''}")
assert old_dt in t
t = t.replace(old_dt, new_dt)

p.write_text(t, encoding="utf-8")
print("patched app.js")
