import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell, LineChart, Line
} from 'recharts';
import './styles.css';

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

function App() {
  const [page, setPage] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [ranking, setRanking] = useState([]);
  const [selected, setSelected] = useState(null);
  const [stress, setStress] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function load() {
    setLoading(true);
    setError('');
    try {
      const [o, r, e] = await Promise.all([
        fetch(`${API}/overview`), fetch(`${API}/risk-ranking?limit=100`), fetch(`${API}/evaluation`)
      ]);
      if (!o.ok || !r.ok) throw new Error('The backend could not load the dataset.');
      setOverview(await o.json());
      setRanking(await r.json());
      setEvaluation(e.ok ? await e.json() : null);
    } catch (err) {
      setError(err.message || 'Unable to connect to TrustCatalog API.');
    } finally { setLoading(false); }
  }

  useEffect(() => { load(); }, []);

  async function openSeller(id) {
    const res = await fetch(`${API}/sellers/${id}`);
    if (res.ok) { setSelected(await res.json()); setPage('seller'); }
  }

  async function runStress() {
    setPage('stress'); setStress(null);
    try {
      const res = await fetch(`${API}/stress-test`, {
        method: 'POST', headers: {'Content-Type':'application/json'},
        body: JSON.stringify({count: 10, severity: 1})
      });
      if (!res.ok) throw new Error('Stress test failed.');
      setStress(await res.json());
    } catch (e) { setError(e.message); }
  }

  if (loading) return <div className="boot"><div className="logoMark">TC</div><h1>TrustCatalog</h1><p>Loading catalog integrity intelligence…</p></div>;
  if (error && !overview) return <div className="boot"><div className="logoMark">TC</div><h1>TrustCatalog</h1><div className="errorCard"><b>Dataset/API not ready</b><p>{error}</p><p>Start the FastAPI backend and place the Olist CSV files in <code>data/raw/</code>.</p><button onClick={load}>Retry</button></div></div>;

  const nav = [
    ['overview','Overview','⌂'], ['ranking','Risk Ranking','◈'], ['seller','Seller Details','◎'],
    ['agents','Agent Analysis','◇'], ['stress','Stress Test','⚡'], ['evaluation','Evaluation','✓']
  ];

  return <div className="app">
    <aside className="sidebar">
      <div className="brand"><span className="brandMark">TC</span><div><b>TrustCatalog</b><small>Catalog Integrity AI</small></div></div>
      <div className="nav">{nav.map(([id,label,icon]) => <button key={id} className={page===id?'active':''} onClick={() => setPage(id)}><span>{icon}</span>{label}</button>)}</div>
      <div className="sideStatus"><span className="dot"/> <div><b>Monitoring active</b><small>Evidence-first risk engine</small></div></div>
      <div className="sideNote"><b>What TrustCatalog does</b><p>Detects behavioral deterioration before fulfillment problems become customer-facing failures.</p></div>
    </aside>
    <main className="main">
      <header className="topbar">
        <div><span className="eyebrow">ECOMMERCE PLATFORM INTEGRITY</span><h1>{nav.find(x=>x[0]===page)?.[1] || 'TrustCatalog'}</h1></div>
        <div className="topActions"><span className="dataBadge">● OLIST DATA</span><button className="stressBtn" onClick={runStress}>Run Stress Test →</button></div>
      </header>
      {error && <div className="toast">{error}<button onClick={()=>setError('')}>×</button></div>}
      {page==='overview' && <Overview overview={overview} ranking={ranking} onOpen={openSeller} setPage={setPage}/>} 
      {page==='ranking' && <Ranking rows={ranking} onOpen={openSeller}/>} 
      {page==='seller' && <Seller selected={selected} onBack={()=>setPage('ranking')} setPage={setPage}/>} 
      {page==='agents' && <Agents selected={selected}/>} 
      {page==='stress' && <Stress stress={stress}/>} 
      {page==='evaluation' && <Evaluation evaluation={evaluation} stress={stress}/>} 
    </main>
  </div>;
}

