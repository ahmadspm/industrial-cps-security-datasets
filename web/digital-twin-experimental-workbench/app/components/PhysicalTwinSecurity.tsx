"use client";

import { useMemo, useState } from "react";
import ThreatModelDFD from "./ThreatModelDFD";

const VIEWS = [
  "Security posture",
  "Asset exposure",
  "Vulnerability intelligence",
  "Threat model",
  "ATT&CK & campaigns",
  "Threat scenarios",
  "Attack paths",
  "Controls & resilience",
  "Research intelligence",
] as const;

const VULNERABILITIES = [
  {
    id: "CVE-2018-16558",
    category: "Device / firmware",
    component: "SIMATIC S7-1500 CPU",
    weakness:
      "Crafted HTTP(S) packets can cause device denial of service on affected firmware.",
    severity: "High",
    score: "7.5",
    applicability: "Version check required",
    source: "Siemens ProductCERT / NVD",
    action:
      "Record exact CPU order number and firmware; update or restrict TCP 80/443.",
  },
  {
    id: "CVE-2024-3935",
    category: "Network software",
    component: "Eclipse Mosquitto bridge",
    weakness:
      "Crafted bridged topics may trigger a double free and broker crash in affected builds.",
    severity: "High",
    score: "TBC",
    applicability: "Bridge-mode dependent",
    source: "Eclipse Security",
    action:
      "Confirm broker version and bridge configuration; update to a fixed release.",
  },
  {
    id: "CVE-2023-28366",
    category: "Network software",
    component: "Eclipse Mosquitto",
    weakness:
      "Malformed or malicious subscription handling can exhaust broker resources in affected versions.",
    severity: "High",
    score: "TBC",
    applicability: "Version check required",
    source: "Eclipse Mosquitto",
    action:
      "Use a current 2.0.x/2.1.x release; enforce authenticated clients and rate limits.",
  },
  {
    id: "CVE-2021-23980",
    category: "Network software",
    component: "Eclipse Mosquitto 2.0.0–2.0.9",
    weakness:
      "An authenticated MQTT v5 client can trigger a null-pointer crash with malformed protocol data.",
    severity: "High",
    score: "TBC",
    applicability: "Version check required",
    source: "Eclipse Mosquitto",
    action:
      "Update beyond affected releases and monitor malformed client packets.",
  },
  {
    id: "CVE-2019-11779",
    category: "Network software",
    component: "Eclipse Mosquitto ≤1.6.5",
    weakness:
      "A deeply nested SUBSCRIBE topic can cause stack overflow and broker termination.",
    severity: "High",
    score: "7.5",
    applicability: "Legacy-version candidate",
    source: "Eclipse Mosquitto",
    action:
      "Remove legacy broker versions; constrain topic depth and client access.",
  },
  {
    id: "GH-ASYNCUA-1013",
    category: "Software library",
    component: "opcua-asyncio / asyncua",
    weakness:
      "Repository issue reports malformed OPC UA packets causing memory-consuming denial of service.",
    severity: "High",
    score: "Unscored",
    applicability: "Issue verification required",
    source: "FreeOpcUa GitHub",
    action:
      "Pin and test the deployed asyncua version; restrict TCP 4840 and add resource limits.",
  },
  {
    id: "GH-ASYNCUA-1982",
    category: "Software library",
    component: "opcua-asyncio / asyncua",
    weakness:
      "Open issue reports retained subscriptions after CloseSession causing resource accumulation.",
    severity: "Medium",
    score: "Unscored",
    applicability: "Open issue · verify",
    source: "FreeOpcUa GitHub",
    action:
      "Bound sessions/subscriptions; require authentication and monitor resource growth.",
  },
  {
    id: "CFG-OPCUA-001",
    category: "Protocol configuration",
    component: "OPC UA endpoints",
    weakness:
      "SecurityMode=None provides no message security and can permit session hijacking on exposed networks.",
    severity: "Critical",
    score: "Config",
    applicability: "Configuration check required",
    source: "OPC Foundation",
    action:
      "Disable Profile None; use SignAndEncrypt, trusted certificates and role-restricted writes.",
  },
  {
    id: "CFG-MQTT-001",
    category: "Protocol configuration",
    component: "MQTT broker and clients",
    weakness:
      "MQTT does not itself require TLS, authentication or authorization; insecure deployment enables spoofing and eavesdropping.",
    severity: "Critical",
    score: "Config",
    applicability: "Configuration check required",
    source: "OASIS MQTT 5.0",
    action:
      "TLS 1.2+, unique client identities, per-topic ACLs and certificate lifecycle management.",
  },
  {
    id: "CFG-PLC-001",
    category: "Control configuration",
    component: "S7 engineering and web services",
    weakness:
      "Unnecessary reachable engineering/web services enlarge the path to controller availability and program integrity.",
    severity: "High",
    score: "Config",
    applicability: "Exposure check required",
    source: "NIST / Siemens guidance",
    action:
      "Allowlist engineering hosts, disable unused services and monitor program changes.",
  },
  {
    id: "SWC-REPO-001",
    category: "Software supply chain",
    component: "Digital Twin Python runtime",
    weakness:
      "Unpinned or unverified transitive packages prevent reproducible vulnerability and patch assessment.",
    severity: "High",
    score: "Design",
    applicability: "Repository observation",
    source: "Repository assessment",
    action:
      "Add a pinned manifest, SBOM, dependency scanning and controlled update policy.",
  },
  {
    id: "CFG-TWIN-001",
    category: "Application design",
    component: "Twin state reconstruction",
    weakness:
      "Observed, inferred, replayed and simulated state can be confused without enforceable provenance and command authority.",
    severity: "High",
    score: "Design",
    applicability: "Implementation observation",
    source: "Repository assessment",
    action:
      "Sign events; record source/confidence; isolate observation topics from command topics.",
  },
  {
    id: "CVE-2024-6387",
    category: "Gateway / operating system",
    component: "OpenSSH on jump server or gateway",
    weakness:
      "Affected OpenSSH server versions contain a signal-handler race that may permit unauthenticated remote compromise.",
    severity: "Critical",
    score: "8.1",
    applicability: "OS/version check required",
    source: "OpenSSH / NVD",
    action:
      "Inventory OpenSSH builds, patch affected systems, restrict SSH sources and use key-based access.",
  },
  {
    id: "GHSA-gpg6-pmh7-x5f7",
    category: "Enterprise software",
    component: "ERPNext 15.57.5 candidate",
    weakness:
      "Published advisory describes SQL injection in stock-balance processing that may expose database information.",
    severity: "High",
    score: "Unscored",
    applicability: "ERP version check required",
    source: "GitHub Advisory Database",
    action:
      "Confirm ERPNext/Frappe version, update, restrict API roles and monitor unusual report parameters.",
  },
  {
    id: "GHSA-qwh3-h35h-9j9f",
    category: "Enterprise software",
    component: "ERPNext ≤15.103.1 candidate",
    weakness:
      "Server-side template injection may execute attacker-controlled template expressions for permitted template editors.",
    severity: "High",
    score: "Unscored",
    applicability: "Role/version check required",
    source: "GitHub Advisory Database",
    action:
      "Update ERPNext, minimise template-edit permissions and audit server-side rendering actions.",
  },
  {
    id: "CFG-S7-001",
    category: "Industrial protocol",
    component: "S7 engineering channel",
    weakness:
      "Reachable engineering services combined with valid credentials may enable program download, operating-mode changes or control discovery.",
    severity: "Critical",
    score: "Design",
    applicability: "Architecture-mapped",
    source: "MITRE ATT&CK for ICS",
    action:
      "Use dedicated engineering zones, PLC access protection, change monitoring and maintenance windows.",
  },
  {
    id: "CFG-NFC-001",
    category: "Field technology",
    component: "NFC workpiece identity",
    weakness:
      "Unverified tag identity or replay can corrupt workpiece genealogy, routing and inventory state.",
    severity: "Medium",
    score: "Design",
    applicability: "Test required",
    source: "Testbed threat analysis",
    action:
      "Bind tag ID to order state, reject duplicates, timestamp reads and reconcile physical slot evidence.",
  },
  {
    id: "CFG-CAM-001",
    category: "Field technology",
    component: "Camera / PTU sensor station",
    weakness:
      "Unauthorised camera or pan/tilt access can disclose operational activity or suppress the expected monitoring view.",
    severity: "Medium",
    score: "Design",
    applicability: "Exposure check required",
    source: "MITRE Enterprise + ICS mapping",
    action:
      "Isolate the camera, remove defaults, restrict streams and alert on PTU/state divergence.",
  },
] as const;

