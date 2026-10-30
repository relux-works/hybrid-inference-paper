#!/usr/bin/env bash
# Check that a tag may become a GitHub Release, and write its release notes.
#
# Usage: .scripts/release-check.sh vX.Y.Z[-PRERELEASE] [NOTES_FILE]
#
# Passes only when all of these hold:
#   - the tag is Semantic Versioning with a leading "v" and no build metadata;
#   - the tag exists and points at a commit on the release branch (default origin/main);
#   - it is annotated and SSH-signed by ivan@relux.works, using the allowed_signers
#     from that branch, with the same pin in the tagged tree;
#   - CHANGELOG.md at that commit has a non-empty section "## [X.Y.Z]".
# On success the section is written to NOTES_FILE (default build/release-notes.md).
set -euo pipefail

tag=${1:?usage: .scripts/release-check.sh vX.Y.Z[-PRERELEASE] [NOTES_FILE]}
notes_file=${2:-build/release-notes.md}
branch=${RELEASE_BRANCH:-origin/main}
signers_path=.github/allowed_signers
semver='^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)(-((0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*)(\.(0|[1-9][0-9]*|[0-9]*[A-Za-z-][0-9A-Za-z-]*))*))?$'

fail() { echo "release-check: $*" >&2; exit 1; }

[[ $tag =~ $semver ]] || fail "'$tag' is not vMAJOR.MINOR.PATCH[-PRERELEASE] (semver.org, without build metadata)"
version=${tag#v}

commit=$(git rev-parse --verify --quiet "refs/tags/$tag^{commit}") || fail "tag $tag does not exist"
# Resolve once: ancestry and signer policy must come from the same default-branch commit.
branch_commit=$(git rev-parse --verify --quiet "$branch^{commit}") || fail "release branch $branch not found"
git merge-base --is-ancestor "$commit" "$branch_commit" || fail "$tag ($commit) is not on $branch"
tag_object=$(git rev-parse --verify "refs/tags/$tag")
[[ $(git cat-file -t "$tag_object") == tag ]] || fail "$tag must be an annotated tag"

verify_dir=$(mktemp -d)
trap 'rm -rf "$verify_dir"' EXIT
# Never trust the working tree or the tagged tree to authorize its own signer.
git show "$branch_commit:$signers_path" > "$verify_dir/allowed_signers" 2>/dev/null ||
  fail "trusted allowed_signers is missing on $branch"
[[ -s $verify_dir/allowed_signers ]] || fail "trusted allowed_signers is empty on $branch"
if ! verification=$(LC_ALL=C git -c gpg.format=ssh \
  -c gpg.ssh.allowedSignersFile="$verify_dir/allowed_signers" verify-tag "$tag_object" 2>&1); then
  fail "$tag SSH signature verification failed against $branch:$signers_path"
fi
grep -Eq '^Good "git" signature for ivan@relux\.works with ' <<< "$verification" ||
  fail "$tag SSH signature principal must be ivan@relux.works"

# Even an authorized signature must not smuggle a different signer policy into a release.
git show "$commit:$signers_path" > "$verify_dir/tag_allowed_signers" 2>/dev/null ||
  fail "$tag allowed_signers is missing from the tagged tree"
cmp -s "$verify_dir/allowed_signers" "$verify_dir/tag_allowed_signers" ||
  fail "$tag allowed_signers differs from the trusted pin on $branch"

changelog=$(git show "$commit:CHANGELOG.md" 2>/dev/null) || fail "CHANGELOG.md is missing at $commit"
section=$(printf '%s\n' "$changelog" | awk -v head="## [$version]" '
  /^## \[/ { if (on) exit; on = (index($0, head) == 1); next }
  on { print }
' | sed -e '/./,$!d')
[[ -n ${section//[[:space:]]/} ]] || fail "CHANGELOG.md at $commit has no non-empty section \"## [$version]\""

mkdir -p "$(dirname "$notes_file")"
printf '%s\n' "$section" > "$notes_file"
echo "release-check: $tag is releasable (commit $commit on $branch); notes in $notes_file"
