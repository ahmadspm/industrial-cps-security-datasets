"use client";

import { useEffect, useMemo, useState } from "react";

const STEPS = [
  [
    "Scope",
    "AOA policy engine",
    "PTES pre-engagement",
    "Validate authorisation and Digital Twin boundary",
    "Load mission, permitted aliases, test window and non-interference limits.",
    [
      "scope: DT-CYBERRANGE-01",
      "authority: simulation-only",
      "excluded: physical PLC · production broker · external hosts",
    ],
    "Signed scope manifest",
    "12 twin assets authorised",
    "None",
  ],
  [
    "Passive",
    "Zeek + PCAP observer",
    "T1040",
    "Observe existing communication without probing",
    "Reconstruct conversations, protocols and traffic rates from replayed twin telemetry.",
    [
      "zeek [replayed-twin-pcap]",
      "mqtt  1883/tcp  14 peers",
      "opcua 4840/tcp   3 peers",
      "s7comm 102/tcp   2 peers",
    ],
    "conn.log · protocol histogram",
    "Three industrial protocols observed",
    "Low",
  ],
  [
    "Plan",
    "AOA reasoning",
    "T1595 / T1046",
    "Select minimum-impact discovery plan",
    "Prefer passive evidence, then low-rate host discovery before fingerprinting.",
    [
      "policy: passive-first",
      "probe ceiling: 8 packets/s",
      "fragile assets: PLC · TXT controller",
      "decision: staggered hybrid discovery",
    ],
    "Plan decision · confidence 0.96",
    "Two assets marked fragile",
    "Low",
  ],
  [
    "Discover",
    "Nmap host discovery",
    "T1046",
    "Identify reachable Digital Twin hosts",
    "Simulate low-rate host discovery against the approved twin scope.",
    [
      "$ nmap [DT-approved-scope] --host-discovery --safe-rate",
      "host BROKER-DT  up  latency 2.1ms",
      "host GATEWAY-DT up  latency 3.8ms",
      "host PLC-DT     up  latency 1.6ms",
      "host HMI-DT     up  latency 4.2ms",
    ],
    "Host discovery XML",
    "8 of 12 aliases reachable",
    "Low",
  ],
  [
    "Map",
    "Nmap route mapping",
    "T0840",
    "Infer zones and communication paths",
    "Correlate simulated routes with the twin knowledge graph and trust boundaries.",
    [
      "path: KALI-DT → DMZ-FW-DT → BROKER-DT",
      "path: BROKER-DT → IOT-GW-DT → PLC-DT",
      "boundary TB-02: restricted",
      "new relation: HMI-DT ↔ OPCUA-DT",
    ],
    "Route graph delta",
    "One undocumented HMI–OPC UA relation",
    "Medium",
  ],
  [
    "Enumerate",
    "Nmap service detection",
    "T1046",
    "Fingerprint exposed services and versions",
    "Simulate bounded service identification only on discovered aliases.",
    [
      "$ nmap [8 DT hosts] --service-detection --safe-profile",
      "BROKER-DT  1883 mqtt  Mosquitto-like",
      "OPCUA-DT  4840 opcua asyncua-like",
      "PLC-DT      102 iso-tsap S7-family",
      "JUMP-DT      22 ssh   OpenSSH-like",
    ],
    "Service inventory + confidence",
    "11 services · 4 OT-relevant",
    "Low",
  ],
  [
    "OT Identify",
    "PROFINET/S7 safe metadata",
    "T0888",
    "Identify industrial roles and device metadata",
    "Use simulated read-only metadata; do not alter controller state.",
    [
      "profinet discovery: PLC-DT / controller role",
      "s7 metadata: SIMATIC S7-1500 family",
      "module role: factory sequencing",
      "write capability: blocked by simulation guardrail",
    ],
    "Industrial asset identity record",
    "PLC family and role confirmed",
    "Medium",
  ],
  [
    "OT Identify",
    "MQTT/OPC UA inspector",
    "T0888",
    "Enumerate industrial application surfaces",
    "Inspect synthetic broker metadata and OPC UA security profiles without production subscriptions or writes.",
    [
      "MQTT-DT: anonymous=false · TLS optional",
      "topic families: state · stock · command · ack",
      "OPCUA-DT: 2 endpoints",
      "security modes: SignAndEncrypt · None",
      "writable nodes: hidden from recon role",
    ],
    "Protocol surface summary",
    "One insecure OPC UA profile represented",
    "Medium",
  ],
  [
    "Correlate",
    "Metasploit/Rapid7 catalogue",
    "T1595.002",
    "Correlate fingerprints with assessment modules",
    "Simulate module search and vulnerability correlation; no exploit or payload is executed.",
    [
      "msfconsole [catalogue-only mode]",
      "match: mqtt_version / auxiliary scanner",
      "match: opcua endpoint review",
      "match: ssh version assessment",
      "exploitation: DISABLED",
    ],
    "Module-candidate list",
    "5 validation candidates",
    "None",
  ],
  [
    "Validate",
    "NVD/CVE + configuration rules",
    "T1588.006",
    "Prioritise plausible weaknesses",
    "Combine version uncertainty, security modes, trust paths and asset criticality.",
    [
      "V-01 OPC UA SecurityMode=None   confidence high",
      "V-02 MQTT TLS not enforced       confidence medium",
      "V-03 SSH version verification     confidence low",
      "V-04 undocumented HMI relation    confidence high",
    ],
    "Applicability matrix",
    "2 high-confidence weaknesses",
    "Medium",
  ],
  [
    "Model",
    "AOA knowledge graph",
    "T0846 / T0888",
    "Build reconnaissance attack-surface graph",
    "Merge verified hosts, services, zones, dependencies and uncertainty into Kₜ.",
    [
      "nodes: 12 assets · 11 services · 6 protocols",
      "edges: 28 observed · 7 inferred",
      "entry candidates: JUMP-DT · HMI-DT",
      "crown jewels: PLC-DT · BROKER-DT · OPCUA-DT",
    ],
    "K₁ reconnaissance graph",
    "Two candidate paths require validation",
    "Low",
  ],
  [
    "Report",
    "AOA report generator",
    "Stage gate",
    "Close reconnaissance and generate findings",
    "Freeze evidence and recommend authorised next-stage validation without executing it.",
    [
      "stage status: COMPLETE",
      "coverage: 12/12 scoped assets",
      "evidence integrity: VERIFIED",
      "next stage: vulnerability validation · approval required",
    ],
    "AOA-RECON-016 report",
    "Ready for analyst review",
    "None",
  ],
] as const;

