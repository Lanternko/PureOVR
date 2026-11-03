"""球隊戰力排行檢視（使用者 2026-11-02「直接合併單頁」）：嵌進名單頁當第二個檢視，和球員分頁共用同一個眉頭，切換不重載。
用 Shadow DOM 隔離樣式（名單頁的 .pn／.av／.seg／table 規則不會污染排行表；色票與字型變數從名單頁繼承）；
資料放獨立的 teams-data.json（build_teams_page.py 產生），第一次進排行（或閒置時預載）才 fetch，每日只更新傷病時不用重建 2.3 MB 的名單頁。
網址：/rank/＝排行；/rank/LAL/＝展開某隊。對外 API：window.PureRank = {ensure(), open(abbr)}，檢視切換由 site_header.JS 負責。"""

STYLE = """@import url("https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@1,700;1,800&family=Barlow+Condensed:wght@600;700&display=swap");
*{box-sizing:border-box}
:host{--nf:"Barlow Condensed","Arial Narrow",Impact,sans-serif}
:host{display:block}
.rkroot{color:var(--fg);font-family:var(--f-body);font-size:14px}
.rkw{max-width:1360px;margin:0 auto;padding-block:16px 40px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:12px}
@media (min-width:641px){.rkw{max-width:min(1360px,calc(var(--tw,1328px) + 32px))}}
.hd{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;border-bottom:3px solid var(--fg);padding-bottom:10px}
h1{font:italic 800 4.2rem/.85 var(--nf);text-transform:uppercase;margin:0;letter-spacing:-.01em}
h1 span{display:block;font:600 1rem var(--f-body);font-style:normal;letter-spacing:.3em;color:var(--muted);margin-top:8px;text-transform:none}
.stamp{white-space:nowrap;font:700 1.15rem/1.2 var(--nf);text-transform:uppercase;letter-spacing:.06em;text-align:right;color:var(--muted)}
.stamp b{display:block;color:var(--fg);font-size:1.9rem;font-style:italic;font-weight:800}
.meta{color:var(--muted);font-size:.82rem;line-height:1.5}
.meta b{color:var(--fg);font-weight:600}
.warn{color:var(--gold)}
.vctl{display:flex;flex-wrap:wrap;gap:10px;align-items:center}
.seg{display:flex;border:1px solid var(--line);border-radius:3px;overflow:hidden}
.seg button{background:var(--panel);color:var(--muted);border:0;border-right:1px solid var(--line);font:600 .95rem var(--f-disp);letter-spacing:.04em;padding:7px 14px;cursor:pointer}
.seg button:last-child{border-right:0}
.seg button[aria-pressed="true"]{background:var(--gold);color:var(--gold-ink)}
.hint{color:var(--muted);font-size:.78rem}
button:focus-visible,th:focus-visible,tr.row:focus-visible{outline:2px solid var(--gold);outline-offset:1px}
.tbox{overflow:auto}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
thead th{background:var(--bg,#0d1014);color:var(--muted);font:700 1.3rem var(--nf);text-transform:uppercase;letter-spacing:.1em;padding:10px 8px;text-align:right;cursor:pointer;user-select:none;white-space:nowrap;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:2}
thead th.l,td.l{text-align:left}
thead th .zh{display:block;font:500 .85rem var(--f-body);opacity:.8}
thead th[aria-sort]{color:#fff;font-weight:700;box-shadow:inset 0 0 0 999px rgba(255,255,255,.05)}
thead th[aria-sort] .zh{color:#fff;font-weight:700;opacity:1}
td.sorted{box-shadow:inset 0 0 0 999px rgba(255,255,255,.05)}
td{padding:5px 8px;text-align:right;border-bottom:1px solid var(--line);white-space:nowrap;font:600 1.05rem var(--nf);letter-spacing:.02em}
tr.row{cursor:pointer}
tr.row:hover td{background:#1a2128}
tr.row.open td{background:#1d252d}
td.rk{width:72px;text-align:right;padding-right:14px;font:italic 800 1.7rem/1 var(--nf);letter-spacing:-.02em}
td.tm{font:italic 800 1.3rem/1 var(--nf);text-transform:uppercase;letter-spacing:.01em}
td.tm .tmw{display:flex;align-items:center;gap:9px}
td.tm .lg{width:32px;height:32px;flex:none;object-fit:contain}
td.tm .tt{min-width:0}
td.tm small{display:block;font:500 .7rem var(--f-body);font-style:normal;text-transform:none;color:var(--muted);letter-spacing:.04em;margin-top:2px}
td.net{font:italic 800 1.7rem/1 var(--nf);letter-spacing:-.01em}
.pos{color:var(--g-a)}.neg{color:var(--g-f)}
.inj{color:var(--g-f)}
tbody tr.row td:not(.rk):not(.net):not(.tm){color:var(--muted)}
.det td{padding:0;background:#10151a;white-space:normal;text-align:left}
.dg{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:18px;padding:12px 16px 16px}
.dg h3{margin:0 0 6px;font:700 .85rem var(--f-disp);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.dg table{font-size:.88rem}
.dg td{padding:4px 6px;border-bottom:1px solid #1a2128;white-space:normal;font:500 .9rem var(--f-body);letter-spacing:0}
.dg td.n{min-width:0;overflow-wrap:anywhere}
.dg td.n{text-align:left}
.pn{display:flex;align-items:center;gap:9px;min-width:0}
.av{flex:none;width:34px;height:34px;border-radius:50%;background:var(--panel-2);border:1px solid var(--line);overflow:hidden;display:block}
.av img{display:block;width:100%;height:100%;object-fit:cover;object-position:50% 12%}
.pn>span:last-child{min-width:0}
.sum{grid-column:1/-1;color:var(--muted);font-size:.8rem}
.sum b{color:var(--fg)}
.cm{color:var(--muted);font-size:.74rem;display:block;white-space:normal;max-width:46ch}
.cm.rt{color:var(--gold)}
.note{color:var(--muted);font-size:.8rem;line-height:1.6;border-top:1px solid var(--line);padding-top:10px}
.meta .nb{margin:0;padding-left:1.2em;color:var(--fg)}
.meta .warn{display:block}
@media (max-width:900px){.hide-m{display:none}}
@media (max-width:760px){.dg{grid-template-columns:minmax(0,1fr)}.cm{max-width:none}}
@media (max-width:640px){
  .rkroot{font-size:13px}
  h1{font-size:2.6rem}
  .stamp{font-size:.9rem}.stamp b{font-size:1.1rem}
  td.rk{width:40px;font-size:1.4rem;padding-right:8px}
  td.tm{font-size:1.1rem}
  td.net{font-size:1.5rem}
  .hide-m,thead th .zh{display:none}
  .dg td:not(:first-child){white-space:nowrap;font-size:.8rem}
  .rkw{gap:10px}
  td{padding:5px 4px}
  thead th{padding:7px 4px;font-size:1rem;letter-spacing:.02em}
  td.tm small{display:none}
  td.tm .tmw{gap:6px}
  td.tm .lg{width:26px;height:26px}
  .av{width:30px;height:30px}
  .pn{gap:7px}
  td.net{font-size:1.6rem}
  .seg button{padding:9px 16px}
  .vctl{gap:6px}
}
.msg{color:var(--muted);padding:40px 16px;text-align:center}"""

