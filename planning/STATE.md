Last confirmed: 2026-11-07

# State: the citation checker sitting

**Where it stands:** built, scrubbed and merged into `main` (fast-forward, local) on Danish's yes, 7 Nov. Not pushed,
not public. `logs/session.txt` is committed; the three backup refs and `.review/` are deleted.

## Waits on Danish
- **Card 4, the author email:** every commit carries his webmail address; keep it, or rewrite to the noreply address
  (every commit, main's too) before any push.
- **The reflog:** it still points at the old commits that held the home path and the folder names; local only, gone
  after `git reflog expire --expire=now --all && git gc --prune=now`, on his word.
- **Not in this sitting:** pushing, making the repo public, recording the demo.

## Done this sitting
- Tests: 63, all pass; the golden set came before any checker code.
- Dog-food run on `planning/*.md`: 19 red, all explained in `planning/decisions.md` (01:39 entry).
- Fix session (decisions 02:56, 02:59): the home path left the head commit (now 224cf86); the scrub now
  reports hits wholly inside the build's own text instead of failing the export (2c988d0, then a214578
  and de9333b after its review and recheck: `planning/reviews/fix-2-*.md`). de9333b is not rechecked,
  on his word. A folder name from the sandbox settings left those commits by a rewrite (decisions 03:26).
- Task 13: Danish ran finish-sitting.sh, read and accepted its remaining hits; it still exits 1 on them
  (decisions 03:30, README weakest part). Task 14: merged.
- Known small gaps: `planning/decisions.md`, `## Lows`.
