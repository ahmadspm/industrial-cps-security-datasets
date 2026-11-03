# Digital-twin modelling examples

Use native modelling languages to represent the complementary parts of a cyber-physical digital twin. The [tank-and-pump example](tank_pump/README.md) combines physical equations, industrial controller logic, behavioural states and formal communication properties. No Python implementation is required by this example.

**[Launch the Smart Factory Digital Twin Experimental Workbench](https://ahmadspm.github.io/industrial-cps-security-datasets/)** for the repository's broader interactive manufacturing environment. Its [complete React/Vite source](../../web/digital-twin-experimental-workbench/) includes behavioural, 3D, operations, engineering, network, emulator, simulation, cybersecurity, agentic-AI and evidence views.

**[Launch the public browser demonstrator](https://ahmadspm.github.io/research-info/industrial-cps-model-lab/)** to explore the shared policy, adjust parameters, inject telemetry faults, replay all 12 sequential cases and export a trace. It is an educational browser implementation, not a substitute for native compiler, simulation or refinement-tool execution.

| Language | Modelled concern | Example |
|---|---|---|
| Modelica | Physical dynamics and sampled controller interaction | [TankPump.mo](tank_pump/modelica/TankPump.mo) |
| IEC 61131-3 Structured Text | PLC-style control scans and a discrete plant simulator | [TankPump.st](tank_pump/structured_text/TankPump.st) |
| SCXML | Event-driven states, transition priorities and observation-fault handling | [controller.scxml](tank_pump/scxml/controller.scxml) |
| CSP_M | Communicating processes, fault-latch properties, refinement and deadlock checks | [controller.csp](tank_pump/csp/controller.csp) |

The models describe one illustrative process from different perspectives; they are not interchangeable file formats. State and event mappings are explicit in the example documentation. A simulation becomes a testbed-specific digital twin only through separately established identity, synchronization, calibration and validation.

The repository also includes [manufacturing statecharts and a BPMN production process](../../code/twin_reference/digital-twin/Smart-Manufacturing-Behavioural-Digital-Twin/model-driven/). These and the tank example provide different modelled contexts. No physical identity equivalence between them is implied.