const TWIN_ASSETS = [
  ["KALI-DT", "Assessment node", "Cyber-range", "10.40.0.2"],
  ["DMZ-FW-DT", "IT/OT boundary", "DMZ", "10.40.0.1"],
  ["JUMP-DT", "Jump service", "DMZ", "10.40.0.10"],
  ["BROKER-DT", "MQTT broker", "OT services", "10.40.1.10"],
  ["OPCUA-DT", "OPC UA projection", "OT services", "10.40.1.11"],
  ["IOT-GW-DT", "IoT/TXT gateway", "OT control", "10.40.1.20"],
  ["PLC-DT", "SIMATIC S7-1500", "OT control", "10.40.1.30"],
  ["HMI-DT", "Operations HMI", "OT control", "10.40.1.31"],
  ["POSTGRES-DT", "Evidence database", "OT services", "10.40.1.40"],
  ["VGR-AGENT", "Robot transport twin", "Physical model", "agent://vgr"],
  ["HBW-AGENT", "Warehouse twin", "Physical model", "agent://hbw"],
  [
    "MPO-SLD-DT",
    "Processing/sorting twins",
    "Physical model",
    "agent://process",
  ],
] as const;

const CONSOLE = [
  {
    command: "aoa-scope verify --manifest missions/AOA-RECON-016.yaml",
    output: [
      "[PASS] twin project: smart-factory-digital-twin",
      "[PASS] 12 aliases authorised",
      "[BLOCK] physical endpoints and external routing",
      "[READY] evidence directory created",
    ],
    rationale:
      "I must verify authority and isolate the virtual targets before any discovery tool is available.",
    state: "Scope graph loaded; all real-world connectors denied.",
  },
  {
    command: "zeek -r replay/mqtt-opcua-s7.pcap LogAscii::use_json=T",
    output: [
      "conn.log: 41 simulated conversations",
      "mqtt: BROKER-DT ↔ IOT-GW-DT ↔ station agents",
      "opcua: OPCUA-DT ↔ PLC-DT",
      "s7comm: HMI-DT ↔ PLC-DT",
    ],
    rationale:
      "Passive evidence has zero process impact and reveals the real communication relationships modelled by this twin.",
    state: "Four DT protocols and seven communicating assets observed.",
  },
  {
    command:
      "aoa-plan --strategy passive-first --max-rate 8pps --protect PLC-DT,IOT-GW-DT",
    output: [
      "candidate 1: broad active scan     rejected",
      "candidate 2: passive-only          incomplete",
      "candidate 3: staggered discovery   selected",
      "confidence: 0.96",
    ],
    rationale:
      "The gateway and controller represent timing-sensitive OT assets, so I select the least intrusive plan that can close the evidence gaps.",
    state: "Probe ceiling and fragile-asset rules added to Kₜ.",
  },
  {
    command:
      "nmap -sn -PE -PS22,80,443,102,1883,4840 --max-rate 8 -oX evidence/hosts.xml 10.40.0.0/23",
    output: [
      "Nmap scan report for DMZ-FW-DT (10.40.0.1)    Host is up",
      "Nmap scan report for JUMP-DT (10.40.0.10)     Host is up",
      "Nmap scan report for BROKER-DT (10.40.1.10)   Host is up",
      "Nmap scan report for OPCUA-DT (10.40.1.11)    Host is up",
      "Nmap scan report for IOT-GW-DT (10.40.1.20)   Host is up",
      "Nmap scan report for PLC-DT (10.40.1.30)      Host is up",
      "Nmap scan report for HMI-DT (10.40.1.31)      Host is up",
      "Nmap scan report for POSTGRES-DT (10.40.1.40) Host is up",
    ],
    rationale:
      "Host discovery is limited to the exact private addresses assigned to the Digital Twin and avoids full port interrogation.",
    state: "8 live network assets linked to existing twin components.",
  },
  {
    command:
      "nmap -sn --traceroute --max-rate 8 -oX evidence/routes.xml 10.40.1.10,10.40.1.20,10.40.1.30",
    output: [
      "KALI-DT → DMZ-FW-DT → BROKER-DT",
      "KALI-DT → DMZ-FW-DT → IOT-GW-DT",
      "IOT-GW-DT → PLC-DT",
      "knowledge delta: HMI-DT ↔ OPCUA-DT not in baseline",
    ],
    rationale:
      "I need to distinguish direct reachability from inferred dependencies before choosing service-level probes.",
    state: "Trust-boundary graph updated; one undocumented relation flagged.",
  },
  {
    command:
      "nmap -sT -sV --version-light -p 22,80,443,102,1883,4840,5432 --max-rate 8 -oX evidence/services.xml 10.40.0.10,10.40.1.10-11,10.40.1.20,10.40.1.30-31,10.40.1.40",
    output: [
      "JUMP-DT      22/tcp   open  ssh",
      "BROKER-DT  1883/tcp  open  mqtt",
      "OPCUA-DT   4840/tcp  open  opcua",
      "IOT-GW-DT   80/tcp   open  http",
      "PLC-DT      102/tcp  open  iso-tsap",
      "HMI-DT      443/tcp  open  https",
      "POSTGRES-DT 5432/tcp open  postgresql",
    ],
    rationale:
      "A short allowlist of ports matches services already represented in the twin, reducing unnecessary probes and false assumptions.",
    state: "11 services fingerprinted and attached to eight asset nodes.",
  },
  {
    command:
      "nmap -p102 --script s7-info PLC-DT && nmap --script multicast-profinet-discovery",
    output: [
      "PLC name: PLC-DT",
      "device family: SIMATIC S7-1500 (simulated metadata)",
      "role: station sequencing and interlocks",
      "PROFINET name: smartfactory-plc-dt",
      "write functions: denied by recon policy",
    ],
    rationale:
      "The S7 and PROFINET identities confirm that PLC-DT is the control crown jewel; read-only identification is sufficient at this stage.",
    state: "PLC role, protocol and criticality verified.",
  },
  {
    command:
      "mosquitto_sub -h BROKER-DT -t '$SYS/#' -C 5 && opcua-client OPCUA-DT:4840 --endpoints-only",
    output: [
      "MQTT broker: authentication required",
      "TLS listener: optional in simulated configuration",
      "topic families from DT schema: state / stock / command / ack",
      "OPC UA endpoints: SignAndEncrypt, None",
      "node browsing and writes: not requested",
    ],
    rationale:
      "Broker system metadata and endpoint descriptions identify exposure without consuming factory command topics or modifying process variables.",
    state: "MQTT and OPC UA security-profile observations added.",
  },
  {
    command:
      "msfconsole -q -x 'workspace -a AOA-RECON-016; db_import evidence/services.xml; hosts; services; exit'",
    output: [
      "Workspace: AOA-RECON-016",
      "Imported 8 hosts and 11 services",
      "auxiliary scanner candidates: mqtt / ssh / http",
      "exploit and payload modules: policy-disabled",
      "database status: evidence-only",
    ],
    rationale:
      "Metasploit is useful here as an evidence organiser and module catalogue, not as an exploitation engine.",
    state: "Five non-executed validation candidates correlated.",
  },
  {
    command:
      "aoa-correlate --services evidence/services.xml --sources NVD,CWE,ATTACK-ICS --require-version-confidence",
    output: [
      "V-01 OPC UA SecurityMode=None      HIGH confidence",
      "V-02 MQTT TLS not enforced         MEDIUM confidence",
      "V-03 SSH version unresolved        LOW confidence",
      "V-04 HMI↔OPCUA undocumented edge   HIGH confidence",
      "confirmed vulnerabilities: 0 (validation not executed)",
    ],
    rationale:
      "I separate observed configuration weaknesses from version-dependent candidates so the report does not overclaim vulnerabilities.",
    state: "Four candidates ranked; uncertainty retained explicitly.",
  },
  {
    command:
      "aoa-kg merge evidence/*.xml conn.log --baseline twin-topology.json --output K1-recon.json",
    output: [
      "assets: 12  services: 11  protocols: 6",
      "relations: 28 observed  7 inferred",
      "crown jewels: PLC-DT / BROKER-DT / OPCUA-DT",
      "candidate paths: JUMP-DT→BROKER-DT; HMI-DT→OPCUA-DT",
      "physical station agents: observed through MQTT only",
    ],
    rationale:
      "The attack-surface graph must include the same stations, services and dependencies used by the behavioural Digital Twin.",
    state:
      "K₁ now represents the developed twin rather than a generic OT network.",
  },
  {
    command:
      "aoa-report build --stage reconnaissance --knowledge K1-recon.json --evidence evidence/ --sign",
    output: [
      "coverage: 12/12 scoped twin assets",
      "evidence items: 18 verified",
      "high-confidence observations: 2",
      "exploitation performed: no",
      "next gate: analyst-approved validation",
      "report: AOA-RECON-016.json",
    ],
    rationale:
      "The reconnaissance objective is complete. Continuing would cross into vulnerability validation and requires a separate mission decision.",
    state: "Stage closed; evidence frozen and signed.",
  },
] as const;

