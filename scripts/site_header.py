"""名單頁眉頭（使用者 2026-11-02「重新設計眉頭，參考 arammeta」）：黏頂毛玻璃一列＝PUREOVR 字標｜球員・球隊分頁｜篩選・設定・搜尋。
原本的控制項（#posSeg、#teamPick、#modeSeg、#q、賽季切換、更新說明）在頁尾腳本裡原封搬進眉頭，事件與 render 不用改；
舊的 .top 標題列與 .ctrl 控制列只剩空殼，直接隱藏。add_season_nav 之後呼叫。"""
import re

ICON = {
    'filter': '<path d="M4.2 4h15.6a1 1 0 0 1 .78 1.63L14.5 13.2v5.3a1 1 0 0 1-.55.9l-3 1.5A1 1 0 0 1 9.5 20v-6.8L3.42 5.63A1 1 0 0 1 4.2 4z" fill="currentColor" stroke="none"/>',
    'gear': '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>',
    'search': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
}


def _svg(k, size=16):
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICON[k]}</svg>')


SEASON = {'inseason': '2026-27', 'card': '2025-26'}

CSS = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Righteous&display=swap">
<style>
body{margin:0}  /* 名單頁原本留瀏覽器預設 8px，眉頭在球員／戰力排行兩頁之間會上下左右跳 */
.mast{position:sticky;top:0;z-index:50;background:color-mix(in srgb,var(--bg) 78%,transparent);
  -webkit-backdrop-filter:saturate(180%) blur(14px);backdrop-filter:saturate(180%) blur(14px);border-bottom:1px solid var(--line);transition:box-shadow .25s,border-color .25s}
.mast.scrolled{border-bottom-color:transparent;box-shadow:0 6px 22px -10px rgba(0,0,0,.6)}
.mast-in{display:flex;align-items:center;gap:16px;height:56px;max-width:1360px;margin:0 auto;box-sizing:border-box;
  padding:0 max(16px,env(safe-area-inset-right,0px)) 0 max(16px,env(safe-area-inset-left,0px))}
.mbrand{display:inline-flex;align-items:baseline;gap:8px;text-decoration:none;flex:none;width:168px}  /* 固定寬：Righteous 字型晚到時分頁不會被推動 */
.mbrand b{font:400 1.6rem/1 "Righteous",var(--f-disp);letter-spacing:.02em;color:var(--fg)}
.mbrand b span{color:var(--muted)}
.mbrand b i{font-style:inherit;color:var(--gold)}
.mbrand:hover b span{color:var(--fg)}
.mbrand small{font:600 .78rem var(--f-disp);letter-spacing:.06em;color:var(--muted);font-variant-numeric:tabular-nums}
.mtabs{position:relative;display:flex;align-items:center;gap:2px;margin:0 auto 0 8px}
.mtab,.mtabs .tpick summary{appearance:none;box-sizing:border-box;margin:0;border:0;background:none;color:var(--muted);font:600 1.02rem/1 var(--f-body);letter-spacing:.02em;
  height:36px;padding:0 14px;border-radius:8px;cursor:pointer;white-space:nowrap;display:flex;align-items:center;gap:6px;transition:color .14s,background-color .14s}
.mtabs .tpick summary img{width:18px;height:18px;margin:0}
.mtab{text-decoration:none}
.mtab:hover,.mtabs .tpick summary:hover{color:var(--fg);background:color-mix(in srgb,var(--fg) 7%,transparent)}
.mtab[aria-selected="true"],.mtabs .tpick.on summary{color:var(--fg);background:var(--panel)}
.mtabs .tpick summary{border:0}
/* 選隊沿用 #teamPick 的舊規則（ID 選擇器，手機版會把「球隊」縮成 .85rem），這裡一律用 #teamPick 蓋回，選隊前後字級相同 */
.mtabs #teamPick summary::after,.mtab-pick::after{content:"▾";font-size:.75rem;letter-spacing:.02em;opacity:.7;margin:0}
.mtabs #teamPick:not(.on) summary{font-size:0;gap:0}
.mtabs #teamPick:not(.on) summary::before{content:"球隊";font-size:1.02rem;letter-spacing:.02em}
/* 「球隊」格固定最小寬（最寬的 GSW＋隊徽約 104px），選哪隊後面的「戰力排行」都不會被推動 */
.mtabs #teamPick summary,.mtab-pick{min-width:106px;justify-content:center}
.mtabs #teamPick:not(.on) summary::after{margin-left:6px}
.mtabs .tpick.on summary{border:0;color:var(--fg)}
.mtabs .tpick summary:focus-visible,.mtab:focus-visible,.micon:focus-visible{outline:2px solid var(--gold);outline-offset:1px}
.mind{position:absolute;bottom:0;left:var(--ix,0);width:var(--iw,0);height:3px;border-radius:3px 3px 0 0;background:var(--gold);
  box-shadow:0 0 8px color-mix(in srgb,var(--gold) 50%,transparent);pointer-events:none}
