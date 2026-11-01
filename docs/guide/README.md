# Researcher guide source

The root `RESEARCHERS_GUIDE.pdf` contains 30 pages and 14 figures. Figures 3-14 were redesigned with the built-in image-generation system. Figure 2 includes a photorealistic AI-generated infrastructure strip representing water, energy and manufacturing; these are illustrative scenes, not photographs of identified facilities or dataset collection sites.

When Ghostscript is installed, the build also optimizes the PDF with JPEG quality 92 and no image downsampling. Original PNG assets remain intact. Without Ghostscript, the larger direct compiler output is retained.

The title and footer omit the typesetting-system label and document date. Publication years and dates in source citations are retained. Creation/modification dates are omitted from PDF metadata.

## Build

Install TeX Live or MiKTeX with `latexmk`, TikZ/PGF, graphicx, Latin Modern, microtype, caption, fancyhdr, fvextra, booktabs and tabularx. From the repository root:

```sh
bash docs/guide/build.sh
```

For Overleaf, upload `RESEARCHERS_GUIDE.tex`, `sections.tex` and the `images` directory, then compile the main document with pdfLaTeX.

## Sources and assets

- `RESEARCHERS_GUIDE.tex`: typography and opening context pages.
- `sections.tex`: research problems, suitability, study protocols, metrics and references.
- `images/figure-03.png` through `images/figure-14.png`: selected image-generation outputs, retained without pixel edits.
- `images/ci-context.png`: generated infrastructure strip.
- `IMAGE_GENERATION_PROMPTS.json`: final prompt set and the shared diagram style; built-in generation mode was used.
- `build.sh`: compilation using a temporary build directory.

Source-image margins are trimmed only in document placement; the original PNG assets remain intact. Icons, topology sketches, curves and extra governance motifs are illustrative and are not new dataset fields, measured results or implemented controls. All study claims remain bounded by the accompanying text. Review generated labels and arrows as well as rendered layout after any revision. The data and recorded replay results are unchanged.

The guide traces the programme to its 2023 shift-left/shift-right paper and connects the 2024 AI/XAI review, later security/privacy chapter and supplied railway paper to the study protocols. Full references and attribution notes are in `docs/RELATED_PUBLICATIONS.md`.
