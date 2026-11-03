"use client";

import { useEffect, useMemo, useState } from "react";
import StationDiagnostics from "./StationDiagnostics";
import SimulationScience from "./SimulationScience";

const STEPS = [
  [
    "DPS",
    "Receive order",
    "Input light barrier detects carrier; NFC reader identifies WP-024",
    5,
    ["Input barrier HIGH", "NFC UID read", "Order released"],
  ],
  [
    "VGR",
    "Reference axes",
    "X, Y and Z axes return to reference switches",
    7,
    ["X ref HIGH", "Y ref HIGH", "Z ref HIGH"],
  ],
  [
    "VGR",
    "Pick from DPS",
    "Robot positions, lowers vacuum cup and confirms grip",
    10,
    ["Encoders counting", "Vacuum −0.42 bar", "Grip confirmed"],
  ],
  [
    "HBW",
    "Identify carrier",
    "Conveyor moves carrier past IR trail sensor and decodes colour",
    7,
    ["I2 barrier HIGH", "A1/A2 barcode", "BLUE identified"],
  ],
  [
    "HBW",
    "Store workpiece",
    "Rack feeder moves to calibrated slot B2 and extends cantilever",
    16,
    ["X 1365 pulses", "Y 460 pulses", "I5 front limit"],
  ],
  [
    "HBW",
    "Retrieve for order",
    "Warehouse retrieves WP-024 and returns it to transfer belt",
    15,
    ["B2 allocated", "I6 rear limit", "I3 outside barrier"],
  ],
  [
    "VGR",
    "Transport to MPO",
    "Robot collects carrier and travels to oven feeder position",
    11,
    ["Vacuum held", "X/Y/Z tracking", "MPO ready"],
  ],
  [
    "MPO",
    "Load oven",
    "I9 detects workpiece; door opens and feeder retracts",
    10,
    ["I9 barrier HIGH", "Q13 door valve", "I6 feeder inside"],
  ],
  [
    "MPO",
    "Firing process",
    "Oven light is energized while the timed process completes",
    20,
    ["Q9 oven light ON", "Timer running", "Interlock healthy"],
  ],
  [
    "MPO",
    "Transfer to turntable",
    "Vacuum unit collects workpiece and moves it to the turntable",
    12,
    ["I8 oven position", "Q11 vacuum valve", "I5 table position"],
  ],
  [
    "MPO",
    "Saw processing",
    "Turntable indexes under saw and Q4 processes the workpiece",
    14,
    ["I4 saw reference", "Q4 saw ON", "Guard accepted"],
  ],
  [
    "MPO",
    "Eject to conveyor",
    "Pneumatic ejector transfers workpiece; conveyor starts",
    8,
    ["Q14 ejector", "Q3 conveyor ON", "I3 end barrier"],
  ],
  [
    "SLD",
    "Detect colour",
    "Reflected-light value is compared with calibrated thresholds",
    7,
    ["Input barrier HIGH", "Colour 842 raw", "Class BLUE"],
  ],
  [
    "SLD",
    "Sort workpiece",
    "Blue ejector activates and chute barrier confirms delivery",
    8,
    ["Pulse counter 186", "Blue valve ON", "Chute barrier HIGH"],
  ],
  [
    "VGR",
    "Return to HBW",
    "VGR collects the sorted carrier and returns it to warehouse",
    12,
    ["Grip confirmed", "Transport clear", "HBW reserved"],
  ],
  [
    "HBW",
    "Complete storage",
    "Carrier is stored; inventory and digital record are updated",
    14,
    ["Slot B2 occupied", "Inventory +1", "Cycle complete"],
  ],
] as const;

const IMAGES: Record<string, string> = {
  DPS: "assets/station-dps-official.png",
  VGR: "assets/station-vgr-official.jpg",
  HBW: "assets/station-hbw-official.jpg",
  MPO: "assets/station-mpo-official.jpg",
  SLD: "assets/station-sld-official.jpg",
};

