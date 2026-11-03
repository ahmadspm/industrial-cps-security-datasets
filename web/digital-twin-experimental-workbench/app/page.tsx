"use client";

import { useEffect, useMemo, useState } from "react";
import PhotographicTwin from "./components/PhotographicTwin";
import CyberPhysicalNetwork from "./components/CyberPhysicalNetwork";
import FactoryEmulator from "./components/FactoryEmulator";
import StationDiagnostics from "./components/StationDiagnostics";
import StationIODashboard from "./components/StationIODashboard";
import OperationsWorkspace from "./components/OperationsWorkspace";
import {
  BehaviourGraph,
  FSMCatalogue,
  StateMachineGraph,
} from "./components/BehaviourGraphs";
import SimulationScience from "./components/SimulationScience";
import PhysicalTwinSecurity from "./components/PhysicalTwinSecurity";
import AgenticSecurityAssessment from "./components/AgenticSecurityAssessment";

type Page =
  | "overview"
  | "physical"
  | "operations"
  | "engineering"
  | "networkfidelity"
  | "emulator"
  | "simulation"
  | "security"
  | "agentic"
  | "evidence";
type Station = {
  id: string;
  name: string;
  role: string;
  state: string;
  active: boolean;
  temp: number;
  cycle: number;
};
const NAV: { id: Page; label: string; icon: string }[] = [
  { id: "overview", label: "Overview", icon: "⌂" },
  { id: "physical", label: "3D Physical Twin", icon: "⬡" },
  { id: "operations", label: "Operations", icon: "▦" },
  { id: "engineering", label: "Engineering", icon: "⌘" },
  { id: "networkfidelity", label: "Network Fidelity", icon: "⌁" },
  { id: "emulator", label: "Factory Emulator", icon: "▷" },
  { id: "simulation", label: "Simulation", icon: "▶" },
  { id: "security", label: "Security", icon: "◇" },
  { id: "agentic", label: "DT–Agentic AI", icon: "AI" },
  { id: "evidence", label: "Evidence", icon: "≡" },
];
const BASE: Station[] = [
  {
    id: "DSI",
    name: "Delivery Station In",
    role: "Input & NFC",
    state: "READY",
    active: false,
    temp: 23.1,
    cycle: 8.4,
  },
  {
    id: "VGR",
    name: "Vacuum Gripper Robot",
    role: "Shared transport",
    state: "MOVING",
    active: true,
    temp: 26.4,
    cycle: 12.7,
  },
  {
    id: "HBW",
    name: "High-Bay Warehouse",
    role: "Storage",
    state: "STORE_WP",
    active: true,
    temp: 24.8,
    cycle: 16.2,
  },
  {
    id: "MPO",
    name: "Multi-Processing Station",
    role: "Processing",
    state: "IDLE",
    active: false,
    temp: 28.2,
    cycle: 31.6,
  },
  {
    id: "SLD",
    name: "Sorting Line",
    role: "Sorting",
    state: "IDLE",
    active: false,
    temp: 24.1,
    cycle: 11.3,
  },
  {
    id: "DSO",
    name: "Delivery Station Out",
    role: "Output",
    state: "IDLE",
    active: false,
    temp: 23.6,
    cycle: 7.9,
  },
];
const EVENTS = [
  ["12:42:08.914", "MQTT", "VGR", "Target updated → HBW", "Observed"],
  ["12:42:08.602", "PLC", "HBW", "STORE_WP transition accepted", "Observed"],
  ["12:42:07.931", "TWIN", "VGR", "MOVE_VGR2HBW inferred", "Inferred"],
  ["12:42:06.120", "NFC", "DSI", "Workpiece WP-024 identified", "Observed"],
  [
    "12:42:05.488",
    "NET",
    "MQTT",
    "Latency 18 ms · reliability 99.7%",
    "Observed",
  ],
  [
    "12:42:03.201",
    "SIM",
    "MPO",
    "Nominal process duration loaded",
    "Simulated",
  ],
];
const FSM = [
  "IDLE",
  "FETCH_WP",
  "MOVE_VGR2MPO",
  "START_PRODUCE",
  "MOVE_VGR2SLD",
  "DELIVER_DSO",
];

function Badge({
  children,
  tone = "green",
}: {
  children: React.ReactNode;
  tone?: string;
}) {
  return <span className={`badge ${tone}`}>{children}</span>;
}
function Metric({
  label,
  value,
  note,
  tone = "",
}: {
  label: string;
  value: string;
  note?: string;
  tone?: string;
}) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong className={tone}>{value}</strong>
      {note && <small>{note}</small>}
    </div>
  );
}
function Tabs({
  items,
  value,
  set,
}: {
  items: string[];
  value: string;
  set: (v: string) => void;
}) {
  return (
    <div className="tabs">
      {items.map((x) => (
        <button
          key={x}
          className={value === x ? "active" : ""}
          onClick={() => set(x)}
        >
          {x}
        </button>
      ))}
    </div>
  );
}
function Flow({ stations }: { stations: Station[] }) {
  return (
    <div className="flow">
      {stations.map((s, i) => (
        <div className="flow-wrap" key={s.id}>
          <div className={`flow-node ${s.active ? "active" : ""}`}>
            <b>{s.id}</b>
            <span>{s.role}</span>
          </div>
          {i < stations.length - 1 && (
            <i className={s.active ? "active" : ""}>→</i>
          )}
        </div>
      ))}
    </div>
  );
}
function StationCard({
  s,
  selected,
  onClick,
}: {
  s: Station;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      className={`station ${s.active ? "active" : ""} ${selected ? "selected" : ""}`}
      onClick={onClick}
    >
      <div>
        <b>{s.id}</b>
        <i />
      </div>
      <strong>{s.name}</strong>
      <small>{s.role}</small>
      <code>{s.state}</code>
      <footer>
        <span>{s.temp.toFixed(1)}°C</span>
        <span>{s.cycle}s avg</span>
      </footer>
    </button>
  );
}
function Panel({
  title,
  sub,
  action,
  children,
  className = "",
}: {
  title: string;
  sub?: string;
  action?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <article className={`panel ${className}`}>
      <header>
        <div>
          <h3>{title}</h3>
          {sub && <p>{sub}</p>}
        </div>
        {action}
      </header>
      {children}
    </article>
  );
}
function Events({ count = 4 }: { count?: number }) {
  return (
    <div className="events">
      {EVENTS.slice(0, count).map((e, i) => (
        <div key={i}>
          <i>{e[1][0]}</i>
          <p>
            <b>{e[2]}</b>
            {e[3]}
            <small>
              {e[0]} · {e[4]}
            </small>
          </p>
        </div>
      ))}
    </div>
  );
}