BODY = """<div class="rkroot"><div class="msg" id="msg">載入中…</div>
<div class="rkw" id="rkw" hidden>
<div class="hd"><h1>Power Ranking</h1><div class="stamp" id="stamp"></div></div>
<div class="meta" id="meta"></div>
<div class="vctl"><div class="seg" id="viewSeg" role="group" aria-label="名單版本"><button type="button" data-v="today" aria-pressed="true">可用</button><button type="button" data-v="c" aria-pressed="false">全員</button></div>
<span class="hint" id="viewHint"></span></div>
<div class="tbox"><table id="tbl"><thead><tr>
<th data-k="rank" class="rk">#</th><th data-k="name" class="l">球隊</th><th data-k="net" aria-sort="descending">Net<span class="zh">淨效率</span></th>
<th data-k="ortg" class="hide-m">ORtg<span class="zh">進攻</span></th><th data-k="drtg" class="hide-m">DRtg<span class="zh">防守</span></th>
<th data-k="wpct">戰績<span class="zh">W-L</span></th><th data-k="pred">預測勝場<span class="zh">全季</span></th><th data-k="nOut">傷兵<span class="zh">不可用</span></th>
</tr></thead><tbody id="tb"></tbody></table></div>
<div class="note" id="note"></div>
</div></div>"""