function Cards({o}) { return <div className="cards">
  <Card title="Sellers analyzed" value={fmt(o.total_sellers)} icon="S" />
  <Card title="Orders analyzed" value={fmt(o.total_orders)} icon="O" />
  <Card title="High-risk sellers" value={fmt(o.high_risk_sellers)} icon="!" tone="high" />
  <Card title="Detected anomalies" value={fmt(o.anomalies)} icon="A" />
</div>; }
function Card({title,value,icon,tone=''}) { return <div className="card"><div className="cardIcon">{icon}</div><span>{title}</span><strong className={tone}>{value}</strong></div>; }
function fmt(v) { return Number(v||0).toLocaleString(); }
function score(v) { return Number(v||0).toFixed(1); }
function pct(v) { return `${(Number(v||0)*100).toFixed(1)}%`; }

function Overview({overview,ranking,onOpen,setPage}) {
  const dist=[{name:'LOW',value:overview.low_risk_sellers},{name:'MEDIUM',value:overview.medium_risk_sellers},{name:'HIGH',value:overview.high_risk_sellers}];
  const colors=['#55a875','#d6a33e','#d45b5b'];
  const bars=ranking.slice(0,10).map(r=>({seller:r.seller_id.slice(0,6),risk:Number(r.risk_score)}));
  return <>
    <section className="heroIntro"><div><span className="eyebrow">EARLY-WARNING CONTROL CENTER</span><h2>Know which listings are becoming unreliable.</h2><p>TrustCatalog combines seller behavior, fulfillment signals, delivery performance and anomaly detection into an explainable risk score.</p></div><div className="heroScore"><span>Average risk</span><b>{score(overview.average_risk_score)}</b><small>/ 100</small></div></section>
    <Cards o={overview}/>
    <div className="grid two">
      <section className="panel chartPanel"><PanelTitle title="Risk distribution" sub="Current seller risk bands"/><div className="chartBox"><ResponsiveContainer><PieChart><Pie data={dist} dataKey="value" nameKey="name" innerRadius={65} outerRadius={92} paddingAngle={4}>{dist.map((d,i)=><Cell key={d.name} fill={colors[i]}/>)}</Pie><Tooltip/></PieChart></ResponsiveContainer><div className="legend">{dist.map((d,i)=><div key={d.name}><i style={{background:colors[i]}}/>{d.name}<b>{d.value}</b></div>)}</div></div></section>
      <section className="panel chartPanel"><PanelTitle title="Risk landscape" sub="Top-ranked seller risk scores"/><ResponsiveContainer width="100%" height={270}><BarChart data={bars} margin={{top:15,right:5,left:-20,bottom:10}}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="seller" tick={{fontSize:10}}/><YAxis domain={[0,100]} tick={{fontSize:10}}/><Tooltip/><Bar dataKey="risk" radius={[5,5,0,0]} fill="#163c40"/></BarChart></ResponsiveContainer></section>
    </div>
    <section className="panel"><PanelTitle title="Top Risk Alerts" sub="Highest-risk sellers requiring review" action={<button className="linkBtn" onClick={()=>setPage('ranking')}>View all →</button>}/><RiskTable rows={ranking.slice(0,8)} onOpen={onOpen}/></section>
  </>;
}
function PanelTitle({title,sub,action}) { return <div className="panelHead"><div><b>{title}</b><small>{sub}</small></div>{action}</div>; }

function RiskTable({rows,onOpen}) { return <div className="tableWrap"><table><thead><tr><th>Seller</th><th>Risk</th><th>Level</th><th>Orders</th><th>Cancellation</th><th>Delay</th><th>Deterioration</th><th>Anomaly</th></tr></thead><tbody>{rows.map((r,i)=><tr key={r.seller_id} onClick={()=>onOpen(r.seller_id)}><td><span className="rank">{i+1}</span><span className="mono">{r.seller_id}</span></td><td><b className="riskNum">{score(r.risk_score)}</b></td><td><span className={`pill ${String(r.risk_level).toLowerCase()}`}>{r.risk_level}</span></td><td>{fmt(r.orders)}</td><td>{pct(r.cancellation_rate)}</td><td>{score(r.delivery_delay_days)} d</td><td>{pct(r.deterioration)}</td><td>{score(r.anomaly_score)}</td></tr>)}</tbody></table></div>; }
function Ranking({rows,onOpen}) { return <section className="panel"><PanelTitle title="Seller Risk Ranking" sub="Sorted by reproducible 0–100 behavioral risk score"/><div className="filterRow"><span>Showing {rows.length} analyzed sellers</span><span className="smallNote">Click a row for evidence →</span></div><RiskTable rows={rows} onOpen={onOpen}/></section>; }

