# Scrubs the exported session log and checks every tracked file and every branch commit message against
# Danish's private word list. Run by Danish after the session ends, never by the agent:
#   bash planning/finish-sitting.sh <private-list>
# The private list must live outside the repo; the two reports stay in a temp folder outside it too.
# Writes logs/session.txt only when the scrub finds no private-list hit. Commits and pushes nothing.
set -euo pipefail

list="${1:-}"
[ -n "$list" ] || { echo "usage: bash planning/finish-sitting.sh <private-list>"; exit 2; }
[ -f "$list" ] || { echo "stop: no private list at $list"; exit 1; }
repo=$(cd "$(dirname "$0")/.." && pwd) || exit 1
list_dir=$(cd "$(dirname "$list")" && pwd) || exit 1
case "$list_dir/" in "$repo"/*) echo "stop: the private list must live outside the repo"; exit 1 ;; esac
cd "$repo"
[ -f logs/raw/session.txt ] || { echo "stop: no logs/raw/session.txt; in the session: /export logs/raw/session.txt"; exit 1; }
git rev-parse --verify -q main >/dev/null || { echo "stop: no main branch to compare commit messages against"; exit 1; }

tmp=$(mktemp -d "${TMPDIR:-/tmp}/scrub.XXXXXX") || exit 1
status=0

python3 scrub.py logs/raw/session.txt logs/session.txt "$list" "$tmp/scrub-report.txt" || status=1

git log --format=%B main..HEAD > "$tmp/commit-messages.txt"
git ls-files -z > "$tmp/files"
set -- "$tmp/commit-messages.txt"
while IFS= read -r -d '' f; do
  [ -f "$f" ] && set -- "$@" "$f"
done < "$tmp/files"
python3 scrub.py --check-only "$list" "$tmp/check-report.txt" "$@" || status=1

echo "scrub report:  $tmp/scrub-report.txt"
echo "check report:  $tmp/check-report.txt"
echo "last lines:    $(tail -1 "$tmp/scrub-report.txt") | $(tail -1 "$tmp/check-report.txt")"
if [ "$status" -eq 0 ]; then
  echo "clean. Read both reports and logs/session.txt in full before committing logs/session.txt."
else
  echo "hits found: fix each by a new commit (nothing is pushed), then run this again."
fi
exit "$status"