JS = r"""<script>(()=>{
const host=document.getElementById('rankHost'),tpl=document.getElementById('rankTpl');if(!host||!tpl)return;
const root=host.attachShadow({mode:'open'});root.append(tpl.content.cloneNode(true));
let D=null,T=[],loading=null;
const $=s=>root.querySelector(s),esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let view=(()=>{try{return localStorage.getItem('bbac.teamsView')==='c'?'c':'today'}catch(e){return 'today'}})(),sk='net',sd=-1,open=null;
const CDN='https://cdn.nba.com/';
const logo=id=>id?'<img class="lg" alt="" loading="lazy" src="'+CDN+'logos/nba/'+id+'/global/D/logo.svg" onerror="this.style.visibility=\'hidden\'">':'<span class="lg"></span>';
const av=pid=>'<span class="av">'+(pid?'<img alt="" loading="lazy" src="'+CDN+'headshots/nba/latest/260x190/'+pid+'.png" onerror="this.remove()">':'')+'</span>';
const f1=v=>(v>=0?'+':'')+v.toFixed(1),f0=v=>v.toFixed(1);
const cls=v=>v>=0?'pos':'neg';
const d10=s=>s?String(s).slice(0,10):'';
const ret=x=>{const out=x.missGames!=null,g=out?'（缺 '+x.missGames+' 場）':'';return x.returnDate?'<br><span class="cm rt">預計回 '+esc(String(x.returnDate).slice(0,10))+g+'</span>':(out?'<br><span class="cm rt">無回歸日，當整季缺陣'+g+'</span>':'')};
function info(){
  const i=D.injuries||{};
  $('#stamp').innerHTML='<b>'+esc(D.dataCutoff)+'</b>'+esc(D.generatedAt.slice(11,16))+' 更新';
  const isT=D.engineKind==='t';
  $('#meta').innerHTML='<ul class="nb"><li>'+(isT?'戰力排行由陣容模型（Transformer，用過去五季每段上場陣容的得失分訓練）估計：依分鐘抽出每隊的五人陣容，對其他 29 隊各抽 '+D.opponent.drawsPerTeam+' 組陣容對打，平均得出。'
     :'戰力排行是模型模擬比賽（每隊對五支不同強度、位置配置的對手隊共打 '+D.seeds+' 場）得出的數據。')+'目前還在 beta 版本，有不準的地方，僅供參考。</li>'
   +(isT?'':'<li>76 人被低估：模型認為同一隊持球單打手太多，彼此搶球，化學反應不好。</li>')+'</ul>'
   +(i.stale&&(!i.fetchedAt||Date.now()-Date.parse(i.fetchedAt)>3*864e5)?'<span class="warn">傷病名單已超過三天沒更新。</span>':'')
   +(D.schedule&&D.schedule.remainingGames?'':'<span class="warn">抓不到賽程，剩餘場次以對全聯盟平均勝率計。</span>');
  $('#viewHint').textContent=view==='today'?'排除傷兵':'全員健康的版本';
  $('#note').innerHTML=(isT?'評分模型 '+esc(D.engine)+'（2025-26 整季與本季已完賽場次回測都比舊模擬引擎準）':'模擬引擎 '+esc(D.engine))+'；ORtg／DRtg／Net 已扣聯盟平均。'
   +'<br>分鐘規則：每位現役球員取他自己最近 '+D.lastN+' 場「有出場」的平均分鐘（沒上場的比賽不算，不管當時在哪隊）；候選人是該隊最近 '+D.lastN+' 場出場過的人，加上最近沒出場但自己平均 ≥'+(D.returnMin||15)+' 分鐘的人（視為傷缺復出）；照教練實際用人：每人的起點分鐘就是上述平均分鐘，再乘上「焦灼比賽乘數」（依該隊球員的分鐘名次分 11 槽，乘數＝2024-25、2025-26 兩季焦灼場〔分差 ≤5 或延長賽〕的平均分鐘 ÷ 全部場的平均分鐘，約 1.02–1.11，由資料直接量），再等比放大到合計 240 分鐘；單人上限 36（超出的分鐘依比例分給沒到上限的人，反覆到收斂），不設下限；可上場人數太少（不到 7 人）時上限放寬到 40。名次只用來決定乘數，不直接決定分鐘。「可用」先拿掉 Out／Doubtful／Questionable／Day-To-Day（含停賽），只留 Probable 與沒上名單的人，不做機率加權；「傷兵」欄＝被拿掉的人數。'
   +((D.baseProfiles||[]).length?'<br>上季整季缺陣、今年還沒有排名的人（'+D.baseProfiles.map(x=>esc(x.name)).join('、')+'）：模擬用他最近一張賽季卡的能力值（不做年齡調整），OVR 欄標「24-25 卡」等來源；沒有任何歷史卡的新人仍當聯盟平均球員。':'')
   +'<br>預測勝場＝目前勝場＋剩餘賽程逐場勝率（主場 +'+D.H+' 分、σ='+D.sigma+'）。「可用」版依 ESPN 預計回歸日逐場換陣容：比賽日期早於回歸日就缺陣，之後回來；'
   +((D.injuries&&D.injuries.outNoReturnDate)?'<span class="warn">目前有 '+D.injuries.outNoReturnDate+' 位缺陣者沒有回歸日（官方 PDF 備援不提供），當整季缺陣。</span>':'沒有回歸日的缺陣者當整季缺陣。')+'「全員」版不扣人、陣容全程不變。主表的 Net 是今天的陣容。';
}
function rows(){
  const R=T.map(t=>({t,v:t[view]})).sort((a,b)=>b.v.net-a.v.net).map((o,i)=>({...o,rank:i+1}));
  const val={rank:o=>o.rank,name:o=>o.t.name,net:o=>o.v.net,ortg:o=>o.v.ortg,drtg:o=>-o.v.drtg,wpct:o=>(o.t.W+o.t.L)?o.t.W/(o.t.W+o.t.L):0,pred:o=>o.v.predWins,nOut:o=>o.t.nOut};
  R.sort((a,b)=>{const x=val[sk](a),y=val[sk](b);return (x<y?-1:x>y?1:0)*sd||a.rank-b.rank});
  return R;
}
function detail(o){
  const t=o.t,v=o.v,back=new Set((t.restored||[]).map(x=>x.pid)),rot=v.rotation.map(r=>'<tr><td class="n"><div class="pn">'+av(r.pid)+'<span>'+esc(r.name)+(back.has(r.pid)?'<span class="cm">傷缺復出：最近 10 場沒出場，自己平均 ≥'+(D.returnMin||15)+' 分</span>':'')+'</span></div></td><td>'+r.min.toFixed(1)+'</td><td>'+(r.ovr==null?'—':Math.round(r.ovr)+(r.ovrSrc?'<span class="cm">'+esc(r.ovrSrc)+'</span>':''))+'</td></tr>').join('');
  const inj=t.injured.length?t.injured.map(x=>'<tr><td class="n"><div class="pn">'+av(x.playerId)+'<span>'+esc(x.name)+''+(x.injury?'<span class="cm">'+esc(x.injury)+'</span>':'')+'</span></div></td><td class="n">'+esc(x.status)+'</td><td>'+esc(d10(x.date))+ret(x)+'</td></tr>').join(''):'<tr><td class="n" colspan="3">傷病名單沒有這隊的人</td></tr>';
  return '<div class="dg"><div class="sum"><b>'+esc(t.name)+'</b>　ORtg '+f1(v.ortg)+'・DRtg '+f1(v.drtg)+'・Net '+f1(v.net)+(D.engineKind==='t'?'・對聯盟平均對手每場 ':'・對梯度對手每場 ')+f1(v.margin)+' 分　剩餘賽程 '+v.schedGames+' 場逐場計算'+(v.poolGames?'、'+v.poolGames+' 場以平均勝率補':'')+(view==='today'&&v.lineupStates>1?'　傷兵回歸讓陣容分 '+v.lineupStates+' 種狀態':'')+'</div>'
   +'<div><h3>'+(view==='today'?'可用輪替':'全員輪替')+'（分鐘／OVR）</h3><table><tbody>'+rot+'</tbody></table></div>'
   +'<div><h3>傷病名單（狀態／資料日期／預計回歸；Probable 照常上場）</h3><table><tbody>'+inj+'</tbody></table></div></div>';
}
function render(){
  const R=rows();
  $('#tb').innerHTML=R.map(o=>{const t=o.t,v=o.v;
    return '<tr class="row'+(open===t.abbr?' open':'')+'" data-a="'+t.abbr+'" tabindex="0"><td class="rk">'+o.rank+'</td><td class="tm l"><div class="tmw">'+logo(t.id)+'<div class="tt">'+esc(t.abbr)+'<small>'+esc(t.name)+'</small></div></div></td>'
     +'<td class="net '+cls(v.net)+'">'+f1(v.net)+'</td>'
     +'<td class="hide-m">'+f1(v.ortg)+'</td><td class="hide-m">'+f1(v.drtg)+'</td><td>'+t.W+'-'+t.L+'</td><td>'+f0(v.predWins)+'</td><td class="'+(t.nOut?'inj':'')+'">'+(t.nOut||'')+'</td></tr>'
     +(open===t.abbr?'<tr class="det"><td colspan="8">'+detail(o)+'</td></tr>':'');}).join('');
  root.querySelectorAll('#viewSeg button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===view)));
  let si=-1;
  root.querySelectorAll('thead th').forEach((h,i)=>{if(h.dataset.k===sk){si=i;h.setAttribute('aria-sort',sd<0?'descending':'ascending');}else h.removeAttribute('aria-sort');});
  root.querySelectorAll('#tb tr.row').forEach(r=>r.children[si]?.classList.add('sorted'));
  info();
}
$('#tb').addEventListener('click',e=>{const r=e.target.closest('tr.row');if(!r)return;toggle(r.dataset.a);});
$('#tb').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){const r=e.target.closest('tr.row');if(r){e.preventDefault();toggle(r.dataset.a);$('#tb tr[data-a="'+r.dataset.a+'"]')?.focus();}}});
$('thead').addEventListener('click',e=>{const h=e.target.closest('th');if(!h)return;const k=h.dataset.k;if(k===sk)sd=-sd;else{sk=k;sd=(k==='name'||k==='rank')?1:-1;}render();});
$('#viewSeg').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;view=b.dataset.v;try{localStorage.setItem('bbac.teamsView',view)}catch(_){}render();});

function toggle(a){open=open===a?null:a;render();if(/^\/rank\//.test(location.pathname))history.replaceState(null,'','/rank/'+(open?open+'/':''));}
function ensure(){
  if(!loading)loading=fetch('/teams-data.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error(r.status);return r.json()}).then(d=>{
    D=d;T=Object.entries(D.teams).map(([id,t])=>({...t,id}));$('#msg').hidden=true;$('#rkw').hidden=false;render();
  }).catch(()=>{loading=null;$('#msg').textContent='戰力排行載入失敗，重新整理再試一次。';});
  return loading;
}
window.PureRank={ensure,open(a){open=a||null;if(D)render();}};
})()</script>"""


def embed():
    """名單頁用：回傳 (宿主＋template 的 HTML, 腳本)。宿主放在 .wrap 前面，腳本放在眉頭腳本之前。"""
    tpl = '<template id="rankTpl"><style>' + STYLE + '</style>' + BODY + '</template>'
    return '<div id="rankHost"></div>' + tpl, JS