function Seller({selected,onBack,setPage}) {
  if (!selected) return <Empty title="No seller selected" text="Open a seller from Risk Ranking to inspect its evidence."/>;
  const m=selected.metrics, a=selected.analysis, historical=[{name:'Historical',cancel:m.baseline_cancel_rate,delay:m.baseline_avg_delay_days},{name:'Recent',cancel:m.recent_cancel_rate,delay:m.recent_avg_delay_days}];
  return <><button className="back" onClick={onBack}>← Back to ranking</button><section className="sellerHero"><div><span className="eyebrow">SELLER PROFILE</span><div className="sellerId mono">{selected.seller_id}</div><div className="riskLine"><b>{score(selected.risk_score)}</b><span>/100</span><span className={`pill ${selected.risk_level.toLowerCase()}`}>{selected.risk_level} RISK</span></div></div><div className="sellerSummary">{a.explanation.summary}</div></section>
    <div className="grid four"><Metric label="Recent orders" value={fmt(m.recent_orders)}/><Metric label="Recent cancellation" value={pct(m.recent_cancel_rate)}/><Metric label="Recent delay" value={`${score(m.recent_avg_delay_days)} d`}/><Metric label="Anomaly score" value={score(m.anomaly_score)}/></div>
    <div className="grid two"><section className="panel"><PanelTitle title="Historical vs recent" sub="Performance deterioration is measured against a baseline"/><ResponsiveContainer width="100%" height={250}><BarChart data={historical}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="name"/><YAxis yAxisId="left"/><YAxis yAxisId="right" orientation="right"/><Tooltip/><Bar yAxisId="left" dataKey="cancel" name="Cancellation rate" fill="#d45b5b" radius={[5,5,0,0]}/><Bar yAxisId="right" dataKey="delay" name="Delay days" fill="#163c40" radius={[5,5,0,0]}/></BarChart></ResponsiveContainer></section><section className="panel"><PanelTitle title="Why was this seller flagged?" sub="Evidence generated from computed signals"/><ul className="evidence">{a.explanation.evidence.map((x,i)=><li key={i}>{x}</li>)}</ul><div className="actionBox"><b>Recommended action</b><p>{a.explanation.recommended_action}</p></div></section></div>
    <section className="panel"><PanelTitle title="Seller → product signals" sub="Listings associated with this seller"/><ListingTable rows={selected.listing_summary}/></section>
    <div className="quickLinks"><button onClick={()=>setPage('agents')}>Inspect agent reasoning →</button><button onClick={()=>setPage('stress')}>Run stress test →</button></div>
  </>;
}
function Metric({label,value}) { return <div className="metricBox"><span>{label}</span><strong>{value}</strong></div>; }
function ListingTable({rows}) { if(!rows?.length) return <p className="muted">No listing-level records available for this seller.</p>; return <div className="tableWrap"><table><thead><tr><th>Product</th><th>Orders</th><th>Failures</th><th>Late rate</th><th>Avg delay</th><th>Recent orders</th></tr></thead><tbody>{rows.map(r=><tr key={`${r.seller_id}-${r.product_id}`}><td className="mono">{r.product_id}</td><td>{fmt(r.listing_orders)}</td><td>{pct(r.listing_failure_rate)}</td><td>{pct(r.listing_late_rate)}</td><td>{score(r.listing_avg_delay_days)} d</td><td>{fmt(r.recent_listing_orders)}</td></tr>)}</tbody></table></div>; }

function Agents({selected}) {
  if(!selected) return <Empty title="Select a seller first" text="The cooperative agent chain becomes available after selecting a seller."/>;
  const a=selected.analysis; const nodes=[['01','Seller Behavior Agent',a.seller_behavior,'Behavior & deterioration'],['02','Shipping & Delivery Agent',a.shipping,'Delivery time & lateness'],['03','Order Reliability Agent',a.order_reliability,'Fulfillment outcomes'],['04','Anomaly Detection Agent',a.anomaly,'Statistical / ML anomaly'],['05','Risk Aggregator',a.risk,'Transparent weighted score'],['06','Explanation Agent',a.explanation,'Evidence-grounded narrative']];
  return <><section className="agentIntro"><span className="eyebrow">COOPERATIVE ANALYSIS</span><h2>{selected.seller_id}</h2><p>Each agent has a distinct responsibility. The Explanation Agent receives computed evidence; it does not create the underlying risk score.</p></section><div className="agentFlow">{nodes.map((n,i)=><div className="agentWrap" key={n[1]}><div className="agentNode"><div className="agentNum">{n[0]}</div><div className="agentBody"><div className="agentTitle"><div><b>{n[1]}</b><small>{n[3]}</small></div><span className="status">COMPLETE</span></div><pre>{JSON.stringify(n[2],null,2)}</pre></div></div>{i<nodes.length-1&&<div className="connector">↓</div>}</div>)}</div></>;
}