const CAMPAIGNS = [
  {
    name: "Operation CuckooBees",
    id: "C0012",
    domain: "Enterprise",
    actor: "Winnti / APT41-linked",
    objective: "Manufacturing IP and source-code theft",
    mapped: "ERPNext · research workstation · repositories",
    techniques:
      "T1190 public-facing app · T1133 remote service · discovery · collection",
    relevance: "High",
  },
  {
    name: "Unitronics Defacement",
    id: "C0031",
    domain: "ICS",
    actor: "CyberAv3ngers",
    objective: "Internet-reachable PLC/HMI compromise",
    mapped: "PLC web/engineering interface · HMI",
    techniques: "Default credentials · remote services · controller access",
    relevance: "High",
  },
  {
    name: "TRITON / TEMP.Veles",
    id: "G0088",
    domain: "Enterprise → ICS",
    actor: "XENOTIME",
    objective: "Manipulate industrial safety systems",
    mapped: "Engineering workstation · PLC/interlocks · MPO/VGR safety",
    techniques: "Valid accounts · remote services · program modification",
    relevance: "Critical",
  },
  {
    name: "Sandworm / Industroyer",
    id: "G0034 / S0604",
    domain: "Enterprise → ICS",
    actor: "Sandworm Team",
    objective: "Disrupt industrial control operations",
    mapped: "DMZ · operator services · PLC control paths",
    techniques:
      "Credential access · lateral movement · native ICS protocols · impact",
    relevance: "High",
  },
  {
    name: "Dragonfly",
    id: "G0035",
    domain: "Enterprise",
    actor: "FSB-linked",
    objective: "Espionage against ICS suppliers and critical infrastructure",
    mapped: "Supplier software · workstation · remote access",
    techniques: "Supply chain · spearphishing · drive-by compromise",
    relevance: "High",
  },
  {
    name: "PIPEDREAM / INCONTROLLER",
    id: "ICS malware",
    domain: "ICS",
    actor: "CHERNOVITE",
    objective: "Discover and manipulate multiple industrial controllers",
    mapped: "Engineering services · PLC · OPC UA-adjacent control",
    techniques:
      "Network discovery · controller tasking · parameter manipulation",
    relevance: "High",
  },
  {
    name: "2025 Poland Wiper Attacks",
    id: "C0063",
    domain: "Enterprise + ICS",
    actor: "Russian state-linked",
    objective: "Destroy OT/IT data and disrupt communications",
    mapped: "Firewall · jump host · HMI/gateway · historian",
    techniques:
      "External services · default credentials · data destruction · loss of view/control",
    relevance: "High",
  },
] as const;

const THREAT_REGISTER = [
  {
    id: "TM-01",
    stride: "Spoofing",
    asset: "MQTT publisher identity",
    entry: "OT/DMZ network",
    threat:
      "Rogue client publishes legitimate-looking station state or commands.",
    consequence: "Twin deception or unauthorized station action",
    control: "mTLS identities · topic ACL · command signatures",
    residual: "High",
  },
  {
    id: "TM-02",
    stride: "Tampering",
    asset: "PLC program / OPC UA tags",
    entry: "Engineering or OPC UA conduit",
    threat:
      "Attacker modifies controller logic, setpoints or interlock-relevant values.",
    consequence: "Unsafe VGR/MPO motion or process deviation",
    control: "Write allowlist · program integrity · safety interlocks",
    residual: "Critical",
  },
  {
    id: "TM-03",
    stride: "Repudiation",
    asset: "Commands and operator actions",
    entry: "Supervisory interfaces",
    threat:
      "Actions cannot be reliably attributed across PLC, broker, agent and twin logs.",
    consequence: "Weak investigation and unsafe recovery decisions",
    control: "Synchronized audit trail · identity-bound events",
    residual: "Medium",
  },
  {
    id: "TM-04",
    stride: "Information disclosure",
    asset: "Factory telemetry and topology",
    entry: "MQTT, OPC UA, historian",
    threat:
      "Passive observation reveals tags, routes, workpiece state and high-value assets.",
    consequence: "Improved adversary reconnaissance and targeting",
    control: "Encryption · segmentation · minimum data exposure",
    residual: "Medium",
  },
  {
    id: "TM-05",
    stride: "Denial of service",
    asset: "Broker, OPC UA and PLC services",
    entry: "Reachable protocol endpoints",
    threat:
      "Malformed traffic or flooding prevents control and state synchronization.",
    consequence: "Loss of view/control and production stoppage",
    control: "Rate limits · resource budgets · redundancy · safe state",
    residual: "High",
  },
  {
    id: "TM-06",
    stride: "Elevation of privilege",
    asset: "Engineering and gateway accounts",
    entry: "Workstation, SSH or service account",
    threat:
      "A low-trust identity obtains program, write or administrative authority.",
    consequence: "Persistent cross-zone compromise",
    control: "Least privilege · MFA · privileged access workflow",
    residual: "High",
  },
  {
    id: "TM-07",
    stride: "Tampering",
    asset: "Sensors and I/O image",
    entry: "Field wiring or message path",
    threat: "Colour, position, NFC or light-barrier state is manipulated.",
    consequence: "Invalid FSM transition, collision or mis-sort",
    control: "Plausibility checks · redundant evidence · sequence monitor",
    residual: "High",
  },
  {
    id: "TM-08",
    stride: "Spoofing",
    asset: "Digital Twin source mode",
    entry: "Live/replay/simulation pipelines",
    threat: "Replay or simulated events are accepted as physical observations.",
    consequence: "Operator acts on false factory state",
    control: "Namespace isolation · signed provenance · mode interlock",
    residual: "High",
  },
] as const;

