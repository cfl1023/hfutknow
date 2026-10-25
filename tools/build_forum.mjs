// 把校外语料（贴吧 / B 站）转成站点可直接加载的数据。
// 数据源：../corpus/tieba_threads.jsonl、../corpus/bili_videos.jsonl
// 产物：site/data/forum-tieba.json、site/data/forum-bili.json
// 用法：node tools/build_forum.mjs
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const CORPUS = path.resolve(ROOT, '..', 'corpus');
const OUT = path.join(ROOT, 'site', 'data');

const readJsonl = (p) => (fs.existsSync(p)
  ? fs.readFileSync(p, 'utf8').split('\n').filter(Boolean).map((l) => { try { return JSON.parse(l); } catch { return null; } }).filter(Boolean)
  : []);

// —— 分类（面向集成电路大一 + 翡翠湖）——
const CATS = [
  ['shengxue', '保研·转专业·绩点', /保研|考研|复试|调剂|绩点|转专业|双一流|推免|上岸|排名|期中|期末|挂科|补考|大物|高数|线代|四六级|加权/],
  ['ke', '课程·老师·教务', /选课|课程|老师|考试|学分|课表|作业|实验|教材|课本|图书馆|自习|教室|教务|培养方案|小学期|选修|教材|点名/],
  ['shenghuo', '食堂·宿舍·生活', /食堂|宿舍|洗澡|空调|快递|校园卡|澡堂|门禁|外卖|床|电费|热水|网费|宽带|洗衣|超市|军训|校医院/],
  ['shetuan', '社团·竞赛·大创', /社团|大创|竞赛|战队|招新|RoboMaster|学生会|比赛|创新创业|志愿者|协会|蓝桥|数学建模|电赛|IC|芯片|集成电路|微电子/],
  ['jiuye', '就业·实习·考研后路', /秋招|春招|招聘|宣讲|面试|offer|实习|就业|工资|薪资|简历|考公|选调|三方|入职|裁员|保底/],
  ['hefei', '合肥本地', /合肥|轨道交通|地铁|租房|公交|打车|同城|房价|天气|景点|商圈|探店|美食|夜宵|周末去哪儿|翡翠湖/],
  ['tucao', '校园吐槽·水贴', /分手|恋爱|表白|室友|痛苦|累|破防|崩溃|emo|绝望|焦虑|吐槽|水贴|孤独|抑郁|想家|哈基|抽象/],
];
const SQUASH = /合肥工业大学|合肥工大|合工大|宣城校区|工大/g;
const catOf = (txt) => { const norm = String(txt).replace(SQUASH, "工大"); for (const [id, , re] of CATS) if (re.test(norm)) return id; return "qita"; };

