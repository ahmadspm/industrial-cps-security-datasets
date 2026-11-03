"use client";

import { PHYSICAL_STAGES } from "./PhotographicTwin";

const IO = [
  {
    id: "DSI",
    label: "DPS",
    sensors: ["NFC reader", "Input barrier", "Pickup presence"],
    actuators: ["Input conveyor", "Status light", "VGR request"],
  },
  {
    id: "VGR",
    label: "VGR",
    sensors: ["X/Y/Z encoders", "Reference switches", "Vacuum pressure"],
    actuators: ["X/Y/Z motors", "Vacuum valve", "Compressor"],
  },
  {
    id: "HBW",
    label: "HBW",
    sensors: ["Inside barrier I2", "X/Y encoders", "Cantilever limits"],
    actuators: ["Belt motor", "Rack X/Y axes", "Cantilever"],
  },
  {
    id: "MPO",
    label: "MPO",
    sensors: ["Oven barrier I9", "Feeder limits", "Turntable reference"],
    actuators: ["Oven + door", "Turntable + saw", "Ejector conveyor"],
  },
  {
    id: "SLD",
    label: "SLD",
    sensors: ["Input barrier", "Colour sensor", "Chute barriers"],
    actuators: ["Conveyor", "Blue ejector", "Compressor"],
  },
  {
    id: "DSO",
    label: "SSC",
    sensors: ["Environment", "Brightness", "PTU camera"],
    actuators: ["Camera pan/tilt", "Traffic light", "Telemetry publish"],
  },
] as const;

function stateFor(
  active: boolean,
  index: number,
  tick: number,
  sensor: boolean,
) {
  if (!active)
    return sensor && (tick + index) % 5 === 0 ? "UPDATING" : "STANDBY";
  if (sensor)
    return ["HIGH", "VALID", "COUNTING", "TRACKING"][(tick + index) % 4];
  return index < 2 ? "ENERGIZED" : "READY";
}

export default function StationIODashboard({
  tick,
  running,
  selected,
  onSelect,
}: {
  tick: number;
  running: boolean;
  selected: string;
  onSelect: (id: string) => void;
}) {
  const stage = PHYSICAL_STAGES[tick % PHYSICAL_STAGES.length];
  return (
    <section className="io-dashboard">
      <header>
        <div>
          <span>CYBER–PHYSICAL I/O DASHBOARD</span>
          <h3>Station sensors and actuators</h3>
          <p>
            Deterministic signals synchronized with the active production phase.
          </p>
        </div>
        <div className="io-summary">
          <b>{IO.reduce((n, x) => n + x.sensors.length, 0)}</b>
          <span>sensors</span>
          <b>{IO.reduce((n, x) => n + x.actuators.length, 0)}</b>
          <span>actuators</span>
          <em className={running ? "live" : ""}>
            {running ? "LIVE" : "PAUSED"}
          </em>
        </div>
      </header>
      <div className="io-grid">
        {IO.map((unit) => {
          const active =
            running && (unit.id === stage.station || unit.id === "DSO");
          return (
            <button
              key={unit.id}
              className={`io-station ${active ? "active" : ""} ${selected === unit.id ? "selected" : ""}`}
              onClick={() => onSelect(unit.id)}
            >
              <div className="io-title">
                <i className={active ? "on" : ""} />
                <div>
                  <b>{unit.label}</b>
                  <span>
                    {active
                      ? unit.id === "DSO"
                        ? "Continuous supervision"
                        : stage.label
                      : "Ready"}
                  </span>
                </div>
                <em>{active ? "ACTIVE" : "IDLE"}</em>
              </div>
              <section>
                <h4>
                  SENSORS <small>INPUT</small>
                </h4>
                {unit.sensors.map((name, i) => (
                  <div className="io-signal" key={name}>
                    <i className={active || (tick + i) % 5 !== 0 ? "on" : ""} />
                    <span>{name}</span>
                    <b>{stateFor(active, i, tick, true)}</b>
                  </div>
                ))}
              </section>
              <section>
                <h4>
                  ACTUATORS <small>OUTPUT</small>
                </h4>
                {unit.actuators.map((name, i) => (
                  <div className="io-signal actuator" key={name}>
                    <i className={active && i < 2 ? "on" : ""} />
                    <span>{name}</span>
                    <b>{stateFor(active, i, tick, false)}</b>
                  </div>
                ))}
              </section>
            </button>
          );
        })}
      </div>
      <footer>
        <span>
          <i className="observed" /> Observed PLC/TXT signal
        </span>
        <span>
          <i className="commanded" /> Commanded actuator state
        </span>
        <strong>
          Scan #{String(18420 + tick).padStart(6, "0")} · OPC UA{" "}
          {18 + (tick % 7)} ms · MQTT synchronized
        </strong>
      </footer>
    </section>
  );
}
