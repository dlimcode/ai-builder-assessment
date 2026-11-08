## Review of c77f470..6f2aadf (five docs-only commits on build/check-citations)

**Outcome:** all four fixes were made as asked, and the `planning/*.md` counts are right (208 references, 85 hold, 23 red, 100 not checked). One number is wrong where it was written: the demo script gives the reviewers'-notes run as 38 red and 28 hold. That was measured before the demo-script edit, and the edit itself turned 7 more citations red. At head the run prints **45 red, 21 hold**.

### Answers to the four questions
1. **Did each fix do what was asked, and only that?** Yes for all four.
   - (1) The README also lists the 8 Nov doc fixes as missing from the log, which is correct.
   - (2) The read-this-first block is in, with all six word meanings.
   - (3) The unit report is marked superseded, with 44 Lows in both places.
   - (4) The demo now uses the line 129 miscite and the four lines that moved. Decisions entry added; STATE updated under the repo rule.
   - Nothing unneeded was added. The one extra claim is "about as long as the build" (README.md:106). It holds: 02:35 to 03:32 is 57 minutes, against 62 for the build.
2. **Are the facts true?** Most check out. Wrong: the demo's reviews-run counts (F1). Incomplete: the list of sessions missing from the log (F2).
3. **Is the read-this-first block right about each file?** Every description matches the file's head. The only slip is the order (F6).
4. **New reds or stale docs?** The `planning/*.md` run has no new red. The reviews run went from 35 to 45 red: 3 from the block, 7 from the demo edit. Stale lines: F3 and F4, plus the notes below.

### F1. High. The demo script's reviews-run numbers are wrong at the commit that wrote them
- **Evidence:** planning/demo-script.md:36 "Measured on 8 Nov: 242 references, 28 hold, 12 line only, 38 red, 164 not checked". The checker prints `242 references: 21 holds, 12 line only, 45 red, 164 not checked`, the same in the export and in the repo at 6f2aadf.
- **Cause:** the reviews quote the old demo script. Seven of those quotes held at 1c6f593. Commit 4689d35 added 4 lines to section 1 and rewrote line 9 and line 12. Now red:
  - unit-review-docs.md:10 `demo-script.md:28` "point at row 3": now at line 32.
  - :13 `:9` "Measured: 89 references hold, 19 red, all real.": not in file.
  - :26 `:16` and `:17`: now at lines 20 and 21.
  - :46 `:23`: now at line 27.
  - :53 `:26`: now at line 30.
  - :101 `:12` "this is the real red moment, so no planted edit is needed": not in file.
- **Check:** 38 + 7 = 45 red and 28 − 7 = 21 hold, exactly.
- **What goes wrong:** the presenter reads "38 red" and the screen shows 45. The account at demo-script.md:38-39 explains only 3 of the new reds. The same goes for planning/decisions.md:336 "(reviewers' notes run: 35 red before, 38 after)": true after 90f74d2, wrong at the commit holding that entry.
- **History:** the same thing happened on 7 Nov (planning/reviews/unit-review-docs.md:9 "its "19 red, all real" is wrong at its own commit").
- **Fix:** re-measure after the last edit to the demo script and name the 7 self-moved quotes.

### F2. Medium. README says only planning work before 01:05 is missing from the log, but planning went on until 01:31
- **Evidence:** README.md:103 "the planning team's work before 01:05 on 7 Nov, the short fix session after the export, and the 8 Nov doc fixes are not in it".
- **What git shows:**
  - The planning session (`Claude-Session: f8171583…`) made d4f6f1c at 01:04, then 4699865 at 01:17 ("record the fence and export test results") and d7ac655 at 01:27 ("settle the settings and demo-red cards").
  - Danish answered the cards in that window: planning/README.md:163 "Answered 7 Nov ~01:10".
  - The dry run ran at 01:31: planning/decisions.md:11 "the dry run ran at 01:31".
  - logs/session.txt starts with the `/build` prompt and a clock reading of 01:33. Its sessions are 023dd6c7 (01:33 to 02:35) and 211afd2c (02:56 onward, not exported).
- **What goes wrong:** a reader looks in the log for the card answers or the fence test and finds neither, though the README implies only work before 01:05 is missing.
- **Note:** "before 01:05" was the owner's own wording, so this needs his call. A suggested wording is "the planning sessions before the build (to 01:31)".

### F3. Low. STATE still says 19 red, although its "Last confirmed" date was moved to 8 Nov
- **Evidence:** planning/STATE.md:21 "Dog-food run on `planning/*.md`: 19 red, all explained in `planning/decisions.md` (01:39 entry)". It has been 23 red since 03:32 on 7 Nov (decisions.md:312), and the demo says 23.
- **What goes wrong:** the unit report now sends readers to STATE, and STATE contradicts the demo.

