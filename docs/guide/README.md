# Researcher guide

The root `RESEARCHERS_GUIDE.pdf` describes critical-infrastructure cybersecurity research with digital twins, AI and knowledge graphs. It covers dataset suitability, research questions, experimental workflows, reference evaluation and evidence interpretation.

The guide traces the research programme to its 2023 shift-left/shift-right paper, the 2024 AI/XAI review and subsequent graph, digital-twin and virtual-twin studies. References are also available in `docs/RELATED_PUBLICATIONS.md`.

## Editable source

`RESEARCHERS_GUIDE.tex` is the main document. `sections.tex`, `research_protocols.tex` and `research_workflows.tex` contain the study protocols and methods. Images are under `images/`.

Build with `bash docs/guide/build.sh` from the repository root. A TeX installation with latexmk and TikZ is required; Ghostscript provides optional PDF optimization. The PDF and source use the same scope and interpretation of evidence.
