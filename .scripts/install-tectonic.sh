#!/usr/bin/env bash
# Install the pinned tectonic release into a cache directory and print that directory.
# CI adds it to PATH; locally: PATH="$(.scripts/install-tectonic.sh):$PATH" make pdf
# The download is checked against the SHA-256 digest GitHub publishes for the release asset.
set -euo pipefail

version=0.17.0
case "$(uname -s)-$(uname -m)" in
  Linux-x86_64)
    asset=tectonic-$version-x86_64-unknown-linux-musl.tar.gz
    sha256=8533d07f9ccbd7a65824b9e0459041bca34af1eb33daba48f59215593753a3b7 ;;
  Darwin-arm64)
    asset=tectonic-$version-aarch64-apple-darwin.tar.gz
    sha256=a3f1cac7c5678f01661a92212f58480ae3b0634115d880dbc59e2953ded45667 ;;
  *)
    echo "install-tectonic: no pinned tectonic build for $(uname -s)-$(uname -m)" >&2
    exit 1 ;;
esac

dir=${TECTONIC_HOME:-${RUNNER_TOOL_CACHE:-${XDG_CACHE_HOME:-$HOME/.cache}}}/tectonic-$version
if [[ ! -x $dir/tectonic ]]; then
  tmp=$(mktemp -d)
  trap 'rm -rf "$tmp"' EXIT
  curl -fsSL --retry 3 -o "$tmp/$asset" \
    "https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%40$version/$asset"
  if command -v sha256sum >/dev/null; then
    echo "$sha256  $tmp/$asset" | sha256sum -c - >/dev/null
  else
    echo "$sha256  $tmp/$asset" | shasum -a 256 -c - >/dev/null
  fi
  tar -xzf "$tmp/$asset" -C "$tmp"
  mkdir -p "$dir"
  install -m 0755 "$tmp/tectonic" "$dir/tectonic"
fi
"$dir/tectonic" --version >&2
printf '%s\n' "$dir"
