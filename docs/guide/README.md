# Researcher guide source

The root `RESEARCHERS_GUIDE.pdf` is built from `build_researchers_guide.py`. Version 2.1 contains 24 pages, ten experimental workflows, a research agenda and a suitability assessment.

Requirements: Python 3, ReportLab, Pillow and DejaVu Sans/Serif/Mono fonts in `/usr/share/fonts/truetype/dejavu/` (Debian/Ubuntu: `fonts-dejavu-core`).

From the repository root:

```sh
python -m pip install reportlab pillow
python docs/guide/build_researchers_guide.py
```

The script asserts 24 pages and checks vertical overflow. Render and inspect every page after edits. The colour scheme encodes evidence, design, baseline, method, held decisions, evaluation and reporting. The guide describes proposed experiments; dataset files and recorded replay results are unchanged.

Figures A and B are original vector academic diagrams implemented in the builder. Figure A distinguishes the CPS control loop from released research representations; Figure B shows the evidence required for cross-sector validation. No photographs or reproduced article figures are included. NIST OT architecture guidance [12] is cited on page 2, and recent guidance [9-11] on page 3. Related-article details remain in `docs/RELATED_PUBLICATIONS.md`.