// —— 相关性过滤：他只关心学校/学生生活，合肥买房租房地铁美食一律不要 ——
const HFUT_RE = /合工大|合肥工大|合肥工业|宣城校区|翡翠湖校区|斛兵塘|屯溪路|六安路|(?<![理哈北华深浙广南])工大/;
const STUDENT_RE = /大学生|在校|校园|学生|新生|大一|大二|大三|大四|小登|学长|学姐|室友|宿舍|食堂|图书馆|社团|招新|选课|绩点|保研|转专业|考研|复试|四六级|大创|竞赛|军训|开学|放假|奖学金|寝室|辅导员|导员|期末|期中|挂科|补考|专业|课程|老师|学分|课表|教务|校招|秋招|春招|实习|简历|offer|校医院|校园卡|班长|毕业|读研|考公|选调|实验|论文|导师/;
const CITY_NOISE = /租房|买房|房价|楼盘|装修|搬家|二手房|中介|地铁|公交|打车|美食|探店|打卡|同城|周末去哪儿|景点|商圈|夜宵|工资|月薪|年薪|找工作|招聘会|相亲|婚纱|宠物|装修|加盟|开店|买菜|菜市场/;
const CAMPUS_BAR = /合肥工业大学|宣城校区/;
const TIEBA_DROP = /^水贴专区|水贴专区|签到|盖楼|经验\+3|每日一水|来水|水一贴|怎么这么坏|啊啊啊|鼠鼠|烂活|抽奖|广告|招聘代理|兼职群|加微信|私聊我/;
const CAMPUS_KW = /^合工大|^合肥工业大学/;
// 贴吧：只看本校两个吧；合肥吧只留标题里出现工大的
const relevantTieba = (bar, title) => {
  const b = String(bar || '');
  const t = String(title || '');
  if (CAMPUS_BAR.test(b)) return 'hf';
  if (HFUT_RE.test(t)) return 'hf';
  return '';
};
// B 站：只看标题里真的点名工大的（简介/标签里蹭到的不算），且排除考研卷/蹭流量
const BILI_DROP = /超越|模拟卷|逐题|考研数学|押题|真题讲解|张雪峰|志愿填报|择校|分数线/;
const relevantBili = (kw, title, txt) => {
  const t = String(title || '');
  if (HFUT_RE.test(t) && !BILI_DROP.test(t) && !CITY_NOISE.test(t)) return 'hf';
  return '';
};

// 个人加权：集成电路大一 + 翡翠湖 + 新生关心的事
const PERSONAL = [
  ['集成电路', 8], ['微电子', 8], ['芯片', 6], ['电子', 3], ['大一', 6], ['小登', 6], ['新生', 6],
  ['翡翠湖', 5], ['转专业', 6], ['保研', 6], ['选课', 5], ['绩点', 5], ['军训', 4],
  ['食堂', 3], ['宿舍', 3], ['社团', 3], ['大创', 4], ['竞赛', 3], ['四六级', 4], ['课程', 3],
];
const scoreText = (txt) => PERSONAL.reduce((s, [k, w]) => (txt.includes(k) ? s + w : s), 0);

// —— 时间解析 ——
const NOW = new Date();
function parseCn(s) {
  if (!s) return null;
  const str = String(s).trim();
  let m;
  // 贴吧列表里的「今天 HH:MM」只有时分，按今天算（这是最新的那批帖）
  m = /^(\d{1,2}):(\d{2})$/.exec(str);
  if (m) {
    const d = new Date(NOW);
    d.setHours(Number(m[1]), Number(m[2]), 0, 0);
    if (d.getTime() > NOW.getTime()) d.setDate(d.getDate() - 1);
    return d;
  }
  if (/^刚刚$/.test(str)) return new Date(NOW.getTime() - 60e3);
  m = /^(\d+)\s*分钟前/.exec(str);
  if (m) return new Date(NOW.getTime() - Number(m[1]) * 60e3);
  m = /^(\d+)\s*小时前/.exec(str);
  if (m) return new Date(NOW.getTime() - Number(m[1]) * 3600e3);
  m = /^今天\s*(\d{1,2}):(\d{2})/.exec(str);
  if (m) {
    const d = new Date(NOW);
    d.setHours(Number(m[1]), Number(m[2]), 0, 0);
    return d;
  }
  m = /^昨天\s*(\d{1,2}):(\d{2})/.exec(str);
  if (m) {
    const d = new Date(NOW.getTime() - 86400e3);
    d.setHours(Number(m[1]), Number(m[2]), 0, 0);
    return d;
  }
  m = /^(\d+)\s*天前/.exec(str);
  if (m) return new Date(NOW.getTime() - Number(m[1]) * 86400e3);
  m = /^(\d{4})-(\d{1,2})-(\d{1,2})/.exec(str);
  if (m) return new Date(`${m[1]}-${String(m[2]).padStart(2, '0')}-${String(m[3]).padStart(2, '0')}T12:00:00+08:00`);
  m = /^(\d{1,2})-(\d{1,2})$/.exec(str);
  if (m && Number(m[1]) >= 1 && Number(m[1]) <= 12) {
    let y = NOW.getFullYear();
    if (Number(m[1]) > NOW.getMonth() + 1) y -= 1;
    return new Date(`${y}-${String(m[1]).padStart(2, '0')}-${String(m[2]).padStart(2, '0')}T12:00:00+08:00`);
  }
  return null;
}

