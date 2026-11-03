"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Background,
  Controls,
  Handle,
  MarkerType,
  MiniMap,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

type Profile =
  | "Nominal"
  | "Delay + jitter"
  | "Packet loss"
  | "Payload corruption"
  | "MQTT flood";
const meta: Record<
  string,
  { kind: string; detail: string; ip?: string; layer: string }
> = {
  stations: {
    kind: "Physical process",
    detail: "HBW · VGR · MPO · SLD",
    layer: "L0",
  },
  io: {
    kind: "24V field I/O",
    detail: "Adapter boards · 2 cables",
    layer: "L1",
  },
  ssc: {
    kind: "9V smart sensors",
    detail: "NFC · camera · environment",
    layer: "L0",
  },
  plc: {
    kind: "Controller",
    detail: "SIMATIC S7-1500",
    ip: "192.168.0.1",
    layer: "L1",
  },
  txt: {
    kind: "Edge controller",
    detail: "TXT 4.0 · GatewayPLC",
    ip: "192.168.0.10",
    layer: "L1",
  },
  pi: {
    kind: "IoT gateway",
    detail: "Raspberry Pi 4 · Node-RED",
    ip: "192.168.0.5",
    layer: "L2",
  },
  router: {
    kind: "Cell router",
    detail: "TP-Link TL-WR902AC",
    ip: "192.168.0.252",
    layer: "L2",
  },
  nodered: {
    kind: "Local HMI",
    detail: "Node-RED dashboard",
    ip: "192.168.0.5:1880",
    layer: "L2",
  },
  cloud: {
    kind: "External service",
    detail: "fischertechnik Cloud",
    layer: "L4",
  },
  twin: {
    kind: "Research extension",
    detail: "Digital Twin runtime",
    layer: "L3",
  },
  db: {
    kind: "Evidence store",
    detail: "PostgreSQL · JSONL · PCAP",
    layer: "L3",
  },
  operator: {
    kind: "Engineering client",
    detail: "TIA Portal · UaExpert · browser",
    layer: "L3",
  },
};
const baseNodes: Node[] = [
  {
    id: "stations",
    position: { x: 0, y: 40 },
    data: { label: "Factory stations" },
    type: "networkNode",
  },
  {
    id: "ssc",
    position: { x: 0, y: 260 },
    data: { label: "SSC / DPS sensors" },
    type: "networkNode",
  },
  {
    id: "io",
    position: { x: 250, y: 40 },
    data: { label: "PLC connection board" },
    type: "networkNode",
  },
  {
    id: "plc",
    position: { x: 510, y: 40 },
    data: { label: "Siemens S7-1500" },
    type: "networkNode",
  },
  {
    id: "txt",
    position: { x: 250, y: 260 },
    data: { label: "TXT 4.0 controller" },
    type: "networkNode",
  },
  {
    id: "pi",
    position: { x: 510, y: 260 },
    data: { label: "Raspberry Pi 4" },
    type: "networkNode",
  },
  {
    id: "router",
    position: { x: 770, y: 150 },
    data: { label: "TP-Link router" },
    type: "networkNode",
  },
  {
    id: "nodered",
    position: { x: 510, y: 470 },
    data: { label: "Node-RED HMI" },
    type: "networkNode",
  },
  {
    id: "operator",
    position: { x: 770, y: 470 },
    data: { label: "Engineering client" },
    type: "networkNode",
  },
  {
    id: "cloud",
    position: { x: 1040, y: 30 },
    data: { label: "ft Cloud" },
    type: "networkNode",
  },
  {
    id: "twin",
    position: { x: 1040, y: 245 },
    data: { label: "Digital Twin" },
    type: "networkNode",
  },
  {
    id: "db",
    position: { x: 1040, y: 470 },
    data: { label: "Evidence store" },
    type: "networkNode",
  },
];
const rawEdges: Array<[string, string, string, string]> = [
  ["stations", "io", "24V DI/DO + encoder", "field"],
  ["io", "plc", "Backplane / terminals", "field"],
  ["ssc", "txt", "I²C · USB · NFC", "sensor"],
  ["txt", "pi", "MQTT 1883", "mqtt"],
  ["pi", "plc", "OPC UA 4840", "opc"],
  ["plc", "router", "Industrial Ethernet", "ethernet"],
  ["pi", "router", "Ethernet", "ethernet"],
  ["txt", "router", "WLAN / TCP-IP", "ethernet"],
  ["pi", "nodered", "HTTP 1880", "http"],
  ["operator", "plc", "S7 / OPC UA", "opc"],
  ["operator", "nodered", "HTTP dashboard", "http"],
  ["router", "cloud", "MQTT/TLS 8883", "mqtt"],
  ["router", "twin", "MQTT · HTTPS", "twin"],
  ["twin", "db", "SQL · JSONL", "data"],
  ["pi", "twin", "OPC UA projection", "twin"],
];
const colors: Record<string, string> = {
  field: "#d25943",
  sensor: "#8b5fc2",
  mqtt: "#20a88a",
  opc: "#2585c7",
  ethernet: "#586b75",
  http: "#d08a2d",
  twin: "#455ac8",
  data: "#687b73",
};