const ASSETS = [
  {
    id: "PLC",
    name: "Siemens S7-1500",
    zone: "Cell/Area",
    criticality: 5,
    exposure: "High",
    protocols: "S7 · OPC UA",
    concern: "Program and parameter integrity",
    image: "assets/fischertechnik-560840-reference.jpg",
  },
  {
    id: "BROKER",
    name: "MQTT Broker",
    zone: "Operations DMZ",
    criticality: 5,
    exposure: "Critical",
    protocols: "MQTT/TCP",
    concern: "Authentication, ACLs and topic integrity",
    image: "assets/fischertechnik-560840-reference.jpg",
  },
  {
    id: "IOT",
    name: "IoT Gateway / TXT",
    zone: "Cell/Area",
    criticality: 4,
    exposure: "High",
    protocols: "MQTT · HTTP",
    concern: "Gateway trust and message provenance",
    image: "assets/station-ssc-official.png",
  },
  {
    id: "VGR",
    name: "Vacuum Gripper Robot",
    zone: "Physical process",
    criticality: 5,
    exposure: "High",
    protocols: "PLC I/O",
    concern: "Motion, vacuum and collision safety",
    image: "assets/station-vgr-official.jpg",
  },
  {
    id: "HBW",
    name: "High-Bay Warehouse",
    zone: "Physical process",
    criticality: 4,
    exposure: "Medium",
    protocols: "PLC I/O",
    concern: "Slot integrity and feeder motion",
    image: "assets/station-hbw-official.jpg",
  },
  {
    id: "MPO",
    name: "Multi-Processing Station",
    zone: "Physical process",
    criticality: 5,
    exposure: "High",
    protocols: "PLC I/O",
    concern: "Oven, saw and interlock integrity",
    image: "assets/station-mpo-official.jpg",
  },
  {
    id: "SLD",
    name: "Sorting Line",
    zone: "Physical process",
    criticality: 3,
    exposure: "Medium",
    protocols: "PLC I/O",
    concern: "Colour sensing and ejector logic",
    image: "assets/station-sld-official.jpg",
  },
  {
    id: "TWIN",
    name: "Digital Twin Runtime",
    zone: "Supervisory",
    criticality: 4,
    exposure: "High",
    protocols: "MQTT · OPC UA",
    concern: "State provenance and command authority",
    image: "assets/station-ssc-official.png",
  },
];

const SCENARIOS = [
  {
    id: "TS-01",
    title: "Broker-to-PLC lateral movement",
    entry: "Misconfigured MQTT broker",
    technique: "Valid accounts · remote services",
    effect: "Unauthorized control path reaches PLC-dependent stations",
    impact: "Loss or manipulation of control",
    severity: "Critical",
    confidence: "Research-evaluated",
    chain: ["Broker", "MES / service", "Safety PLC", "Actuator"],
  },
  {
    id: "TS-02",
    title: "OPC UA control manipulation",
    entry: "Unauthorized or over-privileged client",
    technique: "Unauthorized message · modify parameter",
    effect: "PLC tag or operating parameter is changed",
    impact: "Unsafe VGR/MPO sequence",
    severity: "Critical",
    confidence: "Modelled",
    chain: ["Engineering client", "OPC UA", "PLC", "MPO / VGR"],
  },
  {
    id: "TS-03",
    title: "Engineering workstation compromise",
    entry: "Credential or endpoint compromise",
    technique: "Program download · modify controller tasking",
    effect: "Control logic or project file is altered",
    impact: "Persistent process deviation",
    severity: "High",
    confidence: "Assessment hypothesis",
    chain: ["Workstation", "S7 service", "PLC", "Station I/O"],
  },
  {
    id: "TS-04",
    title: "Twin deception through telemetry",
    entry: "Gateway or MQTT publisher compromise",
    technique: "Adversary-in-the-middle · manipulation of view",
    effect: "False sensor and station states enter the twin",
    impact: "Incorrect monitoring and decisions",
    severity: "High",
    confidence: "Modelled",
    chain: ["IoT gateway", "MQTT", "Twin", "Operator"],
  },
  {
    id: "TS-05",
    title: "Communication disruption",
    entry: "Broker or network denial of service",
    technique: "Block communications · denial of service",
    effect: "Commands, acknowledgements or observations are delayed",
    impact: "State divergence and production halt",
    severity: "High",
    confidence: "Simulation-ready",
    chain: ["Network", "MQTT", "Agents", "Factory cycle"],
  },
  {
    id: "TS-06",
    title: "Sensor-to-actuator process manipulation",
    entry: "Colour, position or light-barrier signal",
    technique: "Manipulate I/O image · spoof reporting message",
    effect: "Invalid state transition or wrong actuator is selected",
    impact: "Mis-sort, collision or quality loss",
    severity: "High",
    confidence: "Assessment hypothesis",
    chain: ["Sensor", "PLC I/O", "Actuator", "Physical output"],
  },
];

