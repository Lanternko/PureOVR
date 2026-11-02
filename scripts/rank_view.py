"""球隊戰力排行檢視（使用者 2026-11-02「直接合併單頁」）：嵌進名單頁當第二個檢視，和球員分頁共用同一個眉頭，切換不重載。
用 Shadow DOM 隔離樣式（名單頁的 .pn／.av／.seg／table 規則不會污染排行表；色票與字型變數從名單頁繼承）；
資料放獨立的 teams-data.json（build_teams_page.py 產生），第一次進排行（或閒置時預載）才 fetch，每日只更新傷病時不用重建 2.3 MB 的名單頁。
網址：#rank＝排行；#rank/LAL＝展開某隊。對外 API：window.PureRank = {ensure(), open(abbr)}，檢視切換由 site_header.JS 負責。"""

STYLE = """*{box-sizing:border-box}
:host{display:block}
.rkroot{color:var(--fg);font-family:var(--f-body);font-size:14px}
.rkw{max-width:1360px;margin:0 auto;padding-block:16px 40px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:12px}
h1{font:800 1.9rem var(--f-disp);font-style:italic;margin:0;letter-spacing:.01em}
h1 small{font:500 .85rem var(--f-body);font-style:normal;color:var(--muted);margin-left:10px;letter-spacing:0}
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
.tbox{overflow:auto;border:1px solid var(--line);border-radius:4px;background:var(--panel)}
table{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}
thead th{background:#0a0d10;color:var(--muted);font:600 .85rem var(--f-disp);letter-spacing:.04em;padding:8px 8px;text-align:right;cursor:pointer;user-select:none;white-space:nowrap;border-bottom:1px solid var(--line);position:sticky;top:0;z-index:2}
thead th.l,td.l{text-align:left}
thead th .zh{display:block;font:500 .68rem var(--f-body);opacity:.75}
thead th[aria-sort]::after{content:" ▾";color:var(--gold)}
thead th[aria-sort="ascending"]::after{content:" ▴"}
td{padding:8px 8px;text-align:right;border-bottom:1px solid #1d242c;white-space:nowrap}
tr.row{cursor:pointer}
tr.row:hover td{background:#1a2128}
tr.row.open td{background:#1d252d}
td.rk{color:var(--muted);width:34px;text-align:center}
td.tm{font:700 1.05rem var(--f-disp);letter-spacing:.02em}
td.tm .tmw{display:flex;align-items:center;gap:9px}
td.tm .lg{width:26px;height:26px;flex:none;object-fit:contain}
td.tm .tt{min-width:0}
td.tm small{display:block;font:500 .7rem var(--f-body);color:var(--muted);letter-spacing:0}
td.net{font:800 1.15rem var(--f-disp)}
.pos{color:var(--g-a)}.neg{color:var(--g-f)}
.nb{display:inline-block;height:6px;border-radius:3px;vertical-align:middle;margin-left:8px;min-width:2px}
.inj{color:var(--gold)}
.det td{padding:0;background:#10151a;white-space:normal;text-align:left}
.dg{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(0,1fr);gap:18px;padding:12px 16px 16px}
.dg h3{margin:0 0 6px;font:700 .85rem var(--f-disp);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.dg table{font-size:.88rem}
.dg td{padding:4px 6px;border-bottom:1px solid #1a2128;white-space:normal}
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
@media (max-width:760px){.dg{grid-template-columns:minmax(0,1fr)}.cm{max-width:none}}
@media (max-width:640px){
  .rkroot{font-size:13px}
  h1{font-size:1.5rem}
  .hide-m,thead th .zh{display:none}
  .dg td:not(:first-child){white-space:nowrap;font-size:.8rem}
  .rkw{gap:10px}
  td,thead th{padding:7px 5px}
  td.tm{font-size:.98rem}
  td.tm small{display:none}
  td.tm .tmw{gap:6px}
  td.tm .lg{width:22px;height:22px}
  .av{width:30px;height:30px}
  .pn{gap:7px}
  td.net{font-size:1.05rem}
  .nb{display:none}
  .seg button{padding:9px 16px}
  .vctl{gap:6px}
}
.msg{color:var(--muted);padding:40px 16px;text-align:center}"""

