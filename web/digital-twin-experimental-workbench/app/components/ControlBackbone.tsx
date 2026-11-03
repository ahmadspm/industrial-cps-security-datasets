"use client";

export default function ControlBackbone({ pulse = 0 }: { pulse?: number }) {
  const nodes = [
    [
      "SIMATIC S7-1500",
      "PLC",
      "Scan 8.6 ms · RUN",
      "PLC program + physical I/O",
    ],
    [
      "OPC UA",
      "Industrial link",
      "12 nodes updating",
      "PLC ↔ gateway state exchange",
    ],
    [
      "Raspberry Pi 4",
      "IoT Gateway",
      "Node-RED online",
      "Protocol translation + enrichment",
    ],
    ["TXT 4.0", "MQTT Broker", "18 ms · 99.7%", "Telemetry + cloud interface"],
    [
      "Digital Twin",
      "State authority",
      "Synchronized",
      "Models, replay and evidence",
    ],
  ];
  return (
    <section className="control-backbone">
      <header>
        <div>
          <span>CONTROL & CONNECTIVITY BACKBONE</span>
          <b>PLC → OPC UA → IoT Gateway → MQTT → Digital Twin</b>
        </div>
        <em>LIVE</em>
      </header>
      <div className="backbone-flow">
        {nodes.map((n, i) => (
          <div className="backbone-wrap" key={n[0]}>
            <article className={i === pulse % nodes.length ? "active" : ""}>
              <i>{n[1]}</i>
              <div>
                <b>{n[0]}</b>
                <span>{n[3]}</span>
              </div>
              <small>
                <em /> {n[2]}
              </small>
            </article>
            {i < nodes.length - 1 && (
              <div className="data-link">
                <i />
                <span>
                  {i === 0
                    ? "OPC UA"
                    : i === 1
                      ? "Read / write"
                      : i === 2
                        ? "MQTT"
                        : i === 3
                          ? "Events"
                          : ""}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
    </section>
  );
}