const CONTROLS = [
  [
    "Network segmentation",
    "Purdue-aligned IT/DMZ/OT boundaries; explicit conduits",
    72,
  ],
  [
    "Access control & authentication",
    "Certificates, named identities, least privilege and broker ACLs",
    58,
  ],
  [
    "Configuration hardening",
    "Remove defaults, disable unused services and restrict engineering access",
    54,
  ],
  [
    "OT monitoring / IDS",
    "Observe MQTT, OPC UA, S7 and cross-layer behavioural anomalies",
    64,
  ],
  [
    "Patch & vulnerability management",
    "Version inventory, advisory mapping and risk-based maintenance windows",
    46,
  ],
  [
    "Safety-aware response",
    "Fail-safe station states, command validation and recoverable isolation",
    61,
  ],
] as const;

const RISKS = [
  ["Actuator", "PLC", 0.993, 0.484, 0.81],
  ["Broker", "Workstation", 0.886, 0.974, 0.44],
  ["Robot", "Service", 0.878, 0.301, 0.36],
  ["Sensor", "Actuator", 0.852, 0.944, 0.56],
  ["Actuator", "Proxy", 0.851, 0.279, 0.56],
] as const;

function Severity({ value }: { value: string }) {
  return <span className={`sec-severity ${value.toLowerCase()}`}>{value}</span>;
}

