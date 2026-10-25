/* ============ 工大知道 · 首页「今天值得看的」 ============
   从讨论区两份数据里挑出「有效」的条目放到首页。
   有效 = 近 30 天内 + 个人加权（保研/转专业/选课/宿舍/就业…）或合工大相关，再按新旧和热度排。
   点过「已阅」的就从首页消失（记录和讨论区共用 localStorage 的 ck-read）。 */
(() => {
  'use strict';
  const BAND = document.getElementById('pickBand');
  if (!BAND) return;

  const READ_KEY = 'ck-read';
  const READ_KEY2 = 'ck-read-v1'; // 首页 app.js 那一套（两处记录合并读）
  const BILI_RE = /合肥|合工大|工大|工业大学|安徽|宣城校区/;
  const HFUT_RE = /合工大|合肥工业|工业大学|工大|宣城校区|翡翠湖校区|斛兵塘|屯溪路|六安路/;
  const LIMIT = 9;

  const readSet = () => {
    const out = new Set();
    for (const k of [READ_KEY, READ_KEY2]) {
      try { (JSON.parse(localStorage.getItem(k) || '[]') || []).forEach((x) => out.add(String(x))); } catch (e) { /* 忽略 */ }
    }
    return out;
  };
  const isRead = (i, set) => set.has(String(i.id));
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const fmtNum = (n) => (n >= 10000 ? `${(n / 10000).toFixed(1)} 万` : String(n));
  const rel = (at) => {
    const t = new Date(at || 0).getTime();
    if (!t) return '日期未知';
    const h = (Date.now() - t) / 3600000;
    if (h < 1) return '刚刚';
    if (h < 24) return `${Math.round(h)} 小时前`;
    const d = Math.floor(h / 24);
    if (d < 30) return `${d} 天前`;
    return new Date(t).toLocaleDateString('zh-CN', { month: 'numeric', day: 'numeric' });
  };

  const heat = (i) => Math.log10(1 + (i.src === 'bili' ? (i.p || 0) : (i.r || 0))) * 4;
  const ageBoost = (at) => {
    const d = (Date.now() - new Date(at || 0).getTime()) / 86400000;
    if (d < 1) return 16;
    if (d < 3) return 11;
    if (d < 7) return 8;
    if (d < 30) return 4;
    return 0;
  };
  const score = (i) => (i.s || 0) + heat(i) + ageBoost(i.at);

  let data = null;
  async function load() {
    if (data) return data;
    const get = async (f, src) => {
      const r = await fetch(f, { cache: 'no-store' });
      const j = await r.json();
      return (j.items || []).map((i) => Object.assign(i, { src }));
    };
    const [t, b] = await Promise.all([
      get('data/forum-tieba.json', 'tieba'),
      get('data/forum-bili.json', 'bili'),
    ]);
    data = t.concat(b);
    return data;
  }

  // 首页只放真跟工大/合肥本地沾边的，别的学校（安徽大学、中科大…）除非同时也提了合工大就不上
  const OTHER_RE = /安徽大学|中科大|中国科学技术大学|安徽理工|安徽师范|合肥学院|安徽农业|安徽医科|安徽工程/;

  function pick(items, set) {
    const pool = items.filter((i) => {
      if (i.src === 'bili' && !BILI_RE.test(i.t || '')) return false;
      const title = i.t || '';
      if (OTHER_RE.test(title) && !HFUT_RE.test(title)) return false;
      if (isRead(i, set)) return false;
      const d = (Date.now() - new Date(i.at || 0).getTime()) / 86400000;
      return d <= 30;
    });
    const strong = pool.filter((i) => (i.s || 0) >= 4 || (HFUT_RE.test(i.t || '') && (i.s || 0) >= 2));
    const chosen = (strong.length >= 4 ? strong : pool.slice()).sort((a, b) => score(b) - score(a));
    const seen = new Set();
    const out = [];
    for (const i of chosen) {
      const key = String(i.t || '').slice(0, 18).replace(/\s+/g, '');
      if (seen.has(key)) continue;
      seen.add(key);
      out.push(i);
      if (out.length >= LIMIT) break;
    }
    return out;
  }

  function render(items) {
    const set = readSet();
    const rows = pick(items, set);
    if (!rows.length) { BAND.hidden = true; return; }
    BAND.hidden = false;
    BAND.innerHTML = `<div class="pk-head">
        <h2>今天值得看的 ${rows.length} 条<span class="pk-sub">从讨论区 1 万多条里，按新旧 + 跟你相关的程度挑的</span></h2>
        <a class="pk-all" href="forum.html">去讨论区看全部 →</a>
      </div>
      <ol class="pk-list">${rows.map((i, n) => `<li data-id="${esc(i.id)}">
        <span class="pk-n">${n + 1}</span>
        <div class="pk-body">
          <a href="${esc(i.u)}" target="_blank" rel="noopener">${esc(i.t)}</a>
          <div class="pk-meta"><span class="pk-src">${i.src === 'bili' ? 'B站' : esc(i.b || '贴吧')}</span>·<span>${rel(i.at)}</span>${i.src === 'bili' ? `·<span>${fmtNum(i.p || 0)} 播放</span>` : `·<span>${i.r || 0} 回复</span>`}</div>
        </div>
        <button class="pk-read" data-read="${esc(i.id)}" title="标记已阅：从首页沉下去，讨论区还能搜到">已阅</button>
      </li>`).join('')}</ol>`;
  }

  BAND.addEventListener('click', (e) => {
    const b = e.target.closest('[data-read]');
    if (!b) return;
    e.preventDefault();
    const id = String(b.dataset.read);
    const set = readSet();
    set.add(id);
    try { localStorage.setItem(READ_KEY, JSON.stringify([...set])); } catch (err) { /* 忽略 */ }
    const li = b.closest('li');
    if (li) { li.classList.add('pk-gone'); setTimeout(() => { if (data) render(data.filter((x) => String(x.id) !== id)); }, 220); }
  });

  async function boot() {
    try {
      const items = await load();
      render(items);
      window.addEventListener('hashchange', () => {
        const home = !location.hash || location.hash === '#/' || location.hash === '#';
        if (home) render(items); else BAND.hidden = true;
      });
      document.addEventListener('visibilitychange', () => { if (!document.hidden) { const home = !location.hash || location.hash === '#/' || location.hash === '#'; if (home) render(items); } });
      window.addEventListener('storage', (e) => { if (e.key === READ_KEY || e.key === READ_KEY2) render(items); });
    } catch (err) {
      BAND.hidden = true;
    }
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
