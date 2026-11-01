#!/usr/bin/env bash
set -euo pipefail
guide_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
guide_build="$(mktemp -d)"
trap 'rm -rf -- "$guide_build"' EXIT
latexmk -cd -pdf -interaction=nonstopmode -halt-on-error \
  -outdir="$guide_build" "$guide_root/RESEARCHERS_GUIDE.tex"
cp -- "$guide_build/RESEARCHERS_GUIDE.pdf" "$guide_root/../../RESEARCHERS_GUIDE.pdf"
