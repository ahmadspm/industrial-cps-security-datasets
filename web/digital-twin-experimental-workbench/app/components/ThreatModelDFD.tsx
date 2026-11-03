"use client";

import { useState } from "react";

const Flow = ({ label }: { label: string }) => (
  <div className="dfd-flow">
    <span>{label}</span>
    <i>→</i>
  </div>
);
const Entity = ({ children }: { children: React.ReactNode }) => (
  <div className="dfd-entity">{children}</div>
);
const Process = ({
  id,
  children,
  risk = false,
}: {
  id: string;
  children: React.ReactNode;
  risk?: boolean;
}) => (
  <div className={`dfd-process ${risk ? "risk" : ""}`}>
    <i>{id}</i>
    <b>{children}</b>
  </div>
);
const Store = ({ children }: { children: React.ReactNode }) => (
  <div className="dfd-store">
    <span>D</span>
    <b>{children}</b>
  </div>
);

export default function ThreatModelDFD() {
  const [level, setLevel] = useState(0);
  return (
    <article className="security-card threat-dfd professional-dfd">
      <header>
        <div>
          <b>System data-flow and trust-boundary model</b>
          <span>
            Conventional DFD notation · labelled flows · decomposed analysis
            levels
          </span>
        </div>
        <div className="dfd-levels">
          {[0, 1, 2].map((item) => (
            <button
              key={item}
              className={level === item ? "active" : ""}
              onClick={() => setLevel(item)}
            >
              Level {item}
            </button>
          ))}
        </div>
      </header>
      <div className="dfd-legend">
        <span>
          <i className="entity" />
          External entity
        </span>
        <span>
          <i className="process" />
          Process
        </span>
        <span>
          <i className="store" />
          Data store
        </span>
        <span>
          <i className="boundary" />
          Trust boundary
        </span>
      </div>
      {level === 0 && (
        <div className="dfd-canvas level-0">
          <div className="dfd-title">
            <b>Level 0 · Smart Factory security context</b>
            <span>System boundary and external exchanges</span>
          </div>
          <div className="dfd-context-row">
            <Entity>Operator / researcher</Entity>
            <Flow label="orders · control · queries" />
            <Process id="0" risk>
              Smart Factory Cyber-Physical System
            </Process>
            <Flow label="telemetry · status · evidence" />
            <Entity>Enterprise / analyst services</Entity>
          </div>
          <div className="dfd-context-row lower">
            <Entity>Threat intelligence</Entity>
            <Flow label="CVE · CWE · CAPEC · ATT&CK" />
            <Store>Security knowledge & experiment evidence</Store>
            <Flow label="risk · paths · controls" />
            <Entity>Security analyst</Entity>
          </div>
          <div className="dfd-system-boundary">
            <span>
              SYSTEM BOUNDARY · Fischertechnik factory + PLC + gateway + broker
              + digital twin
            </span>
          </div>
        </div>
      )}
      {level === 1 && (
        <div className="dfd-canvas level-1">
          <div className="dfd-title">
            <b>Level 1 · Enterprise-to-physical architecture</b>
            <span>Processes, stores, zones and cross-boundary flows</span>
          </div>
          <section className="dfd-zone enterprise">
            <label>ENTERPRISE / EXTERNAL</label>
            <div>
              <Entity>Research workstation</Entity>
              <Flow label="HTTPS · SSH" />
              <Process id="1.0">Enterprise services</Process>
              <Flow label="orders · analytics" />
              <Store>ERP / research data</Store>
            </div>
          </section>
          <div className="dfd-trust">
            <span>TB-01 · Authenticated enterprise conduit</span>
          </div>
          <section className="dfd-zone dmz">
            <label>OPERATIONS DMZ</label>
            <div>
              <Process id="2.1">Jump / access service</Process>
              <Flow label="session" />
              <Process id="2.2" risk>
                MQTT broker
              </Process>
              <Flow label="events" />
              <Process id="2.3">Historian mirror</Process>
            </div>
          </section>
          <div className="dfd-trust">
            <span>TB-02 · Firewall allowlist · MQTT / OPC UA only</span>
          </div>
          <section className="dfd-zone ot">
            <label>OT SUPERVISORY & CONTROL</label>
            <div>
              <Process id="3.1" risk>
                Digital Twin runtime
              </Process>
              <Flow label="OPC UA read / approved write" />
              <Process id="3.2" risk>
                S7-1500 PLC
              </Process>
              <Flow label="I/O image" />
              <Process id="3.3">IoT / TXT gateway</Process>
              <Flow label="snapshots" />
              <Store>Twin state & logs</Store>
            </div>
          </section>
          <div className="dfd-trust">
            <span>TB-03 · Control-to-physical safety boundary</span>
          </div>
          <section className="dfd-zone physical">
            <label>PHYSICAL PROCESS</label>
            <div>
              <Entity>DPS / sensors</Entity>
              <Flow label="workpiece" />
              <Entity>VGR · HBW · MPO · SLD</Entity>
              <Flow label="state · alarms" />
              <Entity>Actuators / interlocks</Entity>
            </div>
          </section>
        </div>
      )}
      {level === 2 && (
        <div className="dfd-canvas level-2">
          <div className="dfd-title">
            <b>Level 2 · Station control and twin synchronisation</b>
            <span>Detailed sensor-to-decision-to-actuator loop</span>
          </div>
          <div className="dfd-control-loop">
            <Entity>Colour · NFC · position · light barriers</Entity>
            <Flow label="raw signals" />
            <Process id="3.3.1">Gateway acquisition & enrichment</Process>
            <Flow label="signed MQTT observation" />
            <Process id="3.1.1" risk>
              Twin state reconstruction
            </Process>
            <Flow label="decision / command request" />
            <Process id="3.2.1" risk>
              PLC validation & sequencing
            </Process>
            <Flow label="output image" />
            <Entity>Motors · vacuum · oven · saw · ejectors</Entity>
          </div>
          <div className="dfd-control-loop secondary">
            <Store>Observed event log</Store>
            <Flow label="provenance" />
            <Process id="3.1.2">Behaviour / anomaly model</Process>
            <Flow label="alert · confidence" />
            <Store>Security evidence</Store>
            <Flow label="response rule" />
            <Process id="3.2.2">Safe-state & interlock manager</Process>
          </div>
          <div className="dfd-feedback">
            <span>PHYSICAL FEEDBACK</span>
            <i>
              Actuator response and process outcome return through independent
              sensors → compare command, observation and expected behaviour
            </i>
          </div>
          <div className="dfd-hotspots">
            <b>Threat points:</b>
            <span>TP-1 spoofed sensor</span>
            <span>TP-2 unauthorized publisher</span>
            <span>TP-3 twin inference confusion</span>
            <span>TP-4 OPC UA write</span>
            <span>TP-5 PLC logic change</span>
            <span>TP-6 actuator mismatch</span>
          </div>
        </div>
      )}
    </article>
  );
}