function NetworkNode({ id, data }: NodeProps) {
  const m = meta[id];
  return (
    <div className={`cp-node kind-${m.layer.toLowerCase()}`}>
      <Handle type="target" position={Position.Left} />
      <header>
        <i>{m.layer}</i>
        <span>{m.kind}</span>
        <em />
      </header>
      <b>{String(data.label)}</b>
      <small>{m.detail}</small>
      {m.ip && <code>{m.ip}</code>}
      <Handle type="source" position={Position.Right} />
    </div>
  );
}

const STACK = [
  [
    "Application",
    "Factory control · GatewayPLC · Node-RED · dashboards · Digital Twin",
    "ST/SCL · JSON · SQL · browser UI",
  ],
  [
    "Industrial information",
    "OPC UA client/server between Raspberry Pi and S7-1500",
    "OPC UA · TCP 4840",
  ],
  [
    "Telemetry & cloud",
    "TXT ↔ gateway and cloud messaging",
    "MQTT 1883 · MQTT/TLS 8883",
  ],
  [
    "Web & management",
    "Local dashboard, cloud access and time synchronization",
    "HTTP 1880 · HTTPS 443 · NTP 123",
  ],
  ["Transport", "Reliable sessions and datagrams", "TCP · UDP"],
  [
    "Network",
    "Addressing and routing across 192.168.0.0/24",
    "IPv4 · ICMP · DHCP",
  ],
  [
    "Link / physical",
    "PLC Ethernet, gateway Ethernet, TXT WLAN and wired station I/O",
    "802.3 · 802.11 · 24V DI/DO · encoder pulses",
  ],
];

