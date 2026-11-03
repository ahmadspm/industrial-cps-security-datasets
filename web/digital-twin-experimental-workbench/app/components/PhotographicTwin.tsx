"use client";

type TwinStation = { id: string; name: string; state: string; active: boolean };

const CELLS = [
  {
    id: "DPS",
    name: "Delivery & Pickup Station",
    image: "assets/station-dps-official.png",
    components: [
      "Light barrier",
      "Colour sensor",
      "NFC reader",
      "I/O conveyor",
    ],
    source: "DSI",
    x: 14,
    y: 72,
  },
  {
    id: "VGR",
    name: "Vacuum Gripper Robot",
    image: "assets/station-vgr-official.jpg",
    components: [
      "X/Y/Z encoders",
      "Vacuum cup",
      "Compressor",
      "Solenoid valve",
    ],
    source: "VGR",
    x: 76,
    y: 18,
  },
  {
    id: "HBW",
    name: "Automated High-Bay Warehouse",
    image: "assets/station-hbw-official.jpg",
    components: [
      "9 rack slots",
      "X/Y feeder",
      "Cantilever",
      "Transfer conveyor",
    ],
    source: "HBW",
    x: 46,
    y: 18,
  },
  {
    id: "MPO",
    name: "Multi-Processing Station + Oven",
    image: "assets/station-mpo-official.jpg",
    components: [
      "Oven + slide",
      "Vacuum transfer",
      "Rotary table",
      "Saw + ejector",
    ],
    source: "MPO",
    x: 14,
    y: 18,
  },
  {
    id: "SLD",
    name: "Sorting Line + Colour Detection",
    image: "assets/station-sld-official.jpg",
    components: [
      "Colour sensor",
      "Pulse sensor",
      "Belt motor",
      "3 ejectors + chutes",
    ],
    source: "SLD",
    x: 46,
    y: 72,
  },
  {
    id: "SSC",
    name: "Sensor Station + Camera",
    image: "assets/station-ssc-official.png",
    components: ["BME680", "Photoresistor", "PTU camera", "Status LED"],
    source: "DSO",
    x: 76,
    y: 72,
  },
];

export const PHYSICAL_STAGES = [
  {
    station: "DSI",
    label: "DPS intake",
    action: "Light barrier detects carrier · NFC identity read",
    pos: [14, 72],
  },
  {
    station: "VGR",
    label: "VGR pickup",
    action: "Axes reference · vacuum grip established",
    pos: [35, 45],
  },
  {
    station: "HBW",
    label: "HBW storage",
    action: "Rack feeder stores carrier in reserved slot B2",
    pos: [46, 18],
  },
  {
    station: "HBW",
    label: "HBW retrieval",
    action: "Carrier retrieved after production order release",
    pos: [46, 18],
  },
  {
    station: "VGR",
    label: "Transfer to MPO",
    action: "Vacuum robot transports carrier to processing",
    pos: [63, 18],
  },
  {
    station: "MPO",
    label: "Oven loading",
    action: "Door opens · feeder loads workpiece · interlock closes",
    pos: [14, 18],
  },
  {
    station: "MPO",
    label: "Machining",
    action: "Oven cycle · turntable indexing · saw processing",
    pos: [14, 18],
  },
  {
    station: "VGR",
    label: "Transfer to SLD",
    action: "Processed carrier transported to sorting line",
    pos: [31, 45],
  },
  {
    station: "SLD",
    label: "Colour sorting",
    action: "Colour measured · pneumatic ejector selected",
    pos: [46, 72],
  },
  {
    station: "VGR",
    label: "Return transfer",
    action: "VGR collects sorted carrier for final delivery",
    pos: [62, 45],
  },
  {
    station: "DSI",
    label: "DPS output",
    action: "Pickup station confirms completed workpiece",
    pos: [14, 72],
  },
] as const;