export default function Home() {
  const [page, setPage] = useState<Page>("overview"),
    [running, setRunning] = useState(true),
    [mode, setMode] = useState("OT Log Replay");
  const [tick, setTick] = useState(0),
    [selected, setSelected] = useState("VGR"),
    [opTab, setOpTab] = useState("Factory");
  const [engTab, setEngTab] = useState("FSM"),
    [secTab, setSecTab] = useState("Impact"),
    [sim, setSim] = useState(false);
  const [speed, setSpeed] = useState(1),
    [workpieces, setWorkpieces] = useState(6),
    [attack, setAttack] = useState(false),
    [toast, setToast] = useState("");
  const [wpColor, setWpColor] = useState("#1976d2"),
    [autoRotate, setAutoRotate] = useState(false);
  useEffect(() => {
    if (!running && !sim) return;
    const t = setInterval(() => setTick((x) => x + 1), 2400 / speed);
    return () => clearInterval(t);
  }, [running, sim, speed]);
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(""), 2300);
    return () => clearTimeout(t);
  }, [toast]);
  const stations = useMemo(
    () =>
      BASE.map((s, i) => {
        const a = tick % 6;
        return {
          ...s,
          active: running && (i === a || (i === 1 && a > 0 && a < 5)),
          state:
            running && i === a
              ? [
                  "DETECT_WP",
                  "TRANSPORT",
                  "STORE_WP",
                  "PROCESSING",
                  "SORTING",
                  "OUTPUTTING",
                ][i]
              : i === 1 && a > 0 && a < 5
                ? "TRANSPORT"
                : "IDLE",
          temp: s.temp + Math.sin((tick + i) / 3) * 0.6,
        };
      }),
    [tick, running],
  );
  const station = stations.find((s) => s.id === selected) || stations[1],
    progress = Math.round(((tick % 24) / 23) * 100);
  const notify = (s: string) => setToast(s);

  return (
    <div className="shell">
      <aside>
        <div className="brand">
          <i>DT</i>
          <div>
            <b>DT Workbench</b>
            <span>Cyber–physical experiments</span>
          </div>
        </div>
        <nav>
          {NAV.map((n) => (
            <button
              className={page === n.id ? "active" : ""}
              onClick={() => setPage(n.id)}
              key={n.id}
            >
              <i>{n.icon}</i>
              {n.label}
            </button>
          ))}
        </nav>
        <div className="source">
          <span>DATA SOURCE</span>
          <b>{mode}</b>
          <small>
            <i className={running ? "on" : ""} />
            {running ? "Synchronized" : "Disconnected"}
          </small>
        </div>
      </aside>
      <main>
        <div className="top">
          <div>
            <span>DIGITAL TWIN EXPERIMENTAL WORKBENCH</span>
            <h1>{NAV.find((n) => n.id === page)?.label}</h1>
          </div>
          <div className="top-actions">
            <div className="time">
              <span>SIMULATION TIME</span>
              <b>00:42:{String(tick % 60).padStart(2, "0")}</b>
            </div>
            <Badge tone={running ? "green" : "gray"}>
              {running ? "● SYNCHRONIZED" : "○ OFFLINE"}
            </Badge>
            <button onClick={() => notify("No unresolved critical alerts")}>
              ♢<i>{attack ? 1 : 0}</i>
            </button>
          </div>
        </div>

        {page === "overview" && (
          <section className="content">
            <div className="hero">
              <div>
                <p>
                  <Badge tone={attack ? "red" : "green"}>
                    {attack ? "SECURITY EVENT" : "FACTORY NOMINAL"}
                  </Badge>
                  <span>Run ID EXP-2026-0821-014</span>
                </p>
                <h2>Smart Manufacturing System</h2>
                <small>
                  Operational state reconstructed from MQTT, PLC and simulated
                  process observations.
                </small>
              </div>
              <figure className="overview-factory-figure">
                <img
                  src="assets/fischertechnik-560840-reference.jpg"
                  alt="Fischertechnik Training Factory Industry 4.0 24V"
                />
                <figcaption>Physical testbed · Art. No. 560840</figcaption>
              </figure>
              <div className="hero-controls">
                <label>
                  Runtime source
                  <select
                    value={mode}
                    onChange={(e) => setMode(e.target.value)}
                  >
                    <option>OT Log Replay</option>
                    <option>Physical MQTT</option>
                    <option>Agent Simulation</option>
                  </select>
                </label>
                <button
                  className={running ? "danger" : "primary"}
                  onClick={() => setRunning(!running)}
                >
                  {running ? "■ Stop Twin" : "▶ Start Twin"}
                </button>
              </div>
            </div>
            <div className="metrics">
              <Metric
                label="Production status"
                value={running ? "In progress" : "Stopped"}
                note={`WP-024 · ${progress}% complete`}
                tone="teal"
              />
              <Metric
                label="Completed today"
                value={String(38 + Math.floor(tick / 20))}
                note="+6 compared with prior run"
              />
              <Metric
                label="Mean cycle time"
                value="84.6 s"
                note="3.2% within nominal"
              />
              <Metric
                label="Communication"
                value="99.7%"
                note="18 ms MQTT latency"
                tone="teal"
              />
            </div>
            <Panel
              title="Factory process"
              sub="Active workpiece and station progression"
              action={
                <div className="legend">
                  <span>
                    <i className="green" />
                    Active
                  </span>
                  <span>
                    <i />
                    Idle
                  </span>
                </div>
              }
            >
              <Flow stations={stations} />
              <div className="progress">
                <span>WP-024 · BLUE · Raw material</span>
                <i>
                  <b style={{ width: `${progress}%` }} />
                </i>
                <strong>{progress}%</strong>
              </div>
            </Panel>
            <div className="columns">
              <Panel
                title="Operational signals"
                sub="Last 30 synchronization cycles"
                action={<Badge>LIVE</Badge>}
              >
                <div className="signals">
                  {[
                    ["MQTT latency", "18 ms", 56],
                    ["Cycle time", "84.6 s", 78],
                    ["State fidelity", "99.2%", 94],
                  ].map((x, i) => (
                    <div key={x[0]}>
                      <span>{x[0]}</span>
                      <i>
                        <b style={{ width: `${x[2]}%` }} />
                      </i>
                      <strong>{x[1]}</strong>
                    </div>
                  ))}
                </div>
              </Panel>
              <Panel
                title="Recent state evidence"
                sub="Observed and inferred updates"
                action={
                  <button className="link" onClick={() => setPage("evidence")}>
                    View all →
                  </button>
                }
              >
                <Events />
              </Panel>
            </div>
          </section>
        )}

        {page === "physical" && (
          <section className="content physical-page">
            <div className="physical-hero">
              <div>
                <Badge>FISCHERTECHNIK 560840 · 24V</Badge>
                <h2>Training Factory Industry 4.0 Physical Twin</h2>
                <p>
                  Interactive reconstruction of the purchased 24V complete set
                  with Siemens SIMATIC S7-1500, PLC connection board, TXT 4.0,
                  IoT gateway and NFC-tracked production flow.
                </p>
              </div>
              <div className="physical-controls">
                <button
                  className={running ? "danger" : "primary"}
                  onClick={() => setRunning(!running)}
                >
                  {running ? "Ⅱ Pause" : "▶ Run"}
                </button>
                <button className="secondary" onClick={() => setTick(0)}>
                  ↺ Reset
                </button>
                <label>
                  Speed
                  <select
                    value={speed}
                    onChange={(e) => setSpeed(Number(e.target.value))}
                  >
                    <option value={0.5}>0.5×</option>
                    <option value={1}>1×</option>
                    <option value={2}>2×</option>
                    <option value={4}>4×</option>
                  </select>
                </label>
                <label>
                  Workpiece
                  <select
                    value={wpColor}
                    onChange={(e) => setWpColor(e.target.value)}
                  >
                    <option value="#1976d2">Blue</option>
                    <option value="#d7372f">Red</option>
                    <option value="#f2f3f3">White</option>
                  </select>
                </label>
                <button
                  className={`secondary ${autoRotate ? "pressed" : ""}`}
                  onClick={() => setAutoRotate(!autoRotate)}
                >
                  ◎ Auto track
                </button>
              </div>
            </div>
            <div className="physical-layout">
              <Panel
                title="Photographic factory twin"
                sub="Real station imagery arranged as the 560840 production cell"
                action={
                  <div className="legend">
                    <span>
                      <i className="green" />
                      Active
                    </span>
                    <span>
                      <i />
                      Idle
                    </span>
                  </div>
                }
                className="scene-panel"
              >
                <PhotographicTwin
                  stations={stations}
                  tick={tick}
                  running={running}
                  speed={speed}
                  color={wpColor}
                  tracking={autoRotate}
                  selected={selected}
                  onSelect={setSelected}
                />
              </Panel>
              <aside className="physical-rail">
                <Panel
                  title="Physical testbed reference"
                  sub="Official Fischertechnik product visual · Art. No. 560840"
                >
                  <a
                    className="factory-reference"
                    href="https://www.fischertechnik.de/en/products/industry-and-universities/training-models/560840-training-factory-industry-4-0-24v-complete-set-with-plc-s7-1500"
                    target="_blank"
                    rel="noreferrer"
                  >
                    <img
                      src="assets/fischertechnik-560840-reference.jpg"
                      alt="Fischertechnik Training Factory Industry 4.0 24V complete set with Siemens S7-1500"
                    />
                    <span>View official product specification ↗</span>
                  </a>
                </Panel>
                <Panel title="Production token" sub="NFC-tracked workpiece">
                  <div className="token-card">
                    <i style={{ background: wpColor }} />
                    <div>
                      <b>WP-024</b>
                      <span>
                        {
                          [
                            "DPS intake + NFC",
                            "VGR transport",
                            "HBW storage",
                            "MPO machining",
                            "SLD sorting",
                            "DPS pickup + quality",
                          ][tick % 6]
                        }
                      </span>
                    </div>
                    <strong>{progress}%</strong>
                  </div>
                  <div className="route-list">
                    {stations.map((s, i) => {
                      const physical =
                        s.id === "DSI"
                          ? ["DPS", "Delivery & Pickup Station"]
                          : s.id === "DSO"
                            ? ["SSC", "Sensor Station & Camera"]
                            : [s.id, s.name];
                      return (
                        <button
                          key={s.id}
                          className={s.active ? "active" : ""}
                          onClick={() => setSelected(s.id)}
                        >
                          <i>{i + 1}</i>
                          <p>
                            <b>{physical[0]}</b>
                            <span>{physical[1]}</span>
                          </p>
                          <Badge tone={s.active ? "green" : "gray"}>
                            {s.active ? s.state : "IDLE"}
                          </Badge>
                        </button>
                      );
                    })}
                  </div>
                </Panel>
                <Panel
                  title="Motion telemetry"
                  action={<Badge>60 FPS TARGET</Badge>}
                >
                  <div className="property-list">
                    {[
                      [
                        "VGR axis X",
                        `${(Math.sin(tick * 0.8) * 140).toFixed(0)} mm`,
                      ],
                      [
                        "HBW lift",
                        `${(650 + Math.sin(tick * 2) * 450).toFixed(0)} mm`,
                      ],
                      ["MPO turntable", `${(tick * 18) % 360}°`],
                      ["Conveyor", "0.18 m/s"],
                      ["Twin lag", "18 ms"],
                    ].map((x) => (
                      <div key={x[0]}>
                        <span>{x[0]}</span>
                        <b>{x[1]}</b>
                      </div>
                    ))}
                  </div>
                </Panel>
              </aside>
            </div>
            <StationIODashboard
              tick={tick}
              running={running}
              selected={selected}
              onSelect={setSelected}
            />
            <StationDiagnostics stationId={selected} tick={tick} />
            <div className="model-note">
              <b>Model scope</b>
              <span>
                Geometry and layout are aligned to the Fischertechnik 560840
                product visual. DSI and DSO telemetry are projected onto the
                testbed&apos;s combined delivery/pickup station (DPS). This is
                not manufacturer CAD or a physics-certified engineering model.
              </span>
            </div>
          </section>
        )}

        {page === "networkfidelity" && (
          <section className="content">
            <CyberPhysicalNetwork />
          </section>
        )}

        {page === "emulator" && (
          <section className="content">
            <FactoryEmulator />
          </section>
        )}

        {page === "operations" && (
          <section className="content">
            <Tabs
              items={["Factory", "Inventory", "Sensors", "Process"]}
              value={opTab}
              set={setOpTab}
            />
            <OperationsWorkspace tab={opTab} stations={stations} tick={tick} />
            {false && opTab === "Factory" && (
              <>
                <Panel
                  title="Physical factory representation"
                  sub="Select a station for detailed operational state"
                  action={<Badge>{mode.toUpperCase()}</Badge>}
                >
                  <div className="station-grid">
                    {stations.map((s) => (
                      <StationCard
                        key={s.id}
                        s={s}
                        selected={selected === s.id}
                        onClick={() => setSelected(s.id)}
                      />
                    ))}
                  </div>
                </Panel>
                <div className="columns wide">
                  <Panel
                    title={`${station.id} · ${station.name}`}
                    sub="Operational state and provenance"
                    action={
                      <Badge tone={station.active ? "green" : "gray"}>
                        {station.active ? "ACTIVE" : "IDLE"}
                      </Badge>
                    }
                  >
                    <div className="metrics mini">
                      <Metric label="Current state" value={station.state} />
                      <Metric
                        label="Duration"
                        value={`${4 + (tick % 9)}.2 s`}
                      />
                      <Metric
                        label="Temperature"
                        value={`${station.temp.toFixed(1)}°C`}
                      />
                      <Metric label="Controller" value="TXT 4.0" />
                    </div>
                    <div className="provenance">
                      <Badge>OBSERVED</Badge>
                      <b>MQTT · f/i/state/{station.id.toLowerCase()}</b>
                      <small>
                        Updated 0.{(tick % 9) + 1}s ago · confidence 1.00
                      </small>
                    </div>
                  </Panel>
                  <Panel title="Active I/O">
                    <div className="properties">
                      {[
                        "Motor M1",
                        "Position sensor I2",
                        "Workpiece sensor I4",
                        "Safety interlock",
                      ].map((x, i) => (
                        <div key={x}>
                          <span>{x}</span>
                          <i className={(i + tick) % 3 === 0 ? "on" : ""} />
                          <b>{(i + tick) % 3 === 0 ? "HIGH" : "LOW"}</b>
                        </div>
                      ))}
                    </div>
                  </Panel>
                </div>
              </>
            )}
            {false && opTab === "Inventory" && (
              <div className="columns">
                <Panel
                  title="HBW warehouse"
                  sub="Nine-slot storage matrix"
                  action={<Badge tone="blue">6 / 9 OCCUPIED</Badge>}
                >
                  <div className="warehouse">
                    {["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"].map(
                      (x, i) => (
                        <div className={i % 3 === 2 ? "empty" : ""} key={x}>
                          <b>{x}</b>
                          {i % 3 !== 2 ? (
                            <>
                              <i className={["blue", "white", "red"][i % 3]} />
                              <span>WP-{18 + i}</span>
                            </>
                          ) : (
                            <span>Available</span>
                          )}
                        </div>
                      ),
                    )}
                  </div>
                </Panel>
                <Panel title="Workpiece queue">
                  <div className="queue">
                    {["WP-024", "WP-023", "WP-022", "WP-021"].map((x, i) => (
                      <div key={x}>
                        <i className={["blue", "white", "red"][i % 3]} />
                        <p>
                          <b>{x}</b>
                          <span>
                            {
                              [
                                "Transport to HBW",
                                "Stored A2",
                                "Processing",
                                "Completed",
                              ][i]
                            }
                          </span>
                        </p>
                        <Badge tone={i === 0 ? "green" : "gray"}>
                          {i === 0 ? "ACTIVE" : `#${i}`}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </Panel>
              </div>
            )}
            {false && opTab === "Sensors" && (
              <>
                <div className="metrics">
                  <Metric
                    label="Temperature"
                    value="23.8°C"
                    note="Normal · BME680"
                  />
                  <Metric label="Humidity" value="44.2%" note="Normal range" />
                  <Metric
                    label="Air quality"
                    value="91 IAQ"
                    note="Good"
                    tone="teal"
                  />
                  <Metric label="Brightness" value="68%" note="LDR · stable" />
                </div>
                <div className="columns">
                  <Panel title="Environmental history">
                    <div className="chart">
                      <i />
                      <b style={{ height: "61%" }} />
                      <b style={{ height: "54%" }} />
                      <b style={{ height: "68%" }} />
                      <b style={{ height: "47%" }} />
                      <b style={{ height: "72%" }} />
                      <b style={{ height: "58%" }} />
                      <b style={{ height: "64%" }} />
                    </div>
                  </Panel>
                  <Panel title="Camera & PTU">
                    <div className="camera">
                      <span>LIVE CAMERA</span>
                      <b>Pan 14° · Tilt −6°</b>
                    </div>
                  </Panel>
                </div>
              </>
            )}
            {false && opTab === "Process" && (
              <Panel
                title="Business process"
                sub="Order-to-output workflow"
                action={<Badge>WP-024</Badge>}
              >
                <div className="process">
                  {[
                    "Order received",
                    "Input inspection",
                    "Warehouse storage",
                    "Processing",
                    "Quality sorting",
                    "Output delivery",
                  ].map((x, i) => (
                    <div
                      className={
                        i < tick % 6 ? "done" : i === tick % 6 ? "active" : ""
                      }
                      key={x}
                    >
                      <i>{i < tick % 6 ? "✓" : i + 1}</i>
                      <b>{x}</b>
                      <span>
                        {i < tick % 6
                          ? "Completed"
                          : i === tick % 6
                            ? "In progress"
                            : "Waiting"}
                      </span>
                    </div>
                  ))}
                </div>
              </Panel>
            )}
          </section>
        )}

        {page === "engineering" && (
          <section className="content">
            <Tabs
              items={["FSM", "Network", "Behaviour", "PLC & I/O"]}
              value={engTab}
              set={setEngTab}
            />
            {engTab === "FSM" && (
              <>
                <div className="columns wide">
                  <Panel
                    title="Station finite-state machine"
                    sub="Observed transition path"
                    action={
                      <select
                        value={selected}
                        onChange={(e) => setSelected(e.target.value)}
                      >
                        {stations.map((s) => (
                          <option key={s.id}>{s.id}</option>
                        ))}
                      </select>
                    }
                  >
                    <StateMachineGraph station={selected} tick={tick} />
                    <div className="fsm-status">
                      <Badge>VALID TRANSITION</Badge>
                      <span>
                        δ({FSM[tick % 6]}, event) → {FSM[(tick + 1) % 6]}
                      </span>
                    </div>
                  </Panel>
                  <Panel title="Transition properties">
                    <div className="property-list">
                      {[
                        ["Source", "PLC/MQTT"],
                        ["Confidence", "1.00"],
                        ["Validity", "Accepted"],
                        ["Current duration", `${3 + (tick % 10)}.6 s`],
                        ["Nominal duration", "12.0 s"],
                      ].map((x) => (
                        <div key={x[0]}>
                          <span>{x[0]}</span>
                          <b>{x[1]}</b>
                        </div>
                      ))}
                    </div>
                  </Panel>
                </div>
                <FSMCatalogue tick={tick} onSelect={setSelected} />
              </>
            )}
            {engTab === "Network" && (
              <Panel
                title="Industrial communication topology"
                sub="Live paths across Purdue levels L0–L4"
                action={<Badge>99.7% RELIABLE</Badge>}
              >
                <div className="network">
                  {[
                    ["L4 Enterprise", "ERPNext", "Kasm", "Analytics"],
                    ["L3 DMZ", "Firewall", "Historian", "Jump host"],
                    ["L2 Supervisory", "Digital Twin", "MQTT", "OPC UA"],
                    ["L1 Control", "PLC", "TXT VGR", "IoT gateway"],
                    ["L0 Process", "DSI", "VGR", "HBW", "MPO", "SLD", "DSO"],
                  ].map((r, i) => (
                    <div key={r[0]}>
                      <label>{r[0]}</label>
                      {r.slice(1).map((x) => (
                        <span key={x}>{x}</span>
                      ))}
                      {i < 4 && <i />}
                    </div>
                  ))}
                </div>
                <div className="metrics mini">
                  <Metric label="Messages" value={String(18420 + tick * 3)} />
                  <Metric label="Mean latency" value="18 ms" />
                  <Metric label="Jitter" value="3.2 ms" />
                  <Metric label="Reliability" value="99.7%" />
                </div>
              </Panel>
            )}
            {engTab === "Behaviour" && (
              <>
                <div className="behaviour-head">
                  <div>
                    <Badge>H = (F, G, C, T, R)</Badge>
                    <h2>Behavioural Model Workspace</h2>
                    <p>
                      Live, linked views of state, process, decisions, timing
                      and constrained resources for WP-024.
                    </p>
                  </div>
                  <div className="behaviour-health">
                    <span>MODEL HEALTH</span>
                    <b>97.8%</b>
                    <small>Validated against replay evidence</small>
                  </div>
                </div>
                <div className="metrics">
                  <Metric
                    label="Transition accuracy"
                    value="99.2%"
                    note="512 valid · 4 invalid"
                    tone="teal"
                  />
                  <Metric
                    label="Timing fidelity"
                    value="96.8%"
                    note="Mean error 2.7 s"
                  />
                  <Metric
                    label="Resource utilization"
                    value="72.4%"
                    note="VGR reserved by WP-024"
                  />
                  <Metric
                    label="Process completion"
                    value="98.1%"
                    note="37 of 38 workpieces"
                  />
                </div>
                <div className="behaviour-grid">
                  <Panel
                    title="F · Station state behaviour"
                    sub="Executable finite-state model"
                    action={<Badge>OBSERVED</Badge>}
                    className="behaviour-f"
                  >
                    <BehaviourGraph kind="F" tick={tick} />
                    <div className="live-fsm">
                      {[
                        "IDLE",
                        "ACQUIRE",
                        "TRANSPORT",
                        "EXECUTE",
                        "VERIFY",
                      ].map((x, i) => (
                        <div
                          className={
                            i === tick % 5
                              ? "active"
                              : i < tick % 5
                                ? "done"
                                : ""
                          }
                          key={x}
                        >
                          <i>{i < tick % 5 ? "✓" : i + 1}</i>
                          <b>{x}</b>
                          {i < 4 && <em>→</em>}
                        </div>
                      ))}
                    </div>
                    <div className="transition-evidence">
                      <code>δ({FSM[tick % 6]}, mqtt.ack)</code>
                      <strong>→ {FSM[(tick + 1) % 6]}</strong>
                      <Badge>VALID</Badge>
                    </div>
                  </Panel>
                  <Panel
                    title="G · Production workflow"
                    sub="Tokenized DAG with bounded rework"
                    action={<Badge tone="blue">WP-024</Badge>}
                    className="behaviour-g"
                  >
                    <BehaviourGraph kind="G" tick={tick} />
                    <div className="dag">
                      <div className="dag-main">
                        {["INPUT", "STORE", "PROCESS", "SORT", "OUTPUT"].map(
                          (x, i) => (
                            <div
                              className={
                                i === tick % 5
                                  ? "active"
                                  : i < tick % 5
                                    ? "done"
                                    : ""
                              }
                              key={x}
                            >
                              <i>{i + 1}</i>
                              <b>{x}</b>
                              {i < 4 && <em>→</em>}
                            </div>
                          ),
                        )}
                      </div>
                      <div className="rework">
                        <span>Quality fail</span>
                        <b>REWORK</b>
                        <i>↖ bounded ×2</i>
                      </div>
                    </div>
                  </Panel>
                  <Panel
                    title="C · Control decision"
                    sub="Guard evaluation and next command"
                    action={<Badge>PLC SCAN 8.6 ms</Badge>}
                  >
                    <div className="decision">
                      <div className="decision-inputs">
                        {[
                          ["Workpiece detected", true],
                          ["VGR available", tick % 4 !== 0],
                          ["Destination ready", true],
                          ["Safety interlock", true],
                        ].map((x) => (
                          <div key={String(x[0])}>
                            <i className={x[1] ? "on" : ""} />
                            <span>{x[0]}</span>
                            <b>{x[1] ? "TRUE" : "FALSE"}</b>
                          </div>
                        ))}
                      </div>
                      <div className="decision-output">
                        <span>NEXT ACTION</span>
                        <b>
                          {tick % 4 === 0
                            ? "WAIT_FOR_VGR"
                            : "MOVE_TO_" + stations[(tick + 1) % 6].id}
                        </b>
                        <small>Priority 20 · owner WP-024</small>
                      </div>
                    </div>
                  </Panel>
                  <Panel
                    title="T · Temporal conformance"
                    sub="Observed versus nominal duration"
                  >
                    <div className="timing-bars">
                      {[
                        ["DSI", 8, 8.4],
                        ["VGR", 12, 12.7],
                        ["HBW", 15, 16.2],
                        ["MPO", 30, 31.6],
                        ["SLD", 12, 11.3],
                      ].map((x) => (
                        <div key={x[0]}>
                          <b>{x[0]}</b>
                          <span>
                            <i style={{ width: `${Number(x[1]) * 2.5}%` }} />
                            <em style={{ left: `${Number(x[2]) * 2.5}%` }} />
                          </span>
                          <small>
                            {x[2]}s / {x[1]}s
                          </small>
                        </div>
                      ))}
                    </div>
                    <div className="timing-key">
                      <span>
                        <i />
                        Nominal
                      </span>
                      <span>
                        <em />
                        Observed
                      </span>
                    </div>
                  </Panel>
                  <Panel
                    title="R · Resource allocation"
                    sub="Capacity, ownership and reservations"
                  >
                    <div className="resource-grid">
                      {[
                        ["VGR", 84, "WP-024", "RESERVED"],
                        ["HBW", 67, "6 / 9 slots", "ALLOCATED"],
                        ["MPO", 58, "WP-023", "BUSY"],
                        ["SLD", 41, "—", "AVAILABLE"],
                      ].map((x) => (
                        <div key={x[0]}>
                          <header>
                            <b>{x[0]}</b>
                            <Badge
                              tone={x[3] === "AVAILABLE" ? "gray" : "green"}
                            >
                              {x[3]}
                            </Badge>
                          </header>
                          <i>
                            <em style={{ width: `${x[1]}%` }} />
                          </i>
                          <footer>
                            <span>{x[2]}</span>
                            <b>{x[1]}%</b>
                          </footer>
                        </div>
                      ))}
                    </div>
                  </Panel>
                </div>
              </>
            )}
            {engTab === "PLC & I/O" && (
              <div className="columns">
                <Panel
                  title="PLC scan cycle"
                  sub="Input → logic → output"
                  action={<Badge>RUN</Badge>}
                >
                  <div className="scan">
                    {[
                      ["1", "Read inputs", "2.1 ms"],
                      ["2", "Execute logic", "4.8 ms"],
                      ["3", "Write outputs", "1.7 ms"],
                    ].map((x, i) => (
                      <div key={x[0]}>
                        <i>{x[0]}</i>
                        <b>{x[1]}</b>
                        <span>{x[2]}</span>
                        {i < 2 && <em>→</em>}
                      </div>
                    ))}
                  </div>
                  <Metric
                    label="Total scan"
                    value="8.6 ms"
                    note="Below 20 ms threshold"
                  />
                </Panel>
                <Panel title="Controller health">
                  <div className="property-list">
                    {[
                      ["Program", "ProductionSequencer v2"],
                      ["Mode", "AUTOMATIC"],
                      ["Interlocks", "6 / 6 healthy"],
                      ["Last fault", "None"],
                    ].map((x) => (
                      <div key={x[0]}>
                        <span>{x[0]}</span>
                        <b>{x[1]}</b>
                      </div>
                    ))}
                  </div>
                </Panel>
              </div>
            )}
          </section>
        )}

        {page === "simulation" && (
          <section className="content">
            <SimulationScience />
            <div className="sim-layout">
              <Panel
                title="Experiment configuration"
                sub="Run without physical equipment"
                action={
                  <Badge tone={sim ? "green" : "gray"}>
                    {sim ? "RUNNING" : "READY"}
                  </Badge>
                }
                className="config"
              >
                <label>
                  Simulation engine
                  <select>
                    <option>Distributed station agents</option>
                    <option>Behaviour generator</option>
                    <option>OT log replay</option>
                  </select>
                </label>
                <div className="form-row">
                  <label>
                    Workpieces
                    <input
                      type="number"
                      min="1"
                      max="9"
                      value={workpieces}
                      onChange={(e) => setWorkpieces(Number(e.target.value))}
                    />
                  </label>
                  <label>
                    Speed
                    <select
                      value={speed}
                      onChange={(e) => setSpeed(Number(e.target.value))}
                    >
                      <option value={0.5}>0.5×</option>
                      <option value={1}>1×</option>
                      <option value={2}>2×</option>
                      <option value={4}>4×</option>
                    </select>
                  </label>
                </div>
                <label>
                  Network profile
                  <select>
                    <option>Nominal</option>
                    <option>Delay + jitter</option>
                    <option>5% packet loss</option>
                    <option>Payload corruption</option>
                  </select>
                </label>
                <div className="sequence">
                  <span>Sequence</span>
                  {Array.from({ length: workpieces }, (_, i) => (
                    <i className={["blue", "white", "red"][i % 3]} key={i} />
                  ))}
                </div>
                <button
                  className={sim ? "danger full" : "primary full"}
                  onClick={() => {
                    setSim(!sim);
                    setRunning(!sim);
                    setMode("Agent Simulation");
                    notify(
                      sim ? "Simulation stopped" : "Experiment initialized",
                    );
                  }}
                >
                  {sim ? "■ Stop experiment" : "▶ Initialize experiment"}
                </button>
              </Panel>
              <div>
                <Panel
                  title="Simulated factory"
                  sub="Agent messages and equipment behaviour"
                  action={
                    <code>EXP-SIM-0821-{String(tick).padStart(3, "0")}</code>
                  }
                >
                  <Flow stations={stations} />
                  <div className="progress">
                    <span>Elapsed 00:{String(tick % 60).padStart(2, "0")}</span>
                    <i>
                      <b style={{ width: `${progress}%` }} />
                    </i>
                    <strong>{progress}%</strong>
                  </div>
                </Panel>
                <div className="columns">
                  <Panel title="Agent activity">
                    <Events count={5} />
                  </Panel>
                  <Panel title="Network impairment">
                    <div className="property-list">
                      {[
                        ["Forwarded", String(821 + tick)],
                        ["Delayed", "12"],
                        ["Dropped", "0"],
                        ["Corrupted", "0"],
                      ].map((x) => (
                        <div key={x[0]}>
                          <span>{x[0]}</span>
                          <b>{x[1]}</b>
                        </div>
                      ))}
                    </div>
                    <button
                      className="secondary full"
                      onClick={() => notify("Controlled MQTT delay injected")}
                    >
                      Inject controlled fault
                    </button>
                  </Panel>
                </div>
              </div>
            </div>
          </section>
        )}

        {page === "security" && <PhysicalTwinSecurity onNotify={notify} />}

        {page === "agentic" && <AgenticSecurityAssessment onNotify={notify} />}

        {false && page === "security" && (
          <section className="content">
            <Tabs
              items={[
                "Impact",
                "Knowledge graph",
                "Attack paths",
                "MITRE coverage",
              ]}
              value={secTab}
              set={setSecTab}
            />
            {secTab === "Impact" && (
              <div className="columns wide">
                <Panel
                  title="Cyber–physical impact chain"
                  sub="Controlled experiment propagation"
                  action={
                    <button
                      className={attack ? "secondary" : "danger"}
                      onClick={() => {
                        setAttack(!attack);
                        notify(
                          attack
                            ? "Scenario reset"
                            : "MQTT disruption activated",
                        );
                      }}
                    >
                      {attack ? "Reset scenario" : "Run attack scenario"}
                    </button>
                  }
                >
                  <div className="impact">
                    {[
                      ["Network", "MQTT broker"],
                      ["Control", "PLC and agents"],
                      ["Physical", "VGR / HBW"],
                      ["Twin", "State synchronization"],
                      ["Business", "Production throughput"],
                    ].map((x, i) => (
                      <div
                        className={
                          attack ? (i === 0 ? "attacked" : "affected") : ""
                        }
                        key={x[0]}
                      >
                        <i>{i + 1}</i>
                        <p>
                          <b>{x[0]}</b>
                          <span>{x[1]}</span>
                        </p>
                        <Badge
                          tone={attack ? (i === 0 ? "red" : "amber") : "gray"}
                        >
                          {attack
                            ? i === 0
                              ? "ATTACKED"
                              : "AFFECTED"
                            : "NOMINAL"}
                        </Badge>
                      </div>
                    ))}
                  </div>
                </Panel>
                <Panel title="Security state">
                  <div className="risk">
                    <span>Operational risk</span>
                    <b className={attack ? "high" : "low"}>
                      {attack ? "HIGH" : "LOW"}
                    </b>
                    <i>
                      <em style={{ width: attack ? "78%" : "18%" }} />
                    </i>
                  </div>
                  <div className="property-list">
                    {[
                      ["Target", attack ? "MQTT_BROKER" : "None"],
                      ["Technique", attack ? "T0885" : "—"],
                      ["Affected assets", attack ? "5" : "0"],
                      ["Containment", "ACTIVE"],
                    ].map((x) => (
                      <div key={x[0]}>
                        <span>{x[0]}</span>
                        <b>{x[1]}</b>
                      </div>
                    ))}
                  </div>
                </Panel>
              </div>
            )}
            {secTab === "Knowledge graph" && (
              <Panel
                title="Factory security knowledge graph"
                sub="Assets, protocols, vulnerabilities and dependencies"
                action={<Badge tone="blue">42 NODES · 67 EDGES</Badge>}
              >
                <div className="kg">
                  {[
                    [50, 48, "Digital Twin", "core"],
                    [20, 22, "ERPNext", "it"],
                    [78, 20, "MQTT", "risk"],
                    [16, 72, "PLC", "control"],
                    [82, 72, "Historian", "it"],
                    [36, 82, "VGR", "physical"],
                    [64, 84, "HBW", "physical"],
                    [48, 18, "Firewall", "control"],
                    [28, 50, "OPC UA", "risk"],
                    [72, 48, "Kasm", "it"],
                  ].map((n, i) => (
                    <button
                      key={i}
                      className={`node ${n[3]}`}
                      style={{ left: `${n[0]}%`, top: `${n[1]}%` }}
                      onClick={() => notify(`${n[2]} selected`)}
                    >
                      {n[2]}
                    </button>
                  ))}
                </div>
              </Panel>
            )}
            {secTab === "Attack paths" && (
              <Panel
                title="Attack-path explorer"
                sub="Cross-layer routes to manufacturing impact"
                action={
                  <button
                    className="primary"
                    onClick={() => notify("Five feasible paths recalculated")}
                  >
                    Recalculate
                  </button>
                }
              >
                {[
                  ["Internet", "ERPNext", "DMZ", "MQTT", "PLC", "VGR"],
                  ["Kasm", "Jump host", "Historian", "Twin", "OPC UA", "MPO"],
                  ["IoT gateway", "MQTT", "SSC Agent", "HBW"],
                ].map((p, i) => (
                  <div className="path" key={i}>
                    <span>PATH {i + 1}</span>
                    {p.map((x, j) => (
                      <div key={x}>
                        <b>{x}</b>
                        {j < p.length - 1 && <i>→</i>}
                      </div>
                    ))}
                    <Badge tone={i === 0 ? "red" : i === 1 ? "amber" : "blue"}>
                      {["CRITICAL", "HIGH", "MEDIUM"][i]}
                    </Badge>
                  </div>
                ))}
              </Panel>
            )}
            {secTab === "MITRE coverage" && (
              <Panel
                title="MITRE ATT&CK for ICS coverage"
                sub="Techniques represented in the environment"
                action={<Badge>18 TECHNIQUES</Badge>}
              >
                <div className="mitre">
                  {[
                    ["Initial Access", 4],
                    ["Execution", 3],
                    ["Persistence", 2],
                    ["Evasion", 5],
                    ["Discovery", 8],
                    ["Lateral Movement", 4],
                    ["Collection", 3],
                    ["Command & Control", 2],
                    ["Inhibit Response", 4],
                    ["Impair Process", 6],
                  ].map((x) => (
                    <div key={x[0]}>
                      <span>{x[0]}</span>
                      <b>{x[1]}</b>
                      <i>
                        <em style={{ width: `${Number(x[1]) * 10}%` }} />
                      </i>
                    </div>
                  ))}
                </div>
              </Panel>
            )}
          </section>
        )}

        {page === "evidence" && (
          <section className="content">
            <div className="metrics">
              <Metric
                label="Experiment"
                value="EXP-0821-014"
                note="Replay · deterministic"
              />
              <Metric
                label="Events captured"
                value={String(18420 + tick * 3)}
                note="MQTT + OPC UA + Twin"
              />
              <Metric
                label="Snapshots"
                value="1,248"
                note="Revision-controlled"
              />
              <Metric label="Artefacts" value="14" note="JSONL · PCAP · CSV" />
            </div>
            <Panel
              title="Experiment evidence"
              sub="Auditable observations with source and confidence"
              action={
                <div>
                  <button
                    className="secondary"
                    onClick={() => notify("Filters opened")}
                  >
                    Filter
                  </button>{" "}
                  <button
                    className="primary"
                    onClick={() => notify("Evidence export prepared")}
                  >
                    Export
                  </button>
                </div>
              }
            >
              <div className="table">
                <table>
                  <thead>
                    <tr>
                      <th>Time</th>
                      <th>Source</th>
                      <th>Entity</th>
                      <th>Observation</th>
                      <th>Kind</th>
                      <th>Confidence</th>
                      <th>Revision</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...EVENTS, ...EVENTS].map((e, i) => (
                      <tr key={i}>
                        <td>{e[0]}</td>
                        <td>
                          <code>{e[1]}</code>
                        </td>
                        <td>
                          <b>{e[2]}</b>
                        </td>
                        <td>{e[3]}</td>
                        <td>
                          <Badge
                            tone={
                              e[4] === "Observed"
                                ? "green"
                                : e[4] === "Inferred"
                                  ? "amber"
                                  : "blue"
                            }
                          >
                            {e[4]}
                          </Badge>
                        </td>
                        <td>{e[4] === "Inferred" ? "0.78" : "1.00"}</td>
                        <td>#{1248 - i}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Panel>
            <div className="columns">
              <Panel title="Generated artefacts">
                <div className="files">
                  {[
                    ["mqtt_20260821.pcap", "Network capture", "4.8 MB"],
                    ["events.jsonl", "Canonical observations", "1.2 MB"],
                    ["opcua.jsonl", "OPC UA changes", "480 KB"],
                    ["factory_snapshots.json", "Twin revisions", "2.1 MB"],
                    [
                      "experiment_manifest.json",
                      "Configuration & hashes",
                      "8 KB",
                    ],
                  ].map((x) => (
                    <div key={x[0]}>
                      <i>▤</i>
                      <p>
                        <b>{x[0]}</b>
                        <span>{x[1]}</span>
                      </p>
                      <small>{x[2]}</small>
                      <button
                        onClick={() => notify(`${x[0]} download simulated`)}
                      >
                        ↓
                      </button>
                    </div>
                  ))}
                </div>
              </Panel>
              <Panel title="Fidelity summary">
                <div className="fidelity">
                  <div>
                    <b>97.8%</b>
                    <span>Overall fidelity</span>
                  </div>
                </div>
                <div className="property-list">
                  {[
                    ["State agreement", "99.2%"],
                    ["Timing agreement", "96.8%"],
                    ["Inventory consistency", "100%"],
                    ["Communication fidelity", "95.3%"],
                  ].map((x) => (
                    <div key={x[0]}>
                      <span>{x[0]}</span>
                      <b>{x[1]}</b>
                    </div>
                  ))}
                </div>
              </Panel>
            </div>
          </section>
        )}
      </main>
      {toast && (
        <div className="toast">
          <b>✓</b>
          {toast}
        </div>
      )}
    </div>
  );
}
