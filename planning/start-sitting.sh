# Starts the attended build sitting in this repo. Run as: bash planning/start-sitting.sh [--dry-run]
# Writes no file. Switches this checkout to the build branch, then starts Claude Code (interactive) with a read fence.
# Every absolute path is built at run time from this file's own location and $HOME; none is written here.
set -euo pipefail

repo=$(cd "$(dirname "$0")/.." && pwd) || exit 1
branch="build/check-citations"; mode="${1:-}"
brief="$repo/planning/build-brief.md"

command -v claude >/dev/null || { echo "stop: claude is not on PATH"; exit 1; }
command -v python3 >/dev/null || { echo "stop: python3 is not on PATH"; exit 1; }
case "$mode" in ""|--dry-run) ;; *) echo "stop: unknown argument $mode (only --dry-run)"; exit 1 ;; esac
[ -f "$brief" ] || { echo "stop: planning/build-brief.md is missing"; exit 1; }
# Secrets stay out of git: .gitignore must already list .env and .env.*
grep -qxF '.env' "$repo/.gitignore" 2>/dev/null || { echo "stop: .gitignore does not list .env"; exit 1; }
grep -qxF '.env.*' "$repo/.gitignore" 2>/dev/null || { echo "stop: .gitignore does not list .env.*"; exit 1; }

# The build recipe works on the brief's branch in this checkout (a worktree beside the repo would sit outside the fence).
git -C "$repo" rev-parse --verify -q main >/dev/null || { echo "stop: main has no commit yet; commit planning/ first"; exit 1; }
current=$(git -C "$repo" branch --show-current)
if [ "$current" != "$branch" ]; then
  if [ -n "$(git -C "$repo" status --porcelain --untracked-files=no)" ]; then
    echo "stop: uncommitted changes on $current; commit them first"; exit 1
  fi
  if git -C "$repo" rev-parse --verify -q "refs/heads/$branch" >/dev/null; then
    git -C "$repo" switch "$branch"
  else
    git -C "$repo" switch -c "$branch" main
  fi
fi

# The read fence (planning/03-plan.md section 7). File tools: no reads outside the repo, and none under ~/Documents.
# Shell: the sandbox denies ~/Documents and ~/Developer, except this repo.
# If Danish's test shows neither rule stops a shell `cat`, keep these settings anyway and follow 03's fallback
# (his own permission mode shows each shell command before it runs; the scrub's private-list check is the backstop).
settings=$(python3 - "$HOME" "$repo" <<'PY'
import json, sys
home, repo = sys.argv[1], sys.argv[2]
print(json.dumps({
    "permissions": {
        "blockReadsOutsideWorkingDirectories": True,
        "deny": ["Read(/" + home + "/Documents/**)"],
    },
    "sandbox": {
        "enabled": True,
        "filesystem": {
            "denyRead": [home + "/Documents", home + "/Developer"],
            "allowRead": [repo],
        },
    },
}))
PY
)

# Task 0 (planning/README.md): the same fence with `/build` and no request; the recipe should stop at once.
if [ "$mode" = "--dry-run" ]; then
  cd "$repo"
  echo "dry run: then ask for a shell cat of a canary file under ~/Documents and one subagent Read of it;"
  echo "expect BLOCKED twice, then /exit"
  exec claude --settings "$settings" "/build"
fi

# The brief is named by its absolute path: the build recipe's merge guard looks for a path starting with "/".
# No list flags are used (--add-dir, --allowedTools, --tools would swallow the prompt typed after them).
cd "$repo"
echo "repo: $repo | branch: $(git branch --show-current)"
exec claude --settings "$settings" "/build Read $brief and follow it."
