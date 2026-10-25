/* ============ 工大知道 · 讨论区（统一信息流） ============ */
(() => {
  'use strict';

  const S = {
    cat: 'all',
    sort: 'smart',
    win: 0,
    q: '',
    only: false,
    limit: 60,
    tieba: null,
    bili: null,
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
  async function loadAll() {
    const get = async (file, src) => {
      const r = await fetch(file, { cache: 'no-store' });
      const j = await r.json();
      S.meta = S.meta || j.meta;
      return j.items.map((i) => Object.assign(i, { src }));
    };
    const [t, b] = await Promise.all([
      get('data/forum-tieba.json', 'tieba'),
      get('data/forum-bili.json', 'bili'),
    ]);
    S.tieba = t;
    S.bili = b;
  }
  const all = () => (S.tieba || []).concat(S.bili || []);

  const HFUT_RE = /合工大|合肥工业|工业大学|工大|宣城校区|翡翠湖校区|斛兵塘|屯溪路|六安路/;
  const BILI_RE = /合肥|合工大|工大|工业大学|安徽|宣城校区|翡翠湖/;
  const isHfut = (i) => HFUT_RE.test(`${i.t || ''} ${i.src === 'bili' ? '' : (i.b || '')}`);

  const heat = (i) => Math.log10(1 + (i.src === 'bili' ? (i.p || 0) : (i.r || 0))) * 4;
  const relScore = (i) => (i.s || 0) + heat(i);
  // 时效性是第一位的：先按时间分桶，桶内再按重要性（个人加权 + 讨论热度）排
  const bucket = (i) => {
    const t = new Date(i.at || 0).getTime();
    if (!t) return 9;
    const d = (Date.now() - t) / 86400000;
    return d < 1 ? 0 : d < 3 ? 1 : d < 7 ? 2 : d < 30 ? 3 : d < 90 ? 4 : d < 365 ? 5 : 6;
  };

  function list() {
    // B 站搜索接口按关键词召回，标题常常跟合肥/工大无关；只留标题里真的点到地名的
    let arr = all().filter((i) => i.src !== 'bili' || BILI_RE.test(i.t || ''));
    if (S.cat !== 'all') arr = arr.filter((i) => i.cat === S.cat);
    if (S.only) arr = arr.filter(isHfut);
    if (S.win) {
      const cut = Date.now() - S.win * 86400000;
      arr = arr.filter((i) => new Date(i.at || 0).getTime() >= cut);
    }
    if (S.q) {
      const q = S.q.toLowerCase();
      arr = arr.filter((i) => `${i.t} ${i.a} ${i.b || i.kw || ''}`.toLowerCase().includes(q));
    }
    const copy = arr.slice();
    const byDate = (a, b) => String(b.at || '').localeCompare(String(a.at || ''));
    if (S.sort === 'new') copy.sort(byDate);
    else if (S.sort === 'hot') copy.sort((a, b) => (b.src === 'bili' ? b.p || 0 : b.r || 0) - (a.src === 'bili' ? a.p || 0 : a.r || 0));
    else copy.sort((a, b) => bucket(a) - bucket(b) || relScore(b) - relScore(a) || byDate(a, b));
    return copy;
  }

  /* ---------------- 渲染 ---------------- */
  function heroHTML() {
    const items = all();
    const day = items.filter((i) => Date.now() - new Date(i.at || 0).getTime() < 86400000).length;
    const week = items.filter((i) => Date.now() - new Date(i.at || 0).getTime() < 7 * 86400000).length;
    return `<section class="forum-hero">
      <h1>别人替你先踩过的坑，都在这<span class="hl">，${fmtNum(items.length)} 条</span></h1>
      <p>贴吧求问、B 站校园视频、合肥本地的碎消息，全部混在一条时间线上。默认按时间新到旧，刷就行。</p>
      <div class="stats">
        <div class="stat"><b>${fmtNum(day)}</b><span>24 小时内</span></div>
        <div class="stat"><b>${fmtNum(week)}</b><span>最近 7 天</span></div>
        <div class="stat"><b>${fmtNum(items.length)}</b><span>全部</span></div>
      </div>
    </section>`;
  }

  function chips() {
    const items = all();
    const cats = (S.meta && S.meta.cats) || [['all', '全部']];
    const counts = {};
    for (const i of items) counts[i.cat] = (counts[i.cat] || 0) + 1;
    const rows = cats.filter(([id]) => id === 'all' || counts[id]);
    chipsEl.innerHTML = rows.map(([id, name]) => (
      `<button class="chip ${S.cat === id ? 'active' : ''}" data-cat="${id}">${esc(name)}<span class="n">${id === 'all' ? items.length : counts[id] || 0}</span></button>`
    )).join('');
  }

  function pickHTML() {
    const day = all().filter((i) => Date.now() - new Date(i.at || 0).getTime() < 86400000)
      .sort((a, b) => relScore(b) - relScore(a)).slice(0, 8);
    if (!day.length) return '';
    return `<section class="pick">
      <h2>24 小时内冒出来的 ${day.length} 条</h2>
      <p class="hint">新帖子先看这些，不用往下翻。</p>
      <ol>${day.map((i) => `<li><a href="${esc(i.u)}" target="_blank" rel="noopener">${esc(i.t)}</a><span class="m">${i.src === 'bili' ? 'B站' : esc(i.b || '贴吧')} · ${rel(i.at)}</span></li>`).join('')}</ol>
    </section>`;
  }

  function toolbarHTML(total) {
    const opt = (k, label) => `<button data-sort="${k}" class="${S.sort === k ? 'active' : ''}">${label}</button>`;
    const win = (k, label) => `<button data-win="${k}" class="${S.win === k ? 'active' : ''}">${label}</button>`;
    return `<div class="toolbar">
      <span class="count">${total} 条</span>
      <button class="chip ${S.only ? 'active' : ''}" data-only="1" title="只保留标题里出现「合工大 / 合肥工业 / 宣城校区 / 翡翠湖校区」的">只看合工大</button>
      <div class="spacer"></div>
      <div class="seg" id="segWin">${win(0, '全部时间')}${win(1, '24h')}${win(7, '7天')}${win(30, '30天')}</div>
      <div class="seg" id="segSort">${opt('smart', '时效优先')}${opt('new', '纯最新')}${opt('hot', '最热')}</div>
    </div>`;
  }

  function cardHTML(it) {
    const meta = it.src === 'bili'
      ? `${esc(it.a || '未知 UP')} · ${fmtNum(it.p || 0)} 播放 · ${rel(it.at)}`
      : `${esc(it.b || '贴吧')} · ${esc(it.a || '匿名')} · ${it.r || 0} 回复 · ${rel(it.at)}`;
    const catName = ((S.meta && S.meta.cats) || []).find(([id]) => id === it.cat);
    const hit = (it.s || 0) >= 12;
    const src = it.src === 'bili' ? '<span class="badge-src">B站</span>' : '<span class="badge-src">贴吧</span>';
    return `<a class="card" href="${esc(it.u)}" target="_blank" rel="noopener" style="--cat:var(--accent)">
      <div class="card-tags">${src}${hit ? '<span class="badge-related badge-hit">★ 与你相关</span>' : ''}</div>
      <h3>${esc(it.t)}</h3>
      <p class="meta2">${meta}</p>
      <div class="card-foot"><span class="srcname">${esc(catName ? catName[1] : '')}</span><span class="dot"></span><span>${it.at ? fmtDate(it.at) : '日期未知'}</span></div>
    </a>`;
  }

  function render() {
    const rows = list();
    const shown = rows.slice(0, S.limit);
    const sortName = { smart: '时效优先', new: '纯最新', hot: '最热' }[S.sort];
    app.innerHTML = `${heroHTML()}
      <div class="q-bar">
        <input id="q" type="search" placeholder="搜标题、作者、吧名、UP 主…" value="${esc(S.q)}" aria-label="搜索">
      </div>
      ${pickHTML()}
      ${toolbarHTML(rows.length)}
      ${shown.length ? `<div class="grid">${shown.map(cardHTML).join('')}</div>` : '<div class="empty"><b>这段时间里没有匹配的内容</b>把时间窗口放宽或换个关键词</div>'}
      ${rows.length > shown.length ? `<div class="more"><button class="btn ghost" id="moreBtn">加载更多（还有 ${rows.length - shown.length} 条）</button></div>` : ''}
      <p class="note">贴吧主题列表与 B 站搜索接口的公开数据，混排成一个流。抓取时间 ${S.meta ? new Date(S.meta.generatedAt).toLocaleString('zh-CN') : '—'}，链接都指回原文。</p>`;
    chips();
    $('#footMeta').textContent = `${rows.length} 条 · ${sortName}${S.win ? ` · 最近 ${S.win} 天` : ''}${S.only ? ' · 只看合工大' : ''}`;
  }

  /* ---------------- 交互 ---------------- */
  app.addEventListener('click', (e) => {
    const s = e.target.closest('[data-sort]');
    if (s) { S.sort = s.dataset.sort; S.limit = 60; render(); return; }
    const w = e.target.closest('[data-win]');
    if (w) { S.win = Number(w.dataset.win) || 0; S.limit = 60; render(); return; }
    if (e.target.closest('[data-only]')) { S.only = !S.only; S.limit = 60; render(); return; }
    if (e.target.closest('#moreBtn')) { S.limit += 60; render(); return; }
  });
  chipsEl.addEventListener('click', (e) => {
    const c = e.target.closest('[data-cat]');
    if (!c) return;
    S.cat = c.dataset.cat; S.limit = 60; render();
  });
  app.addEventListener('input', (e) => {
    if (e.target.id !== 'q') return;
    S.q = e.target.value.trim();
    S.limit = 60;
    clearTimeout(S._t);
    S._t = setTimeout(() => {
      const pos = e.target.selectionStart;
      render();
      const q = $('#q');
      if (q) { q.focus(); q.setSelectionRange(pos, pos); }
    }, 180);
  });

  $('#themeBtn').addEventListener('click', () => {
    const next = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
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
    app.innerHTML = '<div class="empty"><b>正在读数据…</b></div>';
    await loadAll();
    render();
  })();
})();
