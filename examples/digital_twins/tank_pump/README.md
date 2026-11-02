# Tank-and-pump cyber-physical reference models

This example uses **Modelica, IEC 61131-3 Structured Text, SCXML and CSP_M** to model a shared tank/pump control policy. It is an offline, uncalibrated reference example for digital-twin development. Its parameters and scenarios are illustrative, not measurements of the repository's industrial or water testbeds. There are no hardware addresses, network clients or equipment-write operations.

**[Open the public browser simulation](https://industrial-cps-model-lab.ahmadwaecu.chatgpt.site)** for interactive parameter exploration and a visual replay of the shared 12-case sequential fixture. The web implementation supports teaching and rapid inspection; use the native source files below for tool-specific execution and verification.

## Physical model and assumptions

The Modelica plant represents a constant-area tank:

**A · dh/dt = q_in · u − q_out**

| Parameter | Value | Meaning |
|---|---:|---|
| `A` | 1.0 m² | Tank cross-sectional area |
| `q_in` | 0.05 m³/s | Inflow while the pump is commanded on |
| `q_out` | 0.02 m³/s | Constant outflow |
| Initial `h` | 0.50 m | Physical tank level |
| Low / high thresholds | 0.30 / 0.70 m | Hysteresis switch points |
| High trip | 0.95 m | Latched stop condition |
| Control sample period | 0.1 s | Demonstration sampling; the decision replay uses 1 s |

The model omits head-dependent hydraulics, pump startup transients, saturation, detailed actuator faults and protection hardware. It does not clamp level to conceal an invalid trajectory. Study the configured time horizon and monitor level bounds. `SensorBias` changes a measurement; it is distinct from physical level. `fresh` is a declared experimental condition, not a cryptographic authenticity check.

## Shared controller semantics

Start in **Off** with the fault latch clear. Process one complete observation per control tick in this priority order:

1. A stale observation or measured level **≥ 0.95 m** commands the pump off and latches **Fault**. A simultaneous reset cannot override this condition.
2. A latched fault persists until a **fresh, sub-trip observation with reset**.
3. Otherwise, disabled operation commands **Off**; level **≤ 0.30 m** commands **Filling**; level **≥ 0.70 m** commands **Off**.
4. In the deadband, retain the preceding pump command. A valid reset from Fault in the deadband returns to Off.

The Structured Text controller additionally rejects invalid configurable threshold ordering. SCXML and CSP use the fixed thresholds stated above. All inputs must be finite, correctly typed observations before model execution.

## Native models and execution

### Modelica: physical and sampled hybrid dynamics

[`modelica/TankPump.mo`](modelica/TankPump.mo) contains:

- `Controller`: sampled hysteresis and fault latch.
- `Demonstrator`: continuous tank dynamics, an observation outage from 20–25 s, and a reset pulse at 26–26.2 s.
- `BiasedSensor`: the same demonstration with a +0.25 m measurement bias from 15–18 s.
- `ControllerChecks`: assertions for the twelve shared decision cases.

With OpenModelica installed, run **from `modelica/`**:

```bash
omc run.mos
```

The native `.mos` file checks and simulates the models, producing CSV results. Inspect diagnostics and the simulation result file for each call. An exit code alone is not sufficient because a modelling tool may return diagnostic messages without failing its host process. Inspect the `ControllerChecks` assertions and compare `level`, `measuredLevel`, `controller.pumpOn` and `controller.faultLatched` across demonstrations.

### Structured Text: controller and scan-based plant

Import the function blocks in [`structured_text/TankPump.st`](structured_text/TankPump.st) into an IEC 61131-3 environment such as OpenPLC or CODESYS. Some IDEs require one program organisation unit per imported object; create `TankPumpController` and `TankPumpSimulation` as function blocks, preserving declarations and implementation.

For the decision checks, add [`ControllerChecks.st`](structured_text/ControllerChecks.st) as a program and invoke it once per task scan. After twelve scans, inspect **`Done = TRUE` and `AllPassed = TRUE`**. Reinitialize the program to repeat the test. No process I/O mappings are required.

For physical simulation, call `TankPumpSimulation` once per 0.1 s simulated step. It evaluates the controller at scan start and then advances the plant by forward Euler integration. `MeasuredLevel` is the scan-start value; `Level` is the next-step value. Apply the same time-indexed freshness/reset/bias conditions as the Modelica demonstration when comparing them. Align pre-step/post-step samples and record numerical error; do not assume full numerical equivalence for arbitrary time steps or future nonlinear extensions.

### SCXML: behavioural controller

Load [`scxml/controller.scxml`](scxml/controller.scxml) into a W3C SCXML processor with an ECMAScript datamodel. Validate input data with [`scenarios/tick.schema.json`](scenarios/tick.schema.json), then dispatch the twelve [`tick_events.json`](scenarios/tick_events.json) events in order. These contain the inputs from [`policy_cases.csv`](scenarios/policy_cases.csv). Use `level`, `enabled`, `fresh` and `reset` as event-data fields, and convert CSV values into numbers/booleans before dispatch. Process each event to completion before the next one.

Observe the active state and datamodel values `pumpOn` and `faultLatched` after each event. Document-order transition priority enforces the trip condition before normal hysteresis. This model specifies controller behaviour, not tank differential equations. Use the existing manufacturing SCXML runners only after confirming their supported datamodel and expression semantics; a partial interpreter is not a general SCXML engine.

### CSP_M: communication and formal properties

Open [`csp/controller.csp`](csp/controller.csp) in FDR or use its command-line refinement checker:

```bash
refines controller.csp
```

The file declares a finite-state controller, a safety envelope, a fault-latch specification and a synchronized twelve-case replay. Its assertions express controller deadlock freedom, determinism, trace refinement of the envelope and latch specifications, and deadlock freedom of the replay composition. Inspect each assertion result and any counterexample in the native checker before reporting verification.

The observation channel carries `(band, enabled, fresh, reset)`; the command channel carries the resulting mode. The abstraction is:

| Measured level | CSP band |
|---|---|
| `h ≤ 0.30` | `Low` |
| `0.30 < h < 0.70` | `Mid` |
| `0.70 ≤ h < 0.95` | `High` |
| `h ≥ 0.95` | `Trip` |

CSP events have no physical duration in this model. Passing a finite-state assertion does not establish numerical plant stability, process safety or timed real-system behaviour.

## Shared cases and expected outputs

The twelve rows in [`policy_cases.csv`](scenarios/policy_cases.csv) form a **sequential test**, not twelve independent initial-state tests. They cover low/high threshold equality, deadband memory, disable/enable, stale observation, persistence of the latch, valid reset and reset-versus-trip priority. Native Modelica and ST checks encode the same cases; the CSP replay uses their band abstraction. SCXML consumes the corresponding tick events.

These are newly authored policy expectations. Tool-native compilation, simulation and refinement should be performed with documented tool versions. XML well-formedness, event/target structure and cross-file fixture consistency are different checks from executing the native compilers or proving all properties.

## Cybersecurity research uses

- Compare actual physical level with a biased observation and distinguish cyber-observation effects from physical faults.
- Study command/observation consistency, fault-latch persistence and reset handling.
- Compare statechart conformance with controller-scan outputs on the same event sequence.
- Check whether proposed controller extensions preserve CSP trace properties.
- Generate explicitly labelled synthetic traces from a declared model and injection schedule.

A new controller or AI recommendation must be evaluated against the chosen process constraints, observation assumptions and authority policy. These models are not protective controller designs or equipment-deployment instructions.

## Using this example with the datasets

Inventory and graph tables can supply structural research context only after an explicit mapping is established. This example's tank, pump, units and states are **not** assigned to existing pseudonymous operational signals or manufacturing assets. The original operational records remain without verified signal-unit or attack mappings. Compare derived traces as synthetic model outputs, not as reconstructed physical ground truth.

## Tool references and reuse

[OpenModelica model checking](https://build.openmodelica.org/Documentation/OpenModelica.Scripting.checkModel.html) · [OpenModelica simulation](https://git.openmodelica.org/Documentation/OpenModelica.Scripting.simulate.html) · [Structured Text POUs](https://content.helpme-codesys.com/en/CODESYS%204/_c4_create_a_pou_in_st-2084195.html) · [OpenPLC](https://autonomylogic.com/products/openplc) · [W3C SCXML](https://www.w3.org/TR/scxml/) · [CSP_M assertions](https://cocotec.io/fdr/manual/cspm/definitions.html) · [FDR command line](https://cocotec.io/fdr/manual/command_line.html).

Model source, shared fixtures and this example's documentation are distributed under the included [MIT license](LICENSE). Cite the dataset collection and identify these illustrative models and any modifications used in your experiment. Software tools retain their own licenses.
