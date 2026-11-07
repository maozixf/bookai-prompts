# -*- coding: utf-8 -*-
"""生成单文件可搜索 HTML（含场景速查、分类筛选、一键复制）"""
import json, os

OUT = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(OUT, "prompts.json"), encoding="utf-8"))
P = D["prompts"]

from collections import Counter
dup = Counter(r["cn"] for r in P)
SUF = {"库": "·模板库", "清单": "·清单"}

rows = []
for i, r in enumerate(P):
    cn = r["cn"] + (SUF.get(r["kind"], "·" + r["kind"]) if dup[r["cn"]] > 1 else "")
    rows.append({
        "i": i, "c": cn, "e": r["en"], "m": r["emoji"], "k": r["kind"],
        "g": r["cat"], "u": r["url"], "s": r["skills"][:5], "n": r["tpl"],
        "d": r["intro"][:90], "t": r["copy"], "x": r["search"][:2200],
        "a": " ".join(r["skills"]).lower() + " " + (r.get("alias") or ""),
        "tl": r["templates"] if r["kind"] == "库" else None,
    })

slug2i = {r["slug"]: i for i, r in enumerate(P)}
scen = []
for task, slugs in D["scenarios"]:
    ids = [slug2i[s] for s in slugs if s in slug2i]
    if ids:
        scen.append([task, ids])

cats = [c for c in D["categories"] if any(r["cat"] == c for r in P)]
counts = {c: sum(1 for r in P if r["cat"] == c) for c in cats}

payload = {
    "rows": rows, "cats": cats, "counts": counts, "scen": scen,
    "total": len(P),
    "klabel": {"人设": "结构化人设", "清单": "角色+问题清单", "库": "角色+场景模板库", "文": "长文角色"},
}