.mast:not(.ready) .mind{visibility:hidden}
.mast:not(.ready) .mtab[aria-selected="true"]{position:relative}
.mast:not(.ready) .mtab[aria-selected="true"]::before{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;border-radius:3px 3px 0 0;background:var(--gold);
  box-shadow:0 0 8px color-mix(in srgb,var(--gold) 50%,transparent)}
.mast.ready .mind{transition:left .22s cubic-bezier(.2,.7,.2,1),width .22s cubic-bezier(.2,.7,.2,1)}
.macts{display:flex;align-items:center;gap:8px;flex:none}
.mpop{position:relative}
.mpop>summary{list-style:none}
.mpop>summary::-webkit-details-marker{display:none}
.micon{position:relative;display:inline-flex;align-items:center;gap:6px;height:34px;box-sizing:border-box;padding:0 11px;background:transparent;color:var(--muted);
  border:1px solid var(--line);border-radius:6px;font:600 .85rem var(--f-body);cursor:pointer;white-space:nowrap;transition:color .12s,border-color .12s,background-color .12s}
.micon:hover,.mpop[open]>.micon{color:var(--fg);border-color:var(--muted);background:var(--panel)}
.micon:active{transform:scale(.96)}
.micon.dot::after{content:"";position:absolute;top:5px;right:5px;width:7px;height:7px;border-radius:50%;background:var(--gold);box-shadow:0 0 0 2px var(--bg)}
.mpanel{position:absolute;right:0;top:calc(100% + 8px);z-index:20;min-width:220px;box-sizing:border-box;padding:12px;background:var(--panel-2);
  border:1px solid var(--line);border-radius:8px;box-shadow:0 14px 36px rgba(0,0,0,.6);display:grid;gap:12px}
.mrow{display:grid;gap:6px}
.mrow>b{color:var(--muted);font:600 .72rem var(--f-disp);letter-spacing:.12em;text-transform:uppercase}
.mrow .seg{justify-self:start}
.mrow .seg a{display:block;background:var(--panel);color:var(--muted);border-right:1px solid var(--line);font:600 .9rem var(--f-disp);letter-spacing:.04em;padding:6px 12px;text-decoration:none;white-space:nowrap}
.mrow .seg a:last-child{border-right:0}
.mrow .seg a[aria-current="page"]{background:var(--gold);color:var(--gold-ink)}
.mrow .seg{flex:none;width:max-content}
.mrow .seg button{height:32px;padding:0 12px;white-space:nowrap}
.mrow .pnote summary{height:32px;box-sizing:border-box;padding:0 12px}
.mast .pn{position:fixed;left:auto;right:max(16px,calc((100vw - 1360px)/2 + 16px));top:calc(var(--mh,57px) + 8px);width:min(560px,calc(100vw - 32px));max-height:calc(100vh - 80px)}
.msearch{position:relative;display:flex;align-items:center}
.msearch .sbtn{display:none}
.msearch .sbox{position:relative;display:flex;align-items:center}
.msearch .sbox>svg{position:absolute;left:10px;color:var(--muted);pointer-events:none}
.msearch #q{width:200px;height:34px;box-sizing:border-box;padding:0 10px 0 32px;background:var(--panel);border:1px solid var(--line);color:var(--fg);
  border-radius:6px;font:500 .88rem var(--f-body);transition:width .2s,border-color .12s}
