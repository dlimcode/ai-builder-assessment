# Decisions log: the build sitting (7 Nov 2026)

One entry per real moment the agent helped, failed or was corrected, written as it happens
(format: `planning/03-plan.md` section 6). Times from `date +%H:%M`.

## 01:33 Task 0: the dry run's three answers were not passed to this session
- Agent did: started from `/build` with the brief; `/build` loaded (its text is in this session). The session's own
  sandbox settings list `~/Documents` and `~/Developer` as read-denied for the shell, with this repo allowed.
- Helped / failed: unknown; the dry run (recipe stops at once, shell canary `cat`, subagent canary Read) ran in
  Danish's terminal before this session, and its three answers were not given to the agent. Not invented here.
- Corrected by: Danish, at 02:15: the dry run ran at 01:31. `/build` loaded under the fence; a shell `cat` of a test
  file under `~/Documents` was blocked by auto mode (his permission check, so still not proof of the deny rule or the
  sandbox); a subagent's Read of it was blocked too. Both canaries came back blocked, as expected
- Commit: none (recorded in the commit after the 02:15 entries)

## 01:36 Fixtures committed alone, against the brief's one-commit rule
- Agent did: committed task 1's fixtures as their own commit (18e6421)
- Helped / failed: failed; the brief says the fixtures and the golden-set tests are one commit, and task 10's
  done-check needs the first commit on `tests/` to be `test(checker): add golden set before any code`
- Corrected by: the agent, on re-reading the brief: soft reset, the fixtures go into task 2's commit
- Commit: none (18e6421 undone before any push)

## 01:38 Task 4's done-check needs task 5's command line
- Agent did: ran task 4's done-check (the whole suite); it fails only on the command-line tests, which task 2
  wrote because task 2 asks for the exit codes, and which only task 5 can pass
- Helped / failed: the plan's order, not the code: task 4's own tests (find, golden rows, symlink refusal) pass
- Corrected by: the agent: task 4 is checked on those three test groups; the full-suite `OK` is checked at task 5
- Commit: none

## 01:39 Dog-food run on the planning notes: 174 references, 89 hold, 19 red
- Agent did: ran `python3 check_citations.py planning/*.md --root .` (task 6) and read each red line
- Helped / failed: helped; no red is a checker bug. 18 reds are the "Found at" column of 01's golden table
  (`planning/01-prior-art-and-formats.md` lines 103-125), where `notes.md:3` and `data/plan.txt:1` are written bare,
  outside backticks, and name fixture files relative to `tests/fixtures`, not the repo root: "file missing" is right
  by 01's own rule that only backticked text is an example. One red is a real miscite: `planning/README.md` line 113
  cites `build-brief.md:15`, a path not relative to the repo root (the file is `planning/build-brief.md`).
- Corrected by: none; `planning/0*.md` stay frozen and README.md is the task list, so neither is edited here
- Commit: none

