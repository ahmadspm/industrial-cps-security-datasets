import { useMemo, useState } from "react";
import source from "../trace-counts.json";
import "./trace-dashboard.css";

const traces = source as Record<string, Array<[number, string, number]>>;
const classes = [...new Set(Object.values(traces).flatMap(rows => rows.map(row => row[1])))].sort();

export default function TraceDashboard() {
  const [trace, setTrace] = useState("trace_024");
  const [query, setQuery] = useState("");
  const [eventClass, setEventClass] = useState("");
  const { total, buckets, categories, untimed } = useMemo(() => {
    const totals = new Map<string, number>();
    const byTime = new Map<number, number>();
    let total = 0;
    let untimed = 0;
    for (const [bucket, category, count] of traces[trace]) {
      if ((eventClass && category !== eventClass) || !category.toLowerCase().includes(query.trim().toLowerCase())) continue;
      total += count;
      totals.set(category, (totals.get(category) ?? 0) + count);
      if (bucket < 0) untimed += count;
      else byTime.set(bucket, (byTime.get(bucket) ?? 0) + count);
    }
    return { total, untimed, buckets: [...byTime], categories: [...totals].sort((a, b) => b[1] - a[1]) };
  }, [trace, query, eventClass]);
  const last = Math.max(0, ...buckets.map(([bucket]) => bucket));
  const peak = Math.max(1, ...buckets.map(([, count]) => count));
  const width = 650 / (last + 1);

  return <section className="trace-board" aria-labelledby="trace-board-title">
    <header><div><h2 id="trace-board-title">Operational event dashboard</h2>
      <p>Recorded observations · 10-second elapsed-time buckets</p></div>
      <a href="https://github.com/ahmadspm/industrial-cps-security-datasets/tree/main/data/operational">Dataset ↗</a>
    </header>
    <div className="trace-filters">
      <label>Search event class<input type="search" placeholder="Filter by event-class ID" value={query} onChange={e => setQuery(e.target.value)} /></label>
      <label>Trace<select value={trace} onChange={e => setTrace(e.target.value)}>{Object.keys(traces).map(id => <option key={id}>{id}</option>)}</select></label>
      <label>Event class<select value={eventClass} onChange={e => setEventClass(e.target.value)}><option value="">All event classes</option>{classes.map(id => <option key={id}>{id}</option>)}</select></label>
      <button type="button" onClick={() => { setQuery(""); setTrace("trace_024"); setEventClass(""); }}>Reset filters</button>
    </div>
    <div className="trace-metrics" aria-live="polite">
      <div><span>Matching events</span><strong>{total.toLocaleString()}</strong></div>
      <div><span>Event classes</span><strong>{categories.length}</strong></div>
      <div><span>Events without time</span><strong>{untimed.toLocaleString()}</strong></div>
    </div>
    <div className="trace-charts">
      <article><h3>Event activity over time</h3>
        {buckets.length ? <svg viewBox="0 0 720 235" role="img" aria-label={`Event counts for ${trace}, peak ${peak} events per 10 seconds`}>
          {[0, .25, .5, .75, 1].map(ratio => <g key={ratio}><line x1="45" x2="695" y1={190-160*ratio} y2={190-160*ratio} stroke="#dbe6ef" /><text x="38" y={194-160*ratio} textAnchor="end">{(peak*ratio).toFixed(0)}</text></g>)}
          {buckets.map(([bucket, count]) => <rect key={bucket} x={45+width*bucket} y={190-count*160/peak} width={width*.92} height={count*160/peak} fill="#1479c9"><title>{bucket*10}–{(bucket+1)*10} seconds: {count} events</title></rect>)}
          {[0, .25, .5, .75, 1].map(ratio => <text key={ratio} x={45+650*ratio} y="209" textAnchor="middle">{Math.round((last+1)*10*ratio)}</text>)}
          <text x="370" y="232" textAnchor="middle">Elapsed trace time (s)</text>
        </svg> : <p>No timed events match these filters.</p>}
      </article>
      <article><h3>Events by class</h3>
        {categories.length ? <table><thead><tr><th>Event class</th><th>Count</th></tr></thead><tbody>{categories.map(([id, count]) =>
          <tr key={id}><td><button type="button" title={id} onClick={() => setEventClass(id)}>{id}</button><div className="trace-bar" style={{ width: `${100*count/categories[0][1]}%` }} /></td><td>{count.toLocaleString()}</td></tr>)}</tbody></table> : <p>No events match these filters.</p>}
      </article>
    </div>
    <p className="trace-note">Event classes are pseudonymous. These counts come from the released traces and have no verified mapping to station activity, production cycles, or physical telemetry.</p>
  </section>;
}