export default function FactoryEmulator() {
  const [running, setRunning] = useState(false),
    [elapsed, setElapsed] = useState(0),
    [speed, setSpeed] = useState(1),
    [selected, setSelected] = useState("DPS");
  const total = STEPS.reduce((n, s) => n + s[3], 0);
  useEffect(() => {
    if (!running) return;
    const t = setInterval(
      () => setElapsed((e) => (e + 1) % total),
      1000 / speed,
    );
    return () => clearInterval(t);
  }, [running, speed, total]);
  const current = useMemo(() => {
    let cursor = 0;
    for (let i = 0; i < STEPS.length; i++) {
      if (elapsed < cursor + STEPS[i][3])
        return {
          index: i,
          within: elapsed - cursor,
          start: cursor,
          step: STEPS[i],
        };
      cursor += STEPS[i][3];
    }
    return { index: 0, within: 0, start: 0, step: STEPS[0] };
  }, [elapsed]);
  useEffect(() => setSelected(current.step[0]), [current.index]);
  const pct = Math.round((elapsed / total) * 100);
  return (
    <section className="emulator-page">
      <div className="emulator-head">
        <div>
          <span>DOCUMENTED SEQUENTIAL EMULATION</span>
          <h2>Fischertechnik 560840 Production Cycle</h2>
          <p>
            A slower, inspectable execution of the delivery, storage,
            processing, sorting and return cycle.
          </p>
        </div>
        <div className="emulator-controls">
          <button
            className={running ? "danger" : "primary"}
            onClick={() => setRunning(!running)}
          >
            {running ? "Ⅱ Pause cycle" : "▶ Start cycle"}
          </button>
          <button
            className="secondary"
            onClick={() => {
              setElapsed(0);
              setRunning(false);
            }}
          >
            ↺ Reset
          </button>
          <button
            className="secondary"
            onClick={() =>
              setElapsed((current.start + current.step[3]) % total)
            }
          >
            Step →
          </button>
          <label>
            Speed
            <select
              value={speed}
              onChange={(e) => setSpeed(Number(e.target.value))}
            >
              <option value={0.5}>0.5×</option>
              <option value={1}>1× realistic</option>
              <option value={2}>2×</option>
              <option value={5}>5× review</option>
            </select>
          </label>
        </div>
      </div>
      <div className="emulator-layout">
        <main>
          <article className="emulator-stage">
            <header>
              <div>
                <span>
                  STEP {String(current.index + 1).padStart(2, "0")} /{" "}
                  {STEPS.length}
                </span>
                <h3>
                  {current.step[0]} · {current.step[1]}
                </h3>
                <p>{current.step[2]}</p>
              </div>
              <strong>
                {current.within}s / {current.step[3]}s
              </strong>
            </header>
            <div className="emulator-visual">
              <img
                src={IMAGES[current.step[0]]}
                alt={`${current.step[0]} operating`}
              />
              <div className="machine-overlay">
                <i />
                <b>{current.step[0]} ACTIVE</b>
                <span>{current.step[4][current.within % 3]}</span>
              </div>
              <div className="emulator-token">
                <i />
                <span>WP-024 · BLUE</span>
              </div>
            </div>
            <footer>
              <span>Cycle {Math.floor(elapsed / total) + 1}</span>
              <i>
                <b style={{ width: `${pct}%` }} />
              </i>
              <strong>
                {elapsed}s / {total}s
              </strong>
            </footer>
          </article>
          <div className="cycle-sequence">
            {STEPS.map((s, i) => (
              <button
                key={`${s[0]}${i}`}
                className={
                  i === current.index
                    ? "active"
                    : i < current.index
                      ? "done"
                      : ""
                }
                onClick={() => {
                  let e = 0;
                  for (let j = 0; j < i; j++) e += STEPS[j][3];
                  setElapsed(e);
                  setRunning(false);
                }}
              >
                <i>{i < current.index ? "✓" : i + 1}</i>
                <div>
                  <b>
                    {s[0]} · {s[1]}
                  </b>
                  <span>{s[3]} seconds</span>
                </div>
              </button>
            ))}
          </div>
        </main>
        <aside>
          <section className="signal-trace">
            <header>
              <span>PLC EXECUTION TRACE</span>
              <em>LIVE</em>
            </header>
            {current.step[4].map((x, i) => (
              <div key={x}>
                <code>{String(elapsed + i).padStart(4, "0")}</code>
                <i className={i <= current.within % 3 ? "on" : ""} />
                <p>
                  <b>{x}</b>
                  <span>
                    {i <= current.within % 3 ? "confirmed" : "waiting"}
                  </span>
                </p>
              </div>
            ))}
          </section>
          <section className="emulator-summary">
            <span>CYCLE METRICS</span>
            <div>
              <b>{total}s</b>
              <small>Nominal cycle</small>
            </div>
            <div>
              <b>{STEPS.length}</b>
              <small>Controlled steps</small>
            </div>
            <div>
              <b>0</b>
              <small>Interlock faults</small>
            </div>
            <div>
              <b>99.7%</b>
              <small>MQTT reliability</small>
            </div>
          </section>
        </aside>
      </div>
      <SimulationScience compact />
      <StationDiagnostics
        stationId={selected === "DPS" ? "DSI" : selected}
        tick={elapsed}
      />
    </section>
  );
}