.msearch #q:focus{outline:0;border-color:var(--gold);width:240px}
.wrap>.top,.wrap>.ctrl{display:none}
@media (min-width:641px){.wrap{padding-top:10px}}
@media (max-width:640px){
  .mast-in{flex-wrap:wrap;height:auto;padding-top:8px;padding-bottom:0;gap:0 10px}
  .mbrand b{font-size:1.4rem}
  .mbrand{min-height:34px}  /* 和 .micon 同高：沒有右側按鈕的戰力排行頁，分頁列才不會比首頁高 */
  .macts{margin-left:auto;gap:6px}
  .mtabs{order:10;flex-basis:100%;margin:4px 0 0}
  .mtab,.mtabs .tpick summary{height:40px;padding:0 11px;font-size:15px}
  .mbrand{width:auto}
  .mtabs #teamPick:not(.on) summary::before{font-size:15px}
  .micon{width:34px;padding:0;justify-content:center}
  .micon>span{display:none}
  .mpanel{position:fixed;left:12px;right:12px;top:calc(var(--mh,96px) + 6px);min-width:0}
  /* 舊手機規則 #posSeg{display:none}（位置要點 .pbtn 才展開）在位置列搬進篩選面板後仍生效 → 面板開了卻空的（使用者 2026-11-02） */
  #mPos #posSeg{display:flex;position:static;box-shadow:none}
  #mPos #posSeg button{height:36px;padding:0 13px}
  .mast .pn{top:calc(var(--mh,96px) + 6px);right:12px;width:calc(100vw - 24px)}
  .msearch .sbtn{display:inline-flex}
  .msearch .sbox{display:none;position:fixed;left:12px;right:12px;top:calc(var(--mh,96px) + 6px);z-index:20;padding:10px;background:var(--panel-2);border:1px solid var(--line);border-radius:8px;box-shadow:0 14px 36px rgba(0,0,0,.6)}
  .msearch.open .sbox{display:flex}
  .msearch .sbox>svg{left:20px}
  .msearch #q,.msearch #q:focus{width:100%;height:40px;font-size:16px}
  .mtabs .tpick .tpop{position:fixed;left:12px!important;right:12px;top:calc(var(--mh,96px) + 6px);width:auto}
}
@media (prefers-reduced-motion:reduce){.mast.ready .mind,.msearch #q{transition:none}}
</style>"""

# 頁尾腳本：搬元素、分頁底線、篩選小點、手機搜尋、捲動陰影
JS = """<script>(()=>{
const $=s=>document.querySelector(s),mast=$('.mast');if(!mast)return;
const tabs=$('.mtabs'),ind=$('.mind'),tp=$('#teamPick'),pos=$('#posSeg'),fb=$('#mFilter>summary');
if(tp){$('#mPickPh').replaceWith(tp);if(location.hash==='#team'){history.replaceState(null,'',location.pathname+location.search);setTimeout(()=>tp.open=true);}}
if(pos)$('#mPos').append(pos);
const season=$('.snav .seg');if(season)$('#mSeason').append(season);
const mode=$('#modeSeg');if(mode)$('#mMode').append(mode);
const pn=$('.snav .pnote');if(pn)$('#mNotes').append(pn);else $('#mNotes').closest('.mrow').remove();
const q=$('#q');if(q){$('.msearch .sbox').append(q);q.placeholder='搜尋球員或球隊';}
const pl=$('#mPlayers');
const sync=()=>{
  const on=tp&&tp.classList.contains('on');pl.setAttribute('aria-selected',String(!on));
  const t=on?tp.querySelector('summary'):pl,a=tabs.getBoundingClientRect(),r=t.getBoundingClientRect();
  ind.style.setProperty('--ix',(r.left-a.left)+'px');ind.style.setProperty('--iw',r.width+'px');mast.style.setProperty('--mh',mast.offsetHeight+'px');
  const b=pos&&pos.querySelector('[aria-pressed="true"]');fb.classList.toggle('dot',!!b&&b!==pos.firstElementChild);
};
pl.onclick=()=>{const b=$('#teamGrid [data-t="ALL"]');if(b&&tp.classList.contains('on'))b.click();};
const mo=new MutationObserver(sync);
if(tp)mo.observe(tp,{attributes:true,attributeFilter:['class'],childList:true,subtree:true});
if(pos)mo.observe(pos,{childList:true,subtree:true,attributes:true});
addEventListener('resize',sync);sync();requestAnimationFrame(()=>mast.classList.add('ready'));
if(document.fonts)document.fonts.ready.then(sync);
const pops=[...document.querySelectorAll('.mpop')];
pops.forEach(d=>d.addEventListener('toggle',()=>{if(d.open)pops.forEach(o=>o!==d&&(o.open=false));}));
pos&&pos.addEventListener('click',e=>{if(e.target.closest('button'))$('#mFilter').open=false;});
const ms=$('.msearch'),qd=()=>$('.msearch .sbtn').classList.toggle('dot',!!(q&&q.value.trim()));
q&&q.addEventListener('input',qd);
$('.msearch .sbtn').onclick=e=>{e.stopPropagation();const o=ms.classList.toggle('open');if(o)q&&q.focus();};
document.addEventListener('click',e=>{
  pops.forEach(d=>{if(d.open&&!d.contains(e.target))d.open=false;});
  if(!ms.contains(e.target))ms.classList.remove('open');
});
document.addEventListener('keydown',e=>{if(e.key!=='Escape')return;pops.forEach(d=>d.open=false);ms.classList.remove('open');});
const sc=()=>mast.classList.toggle('scrolled',scrollY>4);addEventListener('scroll',sc,{passive:true});sc();
})()</script>"""


def header_html(current):
    return (
        '<header class="mast"><div class="mast-in">'
        f'<a class="mbrand" href="index.html" aria-label="PureOVR 首頁"><b><span>Pure</span><i>OVR</i></b><small>{SEASON[current]}</small></a>'
        '<nav class="mtabs" aria-label="主要分頁">'
        '<button type="button" class="mtab" id="mPlayers" aria-selected="true">球員</button>'
        '<span class="mtab mtab-pick" id="mPickPh">球隊</span>'
        '<span class="mind" aria-hidden="true"></span>'
        '<a class="mtab" id="mTeams" href="teams.html">戰力排行</a></nav>'
        '<div class="macts">'
        f'<details class="mpop" id="mFilter"><summary class="micon" title="篩選" aria-label="篩選">{_svg("filter", 15)}<span>篩選</span></summary>'
        '<div class="mpanel"><div class="mrow"><b>位置</b><div id="mPos"></div></div></div></details>'
        f'<details class="mpop" id="mSettings"><summary class="micon" title="設定" aria-label="設定">{_svg("gear")}<span>設定</span></summary>'
        '<div class="mpanel"><div class="mrow"><b>賽季</b><div id="mSeason"></div></div>'
        '<div class="mrow"><b>能力值顯示</b><div id="mMode"></div></div>'
        '<div class="mrow"><b>版本</b><div id="mNotes"></div></div></div></details>'
        f'<div class="msearch"><button type="button" class="micon sbtn" title="搜尋" aria-label="搜尋">{_svg("search")}</button>'
        f'<div class="sbox">{_svg("search", 15)}</div></div>'
        '</div></div></header>'
    )


def teams_masthead(season='2026-27'):
    """teams.html 的眉頭：同一組 CSS，分頁＝球員（連回首頁）｜球隊（首頁並打開選隊）｜戰力排行（目前頁）。回傳 (css, header_html, js)。"""
    hdr = (
        '<header class="mast"><div class="mast-in">'
        f'<a class="mbrand" href="index.html" aria-label="PureOVR 首頁"><b><span>Pure</span><i>OVR</i></b><small>{season}</small></a>'
        '<nav class="mtabs" aria-label="主要分頁">'
        '<a class="mtab" id="mPlayers" href="index.html">球員</a>'
        '<a class="mtab mtab-pick" href="index.html#team">球隊</a>'
        '<span class="mind" aria-hidden="true"></span>'
        '<a class="mtab" id="mTeams" href="teams.html" aria-selected="true">戰力排行</a></nav>'
        '</div></header>'
    )
    js = ("<script>(()=>{const m=document.querySelector('.mast'),tabs=m.querySelector('.mtabs'),ind=m.querySelector('.mind'),"
          "cur=m.querySelector('.mtab[aria-selected=\"true\"]');"
          "const sync=()=>{const a=tabs.getBoundingClientRect(),r=cur.getBoundingClientRect();"
          "ind.style.setProperty('--ix',(r.left-a.left)+'px');ind.style.setProperty('--iw',r.width+'px');m.style.setProperty('--mh',m.offsetHeight+'px');};"
          "addEventListener('resize',sync);sync();if(document.fonts)document.fonts.ready.then(sync);requestAnimationFrame(()=>m.classList.add('ready'));"
          "const sc=()=>m.classList.toggle('scrolled',scrollY>4);addEventListener('scroll',sc,{passive:true});sc();})()</script>")
    return CSS, hdr, js


def add_masthead(html_str, current):
    assert current in SEASON, current
    # season_nav 的 #modeSeg 手機／桌機搬家腳本會把它搬回控制列，眉頭接手後拿掉
    s, n = re.subn(r"<script>addEventListener\('DOMContentLoaded',\(\)=>\{const m=document\.getElementById\('modeSeg'\).*?</script>",
                   '', html_str, count=1, flags=re.S)
    assert n == 1, 'modeSeg mover not found'
    # 能力值預設顯示 99 數字（使用者 2026-11-02「預設使用 99，而不是 A+」）；按過 A+ 的人仍記住 A+
    a = "localStorage.getItem('bbac.mode') === 'num' ? 'num' : 'grade'; } catch (e) { return 'grade'; }"
    assert s.count(a) == 1, 'mode default not found'
    s = s.replace(a, "localStorage.getItem('bbac.mode') === 'grade' ? 'grade' : 'num'; } catch (e) { return 'num'; }")
    assert s.count('<div class="wrap">') == 1, 'wrap not found'
    s = s.replace('<div class="wrap">', CSS + header_html(current) + '\n<div class="wrap">', 1)
    i = s.rfind('</body>')
    return s[:i] + JS + s[i:] if i >= 0 else s + JS