export default function CyberPhysicalNetwork() {
  const [tab, setTab] = useState("Topology"),
    [running, setRunning] = useState(true),
    [profile, setProfile] = useState<Profile>("Nominal"),
    [tick, setTick] = useState(0),
    [selected, setSelected] = useState("pi");
  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => setTick((x) => x + 1), 800);
    return () => clearInterval(t);
  }, [running]);
  const affected =
    profile === "Nominal"
      ? ""
      : profile === "MQTT flood"
        ? "mqtt"
        : profile === "Payload corruption"
          ? "opc"
          : profile === "Packet loss"
            ? "ethernet"
            : "twin";
  const edges = useMemo<Edge[]>(
    () =>
      rawEdges.map((e, i) => ({
        id: `e${i}`,
        source: e[0],
        target: e[1],
        label: e[2],
        animated: running,
        type: "smoothstep",
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: affected === e[3] ? "#d63e34" : colors[e[3]],
        },
        style: {
          stroke: affected === e[3] ? "#d63e34" : colors[e[3]],
          strokeWidth: affected === e[3] ? 3 : 1.8,
          strokeDasharray:
            profile === "Packet loss" && affected === e[3] ? "7 7" : undefined,
        },
        labelStyle: { fontSize: 8, fill: "#496159", fontWeight: 700 },
        labelBgStyle: { fill: "#f7faf9", fillOpacity: 0.9 },
      })),
    [affected, profile, running],
  );
  const loss =
      profile === "Packet loss" ? 5.2 : profile === "MQTT flood" ? 1.1 : 0.08,
    latency =
      profile === "Delay + jitter" ? 184 : profile === "MQTT flood" ? 62 : 18,
    jitter = profile === "Delay + jitter" ? 47 : 3.2;
  return (
    <section className="network-page">
      <div className="network-head">
        <div>
          <span>CYBER–PHYSICAL NETWORK FIDELITY</span>
          <h2>Fischertechnik 560840 Network Laboratory</h2>
          <p>
            Interactive representation of field I/O, controllers, protocol
            translation, cell networking, cloud services and Digital Twin
            extensions.
          </p>
        </div>
        <div className="network-controls">
          <button
            className={running ? "danger" : "primary"}
            onClick={() => setRunning(!running)}
          >
            {running ? "Ⅱ Pause traffic" : "▶ Run traffic"}
          </button>
          <label>
            Network condition
            <select
              value={profile}
              onChange={(e) => setProfile(e.target.value as Profile)}
            >
              {[
                "Nominal",
                "Delay + jitter",
                "Packet loss",
                "Payload corruption",
                "MQTT flood",
              ].map((x) => (
                <option key={x}>{x}</option>
              ))}
            </select>
          </label>
        </div>
      </div>
      <div className="network-kpis">
        {[
          ["Messages", (18420 + tick * 7).toLocaleString()],
          ["Mean latency", `${latency} ms`],
          ["Jitter", `${jitter} ms`],
          ["Packet loss", `${loss}%`],
          ["Reliability", `${(100 - loss).toFixed(2)}%`],
        ].map((x) => (
          <div key={x[0]}>
            <span>{x[0]}</span>
            <b>{x[1]}</b>
          </div>
        ))}
      </div>
      <div className="network-tabs">
        {["Topology", "Protocol stack", "Traffic matrix"].map((x) => (
          <button
            key={x}
            onClick={() => setTab(x)}
            className={tab === x ? "active" : ""}
          >
            {x}
          </button>
        ))}
      </div>
      {tab === "Topology" && (
        <div className="topology-layout">
          <article className="network-canvas">
            <ReactFlow
              nodes={baseNodes}
              edges={edges}
              nodeTypes={{ networkNode: NetworkNode }}
              fitView
              minZoom={0.55}
              maxZoom={1.5}
              onNodeClick={(_, n) => setSelected(n.id)}
              colorMode="light"
            >
              <Background gap={22} size={1} color="#d5dfdb" />
              <Controls />
              <MiniMap
                pannable
                zoomable
                nodeColor={(n) => (n.id === selected ? "#11a181" : "#b9cbc5")}
              />
            </ReactFlow>
          </article>
          <aside className="network-inspector">
            <span>SELECTED ASSET</span>
            <h3>
              {String(baseNodes.find((n) => n.id === selected)?.data.label)}
            </h3>
            <b>{meta[selected].kind}</b>
            <p>{meta[selected].detail}</p>
            {meta[selected].ip && <code>{meta[selected].ip}</code>}
            <div>
              {rawEdges
                .filter((e) => e[0] === selected || e[1] === selected)
                .map((e, i) => (
                  <article key={i}>
                    <i style={{ background: colors[e[3]] }} />
                    <span>{e[2]}</span>
                    <b>{e[0] === selected ? "OUT" : "IN"}</b>
                  </article>
                ))}
            </div>
            <footer>
              <span>State</span>
              <b>
                {affected &&
                rawEdges.some(
                  (e) =>
                    (e[0] === selected || e[1] === selected) &&
                    e[3] === affected,
                )
                  ? "DEGRADED"
                  : "HEALTHY"}
              </b>
            </footer>
          </aside>
        </div>
      )}
      {tab === "Protocol stack" && (
        <div className="protocol-stack">
          {STACK.map((s, i) => (
            <article key={s[0]}>
              <i>{7 - i}</i>
              <div>
                <span>{s[0]}</span>
                <b>{s[1]}</b>
              </div>
              <code>{s[2]}</code>
            </article>
          ))}
          <footer>
            <b>Digital Twin position</b>
            <span>
              The Digital Twin is a research/runtime consumer and projection
              layer connected through configured MQTT, OPC UA and database
              interfaces. It is not a native physical controller in the
              factory’s supplied network.
            </span>
          </footer>
        </div>
      )}
      {tab === "Traffic matrix" && (
        <div className="traffic-table">
          <table>
            <thead>
              <tr>
                <th>Source</th>
                <th>Destination</th>
                <th>Protocol</th>
                <th>Direction</th>
                <th>Rate</th>
                <th>Latency</th>
                <th>State</th>
              </tr>
            </thead>
            <tbody>
              {rawEdges.map((e, i) => (
                <tr key={i}>
                  <td>
                    {baseNodes.find((n) => n.id === e[0])?.data.label as string}
                  </td>
                  <td>
                    {baseNodes.find((n) => n.id === e[1])?.data.label as string}
                  </td>
                  <td>
                    <code>{e[2]}</code>
                  </td>
                  <td>Bidirectional</td>
                  <td>
                    {e[3] === "field"
                      ? "PLC scan"
                      : e[3] === "mqtt"
                        ? `${12 + (tick % 5)} msg/s`
                        : `${2 + (i % 4)} msg/s`}
                  </td>
                  <td>
                    {affected === e[3]
                      ? `${latency + i * 3} ms`
                      : `${4 + i} ms`}
                  </td>
                  <td>
                    <span
                      className={affected === e[3] ? "degraded" : "healthy"}
                    >
                      {affected === e[3] ? "DEGRADED" : "HEALTHY"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="network-note">
        <b>Physical baseline</b>
        <span>
          S7-1500: 192.168.0.1 · Raspberry Pi: 192.168.0.5 · TXT 4.0:
          192.168.0.10 · TP-Link router/gateway: 192.168.0.252 · subnet
          255.255.255.0
        </span>
      </div>
    </section>
  );
}
