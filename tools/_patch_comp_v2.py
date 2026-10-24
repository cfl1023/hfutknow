# -*- coding: utf-8 -*-
"""竞赛页 v2：从「名单」升级为「赛事追踪」（报名状态/截止倒计时/校内通知/报名方式）。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "site" / "app.js"
s = p.read_text(encoding="utf-8")

old_start = s.index("  function renderCompetitions() {")
old_end = s.index("  function renderContribute() {")
new_fn = '''  function compStatus(c) {
    const tk = c.tracking || {};
    if (tk.status === 'open') {
      const d = tk.daysLeft;
      return { cls: 'open', text: d === 0 ? '今天截止' : `报名中 · 剩 ${d} 天` };
    }
    if (tk.status === 'closed') return { cls: 'closed', text: `已截止 ${esc(tk.deadline)}` };
    if (tk.status === 'notice') return { cls: 'notice', text: '校内已发通知' };
    return { cls: 'none', text: '校内暂无通知' };
  }

  function compCard(c) {
    const tk = c.tracking || {};
    const st = compStatus(c);
    const how = tk.how || {};
    const howBits = [how.email && `邮箱 ${how.email}`, how.phone && `电话 ${how.phone}`,
      how.qq && `QQ 群 ${how.qq}`].filter(Boolean).join(' · ');
    const notices = (tk.notices || []).slice(0, 3).map((n) =>
      `<a class="cp-n" href="#/i/${esc(n.id)}">${esc(n.title.length > 32 ? n.title.slice(0, 32) + '…' : n.title)}</a>`).join('');
    return `<article class="comp2 ${st.cls}${c.related ? ' rel' : ''}">
      <div class="cp-head"><span class="cp-name">${esc(c.name)}</span><span class="cp-st ${st.cls}">${st.text}</span></div>
      <div class="cp-meta">${esc(c.tier)}${c.level ? ' · ' + esc(c.level) : ''}${c.related ? ' · <b class="cp-rel">★ 集成电路相关</b>' : ''}${tk.deadline ? ` · 报名截止 <b>${esc(tk.deadline)}</b>` : ''}${tk.eventAt ? ` · 比赛 ${esc(tk.eventAt)}` : ''}</div>
      ${tk.snippet ? `<div class="cp-snip">通知原文：「${esc(tk.snippet)}」</div>` : ''}
      ${howBits ? `<div class="cp-how">报名 / 咨询：${howBits}</div>` : ''}
      ${notices ? `<div class="cp-notices">校内通知 ${notices}</div>` : ''}
    </article>`;
  }

  function renderCompetitions() {
    $('#chips').hidden = true;
    const L = t();
    const { params } = parseHash();
    const filter = params.get('f') || '';
    const comps = (S.competitions || []).slice();
    const tk = (c) => c.tracking || {};
    const open = comps.filter((c) => tk(c).status === 'open');
    const closed = comps.filter((c) => tk(c).status === 'closed');
    const related = comps.filter((c) => c.related);

    const noticeMap = new Map();
    comps.forEach((c) => (tk(c).notices || []).forEach((n) => {
      if (!noticeMap.has(n.id)) noticeMap.set(n.id, Object.assign({ compName: c.name }, n));
    }));
    const notices = [...noticeMap.values()].sort((a, b) => (b.date || '').localeCompare(a.date || ''));

    const fchips = [['', `全部 ${comps.length}`], ['open', `报名中 ${open.length}`],
      ['related', `与我相关 ${related.length}`], ['notice', '有校内通知']]
      .map(([k, label]) => `<button class="chip${filter === k ? ' on' : ''}" data-f="${k}">${label}</button>`).join('');

    const noticeHTML = notices.length ? `<section class="cp-block">
      <h2 class="cp-h2">校内竞赛通知 <span class="muted">${notices.length} 条</span></h2>
      <div class="notice-list">${notices.map((n) => `<a class="notice-row" href="#/i/${esc(n.id)}">
        <span class="nr-date">${esc((n.date || '').slice(5))}</span>
        <span class="nr-title">${esc(n.title)}</span>
        <span class="nr-comp">${esc(n.compName)}</span></a>`).join('')}</div></section>` : '';

    let main;
    if (filter) {
      const list = comps.filter((c) => filter === 'open' ? tk(c).status === 'open'
        : filter === 'related' ? c.related : (tk(c).notices || []).length);
      main = list.length ? `<div class="comp2-grid">${list.map(compCard).join('')}</div>`
        : `<div class="empty"><b>这一类暂时没有</b></div>`;
    } else {
      const openHTML = open.length ? `<section class="cp-block">
        <h2 class="cp-h2">⏰ 正在报名 <span class="muted">${open.length} 项 · 按截止日排序</span></h2>
        <div class="comp2-grid">${open.map(compCard).join('')}</div></section>` : '';
      const closedHTML = closed.length ? `<section class="cp-block">
        <h2 class="cp-h2">已截止 <span class="muted">${closed.length} 项，仅供参考时间节奏</span></h2>
        <div class="comp2-grid subtle">${closed.slice(0, 6).map(compCard).join('')}</div></section>` : '';
      const relHTML = related.length ? `<section class="cp-block">
        <h2 class="cp-h2">与你相关（集成电路 / 电子 / 程序）<span class="muted">${related.length} 项</span></h2>
        <div class="comp2-grid">${related.filter((c) => tk(c).status !== 'open').map(compCard).join('')}</div></section>` : '';
      const roster = ['三大赛', 'A类', 'B类'].map((tier) => {
        const list = comps.filter((c) => c.tier === tier);
        return list.length ? `<div class="roster-tier"><div class="grp-title">${esc(tier)} · ${list.length}</div>
          <div class="roster-chips">${list.map((c) => `<span class="roster-chip${c.related ? ' rel' : ''}">${esc(c.name)}</span>`).join('')}</div></div>` : '';
      }).join('');
      main = openHTML + closedHTML + noticeHTML + relHTML + `<details class="roster"><summary>完整赛事名单（教务处 2026 版，${comps.length} 项）</summary>${roster}</details>`;
    }

    document.title = '学科竞赛 · ' + (S.lang === 'en' ? S.site.enName : S.site.name);
    app().innerHTML = `<section class="src-head"><h1>学科竞赛</h1>
      <p>不只是名单：对上校内通知后自动算报名状态和截止倒计时。当前报名中 <b>${open.length}</b> 项，抓到校内通知 <b>${notices.length}</b> 条。</p>
      <div class="chip-row" id="compFilters"><button class="chip${filter ? '' : ' on'}" data-f="">全部</button>${fchips.split('</button>').slice(1).join('</button>')}</div>
      </section>${main}`;
    const row = $('#compFilters');
    if (row) row.addEventListener('click', (e) => {
      const b = e.target.closest('[data-f]');
      if (!b) return;
      const f = b.getAttribute('data-f');
      go(`/competitions${f ? '?f=' + f : ''}`);
    });
  }

'''
s = s[:old_start] + new_fn + s[old_end:]

# 首页加「正在报名」提示条
old_hero = """        <p class="quick-links">"""
new_hero = """        ${(() => {
          const opening = (S.competitions || []).filter((c) => c.tracking && c.tracking.status === 'open');
          if (!opening.length) return '';
          return `<p class="comp-strip">⏰ 正在报名：${opening.slice(0, 3).map((c) => `<a href="#/competitions">${esc(c.name)}<span>${c.tracking.daysLeft === 0 ? '今天截止' : c.tracking.daysLeft + ' 天后截止'}</span></a>`).join('')}</p>`;
        })()}
        <p class="quick-links">"""
assert old_hero in s
s = s.replace(old_hero, new_hero, 1)

p.write_text(s, encoding="utf-8")
print("app.js competitions v2 patched")
