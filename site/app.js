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
      freshSync: '数据 {age}同步',
      freshNew: '24 小时内新增 {n} 条',
      crawlLine: '上次抓取 {age} · {ok}/{all} 源成功 · 本轮新增 {n} 条',
      srcCrawl: '最近抓取 {age}：列表 {got} 条，新增 {n}',
      srcErr: '最近抓取失败：{err}',
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
      voteUp: '推荐', voteDown: '不感兴趣', votedUp: '已推荐', votedDown: '已屏蔽',
      prefsTitle: '我的偏好', prefsHint: '你在卡片上点的 👍/ 会被记下来：命中的词加分，屏蔽的词降权。只存在这台设备上，不上传。',
      prefsUp: '推荐过', prefsDown: '屏蔽过', prefsTokens: '学到的关键词（数字=权重）', prefsClear: '清空全部偏好', prefsEmpty: '还没有点过任何 👍/。去列表里点几下，排序就会变成你的口味。',

      weekdays: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      relNow: '刚刚', relMin: '{n} 分钟前', relHour: '{n} 小时前', relDay: '昨天', relDays: '{n} 天前'
    },
    en: {
      nav: { all: 'All', activities: 'Events', information: 'Notices', calendar: 'Calendar', sources: 'Sources', people: 'Faculty' },
      searchPh: 'Search title, account or unit',
      heroTitle: 'Every notice scattered across hundreds of HFUT accounts, <span class="hl">in one page</span>',
      heroSub: 'Lectures, shows, recruitment, scholarships, course notices — everything on Feicui Lake campus.',
      items: 'items', sourcesN: 'sources', updated: 'updated',
      freshSync: 'Synced {age} ago',
      freshNew: '{n} new in 24h',
      crawlLine: 'Last crawl {age} · {ok}/{all} sources ok · {n} new',
      srcCrawl: 'Crawled {age}: {got} listed, {n} new',
      srcErr: 'Last crawl failed: {err}',
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
      voteUp: 'Like', voteDown: 'Not interested', votedUp: 'Liked', votedDown: 'Hidden',
      prefsTitle: 'My preferences', prefsHint: 'Your 👍/👎 taps are learned locally: matching words boost, blocked words demote. Stored on this device only.',
      prefsUp: 'liked', prefsDown: 'hidden', prefsTokens: 'Learned keywords (weight)', prefsClear: 'Clear all', prefsEmpty: 'No votes yet. Tap 👍/👎 on cards to tune the ranking.',

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
  function dt(iso) { return asDate(iso); }

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
  const PREFS_KEY = 'ck-prefs-v1';
  function loadPrefs() {
    try { S.prefs = JSON.parse(localStorage.getItem(PREFS_KEY)) || { up: {}, down: {} }; }
    catch (e) { S.prefs = { up: {}, down: {} }; }
    if (!S.prefs.up) S.prefs.up = {};
    if (!S.prefs.down) S.prefs.down = {};
    S.tw = tokenWeights();
  }
  function savePrefs() {
    try { localStorage.setItem(PREFS_KEY, JSON.stringify(S.prefs)); } catch (e) {}
    S.tw = tokenWeights();
  }
  function itemTokens(item) {
    const P = S.profile || {};
    const toks = new Set();
    (item.tags || []).forEach((t) => { if (t && t.length >= 2) toks.add(t); });
    if (item.category) toks.add(catName(item.category));
    const sn = (item.sourceName || '').replace(/^B站 · |^贴吧 · |^互联网 · /, '');
    if (sn.length >= 3) toks.add(sn.slice(0, 10));
    const hay = `${item.title} ${item.summary || ''}`;
    (P.keywords || []).forEach((k) => { if (hay.includes(k)) toks.add(k); });
    if (item.competition && item.competition.name) toks.add(item.competition.name);
    return Array.from(toks).slice(0, 8);
  }
  function tokenWeights() {
    const w = {};
    Object.values(S.prefs.up).forEach((ts) => ts.forEach((t) => { w[t] = (w[t] || 0) + 1; }));
    Object.values(S.prefs.down).forEach((ts) => ts.forEach((t) => { w[t] = (w[t] || 0) - 1.5; }));
    return w;
  }
  function toggleVote(id, dir) {
    const item = S.items.find((i) => i.id === id);
    if (!item) return;
    const other = dir === 'up' ? 'down' : 'up';
    if (S.prefs[dir][id]) { delete S.prefs[dir][id]; }
    else { S.prefs[dir][id] = itemTokens(item); delete S.prefs[other][id]; }
    savePrefs();
    if (S.drawerOpen && S.drawerId === id) openDrawer(id, true);
    route();
  }

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
    if (S.prefs) {
      if (S.prefs.down[item.id]) return -999;
      if (S.prefs.up[item.id]) score += 30;
      const tw = S.tw || {};
      let ts = 0;
      for (const k in tw) { if (text.includes(k)) ts += tw[k] * 3; }
      score += Math.max(-15, Math.min(12, ts));
    }
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
    else if (path === 'bili') renderBrowse({ bili: true });
    else if (head === 'c') renderBrowse({ cat: arg });
    else if (head === 'i') renderDetail(arg);
    else if (head === 'calendar') renderCalendar(parseInt(params.get('w') || '0', 10));
    else if (head === 'sources') renderSources();
    else if (head === 'people') renderPeople();
    else if (head === 'competitions') renderCompetitions();
    else if (head === 'prefs') renderPrefs();
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
    const nb = S.items.filter((i) => i.sourceType === 'bili').length;
    if (nb) out += `<a class="chip chip-bili${S.route === 'bili' ? ' active' : ''}" href="#/bili">B站<span class="n">${nb}</span></a>`;
    return out;
  }

  function srcTypeName(type) {
    const L = t();
    return type === 'wechat' ? L.wechat : type === 'bili' ? 'B站' : L.official;
  }

  function fmtPlay(n) {
    n = Number(n) || 0;
    if (n >= 10000) return (n / 10000).toFixed(1).replace('.0', '') + '万';
    return String(n);
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
      <span class="vote-row">
        <button class="vote${S.prefs && S.prefs.up[item.id] ? ' on' : ''}" data-vote="up" data-id="${esc(item.id)}" title="${t().voteUp}" aria-label="${t().voteUp}">👍</button>
        <button class="vote${S.prefs && S.prefs.down[item.id] ? ' on' : ''}" data-vote="down" data-id="${esc(item.id)}" title="${t().voteDown}" aria-label="${t().voteDown}">👎</button>
      </span>
      <h3>${hl(item.title, S._q)}</h3>
      <p class="sum">${hl(item.summary, S._q)}</p>
      ${evHTML}
      <div class="card-foot">
        <span class="srcname">${esc(item.sourceName)}</span>
        <span class="dot"></span>
        <span>${catName(item.category)}</span>
        ${item.bili ? `<span class="dot"></span><span>${esc(item.bili.author)} · ▶${fmtPlay(item.bili.play)}</span>` : ''}
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
  function renderBrowse({ intent = null, cat = null, sourceId = null, q = '', forYou = false, bili = false }) {
    S._q = q;
    let list = S.items.slice();
    if (bili) list = list.filter((i) => i.sourceType === 'bili');
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
    const isHome = !cat && !sourceId && !q && !bili && (!intent || intent === 'all') && !forYou;
    const title = cat ? (S.lang === 'en' ? S.catById[cat].en : S.catById[cat].zh)
      : sourceId ? (S.srcById[sourceId] || {}).name
      : q ? `${L.results} · ${q}`
      : bili ? 'B站 · 真人内容'
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
        ${(() => {
          const opening = (S.competitions || []).filter((c) => c.tracking && c.tracking.status === 'open');
          if (!opening.length) return '';
          return `<p class="comp-strip">⏰ 正在报名：${opening.slice(0, 3).map((c) => `<a href="#/competitions">${esc(c.name)}<span>${c.tracking.daysLeft === 0 ? '今天截止' : c.tracking.daysLeft + ' 天后截止'}</span></a>`).join('')}</p>`;
        })()}
        <p class="quick-links"><a href="#/calendar">📅 ${L.calendar}</a><a href="#/competitions">🏆 学科竞赛</a><a href="#/people">👤 ${L.nav.people}</a></p>
        <div class="stats">
          <div class="stat"><b>${S.items.length}</b><span>${L.items}</span></div>
          <div class="stat"><b>${S.sources.length}</b><span>${L.sourcesN}</span></div>
          <div class="stat"><b>${(S.generatedAt || '').slice(11, 16)}</b><span>${L.updated}</span></div>
        </div>
        <p class="fresh-line" data-fresh>${freshLineHTML()}</p>
      </section>`;
    } else if (cat) {
      html += `<section class="hero" style="padding-bottom:6px"><h1 style="font-size:30px">${esc(title)}</h1><p>${esc(S.catById[cat].desc || '')}</p></section>`;
    } else if (sourceId) {
      const s = S.srcById[sourceId];
      html += `<section class="hero" style="padding-bottom:6px"><h1 style="font-size:30px">${esc(s ? s.name : L.noSource)}</h1>
        <p>${s ? srcTypeName(s.type) : ''}</p>
        ${sourceCrawlHTML(sourceId)}</section>`;
    } else if (q) {
      html += `<section class="hero" style="padding-bottom:6px"><h1 style="font-size:30px">${esc(title)}</h1><p>${list.length} ${L.items}</p></section>`;
    } else {
      html += `<section class="hero" style="padding-bottom:6px"><h1 style="font-size:30px">${esc(title)}</h1>
        <p>${bili ? '从 B 站搜到的学生 / UP 主视频，按发布时间倒序。不是官方通稿。' : forYou ? L.heroSub : ''}</p></section>`;
    }

    html += toolbarHTML(list.length);
    html += list.length ? gridHTML(list, S.limit) : emptyHTML();
    if (list.length > S.limit) html += `<div class="more"><button class="btn ghost" id="moreBtn">${L.loadMore}</button></div>`;

    document.title = (title ? `${title} · ` : '') + (S.lang === 'en' ? S.site.enName : S.site.name);
    app().innerHTML = html;
  }

  function sourceCrawlHTML(id) {
    const L = t();
    const c = S.crawl && S.crawl.sources ? S.crawl.sources.find((x) => x.id === id) : null;
    if (!c) return '';
    if (!c.ok) return `<p class="src-crawl bad">${L.srcErr.replace('{err}', esc(c.err || ''))}</p>`;
    return `<p class="src-crawl">${L.srcCrawl.replace('{age}', relAgeText(S.crawl.at)).replace('{got}', c.got).replace('{n}', c.new || 0)}</p>`;
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
        ${s ? `<span>${srcTypeName(s.type)}</span>` : ''}
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
      <div class="dt-actions">${original}
        <button class="btn ghost${S.prefs && S.prefs.up[item.id] ? ' voted' : ''}" data-vote="up" data-id="${esc(item.id)}">👍 ${t().voteUp}</button>
        <button class="btn ghost${S.prefs && S.prefs.down[item.id] ? ' voted' : ''}" data-vote="down" data-id="${esc(item.id)}">👎 ${t().voteDown}</button>
      </div>`;
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
  function openDrawer(id, keep) {
    const item = S.items.find((i) => i.id === id);
    if (!item) return;
    S.drawerId = id;
    if (!keep) S.scrollY = window.scrollY;
    const drawer = $('#drawer');
    drawer.innerHTML = `<div class="drawer-backdrop" data-close></div>
      <aside class="drawer-panel" role="dialog" aria-modal="true">
        <div class="drawer-bar">
          <button class="icon-btn" data-close aria-label="${t().close}">✕</button>
          <span class="drawer-hint">${esc(item.sourceName)}${item.bili ? ' · ' + esc(item.bili.author) + ' · ▶' + fmtPlay(item.bili.play) : ''}</span>
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
      <span class="nm">${esc(s.name)}<em class="st ${s.verified ? 'ok' : 'pending'}">${s.verified ? L.verified : L.toVerify} · ${srcTypeName(s.type)}</em></span>
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
    const { params } = parseHash();
    const colId = params.get('college') || '';
    const colleges = (S.peopleColleges && S.peopleColleges.length)
      ? S.peopleColleges : (S.colleges || []);
    const people = (S.people || []).filter((p) => !colId || p.collegeId === colId);
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
          <span class="cl">${esc(p.college)}${p.dept ? ' · ' + esc(p.dept) : ''} · ${L.peopleLink} ↗</span>
          ${p.research ? `<span class="rc">${esc(p.research)}</span>` : ''}</span></a>`).join('')}</div>`).join('')
      : `<div class="empty"><b>${L.peopleEmpty}</b></div>`;
    document.title = `${L.peopleTitle} · ${S.lang === 'en' ? S.site.enName : S.site.name}`;
    const plans = S.plans || [];
    const planHTML = plans.length ? `<div class="grp-title">培养方案 · ${plans.length}</div>
      <div class="plan-list">${plans.map((p) => `<a class="plan" href="${esc(p.pdf || p.url)}" target="_blank" rel="noopener">
        <span class="pn">${esc(p.title)}</span><span class="pa">PDF ↗</span></a>`).join('')}</div>` : '';
    const colChips = colleges.map((c) => `<button class="chip${colId === c.id ? ' on' : ''}" data-college="${esc(c.id)}">${esc(c.name)}</button>`).join('');
    app().innerHTML = `<section class="src-head"><h1>${L.peopleTitle}</h1><p>${L.peopleSub}</p></section>
      <div class="chip-row" id="peopleCols"><button class="chip${colId ? '' : ' on'}" data-college="">全部</button>${colChips}</div>
      ${body}${planHTML}`;
    const row = $('#peopleCols');
    if (row) row.addEventListener('click', (e) => {
      const b = e.target.closest('[data-college]');
      if (!b) return;
      const id = b.getAttribute('data-college');
      go(`/people${id ? '?college=' + encodeURIComponent(id) : ''}`);
    });
  }

  function compStatus(c) {
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
      ['related', `与我相关 ${related.length}`], ['notice', `有校内通知 ${notices.length}`]]
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
      <div class="chip-row" id="compFilters">${fchips}</div>
      </section>${main}`;
    const row = $('#compFilters');
    if (row) row.addEventListener('click', (e) => {
      const b = e.target.closest('[data-f]');
      if (!b) return;
      const f = b.getAttribute('data-f');
      go(`/competitions${f ? '?f=' + f : ''}`);
    });
  }

  function renderPrefs() {
    $('#chips').hidden = true;
    const L = t();
    const up = Object.keys(S.prefs.up).length, down = Object.keys(S.prefs.down).length;
    const tw = S.tw || {};
    const toks = Object.entries(tw).sort((a, b) => b[1] - a[1]);
    const body = (up || down)
      ? `<div class="prefs-stats"><span class="tag">👍 ${L.prefsUp} ${up}</span><span class="tag">👎 ${L.prefsDown} ${down}</span></div>
        <div class="grp-title">${L.prefsTokens}</div>
        <div class="roster-chips">${toks.map(([k, v]) => `<span class="roster-chip${v > 0 ? ' rel' : ''}">${esc(k)} · ${v > 0 ? '+' : ''}${Math.round(v * 10) / 10}</span>`).join('')}</div>
        <p style="margin-top:22px"><button class="btn ghost" id="clearPrefs">${L.prefsClear}</button></p>`
      : `<div class="empty"><b>${L.prefsEmpty}</b></div>`;
    document.title = `${L.prefsTitle} · ${S.lang === 'en' ? S.site.enName : S.site.name}`;
    app().innerHTML = `<section class="src-head"><h1>${L.prefsTitle}</h1><p>${L.prefsHint}</p></section>${body}`;
    const btn = $('#clearPrefs');
    if (btn) btn.addEventListener('click', () => { S.prefs = { up: {}, down: {} }; savePrefs(); route(); });
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

  /* ---------------- freshness ---------------- */
  // UTC 字符串（无时区）按 UTC 解析，避免显示成「8 小时前」
  function asDate(iso) {
    if (!iso) return null;
    const hasZone = /[zZ]$|[+-]\d{2}:?\d{2}$/.test(iso);
    const needsZ = !hasZone && iso.includes('T');
    return new Date(needsZ ? iso + 'Z' : iso);
  }
  function fmtLocal(iso) {
    const d = asDate(iso);
    if (!d || isNaN(d)) return '';
    const p2 = (n) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${p2(d.getMonth() + 1)}-${p2(d.getDate())} ${p2(d.getHours())}:${p2(d.getMinutes())}`;
  }

  function relAgeText(iso) {
    const dt = asDate(iso);
    if (!dt || isNaN(dt)) return '';
    const L = t();
    const m = Math.max(0, Math.round((Date.now() - dt.getTime()) / 60000));
    if (m < 1) return L.relNow;
    if (m < 60) return L.relMin.replace('{n}', m);
    const h = Math.floor(m / 60);
    if (h < 24) return L.relHour.replace('{n}', h);
    const d = Math.floor(h / 24);
    return d === 1 ? L.relDay : L.relDays.replace('{n}', d);
  }

  function newIn(hours) {
    const cut = Date.now() - hours * 36e5;
    return (S.items || []).filter((i) => i.publishedAt && asDate(i.publishedAt).getTime() >= cut).length;
  }

  function syncCrawlLine() {
    const el = $('#footCrawl');
    if (!el) return;
    const L = t();
    const c = S.crawl;
    if (!c) { el.textContent = ''; return; }
    el.textContent = L.crawlLine
      .replace('{age}', relAgeText(c.at))
      .replace('{ok}', c.ok).replace('{all}', c.ok + c.failed).replace('{n}', c.new);
  }

  function freshLineHTML() {
    const L = t();
    const age = `<b>${esc(relAgeText(S.generatedAt))}</b>`;
    const n = `<b>${newIn(24)}</b>`;
    return `<span>${L.freshSync.replace('{age}', age)}</span><span>${L.freshNew.replace('{n}', n)}</span>`
      + `<span>最新一条 ${esc(relAgeText((S.items[0] || {}).publishedAt || ''))}</span>`;
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
    const freshAge = S.generatedAt ? (Date.now() - asDate(S.generatedAt).getTime()) / 36e5 : 99;
    const dot = $('#freshDot');
    if (dot) {
      dot.className = 'fresh-dot ' + (freshAge < 2 ? 'ok' : freshAge < 12 ? 'warn' : 'bad');
      dot.title = (S.lang === 'en' ? 'Updated ' : '更新于 ') + fmtLocal(S.generatedAt).slice(5);
    }
    const demoPart = S.demoCount ? ` · ${L.demoNote.replace('{n}', S.demoCount)}` : '';
    const ageH = S.generatedAt ? (Date.now() - asDate(S.generatedAt).getTime()) / 36e5 : 0;
    const stale = ageH > 24 ? ` · <b style="color:var(--accent)">${L.stale}</b>` : '';
    syncCrawlLine();
    $('#footMeta').innerHTML = S.items.length
      ? `${S.items.length} ${L.items} · ${S.sources.length} ${L.sourcesN}${demoPart} · ${L.updated} ${fmtLocal(S.generatedAt)}${stale}`
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

      const vote = e.target.closest('.vote');
      if (vote) { e.preventDefault(); e.stopPropagation(); toggleVote(vote.dataset.id, vote.dataset.vote); return; }

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
    else if (path === 'bili') renderBrowse({ bili: true });
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
      if (await refreshData() > 0) route();
    });
    // 每隔 3 分钟静默拉一次最新数据（页面保持前台时）
    setInterval(async () => {
      if (document.visibilityState !== 'visible') return;
      if (Date.now() - lastLoad < 3 * 60 * 1000) return;
      lastLoad = Date.now();
      const updated = await refreshData();
      if (updated > 0) {
        const { path, params } = parseHash();
        if (path !== 'i') route();   // 详情抽屉打开时不打断阅读
      }
    }, 60 * 1000);
    // 相对时间（「12 分钟前」）自己往前走，不用刷新页面
    setInterval(() => {
      const el = document.querySelector('[data-fresh]');
      if (el && !window.__CK_DATA__) el.innerHTML = freshLineHTML();
      syncCrawlLine();
    }, 30 * 1000);
  }

  const LS_KEY = 'ck-cache-v1';
  function saveCache(payload, srcPayload) {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify({ g: S.generatedAt, items: payload.items, sources: srcPayload.sources }));
    } catch (e) { /* 超配额就放弃缓存，不影响使用 */ }
  }
  function loadCache() {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (!raw) return null;
      const d = JSON.parse(raw);
      return (d && d.items && d.items.length) ? d : null;
    } catch (e) { return null; }
  }

  function registerSW() {
    if (!('serviceWorker' in navigator) || location.protocol === 'file:') return;
    navigator.serviceWorker.register('sw.js').catch(() => {});
  }

  async function refreshData() {
    if (window.__CK_DATA__) return 0;
    try {
      const [a, b] = await Promise.all([
        fetch('data/items.json?t=' + Date.now(), { cache: 'no-store' }),
        fetch('data/sources.json?t=' + Date.now(), { cache: 'no-store' })
      ]);
      if (!a.ok) return 0;
      const payload = await a.json();
      const srcPayload = await b.json();
      const prevGen = S.generatedAt;
      const prevLen = (S.items || []).length;
      S.items = payload.items || [];
      S.sources = srcPayload.sources || [];
      S.sources.forEach((s) => { S.srcById[s.id] = s; });
      S.generatedAt = payload.generatedAt || S.generatedAt;
      fetch('data/crawl_report.json?t=' + Date.now(), { cache: 'no-store' })
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => { if (d) { S.crawl = d.latest || null; syncCrawlLine(); } })
        .catch(() => {});
      S.demoCount = S.items.filter((i) => i.demo).length;
      applyLang();
      if (S.generatedAt === prevGen) return 0;
      return Math.max(1, S.items.length - prevLen);
    } catch (e) {
      return 0;
    }
  }

  function hydrate(d) {
    S.items = d.items || [];
    S.sources = d.sources || [];
    S.srcById = {};
    S.sources.forEach((x) => { S.srcById[x.id] = x; });
    S.generatedAt = d.g || '';
    S.demoCount = S.items.filter((i) => i.demo).length;
    bind();
    applyLang();
    route();
  }

  async function boot() {
    applyTheme();
    const cached = loadCache();
    if (cached) hydrate(cached);   // 秒开：先画缓存，再悄悄换网络数据
    try {
      let payload, srcPayload;
      if (window.__CK_DATA__) {
        payload = window.__CK_DATA__.items;
        srcPayload = window.__CK_DATA__.sources;
        S.peopleData = window.__CK_DATA__.people || null;
        S.plansData = window.__CK_DATA__.plans || null;
        S.competitionsData = window.__CK_DATA__.competitions || null;
    S.crawl = window.__CK_DATA__.crawl || null;
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
      loadPrefs();
      S.people = (S.peopleData && S.peopleData.people) || [];
      S.peopleColleges = (S.peopleData && S.peopleData.colleges) || [];
      S.plans = (S.plansData && S.plansData.plans) || [];
      S.competitions = (S.competitionsData && S.competitionsData.items) || [];
      S.generatedAt = payload.generatedAt || '';
      fetch('data/crawl_report.json?t=' + Date.now(), { cache: 'no-store' })
        .then((r) => (r.ok ? r.json() : null))
        .then((d) => { if (d && d.latest) { S.crawl = d.latest; syncCrawlLine(); } })
        .catch(() => {});
      S.demoCount = S.items.filter((i) => i.demo).length;
      if (!cached) { bind(); applyLang(); route(); }
      saveCache(payload, srcPayload);
      registerSW();
    } catch (err) {
      app().innerHTML = `<div class="empty"><b>数据没能加载</b>${esc(err.message)}</div>`;
    }
  }

  boot();
})();