## 01:41 Task 2's review: one Medium (F1), fixed; three Lows
- Agent did: wrote the golden tests; the reviewer found the H3 copy run did not check the counts, so a checker
  that never resolved `--root` (a root behind /tmp's symlink) passed every test
- Helped / failed: the review helped; the test gap was the agent's
- Corrected by: fix cb5bca6 checks all five counts on the copy, red with `realpath(root)` removed (run on a mutated copy)
- Commit: cb5bca6

## 01:41 The commit guard refused made-up keys and a MAC in the scrub test
- Agent did: wrote `tests/test_scrub.py` with literal fake tokens and a MAC-shaped string
- Helped / failed: failed; Danish's commit guard refuses secret- and MAC-shaped strings even as fixtures
- Corrected by: the guard; the test now builds those values from pieces at run time, so no committed file holds one
- Commit: none

## 01:45 Task 4's review: an unclosed quote came out green; fixed
- Agent did: wrote the quote parse so a quote with no closing mark was dropped, leaving "line only" (exit 0)
- Helped / failed: the review helped; the agent's parse failed open. The recheck of cb5bca6 also corrected the
  task 2 review: plain removal of `realpath(root)` was already caught, only an `abspath` form slipped through
- Corrected by: fix a95a1be: an unclosed quote runs to the end of the line and is checked (red if wrong); a curly
  open may close straight. Chosen over an eighth verdict to keep 01's closed list of seven
- Commit: a95a1be

## 01:46 The scrub: built to 02's five passes, with three choices nobody could check
- Agent did: wrote `scrub.py` (tests first, on a made-up log holding one of each of the six start-up blocks) and
  `planning/finish-sitting.sh`, dry-run once on a made-up export and list
- Helped / failed: open; not verified against a real `/export`, whose format this session has not seen. Choices:
  (1) a loaded skill, hook output or rules file is cut up to the next line starting `> ` or `⏺` (assumed prompt and
  reply marks), and any block whose end is not found is cut to the end of the file, so it fails safe, not open;
  (2) the username is the login name, and its hits are listed apart, not failed; (3) pass 5 runs twice, with line
  breaks removed and with them as spaces, so "Acme\nWidgets" also matches. 200 lines, not 02's "about 40"
- Corrected by: none yet; Danish's read of the pass-1 counts in the real report closes (1)
- Commit: see the scrub commit after this entry

## 01:46 Three entry times were guessed, not read from the clock
- Agent did: wrote the 01:41 (task 2 review), 01:45 (task 4 review) and 01:46 (scrub) entries with guessed times
  (01:40, 01:44, 01:49)
- Helped / failed: failed; 03 section 6 says times come from `date +%H:%M`, and 01:49 was later than the clock
- Corrected by: the agent, on the next `date`: each set to the clock reading taken just before or after it was written
- Commit: none (corrected before this file's next commit)

## 01:48 Reviewers' notes against the final code: 0 red, 37 of 40 not checked
- Agent did: ran `python3 check_citations.py planning/reviews/*.md --root .` (task 9)
- Helped / failed: helped, by showing a limit: the reviewers wrapped their `path:line "words"` citations in
  backticks, which the checker skips as examples, so the run shows 0 red, 0 holds, 3 line only, 37 not checked.
  The planning-notes run already has a real red (the `build-brief.md:15` miscite), so by card 3 (a) the planted
  edit is not used; the demo script says both
- Corrected by: none; the next reviewer brief could ask for citations outside backticks
- Commit: the demo script commit after this entry

## 01:49 The unclosed-quote fix let a curly quote close at a straight mark inside it
- Agent did: in fix a95a1be, let a curly open close at either mark, so `“The kettle" boils fast”` was cut to
  "The kettle" and held
- Helped / failed: failed; the recheck (planning/reviews/task-4-recheck-1.md) caught the new false green
- Corrected by: a curly open now closes at `”`, and at a straight mark only when no `”` follows on the line; one test
  pins it. No second recheck: the unit-end reviewer re-reads this fix
- Commit: the fix commit after this entry

## 01:54 Task 7's review: the scrub let private text through in seven reproduced ways
- Agent did: built the scrub line by line, matched list words literally, checked only the working tree, and left an
  old scrubbed log in place on a failing run
- Helped / failed: the review helped (3 High, 4 Medium, 3 Low, planning/reviews/task-7-review-1.md); the gaps were
  the agent's. Wave 1 (at most four): F1 reminder tags cut by depth, by character position; F2 list words matched
  with whitespace runs as one space and with all whitespace removed; F3 `finish-sitting.sh` also checks
  `git log -p main..HEAD`; F6 a failing run removes `logs/session.txt`. Wave 2 next: F4, F5, F7
- Corrected by: the review. F3 changes the brief's rule "a hit is fixed by a new commit": a new commit fixes the
  files, not history, so a hit in history needs the branch rewritten before any push. That is Danish's call
- Commit: the wave-1 fix commit after this entry

## 01:56 Scrub wave 2: path-shaped list entries, empty lists, quoted lines in loaded text
- Agent did: fixed task-7-review-1 F4 (list entries also matched in their `~/...` form), F5 (list read as
  utf-8-sig, every non-blank line an entry, an empty list refused with exit 2) and F7 (markers may follow an indent
  or the export's tree glyphs; loaded text ends at a reply, or at a `> ` prompt after a blank line)
- Helped / failed: helped; one new test was wrong at first (it expected `#Acme Widgets` to match text without the
  `#`), corrected to match the entry as written
- Corrected by: the agent, on reading the failure
- Commit: the wave-2 fix commit after this entry

## 01:57 Unit-end checker review: the demo script made 2 unexplained reds
- Agent did: wrapped a backticked example in `planning/demo-script.md` across two lines; the checker scans line by
  line, paired the ticks wrongly, and checked `notes.md:3` and `/etc/hosts:1` from the repo root (2 new reds)
- Helped / failed: the review helped (1 Medium, 5 Lows, 1 question: planning/reviews/unit-review-checker.md)
- Corrected by: the reviewer's pick: the demo lines rewrapped so each code span sits on one line; README now says a
  code span is skipped only on one line, and names wrapped inline code and paths with spaces under "What was cut".
  The dog-food run is back to 19 reds, the ones explained at 01:39. The parser limit stays (noisy, never a false green)
- Commit: the fix commit after this entry

## 01:59 Unit-end docs review: the README claimed what had not happened yet
- Agent did: wrote README's "How it was built" as if the unit end and the log export were done, and said each
  Medium had its own fix commit (the scrub waves fix several in one)
- Helped / failed: the review helped (2 Medium, one shared with the checker review; 7 Lows; 2 questions:
  planning/reviews/unit-review-docs.md). Its Q2 checked: main's 4699865 records the 01:16 test script, not task 0's
  dry run, so the dry-run answers are still missing
- Corrected by: the section now says only what is true at merge time: reviews and rechecks as done, fixes may
  share a commit, decisions written during the sitting with three corrected times, and the log present only if
  the scrub after the session was clean
- Commit: the fix commit after this entry

## 02:06 The scrub recheck: the fixes cut and matched too much
- Agent did: in the scrub fix waves, let any opening reminder tag start a cut, matched list words with all spaces
  removed anywhere, and ended loaded text at a `> ` line after a blank line
- Helped / failed: the recheck helped (planning/reviews/task-7-recheck-1.md): one tag quoted in code (this
  session's own commands quote it) would cut the whole rest of the real export; "Tan" matched "that answer"; a
  blockquote after a blank line still leaked the rest of a rules file
- Corrected by: at depth 0 only a tag that starts its line (after an indent, tree glyphs or a closing tag) opens a
  block; the no-space pass counts only matches that cross a line break; loaded text ends only at a `⏺` reply, so
  the prompt after it is cut too (safe). No second recheck: the unit-end re-review reads this fix
- Commit: the fix commit after this entry

## 02:15 Danish: a real folder name sat in the scrub tests and two saved reviews
- Agent did: copied a reviewer's example path into `tests/test_scrub.py` and saved two reviews holding it; the
  reviewer had taken the folder name from this session's sandbox settings
- Helped / failed: failed; the name is Danish's own folder. It is now the invented "Old Shoebox" in the test and
  both reviews (each review says it was edited, and why). The old name is still in three branch commits (2aa7047,
  354f07e, 2c4d52c) and in the git-ignored local exports under `.review/`; no commit message holds it
- Corrected by: Danish. How it leaves history before any push: rewrite the branch from main, replacing the name in
  every commit's files (`git filter-branch --tree-filter` over `main..build/check-citations`), then drop the backup
  refs and expire the reflog so no local ref points at the old commits; nothing is pushed until then. Danish's call
- Commit: the commit after this entry

## 02:15 finish-sitting could never pass: generic path patterns are now reported, not failed
- Agent did: built pass 5 to fail on any list hit, while `scrub.py` and its tests must name path roots like `/tmp`
- Helped / failed: failed (Danish's catch); with a generic entry on his list, every run would fail
- Corrected by: a short set in `scrub.py` (`GENERIC`), chosen from what tracked files really hold: `/Users`,
  `/private`, `/private/tmp`, `/private/var/folders`, `/var/folders`, `/tmp`, `/home`, `/Volumes`, `Documents`,
  `Developer`, `~/Documents`, `~/Developer`, `.claude`, `~/.claude`. A list entry exactly equal to one (any case,
  trailing `/` ignored) has its hits listed in the report's own section and printed as a count; every other entry
  still fails. Two tests (check-only, and finish-sitting in a throwaway repo)
- Commit: the commit after this entry

## 02:18 Unit-end scrub review: the saved session file, indented blocks, slashes, main's history
- Agent did: built the scrub for the `/export` text only, with block ends that assumed unindented lists and headings
- Helped / failed: the review helped (1 High, 6 Medium, 3 Low, 2 questions: planning/reviews/unit-review-scrub.md);
  its F3 and F4 were already fixed by 2c4d52c (its probes rerun on the head: nothing cut wrongly, the recipe cut)
- Corrected by: F1 a file of JSON records (the saved session file, the fallback if `/export` fails) is read as its
  records' strings, each after a reply mark, so markers start lines and escaped line breaks are real; F2 lists and
  headings may be indented, in one pass (was quadratic); F5 a list entry's trailing `/` is dropped; F6 the history
  check covers every commit from HEAD, main's too, without author lines (also answers recheck F3a). F7 is next
- Commit: the fix commit after this entry

## 02:18 Scrub: a hit's line number now points at a file that exists
- Agent did: on a hit, the report named lines of a scrubbed log that was never written (unit-review-scrub F7)
- Helped / failed: the review helped; the no-space half of F7 was already fixed in 2c4d52c
- Corrected by: on a hit, the scrubbed text is written beside the report (`<report>.scrubbed.txt`, in the temp
  folder outside the repo) and both messages say where; one test
- Commit: the fix commit after this entry

## 02:28 The unit-end re-review: one regression and one silent fallback in the scrub fixes
- Agent did: in 2c4d52c let only a line-start tag open a reminder block, which kept a reminder opening after a
  closed one or after a `> ` mark; in ad698d1 dropped the whole records reading on one bad line
- Helped / failed: the re-review helped (2 Medium, 5 Low, 2 questions: planning/reviews/unit-rereview-fixes.md);
  it also confirmed all six fixes answer their findings and all 19 dog-food reds are explained
- Corrected by: closed reminder spans and a `>` before a tag no longer stop it opening a block; a session file is read
  as records when at least half its lines are records, other lines kept as text after their own mark, and the report
  says which path it took. One recheck follows; any finding after that goes to Danish
- Commit: the fix commit after this entry

## 02:28 The shell's grep is a wrapper that dropped results for a pattern with a space
- Agent did: counted the old folder name with `grep -c`, which printed nothing instead of a number
- Helped / failed: failed quietly; `type grep` shows a shell function from the session snapshot
- Corrected by: the agent: every count of the name rerun with `command grep` and Python: working tree 0, HEAD tree 0,
  commit messages 0, history 15 (the rewrite removes these; rehearsed on a clone: 15 to 0)
- Commit: none

## 02:29 History rewritten to remove the old folder name; hashes mapped
- Agent did: on Danish's "history: rewrite", rehearsed on a throwaway clone, then ran `git filter-branch` over
  `main..build/check-citations`: a tree filter replaced the name with "Old Shoebox" in every commit's files, a
  message filter mapped `Fixes:` hashes. Commits before accb3c6 kept their hashes; the final tree is unchanged
- Helped / failed: helped; the history check (`scrub.py --check-only`, a list holding only the name, over
  `git log -p --format=%B HEAD`) gives `private list: 0 hits`; tests OK; no commit message cites an old hash.
  Old to new:
  accb3c6 -> 2aa7047
  60d5e4b -> 354f07e
  c303381 -> 65a489a
  cc51f43 -> 2c4d52c
  79cf188 -> eaaef3a
  72bf29b -> ad698d1
  9a5d184 -> 9791fcf
  3d68565 -> 77e261a
- Corrected by: Danish's conditions: this one commit maps every cited hash in decisions and the reviews; the backup
  ref `refs/original/refs/heads/build/check-citations` and the reflog stay until he says to delete them
- Commit: the commit after this entry

## Lows
- task-2-review-1 F3, `tests/test_check_citations.py`: not tested: first three places only, H3's file never opened
  (patch `open`), a permission-denied file as "file missing"
- task-2-review-1 F4, `tests/test_check_citations.py:121` and `:95`: tests fix choices 01 leaves open (line:col
  counts 0 skipped while a URL counts 1; a huge line number stored as None; found-at on the same output line)
- task-2-recheck-1 F1, `tests/test_check_citations.py:159`: the copy's symlinked root comes from the machine's
  /tmp; on a Linux CI with a real /tmp, an `abspath` root would pass. Fix: build the test's own symlinked root
- task-2-recheck-1 F2, `tests/test_check_citations.py:63`: a missing summary part raises AttributeError, hiding the line
- task-4-review-1 F2, `check_citations.py:115`: quotes match as substrings, so "safe to run" holds on "unsafe to run"
  (01 does not set word boundaries; Danish's call)
- task-4-review-1 F3, `check_citations.py:18`: the URL branch is quadratic on long letter runs (40,000 letters 2.2 s)
- task-4-review-1 F4, `check_citations.py:123`: words over three or more lines cited at the wrong place say
  "not in file", though they are in the file
- task-4-review-1 F5: no test pins `realpath` over `abspath` for the root, nor the first-three cap on places
- task-4-review-1 F1 (tail): an empty quote `""` is still "line only"
- task-4-recheck-1 F2, `check_citations.py:130`: an opened but empty quote (`"`, `""`, `"**"`) is still "line only"
- task-4-recheck-1 F3, `check_citations.py:65`: a quote wrapped onto the next report line is checked on its first
  line's words only, and can come out "holds"
- task-7-review-1 F8, `scrub.py` pass 2: `/System/Volumes/Data/Users/...`, lower-case `/users/...` and URL-encoded
  home paths survive pass 2 (they show as username hits only)
- task-7-review-1 F9, `scrub.py` SECRETS: a private key with no END line, lower-case `bearer`, a dash-written MAC
- task-7-review-1 F10, `scrub.py` `read`: a non-UTF-8 export or list is read with replacement characters, so
  matches can silently fail
- unit-review-checker F2, `check_citations.py:102`: no test pins `isfile` (a FIFO would hang `open`); only ESC is
  tested among control characters
- unit-review-checker F3, `check_citations.py:161-170`: usage errors print the report name and `--root` unfiltered
- unit-review-checker F4, `check_citations.py:188`: an output encoding error or a closed pipe exits 1 or 120
- unit-review-checker F5, `check_citations.py:122`: each reference re-reads its file (1,600 refs on a 20,000-line
  file: 37 s)
- unit-review-checker Q1, `check_citations.py:22`: a quote after punctuation (`notes.md:1, "x"`) is never checked and
  comes out "line only"; 01 says "right after the line number". Danish's call
- unit-review-docs F4, `planning/demo-script.md:23` and the 01:45 entry: "came out green" for a "line only" result,
  which README's table calls neutral
- unit-review-docs F5, `planning/demo-script.md` point 4: 03's "one bug the tests caught" is not in the demo
- unit-review-docs F6, `README.md:11-17`: the sample output names no command and is not marked as an excerpt
- unit-review-docs F8, `planning/reviews/`: saved word for word, the replies hold system temp paths (`/tmp/...`,
  `/private/var`); no home folder or username. The brief bars absolute paths; the recipe saves replies verbatim
- task-7-recheck-1 F4a, `scrub.py` check-only: a path-shaped list entry is not matched in its `~/` form in tracked files
- task-7-recheck-1 F4b, `scrub.py` `with_path_forms`: an entry ending in `/` (e.g. a home folder) becomes `~/` and
  matches every scrubbed path, so the run can never pass
- task-7-recheck-1 F6a, `planning/finish-sitting.sh`: an old `logs/session.txt` survives a refused list or a crash,
  and the message then says "hits in the export"
- task-7-recheck-1 F3a (question), `planning/finish-sitting.sh:24`: `git log -p` prints `Author:`; if Danish's list
  holds his commit name or email, every branch fails. Danish's call
- task-7-recheck-1 (note): an indented `SessionStart` or `Contents of ... CLAUDE.md` inside a reply now cuts the
  rest of that reply (safe, loses text)
- unit-review-scrub F8, `planning/finish-sitting.sh:10`: a relative list path breaks after `cd`, with misleading messages
- unit-review-scrub F9, `scrub.py` EMAIL: quadratic on a long run with no `@` (100k hex characters: 13.6 s)
- unit-review-scrub F10, `scrub.py` main: path forms of list entries are tested only directly, not through the command
- unit-review-scrub questions: box-drawing characters between wrapped words; staged content not checked
- unit-rereview-fixes F1 (tail), `scrub.py` cut_reminders: a reminder opening after tool output on the same line
  is still kept (it cannot be told from a tag quoted in code)
- unit-rereview-fixes F3, `scrub.py` match: the spaced pass matches inside words ("Sam" in "same"); whole-word
  matching for short entries is Danish's call
- unit-rereview-fixes F4, `check_citations.py:65`: a curly open now runs to a later curly close on mixed-mark lines (red)
- unit-rereview-fixes F5, `scrub.py` main: `<report>.scrubbed.txt` is written beside any report path, even inside the
  repo, and the docstring's exit-1 line does not mention it
- unit-rereview-fixes F6, `planning/finish-sitting.sh`: "without author lines" has no test
- unit-rereview-fixes F7: the demo's reviews-run numbers are stale (task 12 re-measures)
- unit-rereview-fixes Q1: whether a skill's header and body share one record in the saved session file is unseen
