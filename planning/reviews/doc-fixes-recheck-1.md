## Recheck of ca5e9e2 and 07f3c31 (fixes for doc-fixes-review-1)

**Outcome:** at 07f3c31 every finding is fixed. The demo count, 270 references, 27 hold, 19 line only, 57 red and 167 not checked, matches the checker. The count is wrong at ca5e9e2, the commit that wrote it: there the run prints 31 hold and 53 red. The F5 move also made the unit report's Lows count stale again. There are four Lows and no High or Medium.

### Original findings
| Finding | Status | Evidence |
|---|---|---|
| F1 High | Fixed at 07f3c31; not at ca5e9e2 | planning/demo-script.md:36 "270 references, 27 hold, 19 line only, 57 red, 167 not checked". At 07f3c31 the checker prints `270 references: 27 holds, 19 line only, 57 red, 167 not checked`. At ca5e9e2 it prints `31 holds, 19 line only, 53 red` (new F1). The planning/*.md line (demo-script.md:9 "208 references, 85 hold, 23 red, 100 not checked") matches at both commits. |
| F2 Medium | Fixed | README.md:103 "the planning sessions before the build began at 01:33". d7ac655 is at 01:27 and the dry run at 01:31 (planning/decisions.md:11). logs/session.txt:32 reads "01:33", and b0ead5d is at 01:33. |
| F3 Low | Fixed | planning/STATE.md:21 "23 red, all explained in `planning/decisions.md` (01:39 and 03:32 entries)". The checker prints 23 red. decisions.md:315-318 explains the 4 new ones, and the other 19 are the 01:39 entry's. |
| F4 Low | Fixed | README.md:108-110. I checked all 45 commit messages. Exactly five have no `Claude-Session:`: 90f74d2, 79b2ffe, 1c6f593, 4689d35 and 6f2aadf. |
| F5 Low | Recorded, not fixed (reasonable) | decisions.md:353 "the time was not read when it happened, so none is invented". The move made a 45th Low (new F2). |
| F6 Low | Fixed | planning/README.md:3 "The files here:". The order claim is gone. |
| Banner note | Addressed, now stale on its count | unit-report.md:4 "except the Lows count, fixed to 44 on 8 Nov". `git diff c77f470 07f3c31` changes only the banner and lines 17 and 84, so "only the count changed" is true. But the count is 45 now (new F2). |

### Would the check go red without each fix (state at 6f2aadf)
| Finding | Old text | What 6f2aadf shows |
|---|---|---|
| F1 | demo-script.md:36 "28 hold, 12 line only, 38 red" | Checker prints `242 references: 21 holds, 12 line only, 45 red, 164 not checked`. Red. |
| F2 | README.md:103 "the planning team's work before 01:05" | 4699865 at 01:17 and d7ac655 at 01:27 are planning commits from before the log starts at 01:33. Red. |
| F3 | STATE.md:21 "19 red" | Checker prints 23 red for planning/*.md. Red. |
| F4 | README.md:108 "each commit carries a `Claude-Session:` id" | 90f74d2 to 6f2aadf have none. Red. |
| F6 | planning/README.md:3 "in the order they were written" | finish-sitting.sh (ef0fdaa, 01:46) is listed before decisions.md (b0ead5d, 01:33). Red. |
| Banner | unit-report.md:4 "as written before the merge" | `git diff c77f470 6f2aadf` changed lines 17 and 84. Red. |

### F1. Low. The demo's reviewers'-notes count is wrong at ca5e9e2, the commit that wrote it
- **Evidence:** ca5e9e2 changes planning/demo-script.md:36 to "27 hold, 19 line only, 57 red". At ca5e9e2 the checker prints `270 references: 31 holds, 19 line only, 53 red, 167 not checked`.
- **Why the counts differ:** 07f3c31 adds the other 4 reds. In the saved review, the quotes at doc-fixes-review-1.md lines 31, 41, 45 and 53 go "not in file" when 07f3c31 rewrites README.md:103 and :108, STATE.md:21 and planning/README.md:3.
- **Cause:** all three commits are stamped 11:43:11, so the count was measured with both fixes in place, then split across two commits.
- **What goes wrong:** ca5e9e2's message says "The count is now taken after the last edit and stays put when re-run". That is false at its own commit, for anyone who checks out or bisects to it.
- **Severity:** only the history is wrong; at 07f3c31 the count is right. It is the same kind of slip as the original F1.

### F2. Low. Moving F5 into `## Lows` made the unit report's "44" stale again
- **Evidence:** `## Lows` has 44 entries at 6f2aadf and 45 at ca5e9e2 and 07f3c31.
- **Stale text:** planning/unit-report.md:17 "44 entries under `## Lows` in `planning/decisions.md`" and :84 "44 Lows remain".
- **The banner:** 07f3c31 also wrote planning/unit-report.md:4 "the Lows count, fixed to 44 on 8 Nov".
- **What goes wrong:** a reader counts 45 against the table's present-tense 44, the very mismatch 1c6f593 ("count 44 Lows") fixed.

### F3. Low. The demo's account of the reviewers'-notes reds does not cover 8 "file missing" and 1 "refused"
- **Evidence:** planning/demo-script.md:36-38 "The reds are real: where a fix removed the words … "not in file" …; where a fix moved them, "wrong line, found at"". At 07f3c31 the 57 reds are 26 not in file, 22 wrong line, 8 file missing and 1 refused.
- **Where the 6 new "file missing" come from:** the saved review's bare file names, for example `doc-fixes-review-1.md:41 decisions.md:312 file missing`, `:62 decisions.md:1`, `:64 STATE.md:7`. They are shorthand, not reds made by a fix.
- **What goes wrong:** the presenter calls every red a fix's doing. The screen shows `decisions.md:312 file missing` for a file that exists, and the script has no line for it.
- **Contrast:** for the planning run, the script explains its bare-name reds (demo-script.md:10-11).
- **Precedent:** the log treated unexplained demo reds as a finding before (decisions.md:116 "the demo script made 2 unexplained reds").
- **Partly older:** 2 "file missing" (`notes.md:3`) and the refused one were already there at 6f2aadf. ca5e9e2 rewrote this paragraph after the review added 6 more.

### F4. Low. STATE does not record the review or the two fixes
- **Evidence:** planning/STATE.md:7-8 "On 8 Nov, four doc fixes (decisions 8 Nov 11:35) are on `build/check-citations`, not yet in `main`". 07f3c31 edited STATE (line 21) but did not add the 11:42 work.
- **What goes wrong:** the unit report sends readers to STATE. STATE does not say that a review found a High, that 4bc5419, ca5e9e2 and 07f3c31 are also on the branch, or that the fixes await this recheck. This breaks the repo rule that STATE is updated when state changes.

### Notes (not findings)
- **README.md:108 "each commit from the build on":** this under-claims rather than misstates.
  - The planning commits d4f6f1c, 4699865 and d7ac655 also carry `Claude-Session: f8171583…` in their message.
  - Git's trailer parser misses those, because a blank line sits before `Co-Authored-By`. So the wording is defensible.
- **decisions.md:350 "Commit: the commits after this entry":** the entry sits in ca5e9e2, which is itself one of the fixes. Earlier entries say "the commit holding this entry".
- **decisions.md:345:** it puts "planning before 01:05" in quote marks, but those were never the README's words. The old line said "the planning team's work before 01:05".
- **decisions.md:336:** the "corrected at 11:42" text was added to an earlier entry and left as one over-long line. Correcting older entries has precedent (the 01:46 entry).
- **F4's `Fixes:` trailer:** it names 79b2ffe. The line was written in 08826ec and became false at 90f74d2.
- **Still open from the review:**
  - The question on README.md:105 "planning about 30 minutes".
  - README.md:92 "one desk sitting on 7 Nov 2026", and decisions.md:1 "(7 Nov 2026)".
  - STATE.md:7 "`.review/` are deleted": `.review/` exists again, as this export.
  - The false green at unit-review-docs.md:85.

### Question 4: the decisions entries
- **Format:** the 11:42 entry has all four fields from planning/03-plan.md section 6. Its heading keeps the "8 Nov" date prefix that the review's F5 mitigation already noted. The F5 entry under `## Lows` follows the other Lows' shape, but it was put first rather than last.
- **Time:** 11:42 falls between 6f2aadf (11:36:31) and ca5e9e2 (11:43:11), so it is not ruled out. I could not confirm it was read from the clock, because that session's log is not exported.

### Coverage
| Source | Compared | Found / not compared |
|---|---|---|
| fixes.patch | Byte-compared with `git diff 4bc5419 07f3c31` (reviews excluded): same. The export also matches `git archive 07f3c31`. Every line read. | Notes, new F2 |
| The review | All of F1-F6, the question and the notes, each traced to a fix | — |
| README.md | Lines 88-110 checked against git times, the session id in all 45 commits, the log start and blame | F2 and F4 fixed; trailer note |
| planning/demo-script.md | Lines 1-49 read. Line 9 and line 36 re-run at ca5e9e2 and 07f3c31. Both examples on lines 37-38 checked in the output | New F1, F3 |
| planning/decisions.md | Headings, lines 300-360, the 03-plan section 6 format, Lows counted at three commits, times against commit seconds | New F2; notes; the clock reading itself not compared (log not exported) |
| planning/STATE.md | Lines 1-28 read; line 21 checked against the checker and the 01:39 and 03:32 entries | F3 fixed; new F4 |
| planning/README.md | Lines 1-25; the file list checked against `ls planning/` and add dates | F6 fixed. Body not re-read (unchanged) |
| planning/unit-report.md | `git diff c77f470 07f3c31`; the Lows count | New F2. Body not re-read (historical) |
| git log | `%ad` for all commits, seconds for the last 4, trailers and message bodies for all 45, blame of the fixed lines | — |
| Checker at ca5e9e2 and 07f3c31 | Both runs at both commits, plus 6f2aadf, 4bc5419 and c77f470 (35 red, confirming "35 before"). Red lists diffed step by step: 35, then 45, then 51 (+6 file missing), then 53 (+2), then 57 (+4) | New F1, F3. Exports to `$TMPDIR` scratch, removed after |
| Test run | `unittest discover` in the export: 63 tests, OK | — |

Nothing tracked in the repo was changed. The test run in the export leaves `__pycache__/` folders inside the gitignored `.review/07f3c31/`, as the brief allowed.
