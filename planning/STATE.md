Last confirmed: 2026-11-07

# State: the citation checker sitting

**Where it stands:** the build is done on `build/check-citations` (tasks 0-12): the checker, the scrub, the README,
the demo script, every review saved in `planning/reviews/`, and `planning/unit-report.md`. Not merged, not pushed.

## Waits on Danish
- **Task 13, the log:** in this session `/export logs/raw/session.txt`, then `/exit`; then in a terminal at the
  repo root `bash planning/finish-sitting.sh <private-list>`, read both reports and `logs/session.txt` in full, and commit `logs/session.txt` if clean.
- **Backup refs from the history rewrite:** `refs/original/refs/heads/build/check-citations` and the reflog still
  hold the old commits with the old folder name; deleted only on his word (`refs: delete`).
- **The merge (task 14):** `yes` under `question:` in `planning/build-brief.md`, then start a session from it.
- **His calls listed as cards in `planning/unit-report.md`.**

## Done this sitting
- Tests: 62, all pass; the golden set came before any checker code.
- Dog-food run on `planning/*.md`: 19 red, all explained in `planning/decisions.md` (01:39 entry).
- Known small gaps: `planning/decisions.md`, `## Lows`.
