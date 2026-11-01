#!/usr/bin/env bash
set -euo pipefail
guide_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
guide_build="$(mktemp -d)"
trap 'rm -rf -- "$guide_build"' EXIT
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error \
  -outdir="$guide_build" "$guide_root/RESEARCHERS_GUIDE.tex"
if command -v gs >/dev/null 2>&1; then
  gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.7 -dNOPAUSE -dBATCH -dQUIET \
    -dDetectDuplicateImages=true -dDownsampleColorImages=false \
    -dDownsampleGrayImages=false -dAutoFilterColorImages=false \
    -dColorImageFilter=/DCTEncode -dJPEGQ=92 -dOmitInfoDate=true -dOmitXMP=true \
    -sOutputFile="$guide_root/../../RESEARCHERS_GUIDE.pdf" "$guide_build/RESEARCHERS_GUIDE.pdf"
else
  cp -- "$guide_build/RESEARCHERS_GUIDE.pdf" "$guide_root/../../RESEARCHERS_GUIDE.pdf"
fi
