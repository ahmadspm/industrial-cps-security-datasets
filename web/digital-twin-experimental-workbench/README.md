# Digital Twin Experimental Workbench

This is smart-factory Digital Twin Experimental Workbench for the [Industrial CPS Security Research Datasets](https://github.com/ahmadspm/industrial-cps-security-datasets).

## Research capabilities

- behavioural and photographic twin monitoring;
- interactive 3D representation of the smart-manufacturing system;
- station-level operations, I/O and diagnostic views;
- finite-state-machine and engineering models;
- cyber-physical network and network-fidelity analysis;
- factory emulation and simulation-science experiments;
- physical-twin security and agentic-AI security assessment; and
- evidence and experiment views.

The application is a research demonstrator. It does not command physical equipment and its simulated values are not safety or security assurance evidence.

## Local use

Requires Node.js 22 or later.

```bash
npm ci
npm run build
npm run dev -- --host 127.0.0.1
```

The production build is written to `github-dist/`. The Vite base path is configured for the `industrial-cps-security-datasets` GitHub Pages site.

## Source provenance

This GitHub version was migrated from version 18 of the Smart Factory Digital Twin Simulator and adapted to a static React/Vite deployment. The application logic, visual components and research views are retained.
