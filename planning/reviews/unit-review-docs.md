# Unit-end review of build/check-citations at 68f73d6: what the branch says and what it must not hold

(Commit hashes updated after the 7 Nov history rewrite, on Danish's instruction: old-to-new map in planning/decisions.md.)

**Outcome:** I found nothing private in the branch. There are two Medium findings. First, the demo script adds two reds that nobody explains, so the brief's done-check fails. Second, the README states as done some work that the unit end and the log export have not yet done. There are also seven Lows, two questions and one note.

I reviewed the export of 68f73d6. While I was reviewing, two more commits landed on the branch: 0cb53ca (01:49) and 2aa7047 (01:54). I did not read them, so some of what follows may already be fixed. Citations below are written without backticks so that `check_citations.py` can check this review. I ran it on them before handing back, and every one holds.

### F1. Medium. The demo script adds two reds that nobody explains, and its "19 red, all real" is wrong at its own commit
- **This state:** the code span at planning/demo-script.md:28 "point at row 3" wraps onto the next line. The checker scans for code spans one line at a time, so on line 29 the fixture example `notes.md:3` and the absolute path `/etc/hosts:1` are read as real references.
- **What happens:** `python3 check_citations.py planning/*.md --root .` on the export prints `187 references: 89 holds, 0 line only, 21 red, 77 not checked`.
  - At 08826ec, the commit before the demo script, the same run gave 19 red. So the two new reds come from the demo script's own text.
  - The script says planning/demo-script.md:9 "Measured: 89 references hold, 19 red, all real."
  - **For a reader:** the presenter says "19, all real" while the screen shows 21, and two of those reds come from the script being shown.
  - **For the merge:** the brief requires planning/build-brief.md:64 "every red it shows is explained in" the decisions log, and nothing there covers these two. That done-check fails.
- **The README is also wrong here:** README.md:39 "Anything in backticks, code fences or URLs is skipped" does not hold for a code span that crosses a line break. I confirmed this with a two-line test file: the reference inside the wrapped span was checked ("line only").
- **Fix:**
  - Rejoin the wrapped code span in demo-script.md lines 28-29 onto one line.
  - Add a decisions entry or a Low for wrapped code spans.
  - Scope README line 39 to code spans that sit on one line.
  - Re-measure the demo's numbers.

### F2. Medium. The README states as done what the unit end and the log export have not done yet
At 68f73d6, these claims are false:
- **Task 7's review:** README.md:90 "a fresh reviewer agent read the commits for tasks 2, 4 and 7, and three more read the branch at the" end. At this commit `planning/reviews/` holds only task 2 and task 4 replies. In the working tree, a task-7 review was added later by 2aa7047.
- **The same claim in the demo:** planning/demo-script.md:16 "a fresh reviewer agent on the commits for tasks 2, 4 and 7" and planning/demo-script.md:17 "every reply saved in" `planning/reviews/`.
- **The three unit-end reviewers:** only true once task 11 finishes (planning/README.md:90 "Three fresh reviewers on the branch").
- **README.md:91 "each Medium-or-worse finding has its own" fix commit:**
  - True for the two Medium findings so far: task 2 F1 was fixed by cb5bca6 and task 4 F1 by a95a1be, and both commits carry `Fixes:` trailers.
  - Not known for the task 7 and unit-end findings. See Q1.
- **The log:** README.md:93 "is the session's /export, scrubbed by scrub.py" and README.md:94 "read in full by a person before any" push. There is no `logs/` folder.
  - The fallback in README.md:95, "this line says so instead", contradicts itself: the file is missing, yet the line does not say so.
- **Failure path:** if the branch merges without tasks 11 and 13 and without a re-read of this section, a stranger reads three false statements about review and logs.
- **Fix:** before task 14, re-read this section against `planning/reviews/` and `logs/`. Write the log line as what is actually true at the time: either "is here, scrubbed" or "is not here because …".

### F3. Low. Two decisions entries name no commit hash
- **This state:**
  - planning/decisions.md:68 "Commit: see the scrub commit after this entry" should name ef0fdaa.
  - planning/decisions.md:84 "Commit: the demo script commit after this entry" should name 68f73d6.
- **Why it matters:** 03's format asks for a hash or "none" (planning/03-plan.md:100 "Commit: none"), and task 12 checks exactly this. A reader cannot follow these two entries to a commit.
- **Fix:** task 12 can fill in the hashes.

### F4. Low. "line only" is called green, but the README's table calls it neutral
- **The README's table:** README.md:44 "line only | neutral". The code agrees: colour code 0, not 32.
- **What the demo and log say:**
  - planning/demo-script.md:23 "task 4's review found an unclosed quote coming out green"
  - planning/decisions.md:51 "Task 4's review: an unclosed quote came out green; fixed"
  - commit a95a1be: `(green, exit 0)`
- **Why it matters:** a stranger who has just read the table hears that the bug was "green" and is left unsure which one is right.
- **Fix:** say "passed (line only, exit 0)" instead.

### F5. Low. The demo leaves out 03's "one bug the tests caught"
03 section 4, point 4, lists planning/03-plan.md:80 "one bug the tests caught". The demo's point 4, planning/demo-script.md:26 "Features and bugs (60 s)", has the seven verdicts, row 3, the outside-root path and the reviewers' run, but no bug that the tests caught. The one bug the demo does show (point 3) was caught by a reviewer, not by the tests. The other five points follow 03's order and add up to 4.5 minutes.

### F6. Low. The README's sample output is an unlabelled excerpt with no command
- **This state:** README lines 11-17 show 4 of the 31 output lines, plus README.md:16 "33 references: 10 holds, 1 line only, 20 red, 2 not checked". The lines themselves and the counts match a real run.
- **Why it matters:** the sample does not say which command produced it (`python3 check_citations.py tests/fixtures/report.md --root tests/fixtures`), and the only commands near it produce different output. A stranger cannot reproduce it.
- **Fix:** put the command above the sample and mark it as an excerpt.

### F7. Low. "skipped, not checked" is not true of path:line:col or paths with spaces
README.md:70 "paths with spaces, and URLs (skipped, not checked)". In the code, `path:line:col` and paths with spaces are dropped silently and never added to the "not checked" count. The log's own Lows say this (planning/decisions.md:89 "line:col" counts 0). A reader would expect those references to appear in the "not checked" total, and they do not.

### F8. Low. Absolute temp-folder paths sit in the committed reviews
- **The rule:** planning/build-brief.md:52 "No absolute paths in committed files".
- **This state:** the review replies hold the machine's temp-folder paths (`/tmp/claude-…`, `/private/tmp/…`, `/var` → `/private/var`), including the numeric user id:
  - planning/reviews/task-2-review-1.md:32 "which resolves to"
  - planning/reviews/task-2-recheck-1.md:19 "I ran this: TMPDIR set to"
  - planning/reviews/task-4-review-1.md:15 "A symlinked root"
  - planning/reviews/task-4-review-1.md:74 "so every reference is refused"
- **How much it matters:** there is no username or home folder in them, and the system paths are the subject of those findings. It still breaks the rule as written. `finish-sitting.sh` only checks tracked files against the private list, so it will not catch these.

### F9. Low. "written as it happened" claims more than the log does
- **The README:** README.md:92 "each moment the agent helped, failed or was corrected, written as it happened".
- **The log itself:**
  - It records planning/decisions.md:70 "Three entry times were guessed, not read from the clock". The diff in 08826ec shows 01:40, 01:44 and 01:49 being changed to 01:41, 01:45 and 01:46.
  - The guessed 01:49 was in the future: the entry was first committed at 01:46:37, in ef0fdaa.
  - The 01:41 entry was committed five minutes after its time.
- **How much it matters:** the log owns up to all of this, which is good. The README should be scoped to match, for example: "written during the sitting; three times corrected (see the 01:46 entry)".

### Q1. Question. Is each Medium-or-worse task 7 finding fixed in its own commit?
2aa7047 is titled "close four leaks the task 7 review reproduced", so it is one commit for four findings. If two or more of them are Medium or worse, README line 91 is false. I did not read task-7-review-1.md because it is past the commit under review.

### Q2. Question. Were the dry run's answers already recorded on main?
- The decisions log says the answers never reached the agent: planning/decisions.md:11 "Danish to add the three answers".
- But card 1 records planning/README.md:147 "run 01:16", and main commit 4699865 is titled "record the fence and export test results".
- If those results are in planning/README.md task 0, the entry could point to them. I did not read task 0, which was outside my read list.

### Note. Commit metadata
- Every commit's author and committer is a personal webmail address, with a +0800 timezone. Both become public when the repo does.
- No tracked file or commit message contains an email other than the `Co-Authored-By` trailer.
- Pass 5 of `finish-sitting.sh` checks commit messages but not author fields.
- Keeping the email public is Danish's call. GitHub's noreply address is the usual alternative.

### Checked and fine
- **README headings and first line:** the seven `##` headings match 03 section 5 in order. README.md:3 "Checks that the words an AI report quotes are really on the file line it cites." matches planning/04-devils-advocate.md:35 "words an AI report quotes are really on the file line it cites".
- **Task 8's asks:** all four are in the README. On whole files in memory, README.md:66 "accepted for v1" answers planning/04-devils-advocate.md:48 "Accept for v1 and say so in the README".
- **Verdict table, match rule, exit codes:** the table and the four-line rule match the code. Exit codes are 2 for a folder, a missing report and a bad flag; 1 for a red; 0 for a clean run (all re-run).
- **Tests:** 40 tests ran, OK.
- **Tests before code:** `git log --reverse --format=%s -- tests check_citations.py | head -1` gives the golden-set commit, and 3d59fa7 contains every fixture.
- **Session trailers:** all 14 commits, main's included, carry `Claude-Session:`, as README line 97 says.
- **Card 3 answer (a):** followed. The notes run is red, so no planted edit is used (planning/demo-script.md:12 "this is the real red moment, so no planted edit is needed"). This agrees with planning/README.md:159 "the staged edit only if that is green, said aloud" and planning/README.md:83 "only if both are green".
- **The reviewers' run:** planning/demo-script.md:31 "Measured: 40 references, 0 red, 37 not checked" matches a re-run at 68f73d6. Two review files were added later, so task 12 must re-measure.
- **The demo's quoted entries exist:** the "helped" entry is the 01:39 entry and the "failed, corrected" entry is the 01:45 entry.
- **The 19 reds are explained:** the 18 golden-table reds plus the `build-brief.md:15` miscite are explained at 01:39. planning/decisions.md:28 "Dog-food run on the planning notes: 174 references, 89 hold, 19 red". A re-run at 1e0a07c gives 177 / 89 / 19; the difference is that entry's own references.
- **No invented entries found:**
  - Every hash in the log exists.
  - The undone fixtures commit, planning/decisions.md:19 "Commit: none (18e6421 undone before any push)", is in the reflog: committed 01:36:01, reset 01:36:08.
  - No entry's time comes before the commit it cites, after the corrections.
  - Every entry has all four fields, and `## Lows` is there.
  - The 01:41 "commit guard" entry cannot be checked from git.

### Searches for what must not hold
Every search ran over `git grep 68f73d6` and over the messages of all 11 commits in main..68f73d6.

| Search | Result |
|---|---|
| `/Users/`, `/home/`, `/private/`, `/var/folders`, `/root/`, `C:\Users` | Commit messages: none. Files: the made-up home `/Users/alex` in tests/test_scrub.py, and system temp roots in scrub.py:180 (both needed as scrub patterns and fixtures); the reviews under F8. |
| `~/` | Only generic `~/Documents`, `~/Developer` and `~/.claude` folder names, plus README line 16's elided root. |
| Email pattern | Files: one made-up `@example.com` in tests/test_scrub.py:58. Messages: only `noreply@anthropic.com`. |
| Secret shapes: `sk-`, `ghp_` and `gh[ousr]_`, `AKIA`, `xox`, `AIza`, PEM private-key header, MAC pattern, `key/secret/password/token=`, base64 runs of 40+, JWT `eyJ` | No secrets. The only hits were false positives: "task-" matching `sk-`, and two sums of task minutes (planning/04-devils-advocate.md:53, planning/README.md:106). Fake tokens in test_scrub.py are built at run time. |
| client / employer / customer / company / colleague / staff / "worked at" / "past work" / "previous job" / "my former" | Only rule text: build-brief lines 50-51, and planning/02 lines 134 and 146. |
| Two employer or project names seen in this session's configuration, plus the author's username and webmail domain | Zero hits in files and messages. Not named here, since this review may be committed. |
| Past-work claims in README and demo script | None. |

### Coverage

| Source | Status |
|---|---|
| planning/build-brief.md (files, secrets, logs, done-when) | Compared. "Every red explained" fails (F1); absolute paths (F8); the logs fallback is not yet true (F2). |
| planning/README.md tasks 8, 9, 12 and card 3 | Compared. Task 8's asks are met; each done-check `grep -c` gives 7, 6 and 11; card 3 (a) is followed. |
| planning/03-plan.md sections 4, 5, 6, 8 | Compared. Headings match; the demo misses one item (F5); the log format has two gaps (F3); the three cuts named in the demo are on 03's list. |
| planning/04-devils-advocate.md lines 30-36 and 48 | Compared. The first line and the memory trade-off are both in the README. |
| README.md | Compared. I ran its commands and checked the sample against a real run (F6), the claims against code and git (F2, F7, F9), and the wrapped-span claim by a direct test (F1). |
| planning/demo-script.md | Compared. Every number re-run (F1), order and timing checked (F5), quoted entries found. |
| planning/decisions.md | Compared. Format, times against author and commit times, the reflog, Lows, reds (F3, F9). |
| Commit messages main..68f73d6 | Compared, for grep and for claims (F4 for a95a1be). I did not check "04 F11", which is outside my read list. |
| Every tracked file (must not hold) | Compared by the greps above. Not compared: names that are not on any list I hold; the private word list lives outside the repo and is Danish's check. |
| planning/reviews/ | Read headings and grepped, only to test the README's claims. |
| 0cb53ca and 2aa7047 (after 68f73d6) | Not compared: outside this review's commit. They may change F2 and Q1. |
| planning/README.md task 0 and commit 4699865 | Not compared: outside my read list (Q2). |
