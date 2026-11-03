"use client";

import {
  Background,
  Controls,
  Edge,
  MarkerType,
  Node,
  ReactFlow,
} from "@xyflow/react";

type Station = { id: string; name: string; state: string; active: boolean };
const META: Record<string, { image: string; role: string; color: string }> = {
  DSI: {
    image: "assets/station-dps-official.png",
    role: "NFC intake",
    color: "#2476c9",
  },
  VGR: {
    image: "assets/station-vgr-official.jpg",
    role: "Shared transport",
    color: "#7758c8",
  },
  HBW: {
    image: "assets/station-hbw-official.jpg",
    role: "Automated storage",
    color: "#d28b25",
  },
  MPO: {
    image: "assets/station-mpo-official.jpg",
    role: "Thermal + machining",
    color: "#d24d42",
  },
  SLD: {
    image: "assets/station-sld-official.jpg",
    role: "Colour sorting",
    color: "#168b72",
  },
  DSO: {
    image: "assets/station-dps-official.png",
    role: "Completed output",
    color: "#367d50",
  },
};
const positions: Record<string, { x: number; y: number }> = {
  DSI: { x: 0, y: 120 },
  VGR: { x: 230, y: 120 },
  HBW: { x: 460, y: 0 },
  MPO: { x: 460, y: 240 },
  SLD: { x: 720, y: 240 },
  DSO: { x: 960, y: 240 },
};
const flowEdges: [
  [string, string, string],
  ...Array<[string, string, string]>,
] = [
  ["DSI", "VGR", "pickup request"],
  ["VGR", "HBW", "store / retrieve"],
  ["HBW", "VGR", "carrier ready"],
  ["VGR", "MPO", "transfer command"],
  ["MPO", "SLD", "processed carrier"],
  ["SLD", "DSO", "sorted output"],
];

function StationNode({ data }: { data: any }) {
  return (
    <div
      className={`ops-station-node node-${data.id.toLowerCase()} ${data.active ? "active" : ""}`}
      style={{ "--node-accent": data.color } as React.CSSProperties}
    >
      <img src={data.image} alt="" />
      <div>
        <b>{data.id}</b>
        <span>{data.role}</span>
        <em>{data.active ? data.state : "READY"}</em>
      </div>
    </div>
  );
}
const nodeTypes = { station: StationNode };

function FactoryGraph({ stations }: { stations: Station[] }) {
  const nodes: Node[] = stations.map((s) => ({
    id: s.id,
    type: "station",
    position: positions[s.id],
    data: { ...s, ...META[s.id] },
  }));
  const edges: Edge[] = flowEdges.map(([source, target, label], i) => ({
    id: `${source}-${target}-${i}`,
    source,
    target,
    label,
    animated: stations.find((s) => s.id === source)?.active,
    type: "smoothstep",
    style: { stroke: META[source].color, strokeWidth: 3.5 },
    labelStyle: { fontSize: 8, fontWeight: 800, fill: "#334c44" },
    labelBgStyle: { fill: "#fff", fillOpacity: 0.94 },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: META[source].color,
      width: 18,
      height: 18,
    },
  }));
  return (
    <div className="operations-graph">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        minZoom={0.55}
        maxZoom={1.25}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable
      >
        <Background color="#dce5e1" gap={22} />
        <Controls showInteractive={false} />
      </ReactFlow>
      <div className="graph-key">
        <b>Physical station image</b>
        <span>Bold arrows show material and control-information exchange</span>
      </div>
    </div>
  );
}