export default function PhysicalTwinSecurity({
  onNotify,
}: {
  onNotify: (message: string) => void;
}) {
  const [view, setView] = useState<(typeof VIEWS)[number]>("Security posture");
  const [asset, setAsset] = useState("BROKER");
  const [scenario, setScenario] = useState(0);
  const [controlled, setControlled] = useState(false);
  const [vulnCategory, setVulnCategory] = useState("All");
  const [vulnSelection, setVulnSelection] = useState(0);
  const [threatSelection, setThreatSelection] = useState(0);
  const [campaignSelection, setCampaignSelection] = useState(0);
  const selectedAsset = useMemo(
    () => ASSETS.find((item) => item.id === asset) || ASSETS[0],
    [asset],
  );
  const path = controlled
    ? { name: "Controlled", avg: 5.12, min: 4, max: 5, affected: 7 }
    : { name: "Enriched", avg: 3.84, min: 1, max: 6, affected: 9 };
  const visibleVulnerabilities = VULNERABILITIES.filter(
    (item) => vulnCategory === "All" || item.category === vulnCategory,
  );
  const selectedVulnerability =
    visibleVulnerabilities[vulnSelection] || visibleVulnerabilities[0];

  return (
    <section className="security-workspace">
      <header className="security-commandbar">
        <div>
          <span>PHYSICAL TWIN SECURITY</span>
          <h2>Cyber-physical security posture</h2>
          <p>
            Research-grounded analysis of assets, trust boundaries, attack
            propagation and operational consequences.
          </p>
        </div>
        <div className="security-scope">
          <i />
          <span>ASSESSMENT SCOPE</span>
          <b>Fischertechnik 24V · S7-1500 · MQTT · OPC UA</b>
        </div>
      </header>
      <nav className="security-subnav" aria-label="Security analysis views">
        {VIEWS.map((item) => (
          <button
            key={item}
            className={view === item ? "active" : ""}
            onClick={() => setView(item)}
          >
            {item}
          </button>
        ))}
      </nav>

      {view === "Security posture" && (
        <>
          <div className="security-kpis">
            <article>
              <span>Overall posture</span>
              <strong className="amber">MODERATE–HIGH</strong>
              <small>Research baseline · validation required</small>
            </article>
            <article>
              <span>Crown jewels</span>
              <strong>5</strong>
              <small>PLC · broker · VGR · MPO · twin state</small>
            </article>
            <article>
              <span>Modelled scenarios</span>
              <strong>6</strong>
              <small>IT → OT → physical consequences</small>
            </article>
            <article>
              <span>Priority control gaps</span>
              <strong className="red">4</strong>
              <small>Identity · segmentation · integrity · recovery</small>
            </article>
          </div>
          <div className="security-grid posture-grid">
            <article className="security-card security-architecture">
              <header>
                <div>
                  <b>Security zones and trust boundaries</b>
                  <span>Attack surface mapped to the implemented twin</span>
                </div>
                <em>ZONE MODEL</em>
              </header>
              <div className="zone-stack">
                <section>
                  <label>Enterprise / research services</label>
                  <div>
                    <b>ERPNext</b>
                    <b>Kasm</b>
                    <b>Analyst workstation</b>
                  </div>
                </section>
                <i>
                  <span>Firewall + authenticated conduit</span>
                </i>
                <section className="dmz">
                  <label>Operations DMZ</label>
                  <div>
                    <b className="hot">MQTT Broker</b>
                    <b>Jump service</b>
                    <b>Historian</b>
                  </div>
                </section>
                <i>
                  <span>Protocol allowlist + monitoring</span>
                </i>
                <section className="ot">
                  <label>OT supervisory and control</label>
                  <div>
                    <b>Digital Twin</b>
                    <b>OPC UA</b>
                    <b className="hot">S7-1500 PLC</b>
                    <b>IoT Gateway</b>
                  </div>
                </section>
                <i>
                  <span>Validated I/O and safe-state interlocks</span>
                </i>
                <section className="process">
                  <label>Physical process</label>
                  <div>
                    <b>VGR</b>
                    <b>HBW</b>
                    <b>MPO</b>
                    <b>SLD</b>
                    <b>DPS</b>
                  </div>
                </section>
              </div>
            </article>
            <article className="security-card priority-findings">
              <header>
                <div>
                  <b>Priority assessment findings</b>
                  <span>Confirmed architecture observations vs hypotheses</span>
                </div>
              </header>
              {[
                [
                  "01",
                  "MQTT is a high-betweenness trust point",
                  "Architecture observation",
                  "Critical",
                ],
                [
                  "02",
                  "PLC commands can produce direct physical effects",
                  "Architecture observation",
                  "Critical",
                ],
                [
                  "03",
                  "Observed and inferred twin state need explicit provenance",
                  "Implementation observation",
                  "High",
                ],
                [
                  "04",
                  "Broker ACL and OPC UA role enforcement require verification",
                  "Assessment hypothesis",
                  "High",
                ],
                [
                  "05",
                  "Recovery must preserve station safety and workpiece integrity",
                  "Safety requirement",
                  "High",
                ],
              ].map((f) => (
                <div className="finding" key={f[0]}>
                  <i>{f[0]}</i>
                  <p>
                    <b>{f[1]}</b>
                    <span>{f[2]}</span>
                  </p>
                  <Severity value={f[3]} />
                </div>
              ))}
            </article>
          </div>
        </>
      )}

      {view === "Asset exposure" && (
        <div className="security-grid asset-grid">
          <article className="security-card asset-register">
            <header>
              <div>
                <b>Cyber-physical asset register</b>
                <span>Select an asset to inspect exposure and consequence</span>
              </div>
              <em>{ASSETS.length} ASSETS</em>
            </header>
            <div className="asset-table">
              <div className="asset-row headings">
                <span>Asset</span>
                <span>Zone</span>
                <span>Criticality</span>
                <span>Exposure</span>
              </div>
              {ASSETS.map((item) => (
                <button
                  key={item.id}
                  className={`asset-row ${asset === item.id ? "selected" : ""}`}
                  onClick={() => setAsset(item.id)}
                >
                  <span>
                    <img src={item.image} alt="" />
                    <b>{item.name}</b>
                    <small>{item.id}</small>
                  </span>
                  <span>{item.zone}</span>
                  <span className="critical-dots">
                    {"●".repeat(item.criticality)}
                    {"○".repeat(5 - item.criticality)}
                  </span>
                  <Severity value={item.exposure} />
                </button>
              ))}
            </div>
          </article>
          <article className="security-card asset-inspector">
            <header>
              <div>
                <b>{selectedAsset.name}</b>
                <span>
                  {selectedAsset.id} · {selectedAsset.zone}
                </span>
              </div>
              <Severity value={selectedAsset.exposure} />
            </header>
            <img src={selectedAsset.image} alt={selectedAsset.name} />
            <dl>
              <div>
                <dt>Protocols</dt>
                <dd>{selectedAsset.protocols}</dd>
              </div>
              <div>
                <dt>Security concern</dt>
                <dd>{selectedAsset.concern}</dd>
              </div>
              <div>
                <dt>Potential consequence</dt>
                <dd>
                  Compromise may propagate beyond the digital asset into factory
                  state, control availability or physical operation.
                </dd>
              </div>
            </dl>
            <button
              className="security-action"
              onClick={() =>
                onNotify(`${selectedAsset.name} evidence request added`)
              }
            >
              Request validation evidence
            </button>
          </article>
        </div>
      )}

      {view === "Vulnerability intelligence" && (
        <>
          <div className="vuln-summary">
            <div>
              <span>Intelligence records</span>
              <b>{VULNERABILITIES.length}</b>
              <small>CVEs · advisories · configuration risks</small>
            </div>
            <div>
              <span>Critical configuration risks</span>
              <b className="red">2</b>
              <small>MQTT and OPC UA security profiles</small>
            </div>
            <div>
              <span>Version-dependent candidates</span>
              <b className="amber">7</b>
              <small>Applicability must be verified</small>
            </div>
            <div>
              <span>Repository/design findings</span>
              <b>2</b>
              <small>Supply chain and state provenance</small>
            </div>
          </div>
          <div className="vuln-filterbar">
            {[
              "All",
              ...Array.from(
                new Set(VULNERABILITIES.map((item) => item.category)),
              ),
            ].map((category) => (
              <button
                key={category}
                className={vulnCategory === category ? "active" : ""}
                onClick={() => {
                  setVulnCategory(category);
                  setVulnSelection(0);
                }}
              >
                {category}
              </button>
            ))}
          </div>
          <div className="security-grid vulnerability-grid">
            <article className="security-card vulnerability-register">
              <header>
                <div>
                  <b>Vulnerability and weakness register</b>
                  <span>
                    Candidate applicability — not a claim of confirmed
                    exploitation
                  </span>
                </div>
                <em>{visibleVulnerabilities.length} RECORDS</em>
              </header>
              <div className="vuln-table-head">
                <span>Identifier / component</span>
                <span>Type</span>
                <span>Applicability</span>
                <span>Severity</span>
              </div>
              {visibleVulnerabilities.map((item, index) => (
                <button
                  key={item.id}
                  className={vulnSelection === index ? "selected" : ""}
                  onClick={() => setVulnSelection(index)}
                >
                  <span>
                    <b>{item.id}</b>
                    <small>{item.component}</small>
                  </span>
                  <span>{item.category}</span>
                  <span>{item.applicability}</span>
                  <Severity value={item.severity} />
                </button>
              ))}
            </article>
            {selectedVulnerability && (
              <article className="security-card vulnerability-detail">
                <header>
                  <div>
                    <b>{selectedVulnerability.id}</b>
                    <span>{selectedVulnerability.component}</span>
                  </div>
                  <Severity value={selectedVulnerability.severity} />
                </header>
                <div className="vuln-score">
                  <span>CVSS / classification</span>
                  <b>{selectedVulnerability.score}</b>
                  <small>{selectedVulnerability.applicability}</small>
                </div>
                <dl>
                  <div>
                    <dt>Weakness</dt>
                    <dd>{selectedVulnerability.weakness}</dd>
                  </div>
                  <div>
                    <dt>Evidence source</dt>
                    <dd>{selectedVulnerability.source}</dd>
                  </div>
                  <div>
                    <dt>Recommended action</dt>
                    <dd>{selectedVulnerability.action}</dd>
                  </div>
                </dl>
                <aside>
                  <b>Applicability gate</b>
                  <p>
                    Confirm product identity, exact version, enabled service,
                    reachable network path and compensating controls before
                    changing this record to Confirmed or Not affected.
                  </p>
                </aside>
                <button
                  className="security-action"
                  onClick={() =>
                    onNotify(
                      `${selectedVulnerability.id} verification task created`,
                    )
                  }
                >
                  Create verification task
                </button>
              </article>
            )}
          </div>
        </>
      )}

      {view === "Threat model" && (
        <>
          <div className="threat-model-banner">
            <div>
              <span>MODEL SCOPE</span>
              <b>
                Enterprise services → Operations DMZ → OT control → Physical
                stations
              </b>
            </div>
            <div>
              <span>METHODS</span>
              <b>STRIDE · MITRE ATT&CK for ICS · attack-path reasoning</b>
            </div>
            <div>
              <span>SAFETY OBJECTIVE</span>
              <b>
                Prevent unsafe motion, process manipulation and loss of
                control/view
              </b>
            </div>
          </div>
          <div className="security-grid threat-context-grid">
            <ThreatModelDFD />
            <article className="security-card model-assumptions">
              <header>
                <div>
                  <b>Assets, entry points and assumptions</b>
                  <span>Threat-model completeness checklist</span>
                </div>
              </header>
              <section>
                <b>Crown jewels</b>
                <p>
                  PLC program and safe state · command authority · broker
                  identities/ACLs · twin state provenance · station interlocks ·
                  production evidence
                </p>
              </section>
              <section>
                <b>Primary entry points</b>
                <p>
                  MQTT 1883/8883 · OPC UA 4840 · PLC engineering/S7 · PLC web
                  service · SSH/jump access · enterprise HTTP APIs · removable
                  project files
                </p>
              </section>
              <section>
                <b>Threat actors</b>
                <p>
                  External attacker · compromised researcher endpoint ·
                  malicious/over-privileged insider · compromised supplier
                  component · rogue OT client
                </p>
              </section>
              <section>
                <b>Assumptions to verify</b>
                <p>
                  Lab network isolation · exact firmware/software versions ·
                  broker authentication · OPC UA security mode · PLC write
                  protection · trusted time source · backup recoverability
                </p>
              </section>
              <section>
                <b>Out of scope</b>
                <p>
                  Mechanical failure without cyber cause · production-certified
                  safety assessment · destructive testing against physical
                  hardware · claims of vendor vulnerability without version
                  evidence
                </p>
              </section>
            </article>
          </div>
          <div className="stride-strip">
            {[
              ["S", "Spoofing", 2],
              ["T", "Tampering", 2],
              ["R", "Repudiation", 1],
              ["I", "Disclosure", 1],
              ["D", "Denial of service", 1],
              ["E", "Privilege", 1],
            ].map((item) => (
              <div key={item[0]}>
                <i>{item[0]}</i>
                <span>{item[1]}</span>
                <b>{item[2]} threats</b>
              </div>
            ))}
          </div>
          <div className="security-grid threat-register-grid">
            <article className="security-card threat-register">
              <header>
                <div>
                  <b>System threat register</b>
                  <span>
                    Select a threat to inspect its complete treatment chain
                  </span>
                </div>
                <em>{THREAT_REGISTER.length} THREATS</em>
              </header>
              {THREAT_REGISTER.map((item, index) => (
                <button
                  key={item.id}
                  className={threatSelection === index ? "selected" : ""}
                  onClick={() => setThreatSelection(index)}
                >
                  <i>{item.id}</i>
                  <p>
                    <b>{item.threat}</b>
                    <span>
                      {item.stride} · {item.asset}
                    </span>
                  </p>
                  <Severity value={item.residual} />
                </button>
              ))}
            </article>
            <article className="security-card threat-treatment">
              <header>
                <div>
                  <b>
                    {THREAT_REGISTER[threatSelection].id} ·{" "}
                    {THREAT_REGISTER[threatSelection].stride}
                  </b>
                  <span>{THREAT_REGISTER[threatSelection].asset}</span>
                </div>
                <Severity value={THREAT_REGISTER[threatSelection].residual} />
              </header>
              <div className="threat-chain-detail">
                <div>
                  <span>ENTRY</span>
                  <b>{THREAT_REGISTER[threatSelection].entry}</b>
                </div>
                <i>→</i>
                <div>
                  <span>THREAT EVENT</span>
                  <b>{THREAT_REGISTER[threatSelection].threat}</b>
                </div>
                <i>→</i>
                <div>
                  <span>CONSEQUENCE</span>
                  <b>{THREAT_REGISTER[threatSelection].consequence}</b>
                </div>
              </div>
              <section>
                <span>Required controls</span>
                <b>{THREAT_REGISTER[threatSelection].control}</b>
              </section>
              <section>
                <span>Validation evidence</span>
                <b>
                  Configuration export · packet capture · identity/ACL test ·
                  PLC/twin event correlation · safe-state and recovery result
                </b>
              </section>
              <section>
                <span>Residual-risk decision</span>
                <b>
                  Accept only after version/configuration verification and a
                  controlled simulation or replay-based test.
                </b>
              </section>
              <button
                className="security-action"
                onClick={() =>
                  onNotify(
                    `${THREAT_REGISTER[threatSelection].id} test case added to experiment plan`,
                  )
                }
              >
                Add validation test case
              </button>
            </article>
          </div>
        </>
      )}

      {view === "ATT&CK & campaigns" && (
        <>
          <div className="attack-domain-flow">
            <div>
              <span>ENTERPRISE ATT&CK</span>
              <b>Initial access · credentials · discovery</b>
            </div>
            <i>→</i>
            <div>
              <span>IT / OT CONVERGENCE</span>
              <b>DMZ · jump service · broker · gateway</b>
            </div>
            <i>→</i>
            <div>
              <span>ATT&CK FOR ICS</span>
              <b>Control manipulation · inhibit response</b>
            </div>
            <i>→</i>
            <div className="impact">
              <span>PHYSICAL IMPACT</span>
              <b>Loss of view/control · unsafe process</b>
            </div>
          </div>
          <div className="security-grid campaign-grid">
            <article className="security-card campaign-list">
              <header>
                <div>
                  <b>Relevant threat campaigns and groups</b>
                  <span>
                    Official MITRE ATT&CK intelligence mapped to this testbed
                  </span>
                </div>
                <em>{CAMPAIGNS.length} PROFILES</em>
              </header>
              {CAMPAIGNS.map((item, index) => (
                <button
                  key={item.name}
                  className={campaignSelection === index ? "selected" : ""}
                  onClick={() => setCampaignSelection(index)}
                >
                  <i>{item.id}</i>
                  <p>
                    <b>{item.name}</b>
                    <span>
                      {item.actor} · {item.domain}
                    </span>
                  </p>
                  <Severity value={item.relevance} />
                </button>
              ))}
            </article>
            <article className="security-card campaign-detail">
              <header>
                <div>
                  <b>{CAMPAIGNS[campaignSelection].name}</b>
                  <span>
                    {CAMPAIGNS[campaignSelection].id} ·{" "}
                    {CAMPAIGNS[campaignSelection].actor}
                  </span>
                </div>
                <Severity value={CAMPAIGNS[campaignSelection].relevance} />
              </header>
              <div className="campaign-path">
                <div>
                  <span>OBJECTIVE</span>
                  <b>{CAMPAIGNS[campaignSelection].objective}</b>
                </div>
                <i>→</i>
                <div>
                  <span>TESTBED MAPPING</span>
                  <b>{CAMPAIGNS[campaignSelection].mapped}</b>
                </div>
                <i>→</i>
                <div>
                  <span>SECURITY OUTCOME</span>
                  <b>Detect · contain · preserve safe state</b>
                </div>
              </div>
              <section>
                <span>Observed ATT&CK behaviours</span>
                <b>{CAMPAIGNS[campaignSelection].techniques}</b>
              </section>
              <section>
                <span>Validation focus</span>
                <b>
                  Identity and remote-access evidence · cross-zone traffic ·
                  command provenance · PLC/twin divergence · safe-state response
                </b>
              </section>
              <div className="campaign-caution">
                <b>Threat-informed, not threat-claimed</b>
                <span>
                  These profiles guide defensive emulation and coverage
                  analysis. They do not assert that the testbed has been
                  compromised.
                </span>
              </div>
            </article>
          </div>
          <article className="security-card attack-matrix">
            <header>
              <div>
                <b>Enterprise + ICS technique coverage</b>
                <span>
                  Cross-domain behaviours mapped to smart-factory telemetry and
                  safeguards
                </span>
              </div>
            </header>
            <div className="attack-matrix-row head">
              <b>Tactic</b>
              <b>Enterprise behaviour</b>
              <b>ICS behaviour</b>
              <b>Testbed evidence / safeguard</b>
            </div>
            {[
              [
                "Initial access",
                "T1190 public-facing application",
                "T0822 external remote services",
                "ERP/Kasm/jump logs · firewall allowlist",
              ],
              [
                "Credentials",
                "T1003 credential access",
                "T0859 valid accounts · T1694.001 default credentials",
                "Broker ACL · PLC/gateway identity audit",
              ],
              [
                "Discovery",
                "T1046 network service discovery",
                "T0840 network connection enumeration",
                "Network-flow baseline · scan alert",
              ],
              [
                "Lateral movement",
                "T1021 remote services",
                "T0886 remote services",
                "IT→DMZ→OT conduit correlation",
              ],
              [
                "Collection",
                "T1005 data from local system",
                "T0882 theft of operational information",
                "Topology/tag access · export audit",
              ],
              [
                "Impair process",
                "T1485 data destruction",
                "T0809 data destruction · T0816 device restart",
                "Historian integrity · PLC restart alarm",
              ],
              [
                "Physical impact",
                "T1486 impact / extortion",
                "T0827 loss of control · T0829 loss of view",
                "Independent sensing · interlock · recovery evidence",
              ],
            ].map((row) => (
              <div className="attack-matrix-row" key={row[0]}>
                {row.map((cell) => (
                  <span key={cell}>{cell}</span>
                ))}
              </div>
            ))}
          </article>
        </>
      )}

      {view === "Threat scenarios" && (
        <div className="security-grid scenario-grid">
          <article className="security-card scenario-list">
            <header>
              <div>
                <b>Cyber-physical threat catalogue</b>
                <span>MITRE ATT&CK for ICS aligned</span>
              </div>
              <em>6 SCENARIOS</em>
            </header>
            {SCENARIOS.map((item, index) => (
              <button
                key={item.id}
                className={scenario === index ? "selected" : ""}
                onClick={() => setScenario(index)}
              >
                <i>{item.id}</i>
                <p>
                  <b>{item.title}</b>
                  <span>{item.entry}</span>
                </p>
                <Severity value={item.severity} />
              </button>
            ))}
          </article>
          <article className="security-card scenario-detail">
            <header>
              <div>
                <b>{SCENARIOS[scenario].title}</b>
                <span>{SCENARIOS[scenario].confidence}</span>
              </div>
              <Severity value={SCENARIOS[scenario].severity} />
            </header>
            <div className="attack-chain">
              {SCENARIOS[scenario].chain.map((step, i) => (
                <div key={step}>
                  <span>{i + 1}</span>
                  <b>{step}</b>
                  {i < SCENARIOS[scenario].chain.length - 1 && <i>→</i>}
                </div>
              ))}
            </div>
            <div className="scenario-facts">
              <div>
                <span>Entry condition</span>
                <b>{SCENARIOS[scenario].entry}</b>
              </div>
              <div>
                <span>ATT&CK behaviour</span>
                <b>{SCENARIOS[scenario].technique}</b>
              </div>
              <div>
                <span>Cyber-physical effect</span>
                <b>{SCENARIOS[scenario].effect}</b>
              </div>
              <div>
                <span>Operational impact</span>
                <b>{SCENARIOS[scenario].impact}</b>
              </div>
            </div>
            <div className="scenario-note">
              <b>Safe experiment design</b>
              <span>
                Execute only against the simulated broker, replay data and
                station agents. Record MQTT/OPC UA traffic, PLC/twin state
                divergence, safety interlocks and recovery time.
              </span>
            </div>
          </article>
        </div>
      )}

      {view === "Attack paths" && (
        <>
          <div className="path-toolbar">
            <div>
              <b>BRIDG-ICS propagation experiment</b>
              <span>MQTT Broker → PLC across graph configurations</span>
            </div>
            <div className="segmented">
              <button
                className={!controlled ? "active" : ""}
                onClick={() => setControlled(false)}
              >
                Enriched graph
              </button>
              <button
                className={controlled ? "active" : ""}
                onClick={() => setControlled(true)}
              >
                After controls
              </button>
            </div>
          </div>
          <div className="security-grid path-grid">
            <article className="security-card path-canvas">
              <header>
                <div>
                  <b>{path.name} attack path</b>
                  <span>Shorter routes indicate easier propagation</span>
                </div>
                <Severity value={controlled ? "Medium" : "Critical"} />
              </header>
              <div
                className={`research-path ${controlled ? "controlled" : ""}`}
              >
                <div className="entry">
                  <span>ENTRY</span>
                  <b>MQTT Broker</b>
                </div>
                <i>→</i>
                <div>
                  <span>SERVICE</span>
                  <b>{controlled ? "Blocked conduit" : "MES / Web service"}</b>
                </div>
                <i>→</i>
                <div>
                  <span>CONTROL</span>
                  <b>Safety PLC</b>
                </div>
                <i>→</i>
                <div>
                  <span>IMPACT</span>
                  <b>Actuator / process</b>
                </div>
              </div>
              <div className="path-story">
                {controlled
                  ? "Segmentation isolates the broker from the control route; remaining paths require more hops and reach fewer PLCs."
                  : "Knowledge enrichment exposes latent dependencies, including a one-hop minimum route and broader PLC reachability."}
              </div>
            </article>
            <article className="security-card propagation-metrics">
              <header>
                <div>
                  <b>Measured propagation metrics</b>
                  <span>Published research results</span>
                </div>
              </header>
              {[
                ["Average hops", path.avg, "5.03 baseline"],
                ["Minimum hops", path.min, "4 baseline"],
                ["Maximum hops", path.max, "6 baseline"],
                ["Affected PLCs", path.affected, "8 baseline"],
              ].map((m) => (
                <div key={m[0]}>
                  <span>
                    {m[0]}
                    <small>{m[2]}</small>
                  </span>
                  <b>{m[1]}</b>
                  <i>
                    <em
                      style={{ width: `${Math.min(100, Number(m[1]) * 11)}%` }}
                    />
                  </i>
                </div>
              ))}
            </article>
          </div>
          <article className="security-card risk-links">
            <header>
              <div>
                <b>Highest-risk inter-product relationships</b>
                <span>
                  Risk, exploit probability and attack cost from BRIDG-ICS
                </span>
              </div>
            </header>
            <div className="risk-link-table">
              <div>
                <b>Connection</b>
                <b>Risk</b>
                <b>Exploit probability</b>
                <b>Attack cost</b>
              </div>
              {RISKS.map((r) => (
                <div key={`${r[0]}${r[1]}`}>
                  <span>
                    {r[0]} <i>→</i> {r[1]}
                  </span>
                  <strong>{r[2].toFixed(3)}</strong>
                  <span>{r[3].toFixed(3)}</span>
                  <span>{r[4].toFixed(2)}</span>
                </div>
              ))}
            </div>
          </article>
        </>
      )}

      {view === "Controls & resilience" && (
        <div className="security-grid controls-grid">
          <article className="security-card control-roadmap">
            <header>
              <div>
                <b>Control implementation roadmap</b>
                <span>
                  NIST SP 800-82 · IEC 62443 principles · BRIDG-ICS factors
                </span>
              </div>
            </header>
            {CONTROLS.map((c) => (
              <div className="control-item" key={c[0]}>
                <div>
                  <b>{c[0]}</b>
                  <span>{c[1]}</span>
                </div>
                <strong>{c[2]}%</strong>
                <i>
                  <em style={{ width: `${c[2]}%` }} />
                </i>
              </div>
            ))}
          </article>
          <article className="security-card resilience-plan">
            <header>
              <div>
                <b>Prioritised treatment plan</b>
                <span>Risk reduction without unsafe production disruption</span>
              </div>
            </header>
            {[
              [
                "P0",
                "Broker identities and per-topic ACLs",
                "Prevent anonymous or over-broad publication",
              ],
              [
                "P0",
                "PLC/OPC UA write allowlist",
                "Separate observation from authorised control",
              ],
              [
                "P1",
                "IT/DMZ/OT segmentation",
                "Constrain broker-to-controller lateral movement",
              ],
              [
                "P1",
                "Signed, attributable twin events",
                "Distinguish observed, inferred and simulated state",
              ],
              [
                "P1",
                "Behavioural baselines",
                "Detect timing, sequence and sensor/actuator divergence",
              ],
              [
                "P2",
                "Recovery playbooks",
                "Restore broker, PLC and station state safely",
              ],
            ].map((x) => (
              <div key={x[1]}>
                <i>{x[0]}</i>
                <p>
                  <b>{x[1]}</b>
                  <span>{x[2]}</span>
                </p>
              </div>
            ))}
            <button
              className="security-action"
              onClick={() => onNotify("Control validation plan exported")}
            >
              Export validation plan
            </button>
          </article>
        </div>
      )}

      {view === "Research intelligence" && (
        <div className="security-grid research-grid">
          <article className="security-card reasoning-flow">
            <header>
              <div>
                <b>Explainable threat reasoning pipeline</b>
                <span>BRIDG-ICS + NeuroGraph / GRICS</span>
              </div>
            </header>
            <div className="reasoning-steps">
              {[
                [
                  "1",
                  "Factory context",
                  "Assets · protocols · zones · physical processes",
                ],
                ["2", "Security knowledge", "CVE → CWE → CAPEC → ATT&CK ICS"],
                [
                  "3",
                  "Symbolic retrieval",
                  "Ontology-constrained Cypher traversal",
                ],
                [
                  "4",
                  "Graph evidence",
                  "Multi-hop paths · risk · centrality · controls",
                ],
                [
                  "5",
                  "Grounded explanation",
                  "Answer generated only from retrieved evidence",
                ],
              ].map((x) => (
                <div key={x[0]}>
                  <i>{x[0]}</i>
                  <p>
                    <b>{x[1]}</b>
                    <span>{x[2]}</span>
                  </p>
                </div>
              ))}
            </div>
          </article>
          <article className="security-card evidence-panel">
            <header>
              <div>
                <b>Evidence and assurance</b>
                <span>What an analyst can inspect</span>
              </div>
            </header>
            {[
              "Generated Cypher query",
              "Retrieved nodes and relationships",
              "Source vulnerability and ATT&CK mappings",
              "Attack-path metrics and assumptions",
              "Control-to-risk recalculation",
              "Human-readable grounded explanation",
            ].map((x, i) => (
              <div key={x}>
                <i>{i + 1}</i>
                <b>{x}</b>
                <span>TRACEABLE</span>
              </div>
            ))}
            <aside>
              <b>Research boundary</b>
              <p>
                NeuroGraph is under review and demonstrates explainable
                graph-grounded reasoning. It does not by itself prove that a
                testbed asset is vulnerable; findings still require
                configuration, version and runtime evidence.
              </p>
            </aside>
          </article>
          <article className="security-card source-card">
            <b>Published foundation</b>
            <h3>BRIDG-ICS</h3>
            <p>
              AI-grounded knowledge graphs for intelligent threat analytics in
              Industry 5.0 cyber-physical systems.
            </p>
            <span>Cybersecurity 9, 167 (2026)</span>
          </article>
          <article className="security-card source-card internal">
            <b>Internal research</b>
            <h3>NeuroGraph / GRICS</h3>
            <p>
              Symbolic-first neuro-symbolic retrieval for explainable multi-hop
              cyber threat reasoning.
            </p>
            <span>Manuscript under review · internal use</span>
          </article>
        </div>
      )}
    </section>
  );
}
