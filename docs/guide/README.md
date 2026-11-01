# Guide source

The root `RESEARCHERS_GUIDE.pdf` is built from `build_researchers_guide.py`.

Requirements: Python 3, ReportLab and DejaVu Sans/DejaVu Sans Mono fonts in `/usr/share/fonts/truetype/dejavu/` (Debian/Ubuntu: `fonts-dejavu-core`).

From the repository root:

```sh
python -m pip install reportlab
python docs/guide/build_researchers_guide.py
```

The script asserts 16 pages and checks vertical overflow. Review rendered pages after edits. The guide describes proposed experiments; the data and recorded replay results are unchanged.
