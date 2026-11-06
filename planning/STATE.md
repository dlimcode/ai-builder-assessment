Last confirmed: 2026-11-07

# State: the citation checker sitting

**Where it stands:** the build is done on `build/check-citations` (tasks 0-12): the checker, the scrub, the README,
the demo script, every review saved in `planning/reviews/`, and `planning/unit-report.md`. Not merged, not pushed.

## Waits on Danish
- **Task 13, the log:** the sitting's export is in `logs/raw/session.txt` (done). In a terminal at the repo root
  `bash planning/finish-sitting.sh <private-list>`, read both reports and `logs/session.txt` in full, and commit
  `logs/session.txt` if clean. The fix session's own log is not exported.
- **Backup refs:** `refs/original/refs/heads/build/check-citations` (the first rewrite, old folder name),
  `refs/backup/home-path/build/check-citations` (19c672c, the home path),
  `refs/backup/folder-name/refs/heads/build/check-citations` (9beb3d5, the fix commits with a folder name), and the
  reflog; deleted only on his word (`refs: delete`).
- **The merge (task 14):** `yes` under `question:` in `planning/build-brief.md`, then start a session from it.
- **His calls listed as cards in `planning/unit-report.md`.**

## Done this sitting
- Tests: 63, all pass; the golden set came before any checker code.
- Dog-food run on `planning/*.md`: 19 red, all explained in `planning/decisions.md` (01:39 entry).
- Fix session (decisions 02:56, 02:59): the home path left the head commit (now 224cf86); the scrub now
  reports hits wholly inside the build's own text instead of failing the export (2c988d0, then a214578
  and de9333b after its review and recheck: `planning/reviews/fix-2-*.md`). de9333b is not rechecked,
  on his word. A folder name from the sandbox settings left those commits by a rewrite (decisions 03:26).
- Known small gaps: `planning/decisions.md`, `## Lows`.