export default function AOAReconnaissanceLab({
  onNotify,
}: {
  onNotify: (message: string) => void;
}) {
  const [scenario, setScenario] = useState(
    "External assessor through operations DMZ",
  );
  const [mode, setMode] = useState("Hybrid · passive first");
  const [pace, setPace] = useState("OT-safe");
  const [step, setStep] = useState(0);
  const [running, setRunning] = useState(false);
  const [consoleView, setConsoleView] = useState<
    "Terminal" | "DT assets" | "Evidence"
  >("Terminal");
  const complete = step >= STEPS.length;
  const active = STEPS[Math.min(step, STEPS.length - 1)];
  const consoleStep = CONSOLE[Math.min(step, CONSOLE.length - 1)];
  const completed = STEPS.slice(0, step);
  useEffect(() => {
    if (!running || complete) {
      if (complete) setRunning(false);
      return;
    }
    const t = setTimeout(
      () => setStep((v) => v + 1),
      pace === "OT-safe" ? 1450 : 850,
    );
    return () => clearTimeout(t);
  }, [running, step, complete, pace]);
  const counts = useMemo(
    () => ({
      hosts: step >= 4 ? 8 : 0,
      services: step >= 6 ? 11 : 0,
      ot: step >= 8 ? 4 : 0,
      findings: step >= 10 ? 4 : 0,
    }),
    [step],
  );
  const reset = () => {
    setRunning(false);
    setStep(0);
    onNotify("Reconnaissance stage reset");
  };
  return (
    <div className="recon-lab">
      <div className="recon-stage-map">
        {[
          "Authorise",
          "Passive recon",
          "Active discovery",
          "OT identification",
          "Correlation",
          "Report",
        ].map((label, i) => {
          const marks = [1, 3, 6, 8, 10, 12],
            state =
              step >= marks[i]
                ? "done"
                : step >= (marks[i - 1] || 0)
                  ? "active"
                  : "";
          return (
            <div className={state} key={label}>
              <i>{state === "done" ? "✓" : i + 1}</i>
              <b>{label}</b>
              <small>
                {
                  ["Scope", "T1040", "T1046", "T0888", "CVE/CWE", "Stage gate"][
                    i
                  ]
                }
              </small>
            </div>
          );
        })}
      </div>
      <div className="recon-banner">
        <div>
          <span>ASSESSMENT STAGE 01</span>
          <b>Reconnaissance and attack-surface discovery</b>
          <small>
            Cyber Kill Chain: Reconnaissance · MITRE Enterprise/ICS: Discovery
          </small>
        </div>
        <div>
          <span>AGENT OBJECTIVE</span>
          <b>
            Map authorised Digital Twin assets and identify evidence-backed
            validation candidates
          </b>
          <small>Exploitation and physical actions are prohibited</small>
        </div>
      </div>
      <div className="agentic-grid recon-config-grid">
        <article className="agent-card recon-config">
          <header>
            <div>
              <b>Scenario and mission</b>
              <span>Interactive assessment configuration</span>
            </div>
            <em>AOA-RECON-016</em>
          </header>
          <div className="recon-fields">
            <label>
              Scenario
              <select
                value={scenario}
                onChange={(e) => setScenario(e.target.value)}
              >
                <option>External assessor through operations DMZ</option>
                <option>Compromised engineering workstation</option>
                <option>Insider with HMI network access</option>
              </select>
            </label>
            <label>
              Discovery strategy
              <select value={mode} onChange={(e) => setMode(e.target.value)}>
                <option>Hybrid · passive first</option>
                <option>Passive only</option>
                <option>Controlled active</option>
              </select>
            </label>
            <label>
              Probe pace
              <select value={pace} onChange={(e) => setPace(e.target.value)}>
                <option>OT-safe</option>
                <option>Accelerated twin replay</option>
              </select>
            </label>
          </div>
          <div className="recon-mission">
            <span>MISSION</span>
            <b>
              Discover the simulated smart-factory attack surface, identify
              IT/OT trust paths, fingerprint exposed services and produce a
              prioritised report—without exploitation.
            </b>
          </div>
          <div className="recon-controls">
            <button
              className="agent-primary"
              disabled={complete || running}
              onClick={() => setRunning(true)}
            >
              {step ? "Continue stage" : "Launch AOA reconnaissance"}
            </button>
            <button
              disabled={complete}
              onClick={() => setStep(Math.min(STEPS.length, step + 1))}
            >
              Next activity
            </button>
            <button onClick={() => setRunning(false)}>Pause</button>
            <button onClick={reset}>Reset</button>
          </div>
        </article>
        <article className="agent-card recon-status">
          <header>
            <div>
              <b>Stage telemetry</b>
              <span>
                {running
                  ? "AOA is executing the next bounded tool"
                  : complete
                    ? "Stage complete"
                    : "Awaiting operator start"}
              </span>
            </div>
            <i className={running ? "pulse" : ""} />
          </header>
          <div className="recon-metrics">
            {[
              ["PROGRESS", `${Math.round((step / STEPS.length) * 100)}%`],
              ["HOSTS", counts.hosts],
              ["SERVICES", counts.services],
              ["OT SURFACES", counts.ot],
              ["FINDINGS", counts.findings],
              ["NOISE BUDGET", pace === "OT-safe" ? "LOW" : "SIM"],
            ].map((x) => (
              <div key={x[0]}>
                <span>{x[0]}</span>
                <b>{x[1]}</b>
              </div>
            ))}
          </div>
          <div className="recon-progress">
            <i style={{ width: `${(step / STEPS.length) * 100}%` }} />
          </div>
        </article>
      </div>
      <article className="agent-card recon-scope-map">
        <header>
          <div>
            <b>Reconnaissance scope: developed Digital Twin</b>
            <span>
              Exact cyber, control and station representations used by the AOA
            </span>
          </div>
          <em>12 AUTHORISED ALIASES</em>
        </header>
        <div className="scope-flow">
          <div>
            <span>ASSESSMENT</span>
            <b>KALI-DT</b>
          </div>
          <i>→</i>
          <div>
            <span>OPERATIONS DMZ</span>
            <b>DMZ-FW-DT · JUMP-DT</b>
          </div>
          <i>→</i>
          <div>
            <span>OT SERVICES</span>
            <b>BROKER-DT · OPCUA-DT · POSTGRES-DT</b>
          </div>
          <i>→</i>
          <div>
            <span>CONTROL</span>
            <b>IOT-GW-DT · PLC-DT · HMI-DT</b>
          </div>
          <i>→</i>
          <div>
            <span>BEHAVIOURAL TWIN</span>
            <b>VGR · HBW · MPO · SLD agents</b>
          </div>
        </div>
      </article>
      <div className="agentic-grid recon-workbench">
        <article className="agent-card aoa-plan">
          <header>
            <div>
              <b>AOA decision workspace</b>
              <span>Plan · tool choice · technique · evidence requirement</span>
            </div>
            <em>{active[0]}</em>
          </header>
          <div className="active-recon">
            <span>CURRENT ACTIVITY {Math.min(step + 1, 12)} OF 12</span>
            <h3>{complete ? "Reconnaissance completed" : active[3]}</h3>
            <p>
              {complete
                ? "All authorised evidence has been frozen and the report is ready."
                : active[4]}
            </p>
            <dl>
              <div>
                <dt>Selected tool</dt>
                <dd>{active[1]}</dd>
              </div>
              <div>
                <dt>ATT&CK mapping</dt>
                <dd>{active[2]}</dd>
              </div>
              <div>
                <dt>Expected evidence</dt>
                <dd>{active[6]}</dd>
              </div>
              <div>
                <dt>Operational risk</dt>
                <dd className={`risk-${active[8].toLowerCase()}`}>
                  {active[8]}
                </dd>
              </div>
            </dl>
          </div>
          <div className="reason-gate">
            <b>AOA decision gate</b>
            <span>
              {complete
                ? "Stop: objective satisfied; later stages require new authorisation."
                : step < 3
                  ? "Continue: scope is authorised and passive evidence remains incomplete."
                  : "Continue only because this activity is simulated, rate-bounded and within approved aliases."}
            </span>
            <em>{complete ? "STOP" : "APPROVED"}</em>
          </div>
        </article>
        <article className="agent-card kali-console">
          <header>
            <div>
              <b>AOA operational console · Kali Digital Twin</b>
              <span>
                Step {Math.min(step + 1, 12)} · {active[1]} · simulated against
                DT aliases only
              </span>
            </div>
            <div className="console-tabs">
              {(["Terminal", "DT assets", "Evidence"] as const).map((tab) => (
                <button
                  className={consoleView === tab ? "active" : ""}
                  onClick={() => setConsoleView(tab)}
                  key={tab}
                >
                  {tab}
                </button>
              ))}
            </div>
          </header>
          {consoleView === "Terminal" && (
            <>
              <div className="terminal-head">
                <i />
                <i />
                <i />
                <span>aoa@kali-dt:~/assessments/AOA-RECON-016</span>
                <b>{running ? "● COMMAND RUNNING" : "● NETWORK ISOLATED"}</b>
              </div>
              <div className="console-command">
                <span>SIMULATED COMMAND</span>
                <code>
                  <i>aoa@kali-dt$</i> {consoleStep.command}
                </code>
              </div>
              <pre className="console-output">
                <span>OUTPUT</span>
                {consoleStep.output.map((line, index) => (
                  <code key={index}>
                    <i>{index === 0 ? "┌─" : "│ "}</i>
                    {line}
                  </code>
                ))}
                <code>
                  <i>└─</i>completed · evidence captured
                </code>
              </pre>
              <div className="console-analysis">
                <section>
                  <span>AOA DECISION RATIONALE</span>
                  <p>{consoleStep.rationale}</p>
                </section>
                <section>
                  <span>DIGITAL TWIN STATE UPDATE</span>
                  <p>{consoleStep.state}</p>
                </section>
              </div>
            </>
          )}
          {consoleView === "DT assets" && (
            <div className="console-assets">
              <div className="console-assets-head">
                <b>Alias</b>
                <b>Modelled role</b>
                <b>Zone</b>
                <b>Simulated address</b>
                <b>Status</b>
              </div>
              {TWIN_ASSETS.map((asset, index) => (
                <div key={asset[0]}>
                  <code>{asset[0]}</code>
                  <span>{asset[1]}</span>
                  <span>{asset[2]}</span>
                  <span>{asset[3]}</span>
                  <b
                    className={
                      step >= (index < 2 ? 1 : index < 8 ? 4 : 10)
                        ? "found"
                        : ""
                    }
                  >
                    {step >= (index < 2 ? 1 : index < 8 ? 4 : 10)
                      ? "DISCOVERED"
                      : "PENDING"}
                  </b>
                </div>
              ))}
            </div>
          )}
          {consoleView === "Evidence" && (
            <div className="console-evidence">
              <div>
                <span>COMMAND RECORD</span>
                <b>{complete ? 12 : Math.max(1, step + 1)} / 12</b>
              </div>
              <div>
                <span>STRUCTURED OUTPUT</span>
                <b>XML · JSON · PCAP metadata</b>
              </div>
              <div>
                <span>OBSERVED RELATIONS</span>
                <b>{step >= 11 ? 28 : Math.min(28, step * 3)}</b>
              </div>
              <div>
                <span>INFERRED RELATIONS</span>
                <b>{step >= 11 ? 7 : Math.min(7, Math.floor(step / 2))}</b>
              </div>
              <div>
                <span>INTEGRITY</span>
                <b>SHA-256 evidence chain</b>
              </div>
              <div>
                <span>PHYSICAL COMMANDS</span>
                <b className="blocked">0 · BLOCKED</b>
              </div>
            </div>
          )}
          <div className="tool-rack">
            {[
              "Nmap",
              "Zeek",
              "Metasploit",
              "PROFINET/S7",
              "MQTT",
              "OPC UA",
              "NVD",
            ].map((tool, index) => (
              <span
                className={step >= [3, 1, 8, 6, 7, 7, 9][index] ? "used" : ""}
                key={tool}
              >
                {tool}
                <i>{step >= [3, 1, 8, 6, 7, 7, 9][index] ? "✓" : "○"}</i>
              </span>
            ))}
          </div>
        </article>
        <article className="agent-card recon-timeline">
          <header>
            <div>
              <b>Activity and evidence timeline</b>
              <span>Each result updates the AOA knowledge state</span>
            </div>
            <em>K₁</em>
          </header>
          <div>
            {completed.length === 0 && (
              <p className="recon-empty">
                Start the mission to generate a timestamped activity trace.
              </p>
            )}
            {completed.map((item, index) => (
              <section key={item[3]}>
                <i>{String(index + 1).padStart(2, "0")}</i>
                <p>
                  <span>
                    {item[0]} · {item[1]}
                  </span>
                  <b>{item[3]}</b>
                  <small>{item[7]}</small>
                </p>
                <em>{item[6]}</em>
              </section>
            ))}
          </div>
        </article>
      </div>
      <article className={`agent-card recon-report ${complete ? "ready" : ""}`}>
        <header>
          <div>
            <b>AOA reconnaissance stage report</b>
            <span>
              {complete
                ? "Generated from verified simulated evidence"
                : "Available after all reconnaissance gates complete"}
            </span>
          </div>
          <button
            disabled={!complete}
            onClick={() => onNotify("AOA reconnaissance report exported")}
          >
            Export stage report
          </button>
        </header>
        <div className="report-summary">
          {[
            ["STAGE STATUS", complete ? "COMPLETE" : "IN PROGRESS"],
            ["SCOPE COVERAGE", complete ? "12 / 12" : "—"],
            ["HIGH-CONFIDENCE", complete ? "2 findings" : "—"],
            ["EVIDENCE ITEMS", complete ? "18 verified" : "—"],
            ["NEXT GATE", complete ? "Analyst approval" : "—"],
          ].map((x) => (
            <div key={x[0]}>
              <span>{x[0]}</span>
              <b>{x[1]}</b>
            </div>
          ))}
        </div>
        {complete && (
          <div className="report-body">
            <section>
              <b>Executive assessment</b>
              <p>
                The simulated reconnaissance identified eight reachable hosts,
                eleven services and four OT-relevant surfaces. No exploit was
                executed. Key observations are an insecure OPC UA endpoint
                profile, optional MQTT transport security and an undocumented
                HMI-to-OPC UA relationship.
              </p>
            </section>
            <section>
              <b>Prioritised validation candidates</b>
              <ol>
                <li>
                  <strong>High:</strong> verify whether OPC UA SecurityMode=None
                  exists in deployment.
                </li>
                <li>
                  <strong>High:</strong> validate the HMI–OPC UA trust path.
                </li>
                <li>
                  <strong>Medium:</strong> confirm MQTT TLS and client identity
                  enforcement.
                </li>
                <li>
                  <strong>Low:</strong> verify SSH software version against the
                  asset register.
                </li>
              </ol>
            </section>
            <section>
              <b>Recommended next stage</b>
              <p>
                Proceed to non-destructive vulnerability validation only after
                analyst approval. Preserve the passive baseline, enforce OT-safe
                pacing and prohibit credential attacks, payload delivery and
                controller writes.
              </p>
            </section>
            <section>
              <b>Limitations</b>
              <p>
                Results use behavioural Digital Twin data and synthetic
                fingerprints. They indicate priorities, not confirmed
                physical-factory vulnerabilities.
              </p>
            </section>
          </div>
        )}
      </article>
    </div>
  );
}
