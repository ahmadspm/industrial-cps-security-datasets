"use client";

import { useState } from "react";

export default function SimulationScience({
  compact = false,
}: {
  compact?: boolean;
}) {
  const [method, setMethod] = useState("Discrete-event agents");
  return (
    <section className={`simulation-science ${compact ? "compact" : ""}`}>
      <header>
        <div>
          <span>MODEL CREDIBILITY &amp; EXPERIMENT DESIGN</span>
          <h3>Evidence-based Digital Twin simulation</h3>
          <p>
            Repeatable scenarios, explicit assumptions and validation against
            physical observations.
          </p>
        </div>
        <strong>
          VVUQ <b>96.8%</b>
        </strong>
      </header>
      <div className="science-grid">
        <label>
          Method
          <select value={method} onChange={(e) => setMethod(e.target.value)}>
            <option>Discrete-event agents</option>
            <option>Deterministic replay</option>
            <option>Hybrid station model</option>
          </select>
        </label>
        <label>
          Random seed
          <input value="240826" readOnly />
        </label>
        <label>
          Replications
          <input value="30" readOnly />
        </label>
        <label>
          Warm-up
          <input value="1 cycle" readOnly />
        </label>
        <div>
          <span>Verification</span>
          <b>Transitions 100%</b>
          <em>Model implemented correctly</em>
        </div>
        <div>
          <span>Validation</span>
          <b>Timing error 3.2%</b>
          <em>Compared with reference cycle</em>
        </div>
        <div>
          <span>Uncertainty</span>
          <b>95% interval</b>
          <em>Replicated stochastic runs</em>
        </div>
        <div>
          <span>Traceability</span>
          <b>Run ID + seed</b>
          <em>Events, snapshots and outputs</em>
        </div>
      </div>
    </section>
  );
}
