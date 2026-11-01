# Researcher guide source

The root `RESEARCHERS_GUIDE.pdf` is built from `build_researchers_guide.py`. Version 2.0 contains 24 pages, ten experimental workflows, a research agenda and a suitability assessment.

Requirements: Python 3, ReportLab, Pillow and DejaVu Sans/Serif/Mono fonts in `/usr/share/fonts/truetype/dejavu/` (Debian/Ubuntu: `fonts-dejavu-core`).

From the repository root:

```sh
python -m pip install reportlab pillow
python docs/guide/build_researchers_guide.py
```

The script asserts 24 pages and checks vertical overflow. Render and inspect every page after edits. The colour scheme encodes evidence, design, baseline, method, held decisions, evaluation and reporting. The guide describes proposed experiments; dataset files and recorded replay results are unchanged.

Photographs and their distinct public-domain attribution are documented in [IMAGE_CREDITS.md](IMAGE_CREDITS.md). They illustrate infrastructure and transfer limits; no pictured site is represented as a dataset source or an incident location. Recent guidance [9-11] is linked on guide page 3, and archival source [12] on page 2. Existing related-article details remain in `docs/RELATED_PUBLICATIONS.md`.
