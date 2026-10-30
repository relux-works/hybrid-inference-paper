#!/usr/bin/env bash
# SSH authorization tests in isolated repositories, with ephemeral keys outside their trees.
set -euo pipefail

here=$(cd "$(dirname "$0")" && pwd)
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
ssh-keygen -q -t ed25519 -N '' -f "$work/owner"
ssh-keygen -q -t ed25519 -N '' -f "$work/other"
passed=0

fail() { echo "FAIL: $*" >&2; exit 1; }
pin() { printf '%s namespaces="git" %s\n' "$1" "$(cat "$2.pub")"; }
commit() { git add -A; git commit -qm "$1"; }
land() { commit "$1"; git update-ref refs/remotes/origin/main HEAD; }
signed_tag() { git -c user.signingkey="$1" tag -s v1.2.3 -m 'Fixture release'; }
fixture() {
  mkdir "$work/$1"
  cd "$work/$1"
  git init -q -b main
  git config user.name 'Release fixture'
  git config user.email ivan@relux.works
  git config commit.gpgsign false
  git config tag.gpgsign false
  git config gpg.format ssh
  mkdir .github
  pin ivan@relux.works "$work/owner" > .github/allowed_signers
  printf '# Changelog\n\n## [1.2.3] - 2026-10-30\n- Fixture.\n' > CHANGELOG.md
  land baseline
}
accept() {
  local out
  out=$("$here/release-check.sh" v1.2.3 notes.md 2>&1) || fail "$1: $out"
  [[ $out == *'v1.2.3 is releasable'* ]] || fail "$1: missing success message: $out"
  [[ $(cat notes.md) == '- Fixture.' ]] || fail "$1: wrong notes"
  echo "PASS: $1"
  passed=$((passed + 1))
}
reject() {
  local out status
  # No release notes (the input to publication) may be created or replaced on rejection.
  if out=$("$here/release-check.sh" v1.2.3 notes.md 2>&1); then
    fail "$1: unexpectedly accepted"
  else
    status=$?
  fi
  [[ $status == 1 ]] || fail "$1: unexpected exit $status: $out"
  [[ $out == *"release-check: $2"* ]] || fail "$1: wrong failure message: $out"
  [[ ! -e notes.md ]] || fail "$1: rejection created release notes"
  printf 'existing notes\n' > notes.md
  if out=$("$here/release-check.sh" v1.2.3 notes.md 2>&1); then
    fail "$1: unexpectedly accepted on retry"
  else
    status=$?
  fi
  [[ $status == 1 && $out == *"release-check: $2"* ]] || fail "$1: wrong retry failure: $out"
  [[ $(cat notes.md) == 'existing notes' ]] || fail "$1: rejection replaced release notes"
  echo "PASS: $1 (exit $status; $2; notes untouched)"
  passed=$((passed + 1))
}

# Claim: an annotated tag signed by the authorized ephemeral key passes and yields notes.
fixture authorized
signed_tag "$work/owner"
accept authorized

# Claim: an unsigned annotated tag fails cryptographic verification before producing notes.
fixture unsigned
git tag -a v1.2.3 -m unsigned
reject unsigned 'v1.2.3 SSH signature verification failed against origin/main:.github/allowed_signers'

# Claim: a lightweight tag fails the annotation requirement, even on the release branch.
fixture lightweight
git tag v1.2.3
reject lightweight 'v1.2.3 must be an annotated tag'

# Claim: a valid SSH signature made by an unlisted key cannot authorize a release.
fixture other-key
signed_tag "$work/other"
reject other-key 'v1.2.3 SSH signature verification failed against origin/main:.github/allowed_signers'

# Claim: even an authorized signature cannot release a tree with a changed pin;
# a later restoration on main makes the tag an ancestor while keeping main's pin authoritative.
fixture tampered-pin
pin ivan@relux.works "$work/other" > .github/allowed_signers
commit 'tamper pin'
signed_tag "$work/owner"
pin ivan@relux.works "$work/owner" > .github/allowed_signers
land 'restore reviewed pin'
reject tampered-pin 'v1.2.3 allowed_signers differs from the trusted pin on origin/main'

# Claim: a tag cannot authorize its own key via its tree or local git signer-file configuration.
fixture self-authorized
pin ivan@relux.works "$work/other" > .github/allowed_signers
commit 'untrusted pin'
signed_tag "$work/other"
pin ivan@relux.works "$work/owner" > .github/allowed_signers
land 'restore reviewed pin'
git checkout -q v1.2.3
git config gpg.ssh.allowedSignersFile "$PWD/.github/allowed_signers"
reject self-authorized 'v1.2.3 SSH signature verification failed against origin/main:.github/allowed_signers'

# Claim: a cryptographically valid key mapped only to a different principal is rejected.
fixture other-principal
pin other@example.invalid "$work/owner" > .github/allowed_signers
land 'different principal'
signed_tag "$work/owner"
reject other-principal 'v1.2.3 SSH signature principal must be ivan@relux.works'

# Claim: an absent trusted pin fails closed even when the tag tree contains a valid pin.
fixture missing-trusted-pin
signed_tag "$work/owner"
rm .github/allowed_signers
land 'remove trusted pin'
reject missing-trusted-pin 'trusted allowed_signers is missing on origin/main'

# Claim: an empty default-branch pin fails closed without falling back to the tag tree.
fixture empty-trusted-pin
signed_tag "$work/owner"
: > .github/allowed_signers
land 'empty trusted pin'
reject empty-trusted-pin 'trusted allowed_signers is empty on origin/main'

# Claim: the working-tree pin is never used; a valid release still passes with it altered locally.
fixture untrusted-working-tree
signed_tag "$work/owner"
pin ivan@relux.works "$work/other" > .github/allowed_signers
accept untrusted-working-tree

# Claim: a tree omitting the pin cannot be released, even with an authorized signature.
fixture missing-tag-pin
rm .github/allowed_signers
commit 'remove tag pin'
signed_tag "$work/owner"
pin ivan@relux.works "$work/owner" > .github/allowed_signers
land 'restore reviewed pin'
reject missing-tag-pin 'v1.2.3 allowed_signers is missing from the tagged tree'

# Claim: changing signed tag contents invalidates its SSH signature, even for an allowed key.
fixture altered-signature
signed_tag "$work/owner"
git cat-file tag refs/tags/v1.2.3 > "$work/tag-object"
sed 's/Fixture release/Altered release/' "$work/tag-object" > "$work/altered-tag-object"
object=$(git hash-object -t tag -w "$work/altered-tag-object")
git update-ref refs/tags/v1.2.3 "$object"
reject altered-signature 'v1.2.3 SSH signature verification failed against origin/main:.github/allowed_signers'

echo "test-release-signatures: $passed passed, 0 failed"