BODY = """<div class="rkroot"><div class="msg" id="msg">載入中…</div>
<div class="rkw" id="rkw" hidden>
<div><h1>戰力排行<small id="stamp"></small></h1></div>
<div class="meta" id="meta"></div>
<div class="vctl"><div class="seg" id="viewSeg" role="group" aria-label="名單版本"><button type="button" data-v="today" aria-pressed="true">可用</button><button type="button" data-v="c" aria-pressed="false">全員</button></div>
<span class="hint" id="viewHint"></span></div>
<div class="tbox"><table id="tbl"><thead><tr>
<th data-k="rank" class="rk">#</th><th data-k="name" class="l">球隊</th><th data-k="net" aria-sort="descending">Net<span class="zh">淨效率</span></th>
<th data-k="ortg" class="hide-m">ORtg<span class="zh">進攻</span></th><th data-k="drtg" class="hide-m">DRtg<span class="zh">防守</span></th>
<th data-k="wpct">戰績<span class="zh">W-L</span></th><th data-k="pred">預測勝場<span class="zh">全季</span></th><th data-k="nOut">傷兵<span class="zh">Out／Doubtful</span></th>
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
  const i=D.injuries||{},ts=i.espnTimestamp||i.reportTime||i.fetchedAt;
  $('#stamp').textContent='數據至 '+D.dataCutoff+'・'+D.version.replace('inseason ','');
  $('#meta').innerHTML='傷病資料日期 <b>'+esc(ts?String(ts).slice(0,16).replace('T',' ')+(String(ts).endsWith('Z')?' UTC':''):'—')+'</b>'+(i.source?'（'+esc(i.source.toUpperCase())+'）':'')
   +(i.stale?' <span class="warn">　今天抓不到傷病名單，沿用前一份。</span>':'')
   +'　評分更新 <b>'+esc(D.generatedAt.slice(0,16).replace('T',' '))+'</b>'
   +'　剩餘賽程 '+(D.schedule&&D.schedule.remainingGames?'逐場計算（NBA.com 賽程）':'<span class="warn">抓不到賽程，剩餘場次以對全聯盟平均勝率計</span>');
  $('#viewHint').textContent=view==='today'?'排除 Out／Doubtful；依回歸日逐場模擬。':'不扣傷兵；陣容全程不變。';
  $('#note').innerHTML='模擬評分（引擎 '+esc(D.engine)+'，名單對聯盟平均隊各打 '+D.seeds+' 場；ORtg／DRtg／Net 已扣聯盟平均）。<b>回測僅與上季淨效率打平，弱隊容易高估，僅供參考。</b>'
   +'<br>分鐘規則：每位現役球員取他自己最近 '+D.lastN+' 場「有出場」的平均分鐘（沒上場的比賽不算，不管當時在哪隊）；候選人是該隊最近 '+D.lastN+' 場出場過的人，加上最近沒出場但自己平均 ≥'+(D.returnMin||15)+' 分鐘的人（視為傷缺復出）；前 10 人、總和 240、單人上限 48。「可用」先拿掉 Out／Doubtful（含停賽），Questionable／Day-To-Day 保留。'
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
  const inj=t.injured.length?t.injured.map(x=>'<tr><td class="n"><div class="pn">'+av(x.playerId)+'<span>'+esc(x.name)+'<span class="cm">'+esc(x.comment)+'</span></span></div></td><td class="n">'+esc(x.status)+'</td><td>'+esc(d10(x.date))+ret(x)+'</td></tr>').join(''):'<tr><td class="n" colspan="3">傷病名單沒有這隊的人</td></tr>';
  return '<div class="dg"><div class="sum"><b>'+esc(t.name)+'</b>　ORtg '+f1(v.ortg)+'・DRtg '+f1(v.drtg)+'・Net '+f1(v.net)+'・對平均隊每場 '+f1(v.margin)+' 分　剩餘賽程 '+v.schedGames+' 場逐場計算'+(v.poolGames?'、'+v.poolGames+' 場以平均勝率補':'')+(view==='today'&&v.lineupStates>1?'　傷兵回歸讓陣容分 '+v.lineupStates+' 種狀態':'')+'</div>'
   +'<div><h3>'+(view==='today'?'可用輪替':'全員輪替')+'（分鐘／OVR）</h3><table><tbody>'+rot+'</tbody></table></div>'
   +'<div><h3>傷病名單（狀態／資料日期／預計回歸）</h3><table><tbody>'+inj+'</tbody></table></div></div>';
}
function render(){
  const R=rows(),mx=Math.max(...T.map(t=>Math.abs(t[view].net)));
  $('#tb').innerHTML=R.map(o=>{const t=o.t,v=o.v,w=Math.round(Math.abs(v.net)/mx*46);
    return '<tr class="row'+(open===t.abbr?' open':'')+'" data-a="'+t.abbr+'" tabindex="0"><td class="rk">'+o.rank+'</td><td class="tm l"><div class="tmw">'+logo(t.id)+'<div class="tt">'+esc(t.abbr)+'<small>'+esc(t.name)+'</small></div></div></td>'
     +'<td class="net '+cls(v.net)+'">'+f1(v.net)+'<span class="nb" style="width:'+w+'px;background:var(--'+(v.net>=0?'g-a':'g-f')+')"></span></td>'
     +'<td class="hide-m">'+f1(v.ortg)+'</td><td class="hide-m">'+f1(v.drtg)+'</td><td>'+t.W+'-'+t.L+'</td><td>'+f0(v.predWins)+'</td><td class="'+(t.nOut?'inj':'')+'">'+(t.nOut||'')+'</td></tr>'
     +(open===t.abbr?'<tr class="det"><td colspan="8">'+detail(o)+'</td></tr>':'');}).join('');
  root.querySelectorAll('#viewSeg button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===view)));
  root.querySelectorAll('thead th').forEach(h=>{if(h.dataset.k===sk)h.setAttribute('aria-sort',sd<0?'descending':'ascending');else h.removeAttribute('aria-sort');});
  info();
}
$('#tb').addEventListener('click',e=>{const r=e.target.closest('tr.row');if(!r)return;toggle(r.dataset.a);});
$('#tb').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){const r=e.target.closest('tr.row');if(r){e.preventDefault();toggle(r.dataset.a);$('#tb tr[data-a="'+r.dataset.a+'"]')?.focus();}}});
$('thead').addEventListener('click',e=>{const h=e.target.closest('th');if(!h)return;const k=h.dataset.k;if(k===sk)sd=-sd;else{sk=k;sd=(k==='name'||k==='rank')?1:-1;}render();});
$('#viewSeg').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;view=b.dataset.v;try{localStorage.setItem('bbac.teamsView',view)}catch(_){}render();});

function toggle(a){open=open===a?null:a;render();if(/^#rank/.test(location.hash))history.replaceState(null,'','#rank'+(open?'/'+open:''));}
function ensure(){
  if(!loading)loading=fetch('teams-data.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw new Error(r.status);return r.json()}).then(d=>{
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