export default function PhotographicTwin({
  stations,
  tick,
  running,
  speed,
  color,
  tracking,
  selected,
  onSelect,
}: {
  stations: TwinStation[];
  tick: number;
  running: boolean;
  speed: number;
  color: string;
  tracking: boolean;
  selected: string;
  onSelect: (id: string) => void;
}) {
  const phase = tick % PHYSICAL_STAGES.length;
  const stage = PHYSICAL_STAGES[phase];
  const activeVisual = stage.station === "DSI" ? "DPS" : stage.station;
  return (
    <div
      className={`photo-twin ${tracking ? "tracking" : ""} process-${activeVisual.toLowerCase()}`}
    >
      <div className="factory-table">
        <div className="table-edge">
          FISCHERTECHNIK TRAINING FACTORY INDUSTRY 4.0 · 24V · 560840
        </div>
      </div>
      <div className="physical-flow-strip" aria-label="Production flow">
        {["DPS", "VGR", "HBW", "VGR", "MPO", "VGR", "SLD", "VGR", "DPS"].map(
          (x, i) => (
            <div key={`${x}${i}`} className={i === phase % 9 ? "active" : ""}>
              <b>{x}</b>
              {i < 8 && (
                <span>
                  <em>
                    {
                      [
                        "pickup",
                        "store",
                        "retrieve",
                        "load",
                        "process",
                        "sort",
                        "return",
                        "deliver",
                      ][i]
                    }
                  </em>
                  →
                </span>
              )}
            </div>
          ),
        )}
      </div>
      {CELLS.map((cell, i) => {
        const active =
          cell.id === activeVisual || (cell.id === "SSC" && running);
        return (
          <button
            key={cell.id}
            className={`photo-station ${active ? "active" : ""} ${selected === cell.source ? "selected" : ""} station-${cell.id.toLowerCase()}`}
            style={{ left: `${cell.x}%`, top: `${cell.y}%` }}
            onClick={() => onSelect(cell.source)}
            aria-label={`Inspect ${cell.name}`}
          >
            <div className="station-photo official-station-photo">
              <img
                src={cell.image}
                alt={`Official Fischertechnik ${cell.name}`}
              />
              <span className="scan-line" />
              <span className="io-beam" />
              <span className="motion-marker">
                {active && cell.id !== "SSC"
                  ? stage.label
                  : cell.id === "SSC" && running
                    ? "MONITORING"
                    : ""}
              </span>
              <div
                className={`hardware-motion hw-${cell.id.toLowerCase()} ${selected === cell.source ? "selected" : ""}`}
                aria-hidden="true"
              >
                <span className="axis axis-x" />
                <span className="axis axis-y" />
                <span className="axis axis-z" />
                <i className="moving-part" />
                <b>
                  {cell.id === "VGR"
                    ? "X/Y/Z + VACUUM"
                    : cell.id === "HBW"
                      ? "LIFT + CANTILEVER"
                      : cell.id === "MPO"
                        ? "OVEN + TURNTABLE + SAW"
                        : cell.id === "SLD"
                          ? "BELT + EJECTOR"
                          : cell.id === "DPS"
                            ? "BELT + NFC"
                            : "CAMERA PAN / TILT"}
                </b>
              </div>
              {cell.id === "SLD" && (
                <div className="sld-sort-demo" aria-hidden="true">
                  <i className="part blue" />
                  <i className="part white" />
                  <i className="part red" />
                  <span>BLUE</span>
                  <span>WHITE</span>
                  <span>RED</span>
                </div>
              )}
              {cell.id === "DPS" && (
                <div className="dps-signal-chain" aria-hidden="true">
                  <span>DETECT</span>
                  <b>→</b>
                  <span>COLOUR</span>
                  <b>→</b>
                  <span>NFC</span>
                </div>
              )}
              <div className="station-component-tags" aria-hidden="true">
                {cell.components.map((component) => (
                  <span key={component}>{component}</span>
                ))}
              </div>
            </div>
            <header>
              <i>{String(i + 1).padStart(2, "0")}</i>
              <div>
                <b>{cell.id}</b>
                <span>{cell.name}</span>
              </div>
              <em className={active ? "on" : ""} />
            </header>
            <footer>
              <span>
                {active
                  ? cell.id === "SSC"
                    ? "OBSERVING"
                    : stage.action.split(" · ")[0]
                  : "IDLE"}
              </span>
              <small>{active ? "Live I/O" : "Ready"}</small>
            </footer>
          </button>
        );
      })}
      <div
        className="photo-workpiece"
        style={{
          left: `${stage.pos[0]}%`,
          top: `${stage.pos[1]}%`,
          background: color,
        }}
      >
        <i />
        <span>WP-024</span>
      </div>
      <div className="process-hud">
        <span>
          PHASE {String(phase + 1).padStart(2, "0")} / {PHYSICAL_STAGES.length}
        </span>
        <b>{stage.label}</b>
        <p>{stage.action}</p>
        <i>
          <em />
        </i>
      </div>
      <div className="control-rack">
        <img
          src="assets/fischertechnik-560840-reference.jpg"
          alt="Siemens S7-1500 PLC and 24V connection board"
        />
        <div>
          <b>SIMATIC S7-1500</b>
          <span>PLC scan synchronized · {18 + (tick % 7)} ms</span>
        </div>
        <i className={running ? "on" : ""} />
      </div>
      {!running && <div className="scene-paused">PAUSED</div>}
      <div className="scene-help">
        Select any station for live I/O · {speed}× operational replay
      </div>
    </div>
  );
}