// —— 贴吧 ——
const threads = readJsonl(path.join(CORPUS, 'tieba_threads.jsonl'));
const tieba = [];
const seenTid = new Set();
for (const t of threads) {
  const tid = String(t.tid || '');
  if (!tid || seenTid.has(tid)) continue;
  seenTid.add(tid);
  const title = String(t.title || '').replace(/\s+/g, ' ').trim();
  if (!title) continue;
  if (TIEBA_DROP.test(title)) continue;
  const rel = relevantTieba(t.bar, title);
  if (!rel) continue; // 合肥吧的城市生活帖（租房/探店/招聘）一律不进站
  const at = parseCn(t.lastReplyAt || t.when);
  const cat = catOf(`${title} ${t.bar || ''}`);
  tieba.push({
    id: `t${tid}`,
    t: title,
    a: t.author || '',
    b: t.bar || '',
    r: Number(t.replies || 0),
    at: at ? at.toISOString() : null,
    cat,
    s: scoreText(title) + (t.isTop ? 0 : 0),
    hf: rel === 'hf' ? 1 : 0,
    u: `https://tieba.baidu.com/p/${tid}`,
  });
}
tieba.sort((x, y) => (y.at || '').localeCompare(x.at || '') || y.r - x.r);

// —— B 站 ——
const videos = readJsonl(path.join(CORPUS, 'bili_videos.jsonl'));
const bili = [];
const seenBv = new Set();
for (const v of videos) {
  const bv = String(v.bvid || '');
  if (!bv || seenBv.has(bv)) continue;
  seenBv.add(bv);
  const title = String(v.title || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
  if (!title) continue;
  const txt = `${title} ${v.tag || ''} ${v.desc || ''}`;
  const rel = relevantBili(v.kw, title, txt);
  if (!rel) continue; // 只要本校本行，其他高校/合肥城市生活都不要
  bili.push({
    id: bv,
    t: title,
    a: v.author || '',
    p: Number(v.play || 0),
    at: v.pubdate ? new Date(v.pubdate * 1000).toISOString() : null,
    kw: v.kw || '',
    cat: catOf(txt),
    hf: rel === 'hf' ? 1 : 0,
    s: scoreText(txt),
    u: `https://www.bilibili.com/video/${bv}`,
  });
}
bili.sort((x, y) => (y.at || '').localeCompare(x.at || '') || y.p - x.p);

const meta = {
  generatedAt: new Date().toISOString(),
  cats: [['all', '全部'], ...CATS.map(([id, name]) => [id, name]), ['qita', '其他']],
  profile: '集成电路创新学院 · 大一 · 翡翠湖校区',
};
fs.writeFileSync(path.join(OUT, 'forum-tieba.json'), JSON.stringify({ meta, items: tieba }));
fs.writeFileSync(path.join(OUT, 'forum-bili.json'), JSON.stringify({ meta, items: bili }));

const stat = (arr) => {
  const byCat = {};
  for (const x of arr) byCat[x.cat] = (byCat[x.cat] || 0) + 1;
  return byCat;
};
console.log(JSON.stringify({
  tieba: tieba.length, bili: bili.length,
  hfut: tieba.filter((x) => x.hf).length + bili.filter((x) => x.hf).length,
  tiebaCats: stat(tieba), biliCats: stat(bili),
  sizeMB: +(((fs.statSync(path.join(OUT, 'forum-tieba.json')).size + fs.statSync(path.join(OUT, 'forum-bili.json')).size) / 1048576).toFixed(2)),
}, null, 1));
