/* ============ 工大知道 · 讨论区 ============ */
(() => {
  'use strict';

  const S = {
    tab: 'tieba',
    cat: 'all',
    sort: 'rel',
    q: '',
    limit: 48,
    data: { tieba: null, bili: null },
    meta: null,
  };

  const $ = (s, r = document) => r.querySelector(s);
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const app = $('#app');
  const chipsEl = $('#chips');

  /* ---------------- 时间 ---------------- */
  function rel(iso) {
    if (!iso) return '';
    const t = new Date(iso).getTime();
    if (!t) return '';
    const d = Date.now() - t;
    if (d < 0) return '刚刚';
    const m = d / 60000;
    if (m < 1) return '刚刚';
    if (m < 60) return `${Math.floor(m)} 分钟前`;
    if (m < 1440) return `${Math.floor(m / 60)} 小时前`;
    const days = Math.floor(m / 1440);
    if (days === 1) return '昨天';
    if (days < 30) return `${days} 天前`;
    if (days < 365) return `${Math.floor(days / 30)} 个月前`;
    return `${Math.floor(days / 365)} 年前`;
  }
  const fmtDate = (iso) => (iso ? new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }) : '');
  const fmtNum = (n) => (n >= 10000 ? `${(n / 10000).toFixed(1)} 万` : String(n));

  /* ---------------- 数据 ---------------- */
  async function load(tab) {
    if (S.data[tab]) return S.data[tab];
    const file = tab === 'bili' ? 'data/forum-bili.json' : 'data/forum-tieba.json';
    const r = await fetch(file, { cache: 'no-store' });
    const j = await r.json();
    S.meta = S.meta || j.meta;
    S.data[tab] = j.items;
    return j.items;
  }

  const heat = (it) => (S.tab === 'bili' ? Math.log10(1 + (it.p || 0)) * 6 : Math.log10(1 + (it.r || 0)) * 5);
  const relScore = (it) => (it.s || 0) + heat(it);

  function list() {
    const items = S.data[S.tab] || [];
    let arr = items;
    if (S.cat !== 'all') arr = arr.filter((i) => i.cat === S.cat);
    if (S.q) {
      const q = S.q.toLowerCase();
      arr = arr.filter((i) => (i.t + ' ' + i.a + ' ' + (i.b || i.kw || '')).toLowerCase().includes(q));
    }
    const copy = arr.slice();
    if (S.sort === 'new') copy.sort((a, b) => String(b.at || '').localeCompare(String(a.at || '')));
    else if (S.sort === 'hot') copy.sort((a, b) => (S.tab === 'bili' ? b.p - a.p : b.r - a.r));
    else copy.sort((a, b) => relScore(b) - relScore(a) || String(b.at || '').localeCompare(String(a.at || '')));
    return copy;
  }

  /* ---------------- 渲染 ---------------- */
  function heroHTML() {
    const tieba = S.data.tieba ? S.data.tieba.length : 0;
    const bili = S.data.bili ? S.data.bili.length : 0;
    return `<section class="forum-hero">
      <h1>别人替你先踩过的坑，都在这<span class="hl">${tieba + bili ? `，${fmtNum(tieba + bili)} 条` : ''}</span></h1>
      <p>贴吧的求助帖和 B 站的校园视频。按「集成电路 · 大一 · 翡翠湖」加权排序，不是按热度堆。</p>
      <div class="stats">
        <div class="stat"><b>${fmtNum(tieba)}</b><span>贴吧主题帖</span></div>
        <div class="stat"><b>${fmtNum(bili)}</b><span>B站视频</span></div>
        <div class="stat"><b>${S.meta ? fmtDate(S.meta.generatedAt) : '—'}</b><span>抓取时间</span></div>
      </div>
    </section>`;
  }

  function tabsHTML() {
    const n = (k) => (S.data[k] ? fmtNum(S.data[k].length) : '…');
    const b = (k, label) => `<button data-tab="${k}" class="${S.tab === k ? 'active' : ''}">${label}<span class="n">${n(k)}</span></button>`;
    return `<div class="tabrow">${b('tieba', '贴吧讨论')}${b('bili', 'B站视频')}</div>`;
  }

  function chips() {
    const items = S.data[S.tab] || [];
    const cats = (S.meta && S.meta.cats) || [['all', '全部']];
    const counts = {};
    for (const i of items) counts[i.cat] = (counts[i.cat] || 0) + 1;
    const list = cats.filter(([id]) => id === 'all' || counts[id]);
    chipsEl.innerHTML = list.map(([id, name]) => (
      `<button class="chip ${S.cat === id ? 'active' : ''}" data-cat="${id}">${esc(name)}<span class="n">${id === 'all' ? items.length : counts[id] || 0}</span></button>`
    )).join('');
  }

  function pickHTML() {
    const items = S.data[S.tab] || [];
    if (!items.length) return '';
    const top = items.slice().filter((i) => (i.s || 0) >= 8).sort((a, b) => relScore(b) - relScore(a)).slice(0, 12);
    if (!top.length) return '';
    return `<section class="pick">
      <h2>先看这 ${top.length} 条</h2>
      <p class="hint">标题里同时命中「集成电路 / 转专业 / 保研 / 新生」这类关键词的，优先给你。</p>
      <ol>${top.map((i) => `<li><a href="${esc(i.u)}" target="_blank" rel="noopener">${esc(i.t)}</a><span class="m">${esc(i.b || i.kw || '')} · ${S.tab === 'bili' ? `${fmtNum(i.p)} 播放` : `${i.r} 回复`} · ${rel(i.at)}</span></li>`).join('')}</ol>
    </section>`;
  }

  function toolbarHTML(total) {
    const opt = (k, label) => `<button data-sort="${k}" class="${S.sort === k ? 'active' : ''}">${label}</button>`;
    return `<div class="toolbar">
      <span class="count">${total} 条</span>
      <div class="spacer"></div>
      <div class="seg" id="segSort">${opt('rel', '与你相关')}${opt('new', '最新')}${opt('hot', '最热')}</div>
    </div>`;
  }

  function cardHTML(it) {
    const meta = S.tab === 'bili'
      ? `${esc(it.a || '未知 UP')} · ${fmtNum(it.p || 0)} 播放 · ${rel(it.at)}`
      : `${esc(it.b || '贴吧')} · ${esc(it.a || '匿名')} · ${it.r || 0} 回复 · ${rel(it.at)}`;
    const catName = ((S.meta && S.meta.cats) || []).find(([id]) => id === it.cat);
    const hit = (it.s || 0) >= 12;
    return `<a class="card" href="${esc(it.u)}" target="_blank" rel="noopener" style="--cat:var(--accent)">
      <div class="card-tags">${hit ? '<span class="badge-related badge-hit">★ 与你相关</span>' : ''}</div>
      <h3>${esc(it.t)}</h3>
      <p class="meta2">${meta}</p>
      <div class="card-foot"><span class="srcname">${esc(catName ? catName[1] : '')}</span><span class="dot"></span><span>${it.at ? fmtDate(it.at) : '日期未知'}</span></div>
    </a>`;
  }

  function render() {
    const all = list();
    const shown = all.slice(0, S.limit);
    app.innerHTML = `${heroHTML()}${tabsHTML()}
      <div class="q-bar">
        <input id="q" type="search" placeholder="搜标题、作者、吧名…" value="${esc(S.q)}" aria-label="搜索">
      </div>
      ${pickHTML()}
      ${toolbarHTML(all.length)}
      ${shown.length ? `<div class="grid">${shown.map(cardHTML).join('')}</div>` : '<div class="empty"><b>这里没有匹配的帖子</b>换个分类或关键词试试</div>'}
      ${all.length > shown.length ? `<div class="more"><button class="btn ghost" id="moreBtn">加载更多（还有 ${all.length - shown.length} 条）</button></div>` : ''}
      <p class="note">数据来自公开的贴吧主题列表与 B 站搜索接口，抓取时间为 ${S.meta ? new Date(S.meta.generatedAt).toLocaleString('zh-CN') : '—'}。链接都指回原文。</p>`;
    chips();
    $('#footMeta').textContent = `${all.length} 条 · 排序：${{ rel: '与你相关', new: '最新', hot: '最热' }[S.sort]}`;
  }

  /* ---------------- 交互 ---------------- */
  async function switchTab(tab) {
    if (S.tab === tab && S.data[tab]) return;
    S.tab = tab; S.cat = 'all'; S.limit = 48;
    app.innerHTML = '<div class="empty"><b>正在读数据…</b></div>';
    await load(tab);
    render();
  }

  app.addEventListener('click', async (e) => {
    const t = e.target.closest('[data-tab]');
    if (t) { await switchTab(t.dataset.tab); return; }
    const s = e.target.closest('[data-sort]');
    if (s) { S.sort = s.dataset.sort; S.limit = 48; render(); return; }
    const m = e.target.closest('#moreBtn');
    if (m) { S.limit += 48; render(); return; }
  });
  chipsEl.addEventListener('click', (e) => {
    const c = e.target.closest('[data-cat]');
    if (!c) return;
    S.cat = c.dataset.cat; S.limit = 48; render();
  });
  app.addEventListener('input', (e) => {
    if (e.target.id !== 'q') return;
    S.q = e.target.value.trim();
    S.limit = 48;
    clearTimeout(S._t);
    S._t = setTimeout(() => {
      const pos = e.target.selectionStart;
      render();
      const q = $('#q');
      if (q) { q.focus(); q.setSelectionRange(pos, pos); }
    }, 180);
  });

  $('#themeBtn').addEventListener('click', () => {
    const cur = document.documentElement.dataset.theme;
    const next = cur === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('ck-theme', next);
  });

  function initTheme() {
    const saved = localStorage.getItem('ck-theme');
    const dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.dataset.theme = saved || (dark ? 'dark' : 'light');
  }

  (async () => {
    initTheme();
    await load('tieba');
    render();
    load('bili').catch(() => {});
  })();
})();