function Stress({stress}) {
  if(!stress) return <section className="empty stressEmpty"><div className="stressIcon">⚡</div><h2>Controlled degradation lab</h2><p>Run the detector against real Olist seller features after a reproducible in-memory degradation transform. The original dataset is never modified.</p><button className="stressBtn" onClick={()=>window.dispatchEvent(new Event('runStress'))}>Run Stress Test</button><div className="simulationRules"><span>REAL DATA</span><b>+</b><span>CONTROLLED DEGRADATION</span><b>→</b><span>EARLY-WARNING DETECTION</span></div></section>;
  const metrics=[['Detection rate',pct(stress.detection_rate)],['Precision@K',pct(stress.precision_at_k)],['Recall',pct(stress.recall)],['F1',pct(stress.f1)],['False-positive rate',pct(stress.false_positive_rate)]];
  return <><section className="stressBanner"><div><span className="eyebrow">SIMULATION ONLY</span><h2>Degraded sellers moved through the same detector.</h2><p>Selected: <b>{stress.degraded_count}</b> sellers · K = {stress.k} · labels are simulated</p></div><div className="simBadge">REAL DATA + CONTROLLED DEGRADATION</div></section><div className="metricStrip">{metrics.map(m=><div key={m[0]}><span>{m[0]}</span><b>{m[1]}</b></div>)}</div><div className="grid two"><section className="panel"><PanelTitle title="Before → after" sub="Risk movement for degraded sellers"/><div className="compare">{stress.before.map(b=>{const a=stress.after.find(x=>x.seller_id===b.seller_id);return <div className="compareRow" key={b.seller_id}><span className="mono">{b.seller_id}</span><span><b>{score(b.risk_score)}</b><small>{b.risk_level}</small></span><span className="arrowTxt">→</span><span><b>{a?score(a.risk_score):'—'}</b><small>{a?.risk_level||'—'}</small></span></div>})}</div></section><section className="panel"><PanelTitle title="Post-degradation top K" sub="Were degraded sellers surfaced near the top?"/><RiskTable rows={stress.ranking_top_k} onOpen={()=>{}}/></section></div><div className="disclaimer">Evaluation labels are created by the stress-test transform. They are not ghost-listing ground truth from Olist.</div></>;
}

function Evaluation({evaluation,stress}) { return <><section className="heroIntro compact"><div><span className="eyebrow">MODEL EVALUATION</span><h2>Measure the detector without pretending simulated labels are real.</h2><p>{evaluation?.note || 'Olist does not provide a direct ghost-listing ground-truth label. TrustCatalog evaluates early-warning behavior through controlled degradation.'}</p></div></section><div className="grid two"><section className="panel"><PanelTitle title="Evaluation protocol" sub="Controlled stress-test methodology"/><ol className="protocol"><li>Select sellers with sufficient historical activity.</li><li>Apply controlled deterioration in memory only.</li><li>Run the same feature scoring and anomaly detector.</li><li>Rank sellers by the resulting risk score.</li><li>Measure top-K detection, precision, recall and F1.</li></ol></section><section className="panel"><PanelTitle title="Latest run" sub="Live values from the last stress test"/>{stress?<div className="evalGrid">{[['Detection rate',stress.detection_rate],['Precision@K',stress.precision_at_k],['Recall',stress.recall],['F1',stress.f1],['FPR',stress.false_positive_rate]].map(x=><div key={x[0]}><span>{x[0]}</span><b>{pct(x[1])}</b></div>)}</div>:<div className="noRun">No stress test has been run in this session.</div>}</section></div></>;
}
function Empty({title,text}) { return <div className="empty"><h2>{title}</h2><p>{text}</p></div>; }

window.addEventListener('runStress', () => document.querySelector('.stressBtn')?.click());
createRoot(document.getElementById('root')).render(<App/>);
