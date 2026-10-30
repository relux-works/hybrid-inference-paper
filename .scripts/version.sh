#!/usr/bin/env bash
# Print the paper version label; with --tex, print the LaTeX file paper/version.tex instead.
#
# A clean checkout exactly at a release tag vX.Y.Z[-PRERELEASE] is a release: label "X.Y.Z".
# Anything else is a draft labelled by `git describe`, for example "0.1.0-3-g1a2b3c4" or
# "1a2b3c4-dirty". The date is the commit date, so rebuilding a tag reproduces its title page.
set -euo pipefail

semver='^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-((0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)(\.(0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?$'

release=false
commit=unknown
date=$(date -u +%Y-%m-%d)
label=unknown
if git rev-parse --verify --quiet HEAD >/dev/null 2>&1; then
  commit=$(git rev-parse --short=12 HEAD)
  date=$(git log -1 --format=%cs HEAD)
  tag=$(git describe --exact-match --tags --match 'v[0-9]*' HEAD 2>/dev/null || true)
  if [[ $tag =~ $semver ]] && git diff --quiet HEAD --; then
    release=true
    label=${tag#v}
  else
    label=$(git describe --tags --match 'v[0-9]*' --always --dirty)
    label=${label#v}
  fi
fi

if [[ ${1:-} != --tex ]]; then
  printf '%s\n' "$label"
  exit 0
fi

year=${date%%-*}
month=${date#*-}; month=${month%-*}
day=${date##*-}
cat <<EOF
% Written by .scripts/version.sh during \`make pdf\`; not tracked by git.
\\newcommand{\\paperversion}{$label}
\\newcommand{\\papercommit}{$commit}
\\newif\\ifpaperrelease
\\paperrelease$release
\\year=$year \\month=$((10#$month)) \\day=$((10#$day))
EOF
