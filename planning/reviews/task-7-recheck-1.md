# Recheck of the task 7 scrub fixes (accb3c6, 60d5e4b)

(Edited on Danish's instruction, 7 Nov: a real folder name in one example was replaced by the invented "Old Shoebox".)

(Saved as received. The agent tool neutralised the reminder tag in this reply, writing it as `<\system-reminder>`.)

**Result:** six of the seven findings are fixed, and F7 is only partly fixed. Every review probe now gives the right result except one F7 variant. The tests pass (`Ran 20 tests ... OK`), and each finding has a test that fails when its fix is taken out. I found three new problems where the fixes cut or match too much (Medium), one place where F7 still leaks (Medium), and four smaller gaps (Low or questions).

| Finding | Fixed? | Test goes red without the fix |
|---|---|---|
| F1 | yes | `test_two_reminders_on_one_line_and_nested_are_both_cut` |
| F2 | yes | `test_wrapped_and_spaced_words_are_caught`, plus `test_list_word_split_by_a_line_break_is_caught` when only the no-whitespace pass is dropped |
| F3 | yes | `test_a_word_removed_by_a_later_commit_is_still_caught` |
| F4 | in the scrub, yes; in `--check-only`, no | `test_a_list_entry_written_as_a_path_still_matches` |
| F5 | yes | `test_an_empty_list_is_refused`, `test_hash_entries_and_a_byte_order_mark_still_match` |
| F6 | yes when the export has a hit; no on a refusal or a crash | `test_a_failing_run_removes_an_earlier_scrubbed_log` |
| F7 | the review's probes pass; a quote after a blank line still leaks | `test_loaded_text_runs_past_a_quoted_line_and_indented_markers_are_cut` |

### F7a. Medium. A quoted line after a blank line still ends the cut, so the rest of the rules file or skill leaks
`scrub.py:52 "lines[j].startswith(\"⏺\") or"` and `:53 "(lines[j].startswith(\"> \") and not lines[j - 1].strip())"` end the cut at any `> ` line that follows a blank line. In markdown, a blank line before a blockquote is the normal way to write one.
- **Probe:** `Contents of /x/CLAUDE.md:\n# rules\n\n> quoted rule after a blank line\nPRIVATE RULE TEXT\n\n> real prompt\n`
- **Result:** `<cut: rules file, 3 lines>\n> quoted rule after a blank line\nPRIVATE RULE TEXT\n...`, the same leak on ef0fdaa and on head.
- The fix follows the review's own suggested rule, so the review's three probes pass. This layout still fails.
- **Fix:** end loaded text only at a `⏺` reply line, or at a `> ` line once the export's real prompt shape is known. The test at `tests/test_scrub.py:125` covers only a quote with no blank line before it.

### F2a. Medium. The no-whitespace pass makes short list entries match across word gaps, so a clean log fails
`scrub.py:176 "for space in (\" \", \"\"):"` together with `flatten` (`:161`) removes every space before matching, not only line breaks. Before the fix, the empty joiner removed only line breaks.
- **Probe** (made-up entries, head): `Tan` hits `I think that answer is right.`; `Sam` hits `This was amazing.`; `Kora` hits `a mock or a stub`; `Vela` hits `we have lazy loading`.
- Each probe gives `[(1, 1)]`, which means exit 1 and no `logs/session.txt`. On ef0fdaa all four gave `[]`.
- 02 §3 says the list holds about 100 entries, including folder and company names. One short name could stop the log from ever being written.
- **Fix:** in the no-whitespace pass, count a match only if it crosses a line break, or only for entries above a set length.

### F1a. Medium. One stray opening tag now cuts the whole rest of the export
`scrub.py:75 "out.append(reminder_cut(text[start:]) if depth else text[pos:])"`: an opening tag that never closes, for example one quoted in source code, raises the depth. Every later block in the export then sits inside it.
- The repo's own `tests/test_scrub.py:80 "for gone in [\"<\system-reminder>\", ..."` is such a line: the file has 6 opening tags and 5 closing tags.
- **Probe:** a Read output showing that line, then a prompt, a reply, a real reminder block and more text.
  - ef0fdaa cut 7 lines and kept `⏺ reply two kept?` and everything after it.
  - Head gives `<cut: system-reminder, 14 lines>`: everything to the end of the file is gone.
- Nothing leaks, but the session log is this build's deliverable. Whether `/export` prints that test line has not been seen.
- **Fix:** at the end of the file, if the depth is not zero, fall back to cutting only the unclosed opener's line or block, and let the report say so.

### F4a. Low. `--check-only` still misses a path-shaped entry written in its `~/` form in a tracked file
`scrub.py:230 "patterns = read_list(argv[1])"`: only the scrub side uses `with_path_forms` (`:248`).
- **Probe** (HOME=/Users/alex): entry `/Users/alex/Documents/Old Shoebox/Zephyr`; a tracked file reads `notes in ~/Documents/Old Shoebox/Zephyr/plan.md`.
- **Result:** `exit 0`, `private list: 0 hits`.
- The review said the check-only side "is not affected", but tracked files are not raw export text.
- This is unlikely here, because Danish's rules make absolute paths the norm. The fix is to call `with_path_forms` in check-only too.

### F4b. Low. A path entry ending in `/` now matches every scrubbed path, so the run can never pass
`scrub.py:187 "if not p or p in (\"~\", \".\", \"<tmp>\", \"<repo-folder>\"):"` skips an entry that is only a machine path, but not one that ends in a slash.
- **Probe:** the entries `/Users/alex/`, `/Users/alex/Developer/demo-repo/` and `/tmp/` become `~/`, `./` and `<tmp>/`.
- Each one hits `⏺ Read ~/notes.txt and ./scrub.py and <tmp>/run.1`.
- Before the fix these entries never matched; now any mention of a file blocks the log.
- **Fix:** strip the trailing `/` from entries before building their forms.

### F6a. Low. An old log survives a refused list or a crash, and the script says it was not written
`scrub.py:257-258` removes the old output only on a list hit. `scrub.py:209-210` exits 2 before that, and `planning/finish-sitting.sh` has no `rm -f logs/session.txt` (the review suggested one before `:21`).
- **Probe** (throwaway repo):
  1. A clean run writes `logs/session.txt`.
  2. A second run with an empty list exits 1, prints `planning/finish-sitting.sh:36 "hits in the export: logs/session.txt is not written"` and two `tail: ... No such file` lines.
  3. The old `logs/session.txt` is still there.
- The script exits 1, so it does not say clean. The message is wrong twice: there was no hit, and the file does exist.

### F3a. Question. A list entry for the commit author's name or email fails every branch
`planning/finish-sitting.sh:24 "git log -p main..HEAD"` prints `Author: name <email>` on every commit. The old `--format=%B` printed messages only.
- **Probe:** with list entry `Quill Ferro`, which is the probe repo's author, a branch with one ordinary commit exits 1. The only way out is re-authoring the commits.
- Does Danish's list hold his commit name or email? If yes, add `--format=` with the message and diff only, for example `git log -p --format=%B main..HEAD`.
- Not probed: `git log -p` shows no diff for merge commits, so a word added while fixing a merge conflict would not be checked.

### Answers to the three questions
- **1. Fixed?** I re-ran the review's own probes on the export with exit and output, and compared them with ef0fdaa:
  - F1: both inputs fully cut; `SECRETUSER` and `INNER-LEAK` are gone.
  - F2: all five inputs hit.
  - F3: exit 1 with "2 hits", where ef0fdaa printed `clean`.
  - F4: exit 1, nothing written.
  - F5: empty and blank-only lists exit 2; `#Acme Widgets` and BOM lists hit (exit 1). All four gave exit 0 on ef0fdaa.
  - F6: the output is removed after a run with a hit.
  - F7: the review's probes 1-3 are cut; the variant above (F7a) is not.
- **2. Broke what it touched?** Tests `Ran 20 tests ... OK`.
  - A clean branch with two ordinary commits still passes finish-sitting (exit 0, log written).
  - The F3 change makes a branch impossible to pass only through F3a.
  - New over-cutting: F1a. New over-matching: F2a and F4b.
  - The indented markers also cut more than before:
    - `⏺ ...\n  SessionStart output is cut...` now cuts the rest of that reply (`<cut: hook output, 3 lines>`), and `  Contents of the CLAUDE.md rules say...` does the same.
    - These are replies, not hook output. It is safe but loses text. Low, not written up as a separate finding.
- **3. Red without the fix?**
  - With all of ef0fdaa's `scrub.py` and `finish-sitting.sh` under the new tests: 13 failures and 1 error. The F4 test errors out (`AttributeError: ... with_path_forms`) rather than failing on behaviour.
  - So I also took out each fix on its own in a copy of head. Every one turned its own test red, as listed in the table at the top.

### Coverage
| Item | Probe (Q1) | Breakage (Q2) | Test goes red (Q3) |
|---|---|---|---|
| F1 | compared, head and ef0fdaa | compared (F1a); line numbers covered by the existing test only | compared (line-rule revert and depth revert) |
| F2 | compared, 6 inputs | compared (F2a); username false hits not probed (they are reported, not failing) | compared (2 mutations) |
| F3 | compared, throwaway repo, head and ef0fdaa | compared (clean branch passes; F3a); merge commits and binary files not compared | compared (ef0fdaa script) |
| F4 | compared, function and CLI with HOME=/Users/alex | compared (F4a, F4b); JSON-escaped and dash forms of an entry not compared (that is review F8's area) | compared (`with_path_forms` stubbed) |
| F5 | compared, 4 lists | compared (exit 2 in finish-sitting, under F6a); a non-UTF-8 list not compared (review F10) | compared (3 mutations) |
| F6 | compared | compared (F6a) | compared |
| F7 | compared, review probes plus blank-line variant | compared (F7a; indented-reply over-cut) | compared (LEAD and end-rule mutations) |
| Test suite on export | `OK`, 20 tests | n/a | n/a |
| Real `/export` format | not compared (no real export exists yet) | not compared | n/a |
| Danish's real list and git config | not compared (outside scope; global and system git config were kept off in the probes) | not compared | n/a |

All probes used made-up text in a `recheck7.*` temp folder, now removed. The repo working tree is unchanged.
