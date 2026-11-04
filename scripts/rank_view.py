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
.dg{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.1fr);gap:14px;padding:14px 16px 18px;align-items:start}
.dg>div{background:var(--panel);border:1px solid var(--line);border-radius:4px;overflow:hidden}
.dg h3{margin:0;padding:10px 12px;border-bottom:1px solid var(--line);font:700 .95rem var(--f-body);letter-spacing:.02em;color:var(--fg);display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.dg h3 small{font:500 .74rem var(--f-body);color:var(--muted)}
.dg table{font-size:.88rem}
.dg thead th{position:static;background:transparent;font:600 .74rem var(--f-body);letter-spacing:.04em;text-transform:none;color:var(--muted);padding:6px 12px;cursor:default;border-bottom:1px solid var(--line);text-align:right;box-shadow:none}
.dg thead th.l{text-align:left}
.dg td{padding:7px 12px;border-bottom:1px solid #1a2128;white-space:normal;font:500 .9rem var(--f-body);letter-spacing:0;vertical-align:middle}
.dg tbody tr:last-child td{border-bottom:0}
.dg td.n{min-width:9.5em;overflow-wrap:break-word;text-align:left;font-weight:600}
.dg td.num{font:700 1rem var(--nf);text-align:right;white-space:nowrap;width:1%}
.mn{display:flex;align-items:center;gap:8px;justify-content:flex-end}
.mn i{display:block;width:64px;height:5px;border-radius:3px;background:#1d252d;overflow:hidden}
.mn i b{display:block;height:100%;background:var(--muted);opacity:.75}
.pill{display:inline-block;padding:2px 9px;border-radius:99px;font:700 .74rem var(--f-body);letter-spacing:.02em;white-space:nowrap;border:1px solid transparent}
.s-out{color:var(--g-f);background:color-mix(in srgb,var(--g-f) 16%,transparent);border-color:color-mix(in srgb,var(--g-f) 40%,transparent)}
.s-dbt,.s-q{color:var(--gold);background:color-mix(in srgb,var(--gold) 14%,transparent);border-color:color-mix(in srgb,var(--gold) 38%,transparent)}
.s-q{opacity:.85}
.s-p{color:var(--g-a);background:color-mix(in srgb,var(--g-a) 14%,transparent);border-color:color-mix(in srgb,var(--g-a) 38%,transparent)}
.rb b{display:block;color:var(--gold);font:700 .9rem var(--f-body)}
.rb b.far{color:var(--g-f)}
.rb small{display:block;color:var(--muted);font:500 .72rem var(--f-body);margin-top:1px}
.chips{display:flex;flex-wrap:wrap;align-items:center;gap:8px}
.chip{background:var(--panel);border:1px solid var(--line);border-radius:3px;padding:3px 10px;font:500 .8rem var(--f-body);color:var(--muted);white-space:nowrap}
.chip b{font:700 1rem var(--nf);margin-left:5px;color:var(--fg)}
.chip b.pos{color:var(--g-a)}.chip b.neg{color:var(--g-f)}
.tname{font:italic 800 1.25rem var(--nf);text-transform:uppercase;margin-right:6px}
.pn{display:flex;align-items:center;gap:9px;min-width:0}
.av{flex:none;width:34px;height:34px;border-radius:50%;background:var(--panel-2);border:1px solid var(--line);overflow:hidden;display:block}
.av img{display:block;width:100%;height:100%;object-fit:cover;object-position:50% 12%}
.pn>span:last-child{min-width:0}
.sum{grid-column:1/-1;color:var(--muted);font-size:.8rem}
.cm{color:var(--muted);font-size:.74rem;display:block;white-space:normal;max-width:46ch}
.cm.rt{color:var(--gold)}
.note{color:var(--muted);font-size:.8rem;line-height:1.7;border-top:1px solid var(--line);padding-top:10px}
.note b,.meta b{color:var(--fg);font-weight:600}
.note em,.meta em{color:var(--gold);font-style:normal;font-weight:600}
.meta .nb{margin:0;padding-left:1.2em;color:var(--muted)}
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
  .dg{padding:10px 10px 14px}
  .dg td{padding:7px 8px}.dg thead th{padding:6px 8px}
  .dg td:not(:first-child){white-space:nowrap;font-size:.8rem}
  .dg>div:last-child .av{display:none}
  .dg td.n{min-width:8em}.pill{padding:2px 7px;font-size:.7rem}.mn i{width:44px}
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
<th data-k="rank" class="rk">#</th><th data-k="name" class="l">球隊</th><th data-k="net" aria-sort="descending">NetRtg<span class="zh">淨效率</span></th>
<th data-k="ortg" class="hide-m">OffRtg<span class="zh">進攻</span></th><th data-k="drtg" class="hide-m">DefRtg<span class="zh">防守</span></th>
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
const TC={ATL:'#E5384B',BOS:'#2EA66B',BKN:'#E6E6E6',CHA:'#1FA3CC',CHI:'#E3294F',CLE:'#C8305A',DAL:'#4A90D9',DEN:'#FEC524',DET:'#E5324B',GSW:'#FFC72C',HOU:'#E5324B',IND:'#FDBB30',LAC:'#E8365A',LAL:'#FDB927',MEM:'#7C9FE0',MIA:'#E5324B',MIL:'#3BAA6E',MIN:'#4F9FE0',NOP:'#D7B26A',NYK:'#F58426',OKC:'#3AA3E0',ORL:'#3A8FDC',PHI:'#3B8BDB',PHX:'#F27A28',POR:'#E5324B',SAC:'#9A7BE0',SAS:'#C4CED4',TOR:'#E5324B',UTA:'#A78BFA',WAS:'#E5324B'};     // 球隊主題色（深底可讀的亮度版）
const absO=v=>D.lgOrtg==null?f1(v.ortg):f0(v.ortg+D.lgOrtg),absD=v=>D.lgDrtg==null?f1(v.drtg):f0(v.drtg+D.lgDrtg);     // 官方寫法：每百回合得／失分；舊資料沒有聯盟平均時退回「相對聯盟」
const cls=v=>v>=0?'pos':'neg';
const d10=s=>s?String(s).slice(0,10):'';
const stc=st=>/^out/i.test(st)?'s-out':/^doubt/i.test(st)?'s-dbt':/^prob/i.test(st)?'s-p':'s-q';
const retCell=x=>{const out=x.missGames!=null,g=out?'缺 '+x.missGames+' 場':'',t=x.date?' title="資料日期 '+esc(d10(x.date))+'"':'';
 return x.returnDate?'<div class="rb"'+t+'><b'+(out&&x.missGames>=20?' class="far"':'')+'>'+esc(String(x.returnDate).slice(5,10))+(String(x.returnDate).slice(0,4)!==String(D.generatedAt||'').slice(0,4)?'<span style="font-weight:500;opacity:.7"> '+esc(String(x.returnDate).slice(0,4))+'</span>':'')+' 回歸</b>'+(g?'<small>'+g+'</small>':'')+'</div>'
  :'<div class="rb"'+t+'><b class="far">整季缺陣</b><small>無回歸日'+(g?'・'+g:'')+'</small></div>'};
function info(){
  const i=D.injuries||{};
  $('#stamp').innerHTML='<b>'+esc(D.dataCutoff)+'</b>'+esc(D.generatedAt.slice(11,16))+' 更新';
  const isT=D.engineKind==='t';
  $('#meta').innerHTML='<ul class="nb"><li>'+(isT?'由<b>過去五季上場陣容得失分</b>訓練的<b>陣容模型（Transformer）</b>估計：依輪替分鐘抽出<b>五人陣容</b>，對<b>其他 29 隊各 '+D.opponent.drawsPerTeam+' 組陣容</b>對戰平均得出。'
     :'由模型<b>模擬比賽</b>（每隊對五支不同強度與位置配置的對手隊共打 <b>'+D.seeds+' 場</b>）得出。')+'<em>目前還在 beta 版本</em>，僅供參考。</li>'
   +(isT?'':'<li><b>76 人被低估</b>：模型認為同隊持球單打手太多、彼此搶球，化學反應不佳。</li>')+'</ul>'
   +(i.stale&&(!i.fetchedAt||Date.now()-Date.parse(i.fetchedAt)>3*864e5)?'<span class="warn">傷病名單已超過三天沒更新。</span>':'')
   +(D.schedule&&D.schedule.remainingGames?'':'<span class="warn">抓不到賽程，剩餘場次以對全聯盟平均勝率計。</span>');
  $('#viewHint').textContent=view==='today'?'排除傷兵':'全員健康的版本';
  $('#note').innerHTML='<em>效率指標</em>：<b>OffRtg／DefRtg</b> 為每百回合得分／失分（<b>DefRtg 越低防守越好</b>），<b>NetRtg＝OffRtg−DefRtg</b>。主表顯示<b>今天的陣容</b>。'
   +'<br><em>上場時間</em>：取球員<b>近 '+D.lastN+' 場有出賽的平均分鐘</b>，依<b>焦灼比賽</b>（分差 5 分內或延長賽）主力縮輪替的比例調整並<b>湊滿 240 分鐘</b>，<b>單人上限 36 分鐘</b>（未滿 7 人時放寬至 40）。近期未出賽但<b>場均滿 '+(D.returnMin||15)+' 分鐘</b>者視為傷癒復出，照常排入輪替。'
   +'<br><em>可用／全員</em>：<b>「可用」</b>排除 <b>Out、Doubtful、Questionable、Day-To-Day 與停賽</b>球員（<b>Probable 照常上場</b>），「傷兵」欄為排除人數；<b>「全員」</b>假設全隊健康。'
   +((D.baseProfiles||[]).length?'<br><em>過往賽季卡</em>：<b>上季整季缺陣、本季尚無排名</b>的球員（'+D.baseProfiles.map(x=>esc(x.name)).join('、')+'），OVR 欄暫標<b>最近一張賽季卡</b>。':'')
   +'<br><em>預測勝場</em>：<b>目前勝場＋剩餘賽程逐場勝率</b>（計入主客場與對手強弱）。<b>「可用」版依 ESPN 預計回歸日逐場更換陣容</b>，回歸日前缺陣、之後歸隊；'
   +((D.injuries&&D.injuries.outNoReturnDate)?'<span class="warn">目前有 '+D.injuries.outNoReturnDate+' 位缺陣者沒有回歸日（官方 PDF 備援不提供），視為整季缺陣。</span>':'<b>無回歸日者視為整季缺陣</b>。')+'「全員」版全程以健康陣容計算。';
}
function rows(){
  const R=T.map(t=>({t,v:t[view]})).sort((a,b)=>b.v.net-a.v.net).map((o,i)=>({...o,rank:i+1}));
  const val={rank:o=>o.rank,name:o=>o.t.name,net:o=>o.v.net,ortg:o=>o.v.ortg,drtg:o=>-o.v.drtg,wpct:o=>(o.t.W+o.t.L)?o.t.W/(o.t.W+o.t.L):0,pred:o=>o.v.predWins,nOut:o=>o.t.nOut};
  R.sort((a,b)=>{const x=val[sk](a),y=val[sk](b);return (x<y?-1:x>y?1:0)*sd||a.rank-b.rank});
  return R;
}
function detail(o){
  const t=o.t,v=o.v,back=new Set((t.restored||[]).map(x=>x.pid)),
  rot=v.rotation.map(r=>'<tr><td class="n"><div class="pn">'+av(r.pid)+'<span>'+esc(r.name)+(back.has(r.pid)?'<span class="cm">傷缺復出：最近 10 場沒出場，自己平均 ≥'+(D.returnMin||15)+' 分</span>':'')+'</span></div></td><td class="num"><div class="mn"><i><b style="width:'+Math.min(100,r.min/40*100).toFixed(0)+'%"></b></i>'+r.min.toFixed(1)+'</div></td><td class="num">'+(r.ovr==null?'—':Math.round(r.ovr)+(r.ovrSrc?'<span class="cm">'+esc(r.ovrSrc)+'</span>':''))+'</td></tr>').join(''),
  inj=t.injured.length?t.injured.map(x=>'<tr><td class="n"><div class="pn">'+av(x.playerId)+'<span>'+esc(x.name)+(x.injury?'<span class="cm">'+esc(x.injury)+'</span>':'')+'</span></div></td><td class="num"><span class="pill '+stc(x.status)+'">'+esc(x.status)+'</span></td><td class="num">'+retCell(x)+'</td></tr>').join(''):'<tr><td class="n" colspan="3">傷病名單沒有這隊的人</td></tr>',
  chip=(k,val,c)=>'<span class="chip">'+k+'<b'+(c?' class="'+c+'"':'')+'>'+val+'</b></span>';
  return '<div class="dg"><div class="sum chips"><span class="tname"'+(TC[t.abbr]?' style="color:'+TC[t.abbr]+'"':'')+'>'+esc(t.name)+'</span>'+chip('OffRtg',absO(v),cls(v.ortg))+chip('DefRtg',absD(v),cls(-v.drtg))+chip('NetRtg',f1(v.net),cls(v.net))
   +chip('剩餘賽程',v.schedGames+' 場'+(v.poolGames?'<span style="font-weight:500;font-size:.75rem;color:var(--muted)">（'+v.poolGames+' 場以平均勝率補）</span>':''))
   +(view==='today'&&v.lineupStates>1?chip('傷兵回歸陣容狀態',v.lineupStates+' 種'):'')+'</div>'
   +'<div><h3>'+(view==='today'?'可用輪替':'全員輪替')+'<small>每場分鐘／OVR</small></h3><table><thead><tr><th class="l">球員</th><th>分鐘</th><th>OVR</th></tr></thead><tbody>'+rot+'</tbody></table></div>'
   +'<div><h3>傷病名單<small>Probable 照常上場</small></h3><table><thead><tr><th class="l">球員</th><th>狀態</th><th>預計回歸</th></tr></thead><tbody>'+inj+'</tbody></table></div></div>';
}
function render(){
  const R=rows();
  $('#tb').innerHTML=R.map(o=>{const t=o.t,v=o.v;
    return '<tr class="row'+(open===t.abbr?' open':'')+'" data-a="'+t.abbr+'" tabindex="0"><td class="rk">'+o.rank+'</td><td class="tm l"><div class="tmw">'+logo(t.id)+'<div class="tt">'+esc(t.abbr)+'<small>'+esc(t.name)+'</small></div></div></td>'
     +'<td class="net '+cls(v.net)+'">'+f1(v.net)+'</td>'
     +'<td class="hide-m">'+absO(v)+'</td><td class="hide-m">'+absD(v)+'</td><td>'+t.W+'-'+t.L+'</td><td>'+f0(v.predWins)+'</td><td class="'+(t.nOut?'inj':'')+'">'+(t.nOut||'')+'</td></tr>'
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
