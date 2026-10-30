#!/usr/bin/env bash
# Tests for .scripts/version.sh and .scripts/release-check.sh on a throwaway git repository.
# Run from anywhere: .scripts/test-release.sh   (needs bash and git; no TeX)
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
cd "$work"
git init -q -b main .
git config user.name test
git config user.email test@example.invalid
git config commit.gpgsign false
git config tag.gpgsign false
mkdir .scripts
cp "$here/version.sh" "$here/release-check.sh" .scripts/

passed=0
failed=0
ok() { passed=$((passed + 1)); }
bad() { echo "FAIL: $*" >&2; failed=$((failed + 1)); }
expect_eq() { if [[ $1 == "$2" ]]; then ok; else bad "$3: got '$1', want '$2'"; fi; }
expect_has() { if [[ $1 == *"$2"* ]]; then ok; else bad "$3: '$2' not in output"; fi; }
check_ok() {
  local out
  if out=$(.scripts/release-check.sh "$1" notes.md 2>&1); then ok; else bad "release-check $1 should pass: $out"; fi
}
check_fails() {
  local out
  if out=$(.scripts/release-check.sh "$1" notes.md 2>&1); then
    bad "release-check $1 should fail"
  else
    expect_has "$out" "$2" "release-check $1 failure reason"
  fi
}
# Commit everything and move the simulated origin/main to it, as a landed pull request would.
land() { git add -A; git commit -q -m "$1"; git update-ref refs/remotes/origin/main HEAD; }

cat > CHANGELOG.md <<'EOF'
# Changelog

## [Unreleased]

## [0.1.0-rc.1] - 2026-10-30
- Candidate.

## [0.0.3] - 2026-10-30
## [0.0.1] - 2026-10-30

### Added
- First.
EOF
echo draft > text.tex
GIT_COMMITTER_DATE='2026-10-30T12:00:00Z' land "first"

# Claim: an untagged commit is a draft, labelled by its abbreviated hash and dated by the commit.
expect_eq "$(.scripts/version.sh)" "$(git describe --always)" "untagged label"
tex=$(.scripts/version.sh --tex)
expect_has "$tex" '\paperreleasefalse' "untagged build is a draft"
expect_has "$tex" '\year=2026 \month=10 \day=30' "title-page date is the commit date"

# Claim: an exact SemVer tag on a clean tree is a release labelled by the bare version.
git tag v0.0.1
expect_eq "$(.scripts/version.sh)" "0.0.1" "release label"
expect_has "$(.scripts/version.sh --tex)" '\paperreleasetrue' "tagged clean build is a release"

# Claim: uncommitted changes to tracked files never produce a release, even at a tag.
echo edited > text.tex
expect_eq "$(.scripts/version.sh)" "0.0.1-dirty" "dirty label"
expect_has "$(.scripts/version.sh --tex)" '\paperreleasefalse' "dirty build is a draft"
git checkout -q -- text.tex

# Claim: release-check accepts a SemVer tag on main with a changelog section and writes that section.
check_ok v0.0.1
expect_eq "$(cat notes.md)" "$(printf '### Added\n- First.')" "release notes of v0.0.1"

# Claims: a commit after a tag is a draft "<tag>-<n>-g<hash>"; a SemVer pre-release tag is a release.
echo second > text.tex
land "second"
described=$(git describe --tags)
expect_eq "$(.scripts/version.sh)" "${described#v}" "label after a tag"
expect_has "$(.scripts/version.sh)" "0.0.1-1-g" "label after a tag names the tag and distance"
git tag v0.1.0-rc.1
expect_eq "$(.scripts/version.sh)" "0.1.0-rc.1" "pre-release label"
check_ok v0.1.0-rc.1
expect_eq "$(cat notes.md)" "- Candidate." "release notes of v0.1.0-rc.1"

# Claim: a tag that is not strict SemVer is never a release, and release-check rejects it.
echo third > text.tex
land "third"
git tag v1.0
expect_has "$(.scripts/version.sh --tex)" '\paperreleasefalse' "non-SemVer tag is a draft"
for t in v1.0 0.0.1 v01.0.0 v1.0.0+build.1 v1.0.0- v1.0.0-01 v1.0.0-rc..1; do
  check_fails "$t" "is not vMAJOR.MINOR.PATCH"
done

# Claim: release-check rejects a missing tag.
check_fails v9.9.9 "does not exist"

# Claim: release-check rejects a tag whose changelog has no section, or only an empty one, for that version.
git tag v0.0.2
check_fails v0.0.2 'no non-empty section "## [0.0.2]"'
git tag v0.0.3
check_fails v0.0.3 'no non-empty section "## [0.0.3]"'
# Claim: a pre-release section does not count for the final version.
git tag v0.1.0
check_fails v0.1.0 'no non-empty section "## [0.1.0]"'

# Claim: the changelog is read at the tagged commit, so adding the section later does not release the tag.
awk '{ print } /^## \[Unreleased\]$/ { print ""; print "## [0.0.2] - 2026-10-31"; print "- Late." }' \
  CHANGELOG.md > CHANGELOG.new
mv CHANGELOG.new CHANGELOG.md
land "late changelog"
check_fails v0.0.2 'no non-empty section "## [0.0.2]"'

# Claim: release-check rejects a tag on a commit that is not on main.
git switch -q -c side
echo side > text.tex
git add -A
git commit -q -m side
git tag v0.2.0
check_fails v0.2.0 "is not on origin/main"
git switch -q main

echo "test-release: $passed passed, $failed failed"
[[ $failed -eq 0 ]]