### F4. Low. README says every commit carries a session id, but the five new commits have none
- **Evidence:** README.md:108 "each commit carries a `Claude-Session:` id". `git show -s` on 90f74d2, 79b2ffe, 1c6f593, 4689d35 and 6f2aadf shows no `Claude-Session:` trailer. All 37 earlier commits have one.
- **What goes wrong:** once these merge, the README's claim is false for anyone who checks.

### F5. Low. One decisions entry has no clock time
- **Evidence:** planning/decisions.md:322 "## 8 Nov, before 11:35 (clock not read)". The format rule at planning/03-plan.md:100 says "time from `date +%H:%M`".
- **Mitigation:** the entry is honest and nothing is made up. Both 8 Nov headings also add a date, which the format does not have. That is reasonable for a new day but differs from it.

### F6. Low. The file list is not quite "in the order they were written"
- **Evidence:** planning/README.md:3 "in the order they were written" puts `finish-sitting.sh` (line 9) before `decisions.md` and `reviews/` (line 10).
- **Git:** finish-sitting.sh was added at 01:46 (ef0fdaa), decisions.md at 01:33 (b0ead5d) and reviews/ at 01:41 (cb5bca6).

### Question
- **"planning about 30 minutes" (README.md:105):** I could not check this. 00-options-considered.md is headed "(6 Nov 2026)". planning/README.md:160 has the lead measuring at "00:56", and the planning session committed until 01:27. Is 30 minutes the 7 Nov team run only? If so, "Time, 7 Nov" covers it, but F2's window is planning time too.

### Notes (not findings)
- **False green:** planning/reviews/unit-review-docs.md:85 cites `planning/README.md:147 "run 01:16"`, which now passes on a different line (a table row). The quoted card-1 line moved to 163. So 4 README quotes moved, not 3. The fourth stays green by chance, which is the cut "also at" note. It would be a good live example for demo point 6.
- **Unit report banner:** planning/unit-report.md:4 says "the report as written before the merge", but the 44 Lows on lines 17 and 84 were edited on 8 Nov.
- **Text that still says one 7 Nov sitting:** README.md:92 "one desk sitting on 7 Nov 2026"; README.md:99 "written during the sitting"; decisions.md:1 "(7 Nov 2026)". The decisions log now has 8 Nov entries.
- **STATE wording:**
  - STATE.md:7 "`.review/` are deleted": `.review/` exists now, but only as this review's export.
  - STATE.md:17 "Not in this sitting: pushing" sits beside a recorded push. Defensible, but may confuse.
- **Facts confirmed:**
  - Times: 01:04 first commit, build 01:33 to 02:35 (log ends "done 2:35 AM"), c77f470 at 03:32, the 8 Nov commits at 11:34 to 11:36.
  - `## Lows` has 44 entries (43 at 224cf86, 44 from ecbf1b3). There are 63 tests (30 + 33) and they pass.
  - `origin/main@{0}: update by push` points at c77f470. Main is c77f470.
  - The miscite is at planning/README.md:129, and the old "line 8" is now line 24.
  - The `scrub.py:221` quote is now found at 238.
  - Every commit has the same single author email. No absolute paths or private text in the diff.

### Coverage
| Source | Compared | Not compared |
|---|---|---|
| the diff | Read in full; every changed line checked below | — |
| README.md | Lines 90-109 checked against git times, session trailers and the log's start and end (F2, F4, notes) | Rest unchanged, read but not re-verified |
| planning/README.md | Block checked against the head of every file it names and the files' add dates (F6); glossary checked against usage; line 129/24 checked; reviews' cites of this file checked old against new | Body unchanged |
| planning/unit-report.md | Banner, 44 Lows (counted), 63 tests (run) | Body beyond the head; historical by design |
| planning/demo-script.md | Both measured lines re-run; old text from `git show 1c6f593` used to trace the 7 self-moved reds (F1) | — |
| planning/decisions.md | Both 8 Nov entries checked against 03-plan §6, commit hashes and times, Lows count, reds (F1, F5) | The first 8 Nov entry's session story: that session's log is not exported |
| planning/STATE.md | Read in full; push via reflog; main vs branch; author email uniformity; backup refs (none) (F3) | Remote not checked (no network); repo rule respected |
| git log times | `%ad` and `%cd` for all 42 commits; Claude-Session trailers per commit | — |
| checker runs | planning: 208/85/0/23/100, the 5 non-golden reds traced. reviews: 242/21/12/45/164, red list traced to its sources. Export and repo give the same results | "35 before" worked out (45 − 3 − 7), not run at c77f470, to avoid writing a second export |
| test run | `unittest discover`: 63 tests, OK | — |

I wrote two checker outputs into the sandbox `$TMPDIR` scratch folder (outside the repo) to read the red lists. Nothing in the repo was changed.
