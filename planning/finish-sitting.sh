# Scrubs the exported session log and checks every tracked file and every commit (message and diff, main's
# too) against Danish's private word list; hits of the generic entries listed in scrub.py are reported, not failed. Run by Danish after the session ends, never by the agent:
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

tmp=$(mktemp -d "${TMPDIR:-/tmp}/scrub.XXXXXX") || exit 1

export_hit=0; repo_hit=0
python3 scrub.py logs/raw/session.txt logs/session.txt "$list" "$tmp/scrub-report.txt" || export_hit=1

# Every commit's message and diff, main's too (nothing is pushed yet, so all of it goes public): a word a later
# commit removed is still in history. Author lines are left out.
git log -p --format=%B HEAD > "$tmp/branch-history.txt"
git ls-files -z > "$tmp/files"
set -- "$tmp/branch-history.txt"
while IFS= read -r -d '' f; do
  [ -f "$f" ] && set -- "$@" "$f"
done < "$tmp/files"
python3 scrub.py --check-only "$list" "$tmp/check-report.txt" "$@" || repo_hit=1

echo "scrub report:  $tmp/scrub-report.txt"
echo "check report:  $tmp/check-report.txt"
echo "last lines:    $(tail -1 "$tmp/scrub-report.txt") | $(tail -1 "$tmp/check-report.txt")"
if [ "$export_hit" -eq 1 ]; then
  echo "hits in the export: logs/session.txt is not written. The report's line numbers point at"
  echo "$tmp/scrub-report.txt.scrubbed.txt. Take the word out of the export, or say in README.md why there is no log."
fi
if [ "$repo_hit" -eq 1 ]; then
  echo "hits in tracked files or branch history (branch-history.txt): a new commit fixes the files, not history;"
  echo "the branch must be rewritten before any push."
fi
if [ "$export_hit" -eq 0 ] && [ "$repo_hit" -eq 0 ]; then
  echo "clean. Read both reports and logs/session.txt in full before committing logs/session.txt."
  exit 0
fi
exit 1