const slots = [
  { id: "A1", wp: "WP-018", color: "blue", stage: "Raw" },
  { id: "A2", wp: "WP-019", color: "white", stage: "Stored" },
  { id: "A3" },
  { id: "B1", wp: "WP-021", color: "red", stage: "Rework" },
  { id: "B2", wp: "WP-024", color: "blue", stage: "Reserved" },
  { id: "B3" },
  { id: "C1", wp: "WP-022", color: "white", stage: "Processed" },
  { id: "C2", wp: "WP-023", color: "red", stage: "Stored" },
  { id: "C3" },
];
function Inventory() {
  return (
    <div className="inventory-workspace">
      <section className="rack-visual">
        <header>
          <div>
            <b>HBW digital inventory</b>
            <span>3 × 3 calibrated storage positions</span>
          </div>
          <strong>
            6 / 9 <small>occupied</small>
          </strong>
        </header>
        <div className="rack-frame">
          {slots.map((s) => (
            <article
              className={`${s.wp ? "occupied" : "empty"} ${s.id === "B2" ? "reserved" : ""}`}
              key={s.id}
            >
              <b>{s.id}</b>
              {s.wp ? (
                <>
                  <i className={s.color} />
                  <div>
                    <strong>{s.wp}</strong>
                    <span>{s.stage}</span>
                  </div>
                </>
              ) : (
                <span>AVAILABLE</span>
              )}
            </article>
          ))}
        </div>
      </section>
      <aside className="inventory-legend">
        <h3>Inventory at a glance</h3>
        {[
          ["Occupied", "6 slots", "67%"],
          ["Available", "3 slots", "33%"],
          ["Reserved", "B2 · WP-024", "Next order"],
          ["Capacity", "9 carriers", "Nominal"],
        ].map((x) => (
          <div key={x[0]}>
            <span>{x[0]}</span>
            <b>{x[1]}</b>
            <em>{x[2]}</em>
          </div>
        ))}
        <footer>
          <i className="blue" /> Blue 3 <i className="white" /> White 2{" "}
          <i className="red" /> Red 2
        </footer>
      </aside>
    </div>
  );
}