tpl = r"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>ChatGPT 职业/人设提示词 · 分类速查（234 条）</title>
<meta name="description" content="234 条 ChatGPT 职业/人设提示词，按 15 个职能分类，含 652 条场景模板，可搜索、一键复制。">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' rx='22' fill='%232563eb'/%3E%3Ctext x='50' y='72' font-size='58' text-anchor='middle' fill='white' font-family='sans-serif' font-weight='bold'%3EP%3C/text%3E%3C/svg%3E">
<meta name="theme-color" content="#2563eb" media="(prefers-color-scheme:light)">
<meta name="theme-color" content="#0e1116" media="(prefers-color-scheme:dark)">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="提示词速查">
<meta name="mobile-web-app-capable" content="yes">
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#16181d;--sub:#6b7280;--line:#e6e8ec;--acc:#2563eb;--accbg:#eef3ff;--code:#f7f8fa}
@media(prefers-color-scheme:dark){:root{--bg:#0e1116;--card:#171b22;--ink:#e8eaed;--sub:#9aa3af;--line:#252b36;--acc:#6ea8fe;--accbg:#1b2432;--code:#11151c}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 20px 80px}
header{padding:44px 0 22px}
h1{font-size:29px;line-height:1.25;margin:0 0 10px;letter-spacing:-.02em}
.lead{color:var(--sub);font-size:14px;margin:0 0 6px}
.lead b{color:var(--ink)}
.bar{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(12px);border-bottom:1px solid var(--line);padding:calc(12px + env(safe-area-inset-top)) 0 12px;margin-bottom:22px}
.bar-in{max-width:1180px;margin:0 auto;padding:0 20px}
#q{width:100%;padding:12px 15px;font-size:15px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);outline:none}
#q:focus{border-color:var(--acc);box-shadow:0 0 0 3px var(--accbg)}
.qrow{display:flex;gap:8px;align-items:stretch}
.qrow #q{flex:1;min-width:0}
.ctoggle{flex:0 0 auto;padding:0 14px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--sub);font-size:13.5px;cursor:pointer;white-space:nowrap}
.ctoggle:hover{border-color:var(--acc);color:var(--acc)}
.chips{display:flex;gap:7px;flex-wrap:nowrap;overflow-x:auto;padding:11px 0 3px;scrollbar-width:none;
  -webkit-mask-image:linear-gradient(to right,#000 88%,transparent);mask-image:linear-gradient(to right,#000 88%,transparent)}
.chips::-webkit-scrollbar{display:none}
.chips.open{flex-wrap:wrap;overflow:visible;mask-image:none;-webkit-mask-image:none}
.chips:not(.open) .chip{flex:0 0 auto}
.chip{flex:0 0 auto;padding:6px 12px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--sub);font-size:13px;cursor:pointer;white-space:nowrap;transition:.15s}
.chip:hover{border-color:var(--acc);color:var(--acc)}
.chip.on{background:var(--acc);border-color:var(--acc);color:#fff}
.chip .n{opacity:.6;margin-left:4px;font-size:11px}
h2.sec{font-size:15px;margin:34px 0 12px;color:var(--sub);font-weight:600;letter-spacing:.04em}
.scen{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:8px}
.sc{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:11px 13px;display:flex;gap:10px;align-items:flex-start;flex-wrap:wrap}
.sc .task{font-weight:600;font-size:13.5px;flex:1 1 100%;margin-bottom:2px}
.sc a{font-size:12.5px;color:var(--acc);text-decoration:none;background:var(--accbg);padding:2px 9px;border-radius:6px;white-space:nowrap}
.sc a:hover{text-decoration:underline}
#meta{color:var(--sub);font-size:13px;margin:0 0 14px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(290px,1fr));gap:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:14px 15px;cursor:pointer;transition:.15s;position:relative}
.card:hover{border-color:var(--acc);transform:translateY(-1px);box-shadow:0 4px 16px rgba(0,0,0,.06)}
.card.open{border-color:var(--acc);grid-column:1/-1}
@keyframes flashring{0%{box-shadow:0 0 0 0 transparent}25%{box-shadow:0 0 0 4px var(--accbg)}100%{box-shadow:0 0 0 0 transparent}}
.card.flash{animation:flashring 1.3s ease}
.card h3{margin:0;font-size:15.5px;font-weight:650;display:flex;align-items:center;gap:7px;line-height:1.4}
.card h3 .em{font-size:17px}
.card .en{color:var(--sub);font-size:11.5px;margin:3px 0 7px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.badge{display:inline-block;font-size:10.5px;padding:1px 7px;border-radius:5px;font-weight:600;letter-spacing:.02em}
.b-人设{background:#eef2f7;color:#475569}.b-清单{background:#e8f7ee;color:#16794a}.b-库{background:#fff2e0;color:#a35a00}.b-文{background:#f0ecff;color:#5b46c9}
@media(prefers-color-scheme:dark){.b-人设{background:#222a36;color:#9aa7b8}.b-清单{background:#12301f;color:#5fd08c}.b-库{background:#3a2a10;color:#e0a355}.b-文{background:#251f3d;color:#a99bf0}}
.sk{color:var(--sub);font-size:12.5px;margin:0}
.pre{display:none;margin-top:12px;border-top:1px solid var(--line);padding-top:12px}
.card.open .pre{display:block}
pre{margin:0;background:var(--code);border:1px solid var(--line);border-radius:9px;padding:14px;font:12.5px/1.7 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;white-space:pre-wrap;word-break:break-word;max-height:420px;overflow:auto}
.acts{display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;align-items:center}
button.copy{background:var(--acc);color:#fff;border:0;border-radius:8px;padding:7px 15px;font-size:13px;font-weight:600;cursor:pointer}
button.copy.ghost{background:transparent;color:var(--acc);border:1px solid var(--acc)}
button.copy.ghost:hover{background:var(--accbg)}
button.copy:hover{filter:brightness(1.08)}
button.copy.done{background:#16a34a}
.acts a{font-size:12.5px;color:var(--sub);text-decoration:none;border:1px solid var(--line);padding:6px 11px;border-radius:8px}
.acts a:hover{color:var(--acc);border-color:var(--acc)}
.empty{color:var(--sub);padding:40px 0;text-align:center}
.empty .chip{display:inline-block;margin:6px 4px 0}
.libbar{display:flex;align-items:center;gap:10px;margin:14px 0 8px;font-size:13px;color:var(--sub);font-weight:600}
.libbar .sp{flex:1}
.lead2{font-size:12px;color:var(--sub);margin:0 0 6px;letter-spacing:.04em}
.libs{margin-top:4px}
.libs details{border:1px solid var(--line);border-radius:9px;margin-bottom:6px;background:var(--code)}
.libs summary{cursor:pointer;padding:9px 12px;font-weight:600;font-size:13.5px;list-style:none;display:flex;gap:8px;align-items:center}
.libs summary::-webkit-details-marker{display:none}
.libs summary:before{content:"▸";color:var(--sub);font-size:11px;transition:.15s}
.libs details[open] summary:before{content:"▾"}
.libs summary .cnt{margin-left:auto;font-size:11.5px;color:var(--sub);font-weight:500}
.libs .grp{padding:0 14px 10px 30px}
.libs h5{margin:13px 0 5px;padding:0;font-size:13.5px;font-weight:600;color:var(--ink);line-height:1.5}
.libs h5:first-child{margin-top:6px}
.libs table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:12.5px}
.libs td{border-top:1px solid var(--line);padding:7px 0;vertical-align:top;line-height:1.55}
.libs td.n{width:108px;padding-right:12px;color:var(--sub);word-break:break-word}
.libs td.p{cursor:pointer}
.libs td.p:hover{color:var(--acc)}
.libs td.p:after{content:" ⧉";opacity:0;font-size:10px}
.libs td.p:hover:after{opacity:.55}
@media(max-width:560px){
  .libs summary{padding:9px 10px;gap:6px}
  .libs summary:before{font-size:9px}
  .libs .grp{padding:0 10px 10px 23px}
  .libs td.n{width:96px;padding-right:8px}
}
#toast{position:fixed;left:50%;bottom:28px;transform:translate(-50%,20px);background:#111827;color:#fff;padding:9px 16px;border-radius:9px;font-size:13px;opacity:0;pointer-events:none;transition:.22s;z-index:99}
#toast.on{opacity:1;transform:translate(-50%,0)}
footer{color:var(--sub);font-size:12.5px;margin-top:50px;border-top:1px solid var(--line);padding-top:16px}
</style>
</head>
<body>
<div class="bar"><div class="bar-in">
  <div class="qrow">
    <input id="q" placeholder="搜岗位、技能或任务，例如：小红书 / SQL / 渗透 / JD / 竞品">
    <button id="ctoggle" class="ctoggle">分类 ▾</button>
  </div>
  <div class="chips" id="chips"></div>
</div></div>
<div class="wrap">
<header>
  <h1>ChatGPT 职业 / 人设提示词 · 分类速查</h1>
  <p class="lead">共 <b id="tot"></b> 条，抓取自 bookai.top 职业提示词栏目，正文已离线存档。</p>
  <p class="lead">不知道挑哪个：先在下面「场景速查」找到你要干的事；知道岗位：直接搜或点分类。点卡片展开全文，一键复制。</p>
</header>
<h2 class="sec">场景速查 · 我要做的事</h2>
<div class="scen" id="scen"></div>
<h2 class="sec">全部提示词</h2>
<p id="meta"></p>
<div class="grid" id="grid"></div>
<div class="empty" id="empty" style="display:none"></div>
<div id="toast"></div>
<footer>数据来源：<a href="https://bookai.top/docs/category/chatgpt-prompt%E6%8F%90%E7%A4%BA%E8%AF%8D-%E8%81%8C%E4%B8%9A" style="color:inherit">bookai.top</a> ｜ 抓取于 2026-11-07 ｜ 本地单文件，可离线使用</footer>
</div>
<script>
const D = __DATA__;
const rows = D.rows, K = D.klabel;
document.getElementById('tot').textContent = D.total;
const esc = s => s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

// 分类 chips
const chips = document.getElementById('chips');
const ctogl = document.getElementById('ctoggle');
function setChips(open) {
  chips.classList.toggle('open', open);
  ctogl.textContent = open ? '收起 ▴' : '分类 ▾';
}
setChips(window.matchMedia('(min-width: 900px)').matches);
ctogl.onclick = () => setChips(!chips.classList.contains('open'));
chips.addEventListener('click', e => {
  if (e.target.closest('.chip')) setChips(false);
});
let cat = 'all';
const mk = (label, key, n) => {
  const b = document.createElement('button');
  b.className = 'chip' + (key === 'all' ? ' on' : '');
  b.dataset.k = key;
  b.innerHTML = label + (n != null ? '<span class="n">' + n + '</span>' : '');
  b.onclick = () => { cat = key; [...chips.children].forEach(c => c.classList.toggle('on', c === b)); render(); };
  chips.appendChild(b);
};
mk('全部', 'all', D.total);
D.cats.forEach(c => mk(c, c, D.counts[c]));

// 场景速查
const scen = document.getElementById('scen');
D.scen.forEach(([task, ids]) => {
  const d = document.createElement('div');
  d.className = 'sc';
  d.innerHTML = '<div class="task">' + esc(task) + '</div>' + ids.map(i => {
    const r = rows[i];
    return '<a href="#' + i + '" data-i="' + i + '">' + r.m + ' ' + esc(r.c) + '</a>';
  }).join('');
  scen.appendChild(d);
});
scen.addEventListener('click', e => {
  const a = e.target.closest('a[data-i]');
  if (!a) return;
  e.preventDefault();
  const i = +a.dataset.i;
  if (!grid.querySelector('.card[data-i="' + i + '"]')) resetFilters();
  openCard(i, true);
});

// 渲染
const grid = document.getElementById('grid'), meta = document.getElementById('meta');
let q = '';
document.getElementById('q').oninput = e => { q = e.target.value.trim().toLowerCase(); render(); };

function match(r) {
  if (cat !== 'all' && r.g !== cat) return false;
  if (!q) return true;
  const hay = (r.x || (r.c + ' ' + r.e + ' ' + r.s.join(' ') + ' ' + r.d)).toLowerCase();
  return q.split(/\s+/).every(w => hay.includes(w));
}

function score(r, words) {
  let s = 0;
  const name = (r.c + ' ' + r.e + ' ' + r.g).toLowerCase();
  const key = (r.a || r.s.join(' ')).toLowerCase();
  for (const w of words) {
    if (name.includes(w)) s += 100;
    else if (key.includes(w)) s += 45;
    else if ((r.x || '').includes(w)) s += 8;
  }
  return s;
}

function render() {
  const words = q ? q.split(/\s+/) : [];
  let list = rows.filter(match);
  if (words.length) {
    list = list.map(r => ({ r, sc: score(r, words) }))
               .sort((a, b) => b.sc - a.sc || a.r.i - b.r.i)
               .map(o => o.r);
  }
  meta.textContent = '显示 ' + list.length + ' / ' + D.total + ' 条' + (cat === 'all' ? '' : ' · ' + cat);
  document.getElementById('empty').style.display = list.length ? 'none' : 'block';
  if (!list.length) {
    document.getElementById('empty').innerHTML = '没有匹配 <b>' + esc(q) + '</b> 的岗位，换个词试试：' +
      ['小红书', 'PRD', 'SQL', '渗透', 'JD', '竞品', '直播', 'logo', '大模型', '合同', '剪辑']
        .map(w => '<button class="chip" onclick="document.getElementById(\'q\').value=\'' + w +
                  '\';document.getElementById(\'q\').dispatchEvent(new Event(\'input\'))">' + w + '</button>')
        .join(' ');
  }
  grid.innerHTML = list.map(r => {
    const isLib = r.k === '库' && r.tl && r.tl.length;
    const sk = r.k === '库' ? '核心角色 Prompt + ' + r.n + ' 条场景模板'
             : r.k === '清单' ? '现成问题清单 ' + r.n + ' 条 · ' + r.s.slice(0, 3).join('、')
             : (r.s.join('、') || r.d);
    return '<div class="card" data-i="' + r.i + '">'
      + '<h3><span class="em">' + r.m + '</span>' + esc(r.c) + '</h3>'
      + '<div class="en">' + esc(r.e || r.g) + '</div>'
      + '<span class="badge b-' + r.k + '">' + K[r.k] + '</span>'
      + '<p class="sk" style="margin-top:7px">' + esc(sk) + '</p>'
      + '<div class="pre">'
      + (isLib ? '<div class="lead2">核心角色 PROMPT</div>' : '')
      + '<pre>' + esc(r.t) + '</pre>'
      + '<div class="acts">'
      + (isLib
          ? '<button class="copy" data-copy="core">复制角色 Prompt</button>'
            + '<button class="copy ghost" data-copy="all">复制角色 + ' + r.n + ' 条模板</button>'
          : '<button class="copy" data-copy="all">复制全文</button>')
      + '<a href="' + r.u + '" target="_blank" rel="noopener">打开原文 ↗</a></div>'
      + (isLib ? libHtml(r) : '')
      + '</div></div>';
  }).join('');
}

const libCache = {};
function libHtml(r) {
  if (libCache[r.i]) return libCache[r.i];
  const total = r.tl.reduce((a, g) => a + g.subs.reduce((b, s) => b + s.items.length, 0), 0);
  let h = '<div class="libbar">场景模板库<span class="sp"></span>共 ' + total + ' 条 · 点任一条即复制</div><div class="libs">';
  r.tl.forEach((g, gi) => {
    let cnt = g.subs.reduce((a, s) => a + s.items.length, 0);
    h += '<details' + (gi === 0 ? ' open' : '') + '><summary>' + esc(g.g)
      + '<span class="cnt">' + cnt + ' 条</span></summary><div class="grp">';
    g.subs.forEach((s, si) => {
      h += '<h5>' + esc(s.s) + '</h5><table>';
      s.items.forEach((it, ii) => {
        h += '<tr><td class="n">' + esc(it.n) + '</td><td class="p" data-g="' + gi
          + '" data-s="' + si + '" data-n="' + ii + '">' + esc(it.p) + '</td></tr>';
      });
      h += '</table>';
    });
    h += '</div></details>';
  });
  return (libCache[r.i] = h + '</div>');
}

function fullText(r) {
  if (!r.tl) return r.t;
  let s = r.t + '\n\n—— 场景模板库 ——';
  r.tl.forEach(g => {
    s += '\n\n【' + g.g + '】';
    g.subs.forEach(su => {
      s += '\n· ' + su.s;
      su.items.forEach(it => { s += '\n  - ' + it.n + '：' + it.p; });
    });
  });
  return s;
}

grid.addEventListener('click', e => {
  const card = e.target.closest('.card');
  if (!card) return;
  const r = rows[+card.dataset.i];
  const td = e.target.closest('td.p');
  if (td) {
    const it = r.tl[+td.dataset.g].subs[+td.dataset.s].items[+td.dataset.n];
    copyText(it.p, '已复制：' + it.n);
    return;
  }
  const btn = e.target.closest('button.copy');
  if (btn) {
    const core = btn.dataset.copy === 'core';
    copyText(core ? r.t : fullText(r), core ? '已复制角色 Prompt' : '已复制：' + r.c);
    return;
  }
  if (e.target.closest('a')) return;
  if (e.target.closest('summary')) return;
  card.classList.toggle('open');
});

function resetFilters() {
  q = '';
  cat = 'all';
  document.getElementById('q').value = '';
  [...chips.children].forEach(c => c.classList.toggle('on', c.dataset.k === 'all'));
  render();
}

function openCard(i, scroll) {
  const card = grid.querySelector('.card[data-i="' + i + '"]');
  if (!card) return;
  grid.querySelectorAll('.card.open').forEach(c => { if (c !== card) c.classList.remove('open'); });
  card.classList.add('open');
  if (scroll) {
    card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    card.classList.remove('flash');
    void card.offsetWidth;
    card.classList.add('flash');
    setTimeout(() => card.classList.remove('flash'), 1300);
  }
}

let toastT;
function toast(msg) {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.classList.add('on');
  clearTimeout(toastT);
  toastT = setTimeout(() => t.classList.remove('on'), 1600);
}
function copyText(txt, msg) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(txt).then(() => toast(msg), () => { fallback(txt); toast(msg); });
  } else { fallback(txt); toast(msg); }
}
function fallback(txt) {
  const ta = document.createElement('textarea');
  ta.value = txt; ta.style.position = 'fixed'; ta.style.opacity = '0';
  document.body.appendChild(ta); ta.select();
  try { document.execCommand('copy'); } catch (e) {}
  document.body.removeChild(ta);
}

render();
</script>
</body>
</html>
"""

html = tpl.replace("__DATA__", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
# index.html 供 GitHub Pages 使用；中文名副本方便本地双击打开（不入库）
for name in ("index.html", "ChatGPT职业提示词-速查.html"):
    open(os.path.join(OUT, name), "w", encoding="utf-8").write(html)
print("written: index.html", round(len(html) / 1024), "KB")
