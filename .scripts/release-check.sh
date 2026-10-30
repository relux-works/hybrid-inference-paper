#!/usr/bin/env bash
# Check that a tag may become a GitHub Release, and write its release notes.
#
# Usage: .scripts/release-check.sh vX.Y.Z[-PRERELEASE] [NOTES_FILE]
#
# Passes only when all of these hold:
#   - the tag is Semantic Versioning with a leading "v" and no build metadata;
#   - the tag exists and points at a commit on the release branch (default origin/main);
#   - CHANGELOG.md at that commit has a non-empty section "## [X.Y.Z]".
# On success the section is written to NOTES_FILE (default build/release-notes.md).
set -euo pipefail

tag=${1:?usage: .scripts/release-check.sh vX.Y.Z[-PRERELEASE] [NOTES_FILE]}
notes_file=${2:-build/release-notes.md}
branch=${RELEASE_BRANCH:-origin/main}
semver='^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-((0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)(\.(0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?$'

fail() { echo "release-check: $*" >&2; exit 1; }

[[ $tag =~ $semver ]] || fail "'$tag' is not vMAJOR.MINOR.PATCH[-PRERELEASE] (semver.org, without build metadata)"
version=${tag#v}

commit=$(git rev-parse --verify --quiet "refs/tags/$tag^{commit}") || fail "tag $tag does not exist"
git rev-parse --verify --quiet "$branch^{commit}" >/dev/null || fail "release branch $branch not found"
git merge-base --is-ancestor "$commit" "$branch" || fail "$tag ($commit) is not on $branch"

changelog=$(git show "$commit:CHANGELOG.md" 2>/dev/null) || fail "CHANGELOG.md is missing at $commit"
section=$(printf '%s\n' "$changelog" | awk -v head="## [$version]" '
  /^## \[/ { if (on) exit; on = (index($0, head) == 1); next }
  on { print }
' | sed -e '/./,$!d')
[[ -n ${section//[[:space:]]/} ]] || fail "CHANGELOG.md at $commit has no non-empty section \"## [$version]\""

mkdir -p "$(dirname "$notes_file")"
printf '%s\n' "$section" > "$notes_file"
echo "release-check: $tag is releasable (commit $commit on $branch); notes in $notes_file"
