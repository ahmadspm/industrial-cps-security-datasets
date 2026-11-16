import { useEffect, useState } from "react";
import { DATA as hardware } from "./StationDiagnostics";
import "./purdue-traffic.css";

const levels = [
  ["L4", "Enterprise", "ERPNext · Kasm · Analytics"],
  ["L3.5", "Industrial DMZ", "Firewall · Jump host"],
  ["L3", "Site operations", "Historian · Operations services"],
  ["L2", "Supervisory", "Digital twin · MQTT broker · OPC UA"],
  ["L1", "Cell control", "PLC · TXT controller · IoT gateway"],
  ["L0", "Physical process", "Sensors · Motors · Pneumatic actuators"],
];
const stations = ["DSI", "VGR", "HBW", "MPO", "SLD", "DSO"];
const paths = [
  { edge: 4, direction: "up", label: "Field I/O", route: "Station → Cell controller" },
  { edge: 3, direction: "up", label: "MQTT telemetry", route: "IoT gateway → MQTT broker" },
  { edge: 2, direction: "up", label: "OPC UA data", route: "OPC UA → Historian" },
  { edge: 1, direction: "up", label: "Filtered export", route: "Historian → DMZ" },
  { edge: 0, direction: "up", label: "Reporting feed", route: "DMZ → Analytics" },
  { edge: 4, direction: "down", label: "Field output", route: "Cell controller → Station" },
];

export default function PurdueTraffic() {
  const [step, setStep] = useState(0);
  const [playing, setPlaying] = useState(true);
  const [selected, setSelected] = useState<string | null>(null);
  useEffect(() => {
    if (!playing) return;
    const timer = window.setInterval(() => setStep(previous => previous + 1), 1250);
    return () => window.clearInterval(timer);
  }, [playing]);
  const path = paths[step % paths.length];
  const activeStation = stations[Math.floor(step / paths.length) % stations.length];
  const inspected = selected ?? activeStation;
  const station = hardware[inspected === "DSO" ? "DSI" : inspected];

  return <div className="purdue-view">
    <div className="purdue-toolbar">
      <div><strong>{path.label}</strong><span>{path.route} · {activeStation} cycle</span></div>
      <div className="purdue-controls">
        <button type="button" onClick={() => setPlaying(!playing)}>{playing ? "Pause traffic" : "Play traffic"}</button>
        <button type="button" disabled={playing} onClick={() => setStep(step + 1)}>Next message</button>
      </div>
    </div>
    <div className="purdue-grid">
      <ol>{levels.map(([level, title, nodes], index) => <li key={level}>
        <div className={index === path.edge || index === path.edge + 1 ? "purdue-level active" : "purdue-level"}>
          <b>{level}</b><div><strong>{title}</strong><span>{nodes}</span></div>
        </div>
        {index < levels.length - 1 && <div className={`purdue-conduit ${path.edge === index ? path.direction : ""}`} aria-hidden="true">
          <i key={step} style={{ animationPlayState: playing ? "running" : "paused" }} />
          {path.edge === index && <span>{path.direction === "up" ? "↑" : "↓"} {path.label}</span>}
        </div>}
      </li>)}</ol>
      <section className="purdue-stations" aria-label="Lower-level factory stations">
        <h4>L1–L0 station hardware</h4>
        <div className="purdue-cards">{stations.map(id => <button key={id} type="button"
          aria-pressed={inspected === id} onClick={() => setSelected(inspected === id && selected ? null : id)}>
          <img src={hardware[id === "DSO" ? "DSI" : id].image} alt="" />
          <strong>{id}</strong>{id === activeStation && <span>Active cycle</span>}
        </button>)}</div>
        <div className="purdue-station-detail">
          <strong>{inspected} · {station.name}</strong>
          <p><b>Sensors:</b> {station.sensors.map(([name]) => name).join(", ")}</p>
          <p><b>Actuators:</b> {station.actuators.filter(name => name !== "VGR request").join(", ")}</p>
        </div>
      </section>
    </div>
    <p className="purdue-note">Illustrative message sequence. DSI and DSO share the delivery and pickup module.</p>
  </div>;
}
