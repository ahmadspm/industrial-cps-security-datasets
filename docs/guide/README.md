# Researcher guide - LaTeX source

The root `RESEARCHERS_GUIDE.pdf` is compiled directly from LaTeX. Edition 3.0 contains 25 pages and 14 original TikZ figures. The first three pages establish the CPS, critical-infrastructure, digital-twin and agentic-AI context. No external image assets are required.

## Build

Install TeX Live (including `latexmk`, TikZ/PGF, Latin Modern, `microtype`, `caption`, `fancyhdr`, `fvextra`, `booktabs` and `tabularx`) or an equivalent MiKTeX installation. From the repository root:

```sh
bash docs/guide/build.sh
```

The build uses a temporary directory, performs the required LaTeX passes and copies the compiled PDF to the repository root. It requires neither Python nor ReportLab.

For Overleaf, upload `RESEARCHERS_GUIDE.tex` and `sections.tex` to one project, select `RESEARCHERS_GUIDE.tex` as the main document, and compile with pdfLaTeX.

## Source organization

- `RESEARCHERS_GUIDE.tex`: document class, typography, first three context pages, TikZ styles and source attribution.
- `sections.tex`: research agenda, suitability assessments, study protocols, workflow diagrams, tables, code examples and references.
- `build.sh`: local compilation entry point.

All figures are original vector academic schematics. Source guidance is cited in the text; these are not reproductions of article or magazine figures. The data and recorded replay results are unchanged. The edition was compiled with pdfTeX / TeX Live 2023 and reviewed after rendering every page. Future edits should be checked for LaTeX warnings and rendered layout defects.
