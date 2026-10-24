/* ============ 工大知道 · app ============ */
(() => {
  'use strict';

  const CAT_COLORS = {
    arts: '#c2543f', recruitment: '#b5793a', lectures: '#3f6ea8', skills: '#4f8a6b',
    careers: '#7a5ba8', exchange: '#3f8f9c', campus: '#6b7f8f', research: '#3f7f6f',
    departments: '#8a6a4f', life: '#a8763f', academics: '#4f6d9a',
    scholarships: '#a87b3f', services: '#6f7f8a'
  };

  const I18N = {
    zh: {
      nav: { all: '全部', activities: '活动', information: '通知', calendar: '日历', sources: '来源', people: '教师' },
      searchPh: '搜索标题、公众号或发布单位',
      heroTitle: '把散落在合工大几百个公众号和官网里的信息，<span class="hl">收进同一个页面</span>',
      heroSub: '讲座、演出、招新、奖学金、选课通知 —— 翡翠湖校区的信息都在这里，不用一个个关注，打开就能看。',
      items: '条信息', sourcesN: '个来源', updated: '更新于',
      recommend: '为你推荐', latest: '最新发布', upcoming: '即将开始',
      forYou: '与我相关', related: '相关',
      all: '全部', activity: '活动', information: '通知',
      loadMore: '加载更多', more: '查看更多', none: '没有符合条件的信息', noneSub: '换个关键词或分类试试',
      signup: '需报名', summary: 'AI 摘要', time: '时间', place: '地点', source: '来源',
      viewOriginal: '查看原文', demoNoLink: '演示数据，没有原文链接', back: '返回', close: '关闭',
      published: '发布于', ended: '已结束', thisWeek: '本周',
      calendar: '活动日历', today: '今天', prevWeek: '上一周', nextWeek: '下一周',
      calendarSub: '按天排好的一周活动，点击任意一条查看详情',
      sourcesTitle: '信息来源', sourcesSub: '全部信息按来源归档，可以只看某一个公众号或网站',
      verified: '已核验', toVerify: '待核验', demoNote: '其中 {n} 条演示数据', stale: '数据可能已过期',
      contribute: '信息源补充', contributeSub: '发现有公众号或网站还没收录？告诉我们，核实归属后会尽快接入。',
      contributeHint: '请附上公众号名称或网站地址，最好再给一篇近期文章链接。', contributeBtn: '写邮件告诉我们',
      wechat: '公众号', official: '官网', count: '条',
      results: '搜索结果', noSource: '没有找到这个来源',
      profileLine: '为 {college} · {grade} 定制排序',
      peopleTitle: '教师与课程', peopleSub: '集成电路创新学院师资名录，点击进入教师个人主页。课程数据整理中。',
      peopleEmpty: '教师数据还没抓取，运行 tools/make_people.py 生成。', peopleLink: '个人主页',
      newBadge: '新',
      weekdays: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      relNow: '刚刚', relMin: '{n} 分钟前', relHour: '{n} 小时前', relDay: '昨天', relDays: '{n} 天前'
    },
    en: {
      nav: { all: 'All', activities: 'Events', information: 'Notices', calendar: 'Calendar', sources: 'Sources', people: 'Faculty' },
      searchPh: 'Search title, account or unit',
      heroTitle: 'Every notice scattered across hundreds of HFUT accounts, <span class="hl">in one page</span>',
      heroSub: 'Lectures, shows, recruitment, scholarships, course notices — everything on Feicui Lake campus.',
      items: 'items', sourcesN: 'sources', updated: 'updated',
      recommend: 'For you', latest: 'Latest', upcoming: 'Upcoming',
      forYou: 'Related to me', related: 'Related',
      all: 'All', activity: 'Events', information: 'Notices',
      loadMore: 'Load more', more: 'View all', none: 'Nothing matches', noneSub: 'Try another keyword or category',
      signup: 'Sign-up', summary: 'AI Summary', time: 'Time', place: 'Place', source: 'Source',
      viewOriginal: 'Read original', demoNoLink: 'Demo data, no original link', back: 'Back', close: 'Close',
      published: 'Published', ended: 'Ended', thisWeek: 'This week',
      calendar: 'Calendar', today: 'Today', prevWeek: 'Previous', nextWeek: 'Next',
      calendarSub: 'A week of events, day by day. Click any card for details.',
      sourcesTitle: 'Sources', sourcesSub: 'All items archived by source — browse a single account or website',
      verified: 'verified', toVerify: 'to verify', demoNote: '{n} demo items', stale: 'may be outdated',
      contribute: 'Add a source', contributeSub: 'Know an account or website we have not covered? Tell us and we will add it.',
      contributeHint: 'Include the account name or site URL, ideally a link to a recent post.', contributeBtn: 'Email us',
      wechat: 'WeChat accounts', official: 'Official sites', count: '',
      results: 'Results', noSource: 'Source not found',
      profileLine: 'Ranked for {college} · {grade}',
      peopleTitle: 'Faculty & Courses', peopleSub: 'Faculty of the School of Integrated Circuits. Course data coming.',
      peopleEmpty: 'No faculty data yet. Run tools/make_people.py.', peopleLink: 'Homepage',
      newBadge: 'NEW',
      weekdays: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
      relNow: 'just now', relMin: '{n}m ago', relHour: '{n}h ago', relDay: 'yesterday', relDays: '{n}d ago'
    }
  };

  const S = {
    items: [], catById: {}, srcById: {}, categories: [], sources: [],
    site: { name: '工大知道', enName: 'HFUT Know' },
    profile: {},
    lang: localStorage.getItem('ck-lang') || 'zh',
    theme: localStorage.getItem('ck-theme') || '',
    sort: localStorage.getItem('ck-sort') || 'recommend',
    limit: 24,
    route: '',
    _q: '',
    drawerOpen: false,
    scrollY: 0
  };

  const $ = (sel) => document.querySelector(sel);
  const app = () => $('#app');
  const t = () => I18N[S.lang];
  const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const catName = (c) => { const k = S.catById[c]; return k ? (S.lang === 'en' ? k.en : k.zh) : c; };
  const catColor = (c) => CAT_COLORS[c] || 'var(--accent)';

  function pad(n) { return String(n).padStart(2, '0'); }
  function dt(iso) { return iso ? new Date(iso) : null; }

  function relTime(iso) {
    const d = dt(iso); if (!d) return '';
    const diff = (Date.now() - d.getTime()) / 1000;
    const L = t();
    if (diff < 60) return L.relNow;
    if (diff < 3600) return L.relMin.replace('{n}', Math.floor(diff / 60));
    if (diff < 86400) return L.relHour.replace('{n}', Math.floor(diff / 3600));
    if (diff < 172800) return L.relDay;
    if (diff < 604800) return L.relDays.replace('{n}', Math.floor(diff / 86400));
    return S.lang === 'en' ? `${pad(d.getMonth() + 1)}/${pad(d.getDate())}` : `${d.getMonth() + 1}月${d.getDate()}日`;
  }

  function fmtEvent(iso) {
    const d = dt(iso); if (!d) return '';
    const wd = t().weekdays[(d.getDay() + 6) % 7];
    return S.lang === 'en'
      ? `${wd} ${d.getMonth() + 1}/${d.getDate()} ${pad(d.getHours())}:${pad(d.getMinutes())}`
      : `${d.getMonth() + 1}月${d.getDate()}日 ${wd} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  function fmtDate(iso) {
    const d = dt(iso); if (!d) return '';
    return S.lang === 'en'
      ? `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
      : `${d.getFullYear()}年${d.getMonth() + 1}月${d.getDate()}日 ${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  const dayKey = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;

  function hl(text, q) {
    const safe = esc(text);
    if (!q) return safe;
    const needle = esc(q).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    try { return safe.replace(new RegExp(needle, 'gi'), (m) => `<mark>${m}</mark>`); } catch { return safe; }
  }

  /* ---------------- 个性化排序 ---------------- */
  function relevance(item) {
    const P = S.profile || {};
    const kws = P.keywords || [];
    const prefer = P.preferSources || [];
    const text = `${item.title} ${item.summary} ${(item.tags || []).join('')} ${item.sourceName}`;
    let score = 0;
    kws.forEach((k) => { if (text.includes(k)) score += 3.5; });
    if (prefer.includes(item.sourceId)) score += 5;
    if (item.category === 'academics' || item.category === 'scholarships') score += 2;
    if (item.category === 'lectures') score += 1;
    if (item.competition && item.competition.ic) score += 6;
    else if (item.competition) score += 3;
    if (item.requiresSignup) score += 1;
    if (item.event && item.event.start) {
      const start = new Date(item.event.start).getTime();
      const days = (start - Date.now()) / 864e5;
      if (days >= 0 && days <= 7) score += 2;
    }
    const age = (Date.now() - new Date(item.publishedAt).getTime()) / 864e5;
    score += Math.max(0, 3 - age * 0.6);
    return Math.round(score * 10) / 10;
  }

  const isRelated = (item) => relevance(item) >= 10;

  /* ---------------- routing ---------------- */
  function parseHash() {
    const raw = location.hash.replace(/^#\/?/, '');
    const [path, qs] = raw.split('?');
    return { path: path || '', params: new URLSearchParams(qs || '') };
  }

  function go(hash) { location.hash = hash; }

  function route() {
    const { path, params } = parseHash();
    S.route = path;
    if (S.drawerOpen) closeDrawer(false);
    S.limit = 24;
    const head = path.split('/')[0];
    const arg = path.split('/')[1];

    $('#chips').hidden = !(path === '' || path === 'activities' || path === 'information' || path === 'foryou' || head === 'c');
    document.querySelectorAll('#mainnav a').forEach((a) => a.classList.remove('active'));
    document.querySelectorAll('.tabbar a').forEach((a) => a.classList.remove('active'));
    const navKey = path === '' ? 'all' : path === 'activities' ? 'activities'
      : path === 'information' ? 'information' : head === 'calendar' ? 'calendar'
      : head === 'sources' ? 'sources' : head === 'people' ? 'people'
      : head === 'competitions' ? 'competitions'
      : head === 'c' && S.catById[arg] ? S.catById[arg].intent : '';
    const navEl = document.querySelector(`#mainnav a[data-nav="${navKey}"]`);
    if (navEl) navEl.classList.add('active');
    const tabEl = document.querySelector(`.tabbar a[data-tab="${navKey}"]`);
    if (tabEl) tabEl.classList.add('active');

    if (path === '') renderBrowse({ intent: 'all' });
    else if (path === 'activities') renderBrowse({ intent: 'activity' });
    else if (path === 'information') renderBrowse({ intent: 'information' });
    else if (path === 'foryou') renderBrowse({ forYou: true });
    else if (head === 'c') renderBrowse({ cat: arg });
    else if (head === 'i') renderDetail(arg);
    else if (head === 'calendar') renderCalendar(parseInt(params.get('w') || '0', 10));
    else if (head === 'sources') renderSources();
    else if (head === 'people') renderPeople();
    else if (head === 'competitions') renderCompetitions();
    else if (head === 's') renderBrowse({ sourceId: arg });
    else if (head === 'search') renderSearch(params.get('q') || '');
    else if (head === 'contribute') renderContribute();
    else renderBrowse({ intent: 'all' });
    window.scrollTo(0, 0);
  }

  /* ---------------- shared pieces ---------------- */
  function chipsHTML(activeCat, activeIntent, forYou) {
    const counts = {};
    S.items.forEach((i) => { counts[i.category] = (counts[i.category] || 0) + 1; });
    const act = S.items.filter((i) => i.intent === 'activity').length;
    const inf = S.items.filter((i) => i.intent === 'information').length;
    const rel = S.items.filter((i) => relevance(i) >= 10).length;
    const L = t();
    const chip = (label, n, href, active) =>
      `<a class="chip${active ? ' active' : ''}" href="${href}">${label}${n != null ? `<span class="n">${n}</span>` : ''}</a>`;
    let out = chip(L.all, S.items.length, '#/', activeCat == null && !activeIntent && !forYou);
    out += `<a class="chip chip-foryou${forYou ? ' active' : ''}" href="#/foryou">${L.forYou}<span class="n">${rel}</span></a>`;
    out += chip(L.activity, act, '#/activities', activeIntent === 'activity');
    out += chip(L.information, inf, '#/information', activeIntent === 'information');
    S.categories.forEach((c, idx) => {
      out += `<a class="chip${idx === 0 ? ' group-start' : ''}${activeCat === c.id ? ' active' : ''}" href="#/c/${c.id}">${S.lang === 'en' ? c.en : c.zh}<span class="n">${counts[c.id] || 0}</span></a>`;
    });
    return out;
  }

  function cardHTML(item) {
    const color = catColor(item.category);
    const ev = item.event;
    const now = Date.now();
    const start = ev && ev.start ? new Date(ev.start).getTime() : 0;
    const hot = start > now && start - now < 7 * 864e5;
    const ended = start > 0 && start < now;
    let evHTML = '';
    if (ev) {
      const bits = [`<span class="${hot ? 'hot' : ''}">${fmtEvent(ev.start)}</span>`];
      if (ev.location) bits.push(`<span>${esc(ev.location)}</span>`);
      if (ended) bits.push(`<span>${t().ended}</span>`);
      evHTML = `<div class="ev">${bits.join('')}</div>`;
    }
    const rel = S.sort !== 'recommend' && isRelated(item);
    const fresh = (Date.now() - new Date(item.publishedAt).getTime()) < 6 * 3600e3;
    return `<a class="card" href="#/i/${encodeURIComponent(item.id)}" data-id="${esc(item.id)}" style="--cat:${color}">
      <div class="card-tags">
        ${item.requiresSignup ? `<span class="badge-signup">${t().signup}</span>` : ''}
        ${rel ? `<span class="badge-related">${t().related}</span>` : ''}
        ${item.competition ? `<span class="badge-comp${item.competition.ic ? ' ic' : ''}">${esc(item.competition.ic ? '★ ' + item.competition.name : item.competition.name)}</span>` : ''}
        ${fresh ? `<span class="badge-new">${t().newBadge}</span>` : ''}
      </div>
      <h3>${hl(item.title, S._q)}</h3>
      <p class="sum">${hl(item.summary, S._q)}</p>
      ${evHTML}
      <div class="card-foot">
        <span class="srcname">${esc(item.sourceName)}</span>
        <span class="dot"></span>
        <span>${catName(item.category)}</span>
        <span class="time">${relTime(item.publishedAt)}</span>
      </div>
    </a>`;
  }

  function toolbarHTML(total) {
    const L = t();
    const opt = (key, label) =>
      `<button data-sort="${key}" class="${S.sort === key ? 'active' : ''}">${label}</button>`;
    return `<div class="toolbar">
      <span class="count">${total} ${L.items}</span>
      <div class="spacer"></div>
      <div class="seg" id="segSort">
        ${opt('recommend', L.recommend)}
        ${opt('new', L.latest)}
        ${opt('soon', L.upcoming)}
      </div>
    </div>`;
  }

  function sortItems(list) {
    const arr = list.slice();
    if (S.sort === 'soon') {
      const now = Date.now();
      return arr.filter((i) => i.event && new Date(i.event.start).getTime() >= now - 36e5)
        .sort((a, b) => new Date(a.event.start) - new Date(b.event.start));
    }
    if (S.sort === 'recommend') {
      return arr.sort((a, b) => (relevance(b) - relevance(a)) || (new Date(b.publishedAt) - new Date(a.publishedAt)));
    }
    return arr.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt));
  }

  function gridHTML(list, limit) {
    return `<div class="grid">${list.slice(0, limit).map(cardHTML).join('')}</div>`;
  }

  function emptyHTML() {
    return `<div class="empty"><b>${t().none}</b>${t().noneSub}</div>`;
  }

  /* ---------------- views ---------------- */
  function renderBrowse({ intent = null, cat = null, sourceId = null, q = '', forYou = false }) {
    S._q = q;
    let list = S.items.slice();
    if (forYou) list = list.filter(isRelated);
    if (intent && intent !== 'all') list = list.filter((i) => i.intent === intent);
    if (cat) list = list.filter((i) => i.category === cat);
    if (sourceId) list = list.filter((i) => i.sourceId === sourceId);
    if (q) {
      const qq = q.toLowerCase();
      list = list.filter((i) => `${i.title} ${i.summary} ${i.sourceName} ${(i.tags || []).join(' ')}`.toLowerCase().includes(qq));
    }
    list = sortItems(list);

    $('#chips').innerHTML = chipsHTML(cat, intent, forYou);
    const L = t();
    const isHome = !cat && !sourceId && !q && (!intent || intent === 'all') && !forYou;
    const title = cat ? (S.lang === 'en' ? S.catById[cat].en : S.catById[cat].zh)
      : sourceId ? (S.srcById[sourceId] || {}).name
      : q ? `${L.results} · ${q}`
      : forYou ? L.forYou
      : intent === 'activity' ? L.activity : intent === 'information' ? L.information : '';

    let html = '';
    if (isHome) {
      const P = S.profile || {};
      const profileLine = P.college
        ? `<p class="profile-line">${L.profileLine.replace('{college}', esc(P.college)).replace('{grade}', esc(P.grade || ''))} · <a href="#/foryou">${L.more} →</a></p>`
        : '';
      html += `<section class="hero">
        <h1>${L.heroTitle}</h1>
        <p>${L.heroSub}</p>
        ${profileLine}
        <div class="stats">
          <div class="stat"><b>${S.items.length}</b><span>${L.items}</span></div>
          <div class="stat"><b>${S.sources.length}</b><span>${L.sourcesN}</span></div>
          <div class="stat"><b>${(S.generatedAt || '').slice(11, 16)}</b><span>${L.updated}</span></div>
        </div>
      </section>`;
    } else if (cat) {
      html += `<section class="hero" style="padding-bottom:6px"><h1 style="font-size:30px">${esc(title)}</h1><p>${esc(S.catById[cat].desc || '')}</p></section>`;
    } else if (sourceId) {
      const s = S.srcById[sourceId];
      html += `<section class="hero" style="padding-bottom:6px"><h1 style="font-size:30px">${esc(s ? s.name : L.noSource)}</h1>
        <p>${s ? (s.type === 'wechat' ? L.wechat : L.official) : ''}</p></section>`;
    } else if (q) {
      html += `<section class="hero" style="padding-bottom:6px"><h1 style="font-size:30px">${esc(title)}</h1><p>${list.length} ${L.items}</p></section>`;
    } else {
      html += `<section class="hero" style="padding-bottom:6px"><h1 style="font-size:30px">${esc(title)}</h1>
        <p>${forYou ? L.heroSub : ''}</p></section>`;
    }

    html += toolbarHTML(list.length);
    html += list.length ? gridHTML(list, S.limit) : emptyHTML();
    if (list.length > S.limit) html += `<div class="more"><button class="btn ghost" id="moreBtn">${L.loadMore}</button></div>`;

    document.title = (title ? `${title} · ` : '') + (S.lang === 'en' ? S.site.enName : S.site.name);
    app().innerHTML = html;
  }

  function renderSearch(q) { renderBrowse({ q }); }

  function detailHTML(item) {
    const L = t();
    const s = S.srcById[item.sourceId];
    const ev = item.event;
    const isDemo = item.demo === true || /example\.edu/.test(item.url || '');
    const tags = (item.tags || []).map((x) => `<span class="tag">${esc(x)}</span>`).join('');
    const original = isDemo
      ? `<span class="btn ghost disabled" title="${L.demoNoLink}">${L.viewOriginal}</span>`
      : `<a class="btn" href="${esc(item.url)}" target="_blank" rel="noopener">${L.viewOriginal} ↗</a>`;
    return `<div class="dt-tags">
        <span class="tag cat" style="background:${catColor(item.category)}1a;color:${catColor(item.category)}">${catName(item.category)}</span>
        ${item.requiresSignup ? `<span class="tag">${L.signup}</span>` : ''}
        ${tags}
        ${item.competition ? `<span class="tag cat" style="background:#3f7a5a1a;color:#3f7a5a">竞赛：${esc(item.competition.name)}</span>` : ''}
      </div>
      <h1 class="dt-title">${esc(item.title)}</h1>
      <div class="dt-meta">
        <span>${L.source}：<a href="#/s/${encodeURIComponent(item.sourceId)}">${esc(item.sourceName)}</a></span>
        <span>${L.published} ${fmtDate(item.publishedAt)}</span>
        ${s ? `<span>${s.type === 'wechat' ? L.wechat : L.official}</span>` : ''}
      </div>
      <div class="ai-box">
        <span class="lab">${L.summary}</span>
        <p>${esc(item.summary)}</p>
        ${ev ? `<dl class="kv">
          <dt>${L.time}</dt><dd>${fmtEvent(ev.start)}</dd>
          ${ev.location ? `<dt>${L.place}</dt><dd>${esc(ev.location)}</dd>` : ''}
          ${ev.speaker ? `<dt>${S.lang === 'en' ? 'Speaker' : '主讲'}</dt><dd>${esc(ev.speaker)}</dd>` : ''}
        </dl>` : ''}
      </div>
      <div class="dt-body">${(item.content || []).join('')}</div>
      <div class="dt-actions">${original}</div>`;
  }

  function renderDetail(id) {
    $('#chips').hidden = true;
    const item = S.items.find((i) => i.id === id);
    if (!item) { app().innerHTML = emptyHTML(); return; }
    document.title = `${item.title} · ${S.lang === 'en' ? S.site.enName : S.site.name}`;
    app().innerHTML = `<article class="detail">
      <a class="back" href="#/">← ${t().back}</a>
      ${detailHTML(item)}
    </article>`;
  }

  /* ---------------- 抽屉（不覆盖主页） ---------------- */
  function openDrawer(id) {
    const item = S.items.find((i) => i.id === id);
    if (!item) return;
    const drawer = $('#drawer');
    S.scrollY = window.scrollY;
    drawer.innerHTML = `<div class="drawer-backdrop" data-close></div>
      <aside class="drawer-panel" role="dialog" aria-modal="true">
        <div class="drawer-bar">
          <button class="icon-btn" data-close aria-label="${t().close}">✕</button>
          <span class="drawer-hint">${esc(item.sourceName)}</span>
        </div>
        <div class="drawer-body">${detailHTML(item)}</div>
      </aside>`;
    drawer.hidden = false;
    document.body.classList.add('drawer-open');
    S.drawerOpen = true;
    history.pushState({ drawer: id }, '');
  }

  function closeDrawer(restore = true) {
    const drawer = $('#drawer');
    if (!drawer || drawer.hidden) return;
    drawer.hidden = true;
    drawer.innerHTML = '';
    document.body.classList.remove('drawer-open');
    S.drawerOpen = false;
    if (restore) window.scrollTo(0, S.scrollY || 0);
  }

  function renderCalendar(offset) {
    $('#chips').hidden = true;
    const L = t();
    const now = new Date();
    const monday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    monday.setDate(monday.getDate() - ((monday.getDay() + 6) % 7) + offset * 7);
    const days = Array.from({ length: 7 }, (_, i) => {
      const d = new Date(monday); d.setDate(monday.getDate() + i); return d;
    });
    const byDay = {};
    S.items.forEach((i) => {
      if (!i.event || !i.event.start) return;
      const d = new Date(i.event.start);
      (byDay[dayKey(d)] = byDay[dayKey(d)] || []).push(i);
    });
    const todayKey = dayKey(now);
    const fmtRange = `${monday.getMonth() + 1}月${monday.getDate()}日 — ${days[6].getMonth() + 1}月${days[6].getDate()}日`;

    const cols = days.map((d, idx) => {
      const key = dayKey(d);
      const list = (byDay[key] || []).sort((a, b) => new Date(a.event.start) - new Date(b.event.start));
      const evs = list.length ? list.map((it) => {
        const st = new Date(it.event.start);
        return `<a class="cal-ev" href="#/i/${encodeURIComponent(it.id)}" data-id="${esc(it.id)}" style="--cat:${catColor(it.category)}">
          <i>${pad(st.getHours())}:${pad(st.getMinutes())}${it.event.location ? ' · ' + esc(it.event.location) : ''}</i>
          <b>${esc(it.title)}</b></a>`;
      }).join('') : `<div class="none">—</div>`;
      return `<div class="cal-day${key === todayKey ? ' today' : ''}">
        <div class="head-row"><div class="dow">${L.weekdays[idx]}</div><div class="dnum">${d.getDate()}</div></div>
        ${evs}
      </div>`;
    }).join('');

    document.title = `${L.calendar} · ${S.lang === 'en' ? S.site.enName : S.site.name}`;
    app().innerHTML = `<section class="cal-head">
      <h1>${L.calendar}</h1><span class="range">${fmtRange}</span>
      <div class="spacer"></div>
      <div class="cal-nav">
        <button data-week="${offset - 1}" title="${L.prevWeek}">‹</button>
        <button data-week="0" class="btn ghost" style="width:auto;padding:0 12px;height:34px">${L.today}</button>
        <button data-week="${offset + 1}" title="${L.nextWeek}">›</button>
      </div>
    </section>
    <p class="muted" style="margin:-8px 0 16px;font-size:13px">${L.calendarSub}</p>
    <div class="cal-grid">${cols}</div>`;
  }

  function renderSources() {
    $('#chips').hidden = true;
    const L = t();
    const groups = { wechat: [], official: [] };
    S.sources.forEach((s) => { (groups[s.type] || groups.wechat).push(s); });
    const row = (s) => `<a class="src-row" href="#/s/${encodeURIComponent(s.id)}">
      <span class="avatar ${s.type === 'official' ? 'official' : ''}">${esc(s.name.slice(0, 1))}</span>
      <span class="nm">${esc(s.name)}<em class="st ${s.verified ? 'ok' : 'pending'}">${s.verified ? L.verified : L.toVerify} · ${s.type === 'wechat' ? L.wechat : L.official}</em></span>
      <span class="cnt">${s.count || 0}</span></a>`;
    document.title = `${L.sourcesTitle} · ${S.lang === 'en' ? S.site.enName : S.site.name}`;
    app().innerHTML = `<section class="src-head"><h1>${L.sourcesTitle}</h1><p>${L.sourcesSub}</p></section>
      <div class="grp-title">${L.wechat}</div>
      <div class="src-grid">${groups.wechat.sort((a, b) => (b.count || 0) - (a.count || 0)).map(row).join('')}</div>
      <div class="grp-title">${L.official}</div>
      <div class="src-grid">${groups.official.sort((a, b) => (b.count || 0) - (a.count || 0)).map(row).join('')}</div>`;
  }

  function renderPeople() {
    $('#chips').hidden = true;
    const L = t();
    const people = S.people || [];
    const order = ['教授', '副教授', '研究员', '副研究员', '讲师', '兼职'];
    const groups = {};
    people.forEach((p) => { (groups[p.title] = groups[p.title] || []).push(p); });
    const keys = Object.keys(groups).sort((a, b) => {
      const ia = order.indexOf(a), ib = order.indexOf(b);
      return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib);
    });
    const body = people.length
      ? keys.map((k) => `<div class="grp-title">${esc(k)} · ${groups[k].length}</div>
        <div class="people-grid">${groups[k].map((p) => `<a class="person" href="${esc(p.url)}" target="_blank" rel="noopener">
          <span class="ava">${esc(p.name.slice(0, 1))}</span>
          <span class="meta"><span class="nm">${esc(p.name)}</span>
          <span class="tt">${esc(p.title)}</span>
          <span class="cl">${esc(p.college)} · ${L.peopleLink} ↗</span>
          ${p.research ? `<span class="rc">${esc(p.research)}</span>` : ''}</span></a>`).join('')}</div>`).join('')
      : `<div class="empty"><b>${L.peopleEmpty}</b></div>`;
    document.title = `${L.peopleTitle} · ${S.lang === 'en' ? S.site.enName : S.site.name}`;
    const plans = S.plans || [];
    const planHTML = plans.length ? `<div class="grp-title">培养方案 · ${plans.length}</div>
      <div class="plan-list">${plans.map((p) => `<a class="plan" href="${esc(p.pdf || p.url)}" target="_blank" rel="noopener">
        <span class="pn">${esc(p.title)}</span><span class="pa">PDF ↗</span></a>`).join('')}</div>` : '';
    app().innerHTML = `<section class="src-head"><h1>${L.peopleTitle}</h1><p>${L.peopleSub}</p></section>${body}${planHTML}`;
  }

  function renderCompetitions() {
    $('#chips').hidden = true;
    const L = t();
    const comps = S.competitions || [];
    const tiers = ['三大赛', 'A类', 'B类'];
    const groups = {};
    comps.forEach((c) => { (groups[c.tier] = groups[c.tier] || []).push(c); });
    const body = comps.length
      ? tiers.filter((tr) => groups[tr]).map((tr) => `<div class="grp-title">${esc(tr)} · ${groups[tr].length}</div>
        <div class="comp-grid">${groups[tr].map((c) => `<div class="comp${c.related ? ' rel' : ''}">
          <span class="cn">${esc(c.name)}</span>
          ${c.related ? '<span class="cr">★ 与集成电路相关</span>' : ''}</div>`).join('')}</div>`).join('')
      : `<div class="empty"><b>${L.peopleEmpty}</b></div>`;
    document.title = '学科竞赛 · ' + (S.lang === 'en' ? S.site.enName : S.site.name);
    app().innerHTML = `<section class="src-head"><h1>学科竞赛</h1>
      <p>依据《合肥工业大学学科竞赛赛事列表（2026年版）》，共 ${comps.length} 项。带 ★ 的与你（集成电路）相关。</p>
      </section>${body}`;
  }

  function renderContribute() {
    $('#chips').hidden = true;
    const L = t();
    const mail = 'mailto:hello@hfutknow.example?subject=' + encodeURIComponent('信息源补充');
    document.title = `${L.contribute} · ${S.lang === 'en' ? S.site.enName : S.site.name}`;
    app().innerHTML = `<section class="src-head"><h1>${L.contribute}</h1><p>${L.contributeSub}</p></section>
      <div class="ai-box" style="margin-top:22px;max-width:620px">
        <span class="lab">${L.contribute}</span>
        <p>${L.contributeHint}</p>
        <div style="display:flex;gap:10px;margin-top:14px;flex-wrap:wrap">
          <a class="btn" href="${mail}">${L.contributeBtn}</a>
          <a class="btn ghost" href="#/sources">${L.sourcesTitle}</a>
        </div>
        <p class="muted" style="margin-top:14px;font-size:12.5px">当前已收录 ${S.sources.length} 个来源，其中 ${S.sources.filter((s) => s.verified).length} 个已完成核验。</p>
      </div>`;
  }

  /* ---------------- chrome ---------------- */
  function applyLang() {
    const L = t();
    $('#brandName').textContent = S.lang === 'en' ? S.site.enName : S.site.name;
    $('#brandEn').textContent = S.lang === 'en' ? '工大知道' : S.site.enName;
    $('#footName').textContent = S.lang === 'en' ? S.site.enName : S.site.name;
    document.querySelectorAll('#mainnav a').forEach((a) => { const k = a.dataset.nav; if (L.nav[k]) a.textContent = L.nav[k]; });
    $('#searchInput').placeholder = L.searchPh;
    $('#langBtn').textContent = S.lang === 'en' ? '中' : 'EN';
    const freshAge = S.generatedAt ? (Date.now() - new Date(S.generatedAt).getTime()) / 36e5 : 99;
    const dot = $('#freshDot');
    if (dot) {
      dot.className = 'fresh-dot ' + (freshAge < 2 ? 'ok' : freshAge < 12 ? 'warn' : 'bad');
      dot.title = (S.lang === 'en' ? 'Updated ' : '更新于 ') + (S.generatedAt || '').replace('T', ' ').slice(5, 16);
    }
    const demoPart = S.demoCount ? ` · ${L.demoNote.replace('{n}', S.demoCount)}` : '';
    const ageH = S.generatedAt ? (Date.now() - new Date(S.generatedAt).getTime()) / 36e5 : 0;
    const stale = ageH > 24 ? ` · <b style="color:var(--accent)">${L.stale}</b>` : '';
    $('#footMeta').innerHTML = S.items.length
      ? `${S.items.length} ${L.items} · ${S.sources.length} ${L.sourcesN}${demoPart} · ${L.updated} ${(S.generatedAt || '').replace('T', ' ').slice(0, 16)}${stale}`
      : '';
  }

  function applyTheme() {
    const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.dataset.theme = S.theme || (systemDark ? 'dark' : 'light');
  }

  function bind() {
    window.addEventListener('hashchange', route);
    window.addEventListener('popstate', () => {
      if (S.drawerOpen) closeDrawer();
      else route();
    });
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && S.drawerOpen) closeDrawer(); });

    $('#themeBtn').addEventListener('click', () => {
      const cur = document.documentElement.dataset.theme;
      S.theme = cur === 'dark' ? 'light' : 'dark';
      localStorage.setItem('ck-theme', S.theme);
      applyTheme();
    });
    $('#langBtn').addEventListener('click', () => {
      S.lang = S.lang === 'zh' ? 'en' : 'zh';
      localStorage.setItem('ck-lang', S.lang);
      applyLang();
      route();
    });
    $('#searchForm').addEventListener('submit', (e) => {
      e.preventDefault();
      const q = $('#searchInput').value.trim();
      if (q) go(`#/search?q=${encodeURIComponent(q)}`);
    });

    document.addEventListener('click', (e) => {
      const close = e.target.closest('[data-close]');
      if (close) { e.preventDefault(); closeDrawer(); return; }

      const card = e.target.closest('a.card, a.cal-ev');
      if (card && !e.metaKey && !e.ctrlKey && !e.shiftKey && e.button === 0) {
        e.preventDefault();
        openDrawer(card.dataset.id);
        return;
      }

      const sortBtn = e.target.closest('#segSort button');
      if (sortBtn) {
        S.sort = sortBtn.dataset.sort;
        localStorage.setItem('ck-sort', S.sort);
        route();
        return;
      }
      const more = e.target.closest('#moreBtn');
      if (more) {
        S.limit += 24;
        const { path, params } = parseHash();
        if (path === '') renderBrowse({ intent: 'all' });
        else if (path === 'activities') renderBrowse({ intent: 'activity' });
        else if (path === 'information') renderBrowse({ intent: 'information' });
        else if (path === 'foryou') renderBrowse({ forYou: true });
        else if (path.startsWith('c/')) renderBrowse({ cat: path.split('/')[1] });
        else if (path.startsWith('s/')) renderBrowse({ sourceId: path.split('/')[1] });
        else if (path.startsWith('search')) renderSearch(params.get('q') || '');
        return;
      }
      const wk = e.target.closest('[data-week]');
      if (wk) { e.preventDefault(); go(`#/calendar?w=${wk.dataset.week}`); }
    });

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => { if (!S.theme) applyTheme(); });
    let lastLoad = Date.now();
    document.addEventListener('visibilitychange', async () => {
      if (document.visibilityState !== 'visible') return;
      if (Date.now() - lastLoad < 5 * 60 * 1000) return;
      lastLoad = Date.now();
      if (await refreshData()) route();
    });
    // 每隔 3 分钟静默拉一次最新数据（页面保持前台时）
    setInterval(async () => {
      if (document.visibilityState !== 'visible') return;
      if (Date.now() - lastLoad < 3 * 60 * 1000) return;
      lastLoad = Date.now();
      const updated = await refreshData();
      if (updated) {
        const { path, params } = parseHash();
        if (path !== 'i') route();   // 详情抽屉打开时不打断阅读
      }
    }, 60 * 1000);
  }

  function registerSW() {
    if (!('serviceWorker' in navigator) || location.protocol === 'file:') return;
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }

  async function refreshData() {
    if (window.__CK_DATA__) return false;
    try {
      const [a, b] = await Promise.all([
        fetch('data/items.json?t=' + Date.now(), { cache: 'no-store' }),
        fetch('data/sources.json?t=' + Date.now(), { cache: 'no-store' })
      ]);
      if (!a.ok) return false;
      const payload = await a.json();
      const srcPayload = await b.json();
      S.items = payload.items || [];
      S.sources = srcPayload.sources || [];
      S.sources.forEach((s) => { S.srcById[s.id] = s; });
      S.generatedAt = payload.generatedAt || S.generatedAt;
      S.demoCount = S.items.filter((i) => i.demo).length;
      applyLang();
      return true;
    } catch (e) {
      return false;
    }
  }

  async function boot() {
    applyTheme();
    try {
      let payload, srcPayload;
      if (window.__CK_DATA__) {
        payload = window.__CK_DATA__.items;
        srcPayload = window.__CK_DATA__.sources;
        S.peopleData = window.__CK_DATA__.people || null;
        S.plansData = window.__CK_DATA__.plans || null;
      } else {
        const [itemsRes, srcRes] = await Promise.all([
          fetch('data/items.json', { cache: 'no-cache' }),
          fetch('data/sources.json', { cache: 'no-cache' })
        ]);
        if (!itemsRes.ok) throw new Error('items.json ' + itemsRes.status);
        payload = await itemsRes.json();
        srcPayload = await srcRes.json();
        for (const [file, key] of [['people.json', 'peopleData'], ['plans.json', 'plansData'], ['competitions.json', 'competitionsData']]) {
          try {
            const res = await fetch('data/' + file, { cache: 'no-cache' });
            if (res.ok) S[key] = await res.json();
          } catch (e) { /* 缺文件也能用 */ }
        }
      }
      S.items = payload.items || [];
      S.categories = payload.categories || [];
      S.categories.forEach((c) => { S.catById[c.id] = c; });
      S.sources = srcPayload.sources || [];
      S.sources.forEach((s) => { S.srcById[s.id] = s; });
      S.site = payload.site || S.site;
      S.profile = S.site.profile || {};
      S.people = (S.peopleData && S.peopleData.people) || [];
      S.plans = (S.plansData && S.plansData.plans) || [];
      S.competitions = (S.competitionsData && S.competitionsData.items) || [];
      S.generatedAt = payload.generatedAt || '';
      S.demoCount = S.items.filter((i) => i.demo).length;
      bind();
      applyLang();
      route();
      registerSW();
    } catch (err) {
      app().innerHTML = `<div class="empty"><b>数据没能加载</b>${esc(err.message)}</div>`;
    }
  }

  boot();
})();
