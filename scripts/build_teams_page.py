"""球隊評分頁 teams.html（E-208 第二階段）。讀 data/season-source-2026-27/team-ratings.json（scripts/team_ratings_daily.py 產生），
輸出單檔 HTML（資料內嵌，不連外取資料；只有 Google Fonts 字型與 NBA CDN 的隊徽、球員頭像，失敗時隱藏）。眉頭用 site_header.teams_masthead，樣式沿用名單頁的色票。

用法：python -I -X utf8 scripts/build_teams_page.py <out.html> [team-ratings.json]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from site_header import teams_masthead  # noqa: E402

RATINGS = ROOT / 'data/season-source-2026-27/team-ratings.json'

STYLE = """<style>
:root{--bg:#0d1014;--panel:#151a20;--panel-2:#1c222a;--line:#29313b;--fg:#e8edf3;--muted:#8d9bad;--gold:#f2c230;--gold-ink:#1a1405;--red:#d8343c;
  --g-a:#5ad37f;--g-f:#e0585a;--f-disp:"Barlow Condensed","Noto Sans TC","Arial Narrow",sans-serif;--f-body:"Barlow","Noto Sans TC",system-ui,sans-serif;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:var(--f-body);font-size:14px}
.wrap{max-width:1360px;margin:0 auto;padding-block:16px 40px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:flex;flex-direction:column;gap:12px}
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
  body{font-size:13px}
  h1{font-size:1.5rem}
  .hide-m,thead th .zh{display:none}
  .dg td:not(:first-child){white-space:nowrap;font-size:.8rem}
  .wrap{gap:10px}
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
</style>"""

BODY = """<div class="wrap">
<div><h1>球隊評分<small id="stamp"></small></h1></div>
<div class="meta" id="meta"></div>
<div class="vctl"><div class="seg" id="viewSeg" role="group" aria-label="名單版本"><button type="button" data-v="today" aria-pressed="true">今日陣容</button><button type="button" data-v="c" aria-pressed="false">近況</button></div>
<span class="hint" id="viewHint"></span></div>
<div class="tbox"><table id="tbl"><thead><tr>
<th data-k="rank" class="rk">#</th><th data-k="name" class="l">球隊</th><th data-k="net" aria-sort="descending">Net<span class="zh">淨效率</span></th>
<th data-k="ortg" class="hide-m">ORtg<span class="zh">進攻</span></th><th data-k="drtg" class="hide-m">DRtg<span class="zh">防守</span></th>
<th data-k="wpct">戰績<span class="zh">W-L</span></th><th data-k="pred">預測勝場<span class="zh">全季</span></th><th data-k="nOut">傷兵<span class="zh">Out／Doubtful</span></th>
</tr></thead><tbody id="tb"></tbody></table></div>
<div class="note" id="note"></div>
</div>"""

JS = r"""<script>(()=>{
const D=JSON.parse(document.getElementById('data').textContent),T=Object.entries(D.teams).map(([id,t])=>({...t,id}));
const $=s=>document.querySelector(s),esc=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
let view=(()=>{try{return localStorage.getItem('bbac.teamsView')==='c'?'c':'today'}catch(e){return 'today'}})(),sk='net',sd=-1,open=T.some(t=>t.abbr===location.hash.slice(1))?location.hash.slice(1):null;
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
  $('#viewHint').textContent=view==='today'?'拿掉 Out／Doubtful 的人；預測勝場依傷兵回歸日逐場換陣容。':'不扣傷兵（含剛復出的人）；預測勝場陣容全程不變。';
  $('#note').innerHTML='模擬評分（引擎 '+esc(D.engine)+'，名單對聯盟平均隊各打 '+D.seeds+' 場；ORtg／DRtg／Net 已扣聯盟平均）。<b>回測僅與上季淨效率打平，弱隊容易高估，僅供參考。</b>'
   +'<br>分鐘規則：每位現役球員取他自己最近 '+D.lastN+' 場「有出場」的平均分鐘（沒上場的比賽不算，不管當時在哪隊）；候選人是該隊最近 '+D.lastN+' 場出場過的人，加上最近沒出場但自己平均 ≥'+(D.returnMin||15)+' 分鐘的人（視為傷缺復出）；前 10 人、總和 240、單人上限 48。今日陣容先拿掉 Out／Doubtful（含停賽），Questionable／Day-To-Day 保留。'
   +'<br>預測勝場＝目前勝場＋剩餘賽程逐場勝率（主場 +'+D.H+' 分、σ='+D.sigma+'）。「今日陣容」版依 ESPN 預計回歸日逐場換陣容：比賽日期早於回歸日就缺陣，之後回來；'
   +((D.injuries&&D.injuries.outNoReturnDate)?'<span class="warn">目前有 '+D.injuries.outNoReturnDate+' 位缺陣者沒有回歸日（官方 PDF 備援不提供），當整季缺陣。</span>':'沒有回歸日的缺陣者當整季缺陣。')+'「近況」版不扣人、陣容全程不變。主表的 Net 是今天的陣容。';
}
function rows(){
  const R=T.map(t=>({t,v:t[view]})).sort((a,b)=>b.v.net-a.v.net).map((o,i)=>({...o,rank:i+1}));
  const val={rank:o=>o.rank,name:o=>o.t.name,net:o=>o.v.net,ortg:o=>o.v.ortg,drtg:o=>-o.v.drtg,wpct:o=>(o.t.W+o.t.L)?o.t.W/(o.t.W+o.t.L):0,pred:o=>o.v.predWins,nOut:o=>o.t.nOut};
  R.sort((a,b)=>{const x=val[sk](a),y=val[sk](b);return (x<y?-1:x>y?1:0)*sd||a.rank-b.rank});
  return R;
}
function detail(o){
  const t=o.t,v=o.v,back=new Set((t.restored||[]).map(x=>x.pid)),rot=v.rotation.map(r=>'<tr><td class="n"><div class="pn">'+av(r.pid)+'<span>'+esc(r.name)+(back.has(r.pid)?'<span class="cm">傷缺復出：最近 10 場沒出場，自己平均 ≥'+(D.returnMin||15)+' 分</span>':'')+'</span></div></td><td>'+r.min.toFixed(1)+'</td><td>'+(r.ovr==null?'—':Math.round(r.ovr))+'</td></tr>').join('');
  const inj=t.injured.length?t.injured.map(x=>'<tr><td class="n"><div class="pn">'+av(x.playerId)+'<span>'+esc(x.name)+'<span class="cm">'+esc(x.comment)+'</span></span></div></td><td class="n">'+esc(x.status)+'</td><td>'+esc(d10(x.date))+ret(x)+'</td></tr>').join(''):'<tr><td class="n" colspan="3">傷病名單沒有這隊的人</td></tr>';
  return '<div class="dg"><div class="sum"><b>'+esc(t.name)+'</b>　ORtg '+f1(v.ortg)+'・DRtg '+f1(v.drtg)+'・Net '+f1(v.net)+'・對平均隊每場 '+f1(v.margin)+' 分　剩餘賽程 '+v.schedGames+' 場逐場計算'+(v.poolGames?'、'+v.poolGames+' 場以平均勝率補':'')+(view==='today'&&v.lineupStates>1?'　傷兵回歸讓陣容分 '+v.lineupStates+' 種狀態':'')+'</div>'
   +'<div><h3>'+(view==='today'?'今日輪替':'近況輪替')+'（分鐘／OVR）</h3><table><tbody>'+rot+'</tbody></table></div>'
   +'<div><h3>傷病名單（狀態／資料日期／預計回歸）</h3><table><tbody>'+inj+'</tbody></table></div></div>';
}
function render(){
  const R=rows(),mx=Math.max(...T.map(t=>Math.abs(t[view].net)));
  $('#tb').innerHTML=R.map(o=>{const t=o.t,v=o.v,w=Math.round(Math.abs(v.net)/mx*46);
    return '<tr class="row'+(open===t.abbr?' open':'')+'" data-a="'+t.abbr+'" tabindex="0"><td class="rk">'+o.rank+'</td><td class="tm l"><div class="tmw">'+logo(t.id)+'<div class="tt">'+esc(t.abbr)+'<small>'+esc(t.name)+'</small></div></div></td>'
     +'<td class="net '+cls(v.net)+'">'+f1(v.net)+'<span class="nb" style="width:'+w+'px;background:var(--'+(v.net>=0?'g-a':'g-f')+')"></span></td>'
     +'<td class="hide-m">'+f1(v.ortg)+'</td><td class="hide-m">'+f1(v.drtg)+'</td><td>'+t.W+'-'+t.L+'</td><td>'+f0(v.predWins)+'</td><td class="'+(t.nOut?'inj':'')+'">'+(t.nOut||'')+'</td></tr>'
     +(open===t.abbr?'<tr class="det"><td colspan="8">'+detail(o)+'</td></tr>':'');}).join('');
  document.querySelectorAll('#viewSeg button').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.v===view)));
  document.querySelectorAll('thead th').forEach(h=>{if(h.dataset.k===sk)h.setAttribute('aria-sort',sd<0?'descending':'ascending');else h.removeAttribute('aria-sort');});
  info();
}
$('#tb').addEventListener('click',e=>{const r=e.target.closest('tr.row');if(!r)return;open=open===r.dataset.a?null:r.dataset.a;render();});
$('#tb').addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){const r=e.target.closest('tr.row');if(r){e.preventDefault();open=open===r.dataset.a?null:r.dataset.a;render();$('#tb tr[data-a="'+r.dataset.a+'"]')?.focus();}}});
document.querySelector('thead').addEventListener('click',e=>{const h=e.target.closest('th');if(!h)return;const k=h.dataset.k;if(k===sk)sd=-sd;else{sk=k;sd=(k==='name'||k==='rank')?1:-1;}render();});
$('#viewSeg').addEventListener('click',e=>{const b=e.target.closest('button');if(!b)return;view=b.dataset.v;try{localStorage.setItem('bbac.teamsView',view)}catch(_){}render();});
render();
})()</script>"""


def build(doc: dict) -> str:
    css, hdr, hjs = teams_masthead(doc.get('season', '2026-27'))
    data = json.dumps(doc, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return ('<!doctype html>\n<html lang="zh-Hant"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>球隊評分 · PureOVR</title>'
            '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 64 64\'%3E%3Crect width=\'64\' height=\'64\' rx=\'14\' fill=\'%230d1014\'/%3E%3Ccircle cx=\'32\' cy=\'32\' r=\'22\' fill=\'%23f2c230\'/%3E%3C/svg%3E">'
            '<link rel="preconnect" href="https://fonts.googleapis.com">'
            '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=Barlow:wght@400;500;600&family=Noto+Sans+TC:wght@400;500;700&display=swap">'
            + STYLE + css + '</head><body>' + hdr + '\n' + BODY
            + '<script type="application/json" id="data">' + data + '</script>' + JS + hjs + '</body></html>\n')


def main(argv=None) -> int:
    a = sys.argv[1:] if argv is None else argv
    out = Path(a[0])
    src = Path(a[1]) if len(a) > 1 else RATINGS
    doc = json.loads(src.read_text(encoding='utf-8'))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build(doc), encoding='utf-8')
    return 0


if __name__ == '__main__':
    sys.exit(main())
