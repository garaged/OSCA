from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse

from osca.analytical_data import (
    ChartSeriesRequest,
    DerivedSeriesKind,
    DerivedSeriesRequest,
    build_chart_series,
)


def visualization_router() -> APIRouter:
    router = APIRouter()

    @router.get("/charts", response_class=HTMLResponse)
    def chart_page() -> str:
        return _chart_html()

    @router.get("/api/chart-series")
    def chart_series(
        payload_path: Path,
        dataset_revision_id: UUID,
        symbol: str,
        timeframe: str,
        start: datetime | None = None,
        end: datetime | None = None,
        max_rows: int = Query(default=2_000, ge=2, le=50_000),
        derived: list[str] = Query(default=[]),
    ) -> dict[str, object]:
        try:
            result = build_chart_series(
                ChartSeriesRequest(
                    dataset_revision_id=dataset_revision_id,
                    payload_path=payload_path,
                    symbol=symbol,
                    timeframe=timeframe,
                    start=start,
                    end=end,
                    max_rows=max_rows,
                    derived=tuple(_parse_derived(item) for item in derived),
                )
            )
        except (FileNotFoundError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return result.model_dump(mode="json")

    @router.get("/api/chart-series.csv", response_class=PlainTextResponse)
    def chart_series_csv(
        payload_path: Path,
        dataset_revision_id: UUID,
        symbol: str,
        timeframe: str,
        start: datetime | None = None,
        end: datetime | None = None,
        max_rows: int = Query(default=2_000, ge=2, le=50_000),
        derived: list[str] = Query(default=[]),
    ) -> str:
        try:
            result = build_chart_series(
                ChartSeriesRequest(
                    dataset_revision_id=dataset_revision_id,
                    payload_path=payload_path,
                    symbol=symbol,
                    timeframe=timeframe,
                    start=start,
                    end=end,
                    max_rows=max_rows,
                    derived=tuple(_parse_derived(item) for item in derived),
                )
            )
        except (FileNotFoundError, ValueError) as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return _csv(result.model_dump(mode="json"))

    return router


def _parse_derived(value: str) -> DerivedSeriesRequest:
    name, separator, raw_window = value.partition(":")
    try:
        kind = DerivedSeriesKind(name)
    except ValueError as exc:
        raise ValueError(f"unknown derived series: {name}") from exc
    window = int(raw_window) if separator else None
    return DerivedSeriesRequest(kind=kind, window=window)


def _csv(payload: dict[str, object]) -> str:
    rows = payload.get("rows")
    if not isinstance(rows, list):
        raise ValueError("chart rows are unavailable")
    derived_names = sorted(
        {
            key
            for row in rows
            if isinstance(row, dict)
            for key in row.get("derived", {})
            if isinstance(key, str)
        }
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["dataset_revision_id", "symbol", "timeframe", "timestamp", "open", "high", "low", "close", "volume", *derived_names]
    )
    for row in rows:
        if not isinstance(row, dict):
            continue
        derived_values = row.get("derived", {})
        if not isinstance(derived_values, dict):
            derived_values = {}
        writer.writerow(
            [
                payload["dataset_revision_id"],
                payload["symbol"],
                payload["timeframe"],
                row.get("timestamp"),
                row.get("open"),
                row.get("high"),
                row.get("low"),
                row.get("close"),
                row.get("volume"),
                *(derived_values.get(name) for name in derived_names),
            ]
        )
    return output.getvalue()


def _chart_html() -> str:
    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src 'self' data: blob:">
<title>OSCA Market Data Visualization</title>
<style>
:root { color-scheme: dark; font-family: ui-sans-serif, system-ui, sans-serif; }
body { margin: 0; background: #0b1220; color: #e5e7eb; }
header, main { padding: 1rem max(1rem, 4vw); }
header { border-bottom: 1px solid #334155; }
h1 { margin: 0 0 .35rem; }
p { color: #94a3b8; }
form { display: grid; grid-template-columns: repeat(auto-fit,minmax(180px,1fr)); gap: .75rem; }
label { display: grid; gap: .3rem; font-size: .8rem; color: #cbd5e1; }
input, button, select { padding: .55rem; border-radius: 8px; border: 1px solid #475569; background: #111827; color: #e5e7eb; }
button { cursor: pointer; }
.actions { display:flex; gap:.5rem; align-items:end; flex-wrap:wrap; }
.panel { margin-top: 1rem; border: 1px solid #334155; border-radius: 12px; background: #111827; padding: .75rem; }
#chart { width: 100%; height: 620px; touch-action: none; }
.gridline { stroke: #263449; stroke-width: 1; }
.axis { fill: #94a3b8; font-size: 11px; }
.up { fill: #34d399; stroke: #34d399; }
.down { fill: #f87171; stroke: #f87171; }
.volume { fill: #64748b; opacity: .55; }
.overlay { fill: none; stroke-width: 2; }
.crosshair { stroke: #e2e8f0; stroke-width: 1; stroke-dasharray: 4 4; pointer-events:none; }
#tooltip { position: fixed; display:none; pointer-events:none; background:#020617; border:1px solid #475569; border-radius:8px; padding:.55rem; font-size:.8rem; white-space:pre; }
.status { min-height: 1.4rem; color: #93c5fd; }
.warning { color:#fde68a; }
.error { color:#fca5a5; }
table { width:100%; border-collapse:collapse; font-size:.8rem; }
th,td { text-align:right; padding:.35rem; border-bottom:1px solid #263449; }
th:first-child,td:first-child { text-align:left; }
.sr-only { position:absolute; width:1px; height:1px; overflow:hidden; clip:rect(0,0,0,0); }
</style>
</head>
<body>
<header><h1>Market Data Visualization</h1><p>Local, read-only OHLCV charts powered only by governed U2 analytical output.</p></header>
<main>
<form id="query">
<label>Payload path<input name="payload_path" required></label>
<label>Dataset revision UUID<input name="dataset_revision_id" required></label>
<label>Symbol<input name="symbol" value="AAPL" required></label>
<label>Timeframe<input name="timeframe" value="1d" required></label>
<label>Start<input name="start" type="datetime-local"></label>
<label>End<input name="end" type="datetime-local"></label>
<label>Maximum rows<input name="max_rows" type="number" min="2" max="50000" value="2000"></label>
<label>Overlay<select name="overlay"><option value="">None</option><option value="sma:20">SMA 20</option><option value="ema:20">EMA 20</option><option value="rolling_volatility:20">Volatility 20</option></select></label>
<div class="actions"><button type="submit">Load chart</button><button type="button" id="reset">Reset view</button><button type="button" id="svgExport">Export SVG</button><button type="button" id="csvExport">Export CSV</button><button type="button" id="jsonExport">Export JSON</button></div>
</form>
<div id="status" class="status" aria-live="polite"></div>
<div class="panel"><svg id="chart" role="img" aria-labelledby="chartTitle chartDescription" viewBox="0 0 1200 620"><title id="chartTitle">OHLCV chart</title><desc id="chartDescription">Candlestick price chart with volume and optional derived overlay.</desc></svg><div id="tooltip"></div></div>
<div class="panel"><details><summary>Accessible visible-data table</summary><div style="overflow:auto"><table id="dataTable"><thead></thead><tbody></tbody></table></div></details></div>
<p class="warning">No recommendations, provider credentials, broker connections, or order execution.</p>
</main>
<script>
const form=document.getElementById('query'),svg=document.getElementById('chart'),statusNode=document.getElementById('status'),tooltip=document.getElementById('tooltip');
let payload=null, viewStart=0, viewEnd=0, dragX=null;
const ns='http://www.w3.org/2000/svg';
function el(name,attrs={}){const n=document.createElementNS(ns,name);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,String(v)));return n;}
function params(){const data=new FormData(form),p=new URLSearchParams();for(const [k,v] of data.entries()){if(k==='overlay'){if(v)p.append('derived',String(v));}else if(v)p.set(k,String(v));}return p;}
async function load(){statusNode.textContent='Loading governed chart data…';statusNode.className='status';try{const r=await fetch('/api/chart-series?'+params());if(!r.ok)throw new Error((await r.json()).detail||`HTTP ${r.status}`);payload=await r.json();viewStart=0;viewEnd=payload.rows.length;render();statusNode.textContent=`${payload.returned_row_count} rows · ${payload.symbol} ${payload.timeframe} · revision ${payload.dataset_revision_id}`;}catch(e){statusNode.textContent=String(e);statusNode.className='status error';}}
function visible(){return payload?payload.rows.slice(viewStart,viewEnd):[];}
function render(){while(svg.lastChild&&svg.lastChild.tagName!=='desc'&&svg.lastChild.tagName!=='title')svg.removeChild(svg.lastChild);const rows=visible();if(!rows.length)return;const W=1200,H=620,left=64,right=20,top=20,priceH=420,volTop=470,volH=110;const lows=rows.map(r=>r.low),highs=rows.map(r=>r.high),min=Math.min(...lows),max=Math.max(...highs),span=max-min||1,maxVol=Math.max(...rows.map(r=>r.volume),1),step=(W-left-right)/rows.length,body=Math.max(1,step*.58);for(let i=0;i<6;i++){const y=top+i*priceH/5;svg.append(el('line',{x1:left,y1:y,x2:W-right,y2:y,class:'gridline'}));const t=el('text',{x:8,y:y+4,class:'axis'});t.textContent=(max-i*span/5).toFixed(2);svg.append(t);}rows.forEach((r,i)=>{const x=left+(i+.5)*step,yo=top+(max-r.open)/span*priceH,yc=top+(max-r.close)/span*priceH,yh=top+(max-r.high)/span*priceH,yl=top+(max-r.low)/span*priceH,cls=r.close>=r.open?'up':'down';svg.append(el('line',{x1:x,y1:yh,x2:x,y2:yl,class:cls}));svg.append(el('rect',{x:x-body/2,y:Math.min(yo,yc),width:body,height:Math.max(1,Math.abs(yc-yo)),class:cls}));svg.append(el('rect',{x:x-body/2,y:volTop+volH-(r.volume/maxVol)*volH,width:body,height:(r.volume/maxVol)*volH,class:'volume'}));});const names=Object.keys(rows[0].derived||{});names.forEach((name,index)=>{const points=rows.map((r,i)=>r.derived[name]==null?null:[left+(i+.5)*step,top+(max-r.derived[name])/span*priceH]).filter(Boolean);if(points.length){const path=el('path',{d:points.map((p,i)=>(i?'L':'M')+p[0]+' '+p[1]).join(' '),class:'overlay',stroke:index%2?'#fbbf24':'#60a5fa'});svg.append(path);}});const hit=el('rect',{x:left,y:top,width:W-left-right,height:priceH+volH+30,fill:'transparent'});hit.addEventListener('pointermove',e=>hover(e,rows,left,step));hit.addEventListener('pointerleave',()=>{tooltip.style.display='none';document.querySelectorAll('.crosshair').forEach(n=>n.remove());});hit.addEventListener('wheel',e=>{e.preventDefault();zoom(e.deltaY,Math.floor((e.offsetX-left)/step));},{passive:false});hit.addEventListener('pointerdown',e=>{dragX=e.clientX;hit.setPointerCapture(e.pointerId);});hit.addEventListener('pointerup',e=>{if(dragX!==null){pan(Math.round((dragX-e.clientX)/Math.max(step,1)));dragX=null;}hit.releasePointerCapture(e.pointerId);});svg.append(hit);renderTable(rows);}
function hover(e,rows,left,step){document.querySelectorAll('.crosshair').forEach(n=>n.remove());const i=Math.max(0,Math.min(rows.length-1,Math.floor((e.offsetX-left)/step))),r=rows[i],x=left+(i+.5)*step;svg.append(el('line',{x1:x,y1:20,x2:x,y2:600,class:'crosshair'}));tooltip.style.display='block';tooltip.style.left=(e.clientX+12)+'px';tooltip.style.top=(e.clientY+12)+'px';tooltip.textContent=`${r.timestamp}\nO ${r.open}  H ${r.high}\nL ${r.low}  C ${r.close}\nVolume ${r.volume}`+Object.entries(r.derived||{}).map(([k,v])=>`\n${k} ${v==null?'warm-up':v}`).join('');}
function zoom(delta,anchor){if(!payload)return;const len=viewEnd-viewStart,next=Math.max(5,Math.min(payload.rows.length,len+(delta>0?Math.ceil(len*.2):-Math.ceil(len*.2))));const ratio=Math.max(0,Math.min(1,anchor/Math.max(1,len-1)));let start=Math.round((viewStart+anchor)-ratio*next);start=Math.max(0,Math.min(payload.rows.length-next,start));viewStart=start;viewEnd=start+next;render();}
function pan(amount){if(!payload)return;const len=viewEnd-viewStart,start=Math.max(0,Math.min(payload.rows.length-len,viewStart+amount));viewStart=start;viewEnd=start+len;render();}
function renderTable(rows){const head=document.querySelector('#dataTable thead'),body=document.querySelector('#dataTable tbody'),derived=Object.keys(rows[0].derived||{});head.innerHTML='<tr>'+['Timestamp','Open','High','Low','Close','Volume',...derived].map(x=>`<th>${x}</th>`).join('')+'</tr>';body.innerHTML=rows.map(r=>'<tr>'+[r.timestamp,r.open,r.high,r.low,r.close,r.volume,...derived.map(k=>r.derived[k]??'')].map(x=>`<td>${x}</td>`).join('')+'</tr>').join('');}
function download(name,type,text){const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type}));a.download=name;a.click();URL.revokeObjectURL(a.href);}
form.addEventListener('submit',e=>{e.preventDefault();load();});document.getElementById('reset').onclick=()=>{if(payload){viewStart=0;viewEnd=payload.rows.length;render();}};document.getElementById('svgExport').onclick=()=>download('osca-chart.svg','image/svg+xml',new XMLSerializer().serializeToString(svg));document.getElementById('jsonExport').onclick=()=>payload&&download('osca-chart-data.json','application/json',JSON.stringify({...payload,rows:visible()},null,2));document.getElementById('csvExport').onclick=()=>{if(!payload)return;fetch('/api/chart-series.csv?'+params()).then(r=>r.text()).then(t=>download('osca-chart-data.csv','text/csv',t));};
</script>
</body>
</html>"""
