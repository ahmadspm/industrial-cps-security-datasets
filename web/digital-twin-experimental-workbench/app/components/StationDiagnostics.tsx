"use client";

const DATA: Record<
  string,
  {
    name: string;
    image: string;
    summary: string;
    sensors: Array<[string, string, string]>;
    actuators: string[];
  }
> = {
  DSI: {
    name: "DPS · Delivery & Pickup Station",
    image: "assets/station-dps-official.png",
    summary:
      "Identifies incoming workpieces and verifies pickup/output conditions.",
    sensors: [
      ["NFC/RFID reader", "WP-024 · UID 04:A2:7C", "READ"],
      ["Input light barrier", "Beam interrupted", "HIGH"],
      ["Quality colour sensor", "Blue · 842 raw", "VALID"],
      ["Pickup presence", "Workpiece present", "HIGH"],
    ],
    actuators: ["Input conveyor", "Status light", "VGR request"],
  },
  VGR: {
    name: "VGR · Vacuum Gripper Robot",
    image: "assets/station-vgr-official.jpg",
    summary:
      "Three encoder-controlled axes position the vacuum cup between factory modules.",
    sensors: [
      ["X encoder", "1,824 pulses · 270° range", "COUNTING"],
      ["Y encoder", "96 mm / 140 mm", "COUNTING"],
      ["Z encoder", "74 mm / 120 mm", "COUNTING"],
      ["X/Y/Z reference switches", "0 · 0 · 0", "CLEAR"],
      ["Vacuum confirmation", "−0.42 bar", "HELD"],
    ],
    actuators: [
      "3× encoder motors",
      "Vacuum exhauster",
      "Compressor",
      "Solenoid valve",
    ],
  },
  HBW: {
    name: "HBW · Automated High-Bay Warehouse",
    image: "assets/station-hbw-official.jpg",
    summary:
      "Identifies carriers and stores or retrieves them across nine calibrated positions.",
    sensors: [
      ["Horizontal reference I1", "Not reached", "LOW"],
      ["Inside light barrier I2", "Container detected", "HIGH"],
      ["Outside light barrier I3", "Clear", "LOW"],
      ["Vertical reference I4", "Not reached", "LOW"],
      ["X/Y encoders B1–B4", "1365 / 460 pulses", "COUNTING"],
      ["IR trail sensor A1/A2", "Barcode: BLUE", "VALID"],
      ["Cantilever limits I5/I6", "Front reached", "HIGH"],
    ],
    actuators: [
      "Belt motor Q1/Q2",
      "Horizontal axis Q3/Q4",
      "Vertical axis Q5/Q6",
      "Cantilever Q7/Q8",
    ],
  },
  MPO: {
    name: "MPO · Multi-Processing Station with Oven",
    image: "assets/station-mpo-official.jpg",
    summary:
      "Coordinates oven, vacuum transfer, turntable, saw, ejector and output conveyor.",
    sensors: [
      ["Turntable references I1/I2/I4", "Saw position", "HIGH"],
      ["Conveyor end barrier I3", "Clear", "LOW"],
      ["Vacuum position I5/I8", "At oven", "HIGH"],
      ["Feeder limits I6/I7", "Inside reached", "HIGH"],
      ["Oven light barrier I9", "Workpiece present", "HIGH"],
    ],
    actuators: [
      "Turntable Q1/Q2",
      "Conveyor Q3",
      "Saw Q4",
      "Feeder Q5/Q6",
      "Vacuum transfer Q7/Q8",
      "Oven light Q9",
      "Compressor Q10",
      "Valves Q11–Q14",
    ],
  },
  SLD: {
    name: "SLD · Sorting Line with Colour Detection",
    image: "assets/station-sld-official.jpg",
    summary:
      "Measures reflected light and directs each workpiece to its colour-specific chute.",
    sensors: [
      ["Input light barrier", "Workpiece entering", "HIGH"],
      ["Colour sensor", "Blue · 842 raw", "BLUE"],
      ["Pulse counter", "186 pulses", "COUNTING"],
      ["Chute 1 barrier", "Clear", "LOW"],
      ["Chute 2 barrier", "Blue received", "HIGH"],
      ["Chute 3 barrier", "Clear", "LOW"],
    ],
    actuators: ["Conveyor motor", "3× pneumatic ejectors", "Compressor"],
  },
  DSO: {
    name: "SSC · Sensor Station with Camera",
    image: "assets/station-ssc-official.png",
    summary:
      "Supervises the cell using environmental sensing, brightness measurement and PTU camera.",
    sensors: [
      ["Temperature", "23.8 °C", "NORMAL"],
      ["Humidity", "44.2 %RH", "NORMAL"],
      ["Air pressure", "1012 hPa", "NORMAL"],
      ["Air quality", "91 IAQ", "GOOD"],
      ["Brightness", "68 %", "STABLE"],
      ["Camera PTU", "Pan 14° · Tilt −6°", "TRACKING"],
    ],
    actuators: ["Camera pan motor", "Camera tilt motor", "Traffic light"],
  },
};

export default function StationDiagnostics({
  stationId,
  tick,
  onClose,
}: {
  stationId: string;
  tick: number;
  onClose?: () => void;
}) {
  const d = DATA[stationId] || DATA.VGR;
  return (
    <section className="diagnostics">
      <header>
        <div>
          <span>LIVE STATION INSPECTOR</span>
          <h3>{d.name}</h3>
          <p>{d.summary}</p>
        </div>
        {onClose && <button onClick={onClose}>×</button>}
      </header>
      <div className="diagnostic-body">
        <div className={`diagnostic-photo diag-${stationId.toLowerCase()}`}>
          <img src={d.image} alt={d.name} />
          <i />
          <span>LIVE IMAGE MODEL</span>
        </div>
        <div className="sensor-bank">
          {d.sensors.map((s, i) => {
            const live = (tick + i) % 4 !== 0;
            return (
              <article key={s[0]}>
                <i className={live ? "on" : ""} />
                <div>
                  <b>{s[0]}</b>
                  <span>{s[1]}</span>
                </div>
                <em>{live ? s[2] : "UPDATING"}</em>
                <small>{live ? "●" : "○"}</small>
              </article>
            );
          })}
        </div>
        <aside>
          <span>ACTIVE ACTUATORS</span>
          {d.actuators.map((a, i) => (
            <div key={a}>
              <i className={(tick + i) % 3 === 0 ? "on" : ""} />
              <b>{a}</b>
              <small>{(tick + i) % 3 === 0 ? "ENERGIZED" : "OFF"}</small>
            </div>
          ))}
        </aside>
      </div>
      <footer>
        <code>PLC.DB_{stationId}.state</code>
        <span>OPC UA update {18 + (tick % 7)} ms</span>
        <span>MQTT synchronized</span>
        <b>Confidence 1.00</b>
      </footer>
    </section>
  );
}
