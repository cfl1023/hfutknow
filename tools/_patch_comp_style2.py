# -*- coding: utf-8 -*-
"""补竞赛页 v2 样式 + 把 build_tracking 接进 workflow 与 standalone。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

css = ROOT / "site" / "style.css"
s = css.read_text(encoding="utf-8")
if ".comp2 {" not in s:
    s += """
/* ---- 竞赛追踪 v2 ---- */
.comp-strip{margin:14px 0 4px;display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center;
  padding:10px 14px;border-radius:12px;background:var(--accent-soft);border:1px solid var(--line);
  font-size:14px;font-weight:600}
.comp-strip a{color:var(--fg);text-decoration:none;display:inline-flex;gap:8px;align-items:baseline}
.comp-strip a span{font-size:12px;font-weight:500;color:var(--accent);white-space:nowrap}
.cp-block{margin-top:30px}
.cp-h2{font-size:16px;font-weight:650;margin:0 0 12px;display:flex;gap:10px;align-items:baseline}
.cp-h2 .muted{font-size:12px;font-weight:500;color:var(--muted)}
.comp2-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}
.comp2-grid.subtle{opacity:.72}
.comp2{border:1px solid var(--line);border-radius:12px;padding:13px 15px;background:var(--card);
  display:flex;flex-direction:column;gap:7px}
.comp2.rel{border-color:color-mix(in oklab,var(--accent) 45%,var(--line))}
.cp-head{display:flex;gap:10px;justify-content:space-between;align-items:flex-start}
.cp-name{font-weight:600;font-size:15px;line-height:1.4}
.cp-st{flex:none;font-size:11.5px;font-weight:600;padding:2px 8px;border-radius:999px;white-space:nowrap;
  border:1px solid var(--line)}
.cp-st.open{background:#e8f6ec;color:#186e3a;border-color:#bfe3ca}
.cp-st.closed{background:var(--bg-alt);color:var(--muted)}
.cp-st.notice{background:var(--accent-soft);color:var(--accent);border-color:transparent}
.cp-st.none{background:transparent;color:var(--muted);border-style:dashed}
@media (prefers-color-scheme:dark){
  .cp-st.open{background:#12321f;color:#7fd6a2;border-color:#1e4a30}
}
.cp-meta{font-size:12.5px;color:var(--muted);line-height:1.5}
.cp-meta b{color:var(--fg);font-weight:600}
.cp-rel{color:var(--accent);font-weight:600}
.cp-snip{font-size:12.5px;line-height:1.6;color:var(--fg);background:var(--bg-alt);
  border-left:2px solid var(--line);padding:6px 10px;border-radius:0 6px 6px 0}
.cp-how{font-size:12.5px;color:var(--muted)}
.cp-notices{display:flex;flex-direction:column;gap:3px;font-size:12.5px}
.cp-n{color:var(--accent);text-decoration:none}
.cp-n:hover{text-decoration:underline}
.notice-list{display:flex;flex-direction:column;border:1px solid var(--line);border-radius:12px;overflow:hidden}
.notice-row{display:grid;grid-template-columns:52px 1fr auto;gap:12px;align-items:center;
  padding:11px 15px;text-decoration:none;color:var(--fg);border-bottom:1px solid var(--line)}
.notice-row:last-child{border-bottom:0}
.notice-row:hover{background:var(--bg-alt)}
.nr-date{font-size:12px;color:var(--muted);font-variant-numeric:tabular-nums}
.nr-title{font-size:14px;line-height:1.45}
.nr-comp{font-size:11.5px;color:var(--muted);white-space:nowrap;max-width:180px;overflow:hidden;text-overflow:ellipsis}
@media (max-width:640px){.notice-row{grid-template-columns:44px 1fr}.nr-comp{display:none}}
.roster{margin-top:30px;border:1px solid var(--line);border-radius:12px;padding:0 16px;background:var(--card)}
.roster summary{cursor:pointer;padding:14px 0;font-size:14px;font-weight:600;list-style:none}
.roster summary::-webkit-details-marker{display:none}
.roster summary:before{content:"▸ ";color:var(--muted)}
.roster[open] summary:before{content:"▾ "}
.roster-tier{padding:6px 0 14px}
.roster-chips{display:flex;flex-wrap:wrap;gap:6px}
.roster-chip{font-size:12px;padding:3px 9px;border-radius:999px;background:var(--bg-alt);
  color:var(--muted);border:1px solid transparent}
.roster-chip.rel{color:var(--accent);border-color:color-mix(in oklab,var(--accent) 35%,transparent);
  background:var(--accent-soft)}
"""
    css.write_text(s, encoding="utf-8")
    print("style v2 ok")

# workflow：sync 后跑 tracking
wf = ROOT / ".github" / "workflows" / "sync.yml"
w = wf.read_text(encoding="utf-8")
if "build_tracking" not in w:
    w = w.replace("python -m pipeline.sync",
                  "python -m pipeline.sync\n          python tools/build_tracking.py", 1)
    wf.write_text(w, encoding="utf-8")
    print("workflow patched")

# standalone：把 tracking 数据留在 competitions.json 里，无需改 build（已经整份嵌进去）
bs = ROOT / "tools" / "build_standalone.py"
b = bs.read_text(encoding="utf-8")
if "competitions" not in b:
    print("WARN standalone 未嵌 competitions，需手工检查")
else:
    print("standalone 已嵌 competitions")