const sensorNames = ["Temperature", "Humidity", "Air quality", "Brightness"];
function SensorChart({
  name,
  index,
  tick,
}: {
  name: string;
  index: number;
  tick: number;
}) {
  const values = Array.from(
    { length: 24 },
    (_, i) => 50 + Math.sin((i + tick + index * 3) / 3) * 18 + index * 4,
  );
  const palette = [
    "#2476c9",
    "#6e55be",
    "#168b72",
    "#d18a26",
    "#d14d43",
    "#2f9bb5",
  ];
  return (
    <article className={`sensor-chart chart-${index}`}>
      <header>
        <div>
          <b>{name}</b>
          <span>SSC behavioural signal</span>
        </div>
        <strong>
          {Math.round(values[23])}
          {index === 0
            ? " °C"
            : index === 1
              ? " %RH"
              : index === 2
                ? " IAQ"
                : " %"}
        </strong>
      </header>
      <svg
        className="sensor-bars"
        viewBox="0 0 100 58"
        preserveAspectRatio="none"
        role="img"
        aria-label={`${name} bar chart for 24 samples`}
      >
        <path d="M0 12H100M0 28H100M0 44H100" />
        {values.map((v, i) => (
          <rect
            key={i}
            x={i * 4.12 + 0.35}
            y={56 - v * 0.5}
            width="3.15"
            height={v * 0.5}
            rx=".7"
            fill={palette[(i + index) % palette.length]}
            className={i === 23 ? "latest" : ""}
          />
        ))}
      </svg>
      <footer>
        <span>24 samples · oldest → newest</span>
        <b>Stable · no anomaly</b>
      </footer>
    </article>
  );
}
function Sensors({ tick }: { tick: number }) {
  const download = () => {
    const rows = [
      "timestamp,station,type,signal,value,state",
      ...Array.from({ length: 24 }, (_, i) =>
        sensorNames
          .map(
            (n, j) =>
              `${new Date(Date.now() - (23 - i) * 1000).toISOString()},SSC,sensor,${n},${Math.round(50 + Math.sin((i + tick + j * 3) / 3) * 18 + j * 4)},VALID`,
          )
          .join("\n"),
      ),
      `now,MPO,actuator,Saw motor,${tick % 4 === 0 ? 1 : 0},${tick % 4 === 0 ? "ENERGIZED" : "OFF"}`,
      `now,VGR,actuator,Vacuum valve,${tick % 3 === 0 ? 1 : 0},${tick % 3 === 0 ? "ENERGIZED" : "OFF"}`,
    ];
    const blob = new Blob([rows.join("\n")], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "smart-factory-sensor-actuator-log.csv";
    a.click();
    URL.revokeObjectURL(a.href);
  };
  return (
    <div className="sensor-workspace">
      <header>
        <div>
          <span>BEHAVIOURAL SIGNAL TWIN</span>
          <h3>Sensor and actuator history</h3>
          <p>
            Time-aligned operational signals reconstructed from station events.
          </p>
        </div>
        <button onClick={download}>⇩ Export CSV log</button>
      </header>
      <div className="sensor-chart-grid">
        {sensorNames.map((x, i) => (
          <SensorChart key={x} name={x} index={i} tick={tick} />
        ))}
      </div>
      <section className="cycle-log">
        <header>
          <b>Cycle behaviour log</b>
          <span>Observed and commanded state changes</span>
        </header>
        {[
          ["00:42:18.204", "VGR", "Vacuum pressure", "−0.42 bar", "HELD"],
          ["00:42:19.011", "HBW", "Cantilever front limit", "HIGH", "OBSERVED"],
          ["00:42:20.326", "MPO", "Oven light Q9", "1", "ENERGIZED"],
          ["00:42:21.642", "SLD", "Colour sensor", "842 raw", "BLUE"],
        ].map((x) => (
          <div key={x.join()}>
            {x.map((v, i) =>
              i === 4 ? <b key={v}>{v}</b> : <span key={v}>{v}</span>,
            )}
          </div>
        ))}
      </section>
    </div>
  );
}

function ProcessGraph({ tick }: { tick: number }) {
  const colors = ["#276fc1", "#6e55be", "#c67d22", "#cc4b41", "#168b72"];
  const bpmn = [
    { id: "start", kind: "event", label: "Order", x: 0, y: 120 },
    { id: "identify", kind: "task", label: "Identify NFC", x: 145, y: 120 },
    { id: "stock", kind: "gateway", label: "Stock?", x: 350, y: 120 },
    { id: "store", kind: "task", label: "Store in HBW", x: 500, y: 20 },
    { id: "produce", kind: "task", label: "Process in MPO", x: 500, y: 215 },
    { id: "quality", kind: "gateway", label: "Quality?", x: 720, y: 215 },
    { id: "sort", kind: "task", label: "Sort in SLD", x: 875, y: 215 },
    { id: "deliver", kind: "task", label: "Deliver at DPS", x: 1070, y: 215 },
    { id: "end", kind: "event-end", label: "Complete", x: 1275, y: 215 },
  ];
  const nodes: Node[] = bpmn.map((n, i) => ({
    id: n.id,
    position: { x: n.x, y: n.y },
    data: {
      label: (
        <div
          className={`bpmn-node ${n.kind} ${i === tick % bpmn.length ? "active" : ""}`}
        >
          {n.kind === "gateway" && <i>×</i>}
          <b>{n.label}</b>
          <span>
            {n.kind.includes("event")
              ? "EVENT"
              : n.kind === "gateway"
                ? "DECISION"
                : "TASK"}
          </span>
        </div>
      ),
    },
    style: {
      border: 0,
      background: "transparent",
      padding: 0,
      width: n.kind.includes("event") ? 88 : n.kind === "gateway" ? 95 : 165,
    },
  }));
  const links = [
    ["start", "identify", "order received"],
    ["identify", "stock", "UID valid"],
    ["stock", "store", "raw delivery"],
    ["store", "produce", "order released"],
    ["stock", "produce", "available"],
    ["produce", "quality", "cycle complete"],
    ["quality", "sort", "pass"],
    ["quality", "produce", "fail · rework"],
    ["sort", "deliver", "colour routed"],
    ["deliver", "end", "pickup confirmed"],
  ];
  const edges: Edge[] = links.map((x, i) => ({
    id: `p${i}`,
    source: x[0],
    target: x[1],
    label: x[2],
    type: "smoothstep",
    animated: i === tick % 5,
    style: {
      stroke: colors[i % colors.length],
      strokeWidth: i === 7 ? 2.5 : 4,
      strokeDasharray: i === 7 ? "7 5" : undefined,
    },
    markerEnd: {
      type: MarkerType.ArrowClosed,
      color: colors[i % colors.length],
    },
    labelStyle: { fontSize: 8, fontWeight: 800 },
  }));
  return (
    <div className="process-graph">
      <div className="bpmn-lane lane-order">ORDER &amp; CONTROL</div>
      <div className="bpmn-lane lane-physical">PHYSICAL PRODUCTION</div>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        nodesDraggable={false}
        nodesConnectable={false}
      >
        <Background color="#e1e8e5" gap={20} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}

export default function OperationsWorkspace({
  tab,
  stations,
  tick,
}: {
  tab: string;
  stations: Station[];
  tick: number;
}) {
  if (tab === "Factory") return <FactoryGraph stations={stations} />;
  if (tab === "Inventory") return <Inventory />;
  if (tab === "Sensors") return <Sensors tick={tick} />;
  return <ProcessGraph tick={tick} />;
}
