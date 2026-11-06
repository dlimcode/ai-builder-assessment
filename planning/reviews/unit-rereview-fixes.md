# Re-review of fixes 0cb53ca to 9a5d184 (head 9a5d184, export reviewed)

**Outcome:** all six fixes answer their findings. Each finding's own probe now gives the right result, and every fix has a test or run that goes red without it. The exception is one untested part of fix 5. The suite passes: `Ran 60 tests ... OK`.

There is one regression, from fix 3 (cc51f43): it reopens a reminder leak that 60d5e4b had closed. There is also one silent fallback in fix 5 that brings back the original High. Both are Medium. There are five Lows and one question. The dog-food run shows 19 red, and every one is explained in `planning/decisions.md`.

### F1. Medium. A reminder that opens after other text on its line is kept whole (regression from cc51f43)
- **Where:**
  - scrub.py:70 "before = text[text.rfind(" removes only closing tags from the text before an opening tag.
  - scrub.py:71 "if depth == 0 and not OPENS_LINE.fullmatch(before):" then skips that opening tag.
  - scrub.py:21 "OPENS_LINE = re.compile(" allows only spaces and tree glyphs before the tag, not `> `.
- **Failure path (probed end to end; exit 0, `logs/session.txt` written):**
  - In `<sr>one</sr><sr>SECOND reminder text</sr>` on one line, the second block survives whole. The text before the second tag becomes `<sr>one` once the closing tag is removed, so it is not blank.
  - In `> <sr>` / `Git user: madeup-user` / `Current branch: ...` / `</sr>`, every line is kept.
  - The same happens for a tag after tool output on the same line (`⎿  result line<sr>...`).
  - At 60d5e4b all three were cut.
- **Why the test misses it:** tests/test_scrub.py:111 "def test_two_reminders_on_one_line_and_nested_are_both_cut" puts a line break before the first closing tag, so the text before the second tag is empty.
- **How real it is:** a user turn that starts with a reminder, rendered after a `> ` prompt mark, gives exactly the second shape. I have not seen how `/export` renders reminders, so the layout is unconfirmed. The regression itself is certain.
- **Fix to consider:**
  - Remove whole closed `<sr>...</sr>` spans from the text before the tag, not just closing tags.
  - Allow `>` in the characters that may come before an opening tag.
  - Add the two probes above as tests.

### F2. Medium. One bad line makes the saved session file fall back silently to raw text, which brings back unit-review-scrub F1 whole
- **Where:** scrub.py:154-157 "except ValueError: return text". Any line that fails `json.loads`, or any record that is not a dict, sends the whole file down the plain-text path.
- **Probe (made-up records: skill text, hook output, a wrapped `Zephyr\nHoldings`):**
  - With all lines valid: 3 blocks cut.
  - The same file plus one truncated line, or one `[1,2]` line: `blocks 0`, both private texts kept, and pass 5 gives `[]` for `Zephyr Holdings`.
  - The report gives no sign of which path the file took.
- **Why it matters:** a session file cut short mid-write (a crash, or a copy taken while it is still being written) is a known way for this format to arrive. The fallback is the input this fix exists for.
- **Fix to consider:**
  - Skip or flag the lines that do not parse, rather than dropping every record.
  - Or stop with exit 2 when more than a few lines start with `{` but the file does not parse.
  - Either way, write the chosen path into the report.

The other two fix-5 probes you asked for behave correctly:
- A plain-text export whose first line is `{ not json` stays text and is scrubbed normally.
- A file holding only `{}` becomes `⏺ record 1`, which is harmless.

### F3. Low. Short list entries still fail a clean log by matching inside words (the half of recheck F2a that cc51f43 left open)
- **Where:** scrub.py:221 "for m in re.finditer(re.escape(p), flat):". The spaced pass is still a plain substring search.
- **Probe:**
  - `Sam` hits "the same answer", `Tan` hits "an important point", `Ana` hits "we analyse it". Each gives exit 1.
  - On the export's planning prose (103 KB), the spaced pass gives `Tan` 13 hits, `Sam` 15 and `Ana` 8. The no-space pass now gives 0 for each, and `Ito` gives 1.
- **Not new:** this behaviour predates cc51f43, and F2a's own probes now pass. But F2a's harm, "one short name could stop the log from ever being written", still holds for names like these.
- **Fix to consider:** whole-word boundaries for entries without a `/`, or for entries under a set length. This is Danish's call, as it was for the checker's substring rule.

### F4. Low. Fix 1 turns a mixed-mark line red: a curly open now runs to a later curly quote
- **Where:** check_citations.py:65 "close = text.find(QUOTE_CLOSE[q.group(1)], q.end())"
- **Probe:** `notes.md:3 “The kettle boils" then a.md:1 “a.md line”`
  - Head: one reference, **not in file**.
  - With the change reverted: two references, both hold.
- **Impact:** red, never a false green. This is the trade-off the recheck's rule accepts, but a reader loses the second reference.

### F5. Low. Fix 6 writes the full scrubbed text, private word included, beside any report path, with no check that it is outside the repo
- **Where:** scrub.py:318 "f.write(text)  # beside the report, outside the repo"
- **Failure path:** someone runs `scrub.py` directly with a report path inside the repo. A hit then writes `<report>.scrubbed.txt`, an untracked file that `.gitignore` does not cover, and one `git add .` commits it. The documented route, `finish-sitting.sh`, is safe because it uses `$tmp`.
- **Stale doc:** scrub.py:8 "1 a private-list hit, and the scrubbed log is not written" no longer mentions this file.
- **Also:** the temp folder is never removed, so a full copy holding the hit stays in `$TMPDIR`.

### F6. Low. Fix 5's "without author lines" has no test
- **Where:** planning/finish-sitting.sh:24 "git log -p --format=%B HEAD >". This answers recheck F3a (planning/decisions.md:175 "check covers every commit from HEAD, main's too, without author lines").
- **Mutation:** changing it to `git log -p HEAD` passes all 60 tests.

### F7. Low. Saved docs are stale against head
- **The demo's reviews run:** planning/demo-script.md:32 "Measured: 40 references, 0 red, 37 not checked". Running it at head prints "191 references: 25 holds, 9 line only, 19 red, 138 not checked".
  - The reds are saved reviews citing lines that have since moved, two of them added by c303381 itself.
  - The script says to re-measure before recording, but the presenter would say "0 red" over a screen showing 19.
- **The README's recheck claim:** README.md:92 "a fresh agent rechecked each fix of a" Medium-or-worse finding. That is true for a95a1be, cb5bca6, accb3c6 and 60d5e4b. It is not true for 0cb53ca, c303381, cc51f43, 72bf29b or 9a5d184 unless this re-review is saved, and then any fix it causes needs its own recheck.

### Q1. In the saved session file, does a skill's or hook's text sit in the same record as its marker?
- The inserted `⏺ record N` line ends "next message" blocks.
- A probe with `Base directory for this skill` in one record and the body in the next kept the body (`SPLITBODY private recipe`).
- I believe Claude Code stores the header and body in one string, which would make this safe, but I have not seen the file.

### Q2. Should scrub.py:151 "after a reply mark that ends any block" say less?
- The record mark does not end sandbox text ("next heading") or a skills list ("end of list").
- In a probe, a `## Bash command sandbox` string with no later heading cut every later record, including two replies.
- This is over-cutting (safe), but the comment overstates.

## Per fix: is the finding fixed, did the fix break anything, does its test go red
- **Fix 1 (0cb53ca):**
  - **Fixed:** yes. The recheck's three probes now give **not in file**, and the nested `a.md:2` is not scanned.
  - **Breaks:** F4.
  - **Red without it:** `test_curly_quote_keeps_straight_marks_inside`.
- **Fix 2 (c303381):**
  - **Fixed:** yes. Dog-food at head: "201 references: 89 holds, 0 line only, 19 red, 93 not checked". With the old demo text put back: 21 red.
  - **README:** line 39 is scoped to "on one line". The "What was cut" claims about `path:line:col`, `#L12` and paths with spaces match the code. The Logs paragraph is conditional and true.
  - **Breaks:** F7.
  - **Red without it:** the dog-food run, not a unit test.
- **Fix 3 (cc51f43):**
  - **Fixed:**
    - F7a: `<cut: rules file, 8 lines>`, nothing leaks.
    - F2a: Tan, Sam, Kora and Vela all `[]`; a wrapped name is still caught.
    - F1a: a quoted tag no longer cuts the rest.
  - **Breaks:** F1 (regression) and F3.
  - **Red without each part:**
    - `test_a_tag_quoted_mid_line_does_not_cut_the_rest`
    - `test_short_entries_do_not_match_across_spaces` (3 subtests)
    - `test_a_quote_after_a_blank_line_does_not_end_loaded_text`
- **Fix 4 (79cf188):**
  - **Fixed:** yes. A private entry cannot pass by looking generic:
    - `/Users/someone`, `/Users/someone/`, `Documents/x` and `/private/tmp/z` all fail (exit 1).
    - ` /tmp `, `/TMP/`, `Documents`, `~/Documents/` and `.Claude` are reported as generic (exit 0). Each is exactly one of the 14 after strip, case-fold and trailing `/`, which is the decided rule.
  - **Breaks:** none found.
  - **Red without it:** `test_generic_path_entries_are_reported_not_failed`, `test_generic_patterns_in_tracked_files_pass`.
- **Fix 5 (72bf29b):**
  - **Fixed:**
    - F1: 3 blocks cut on valid records.
    - F2: an indented list of 40k lines takes 0.03 s and ends correctly.
    - F5: all three of the review's rows hit.
    - F6: main's history is checked; main is an ancestor of HEAD in the repo.
  - **Breaks:** F2, F6, Q1, Q2.
  - **Red without each part:**
    - `test_a_saved_session_file_is_read_as_records`
    - `test_indented_list_and_sandbox_end_where_they_should` (both the heading and list mutants)
    - `test_a_folder_entry_with_a_slash_matches_the_bare_folder`
    - `test_a_word_only_in_mains_history_is_caught`
    - Author lines: no test (F6).
- **Fix 6 (9a5d184):**
  - **Fixed:** yes. A probe with a cut block before the hit reports "scrubbed line 10", and line 10 of `rep.txt.scrubbed.txt` is "about Zephyr". The `finish-sitting.sh` message names the same path.
  - **Breaks:** F5.
  - **Red without it:** `test_a_hit_can_be_found_beside_the_report` (error).

## Dog-food run
`timeout 60 python3 -B check_citations.py planning/*.md --root .` exits 1 with 19 red. All 19 are explained by planning/decisions.md:30 "Dog-food run on the planning notes: 174 references, 89 hold, 19 red":
- 18 are `file missing` in `planning/01-prior-art-and-formats.md` lines 103-125.
- 1 is `planning/README.md:113 build-brief.md:15`.

The demo's line-9 claim, "89 references hold, 19 red", matches the run.

## Coverage
| Item | Compared | Not compared (why) |
|---|---|---|
| Fix 1 0cb53ca | recheck probes, mutation, mixed-mark probe | nothing |
| Fix 2 c303381 | dog-food before/after, README lines 36-40, 68-72 and 86-103 against the code | README sections the fix did not touch |
| Fix 3 cc51f43 | F1a, F2a and F7a probes, regression against 60d5e4b's scrub.py, 3 mutations | the real `/export` reminder layout (not available) |
| Fix 4 79cf188 | scrub.py diff only, as told; 9 list entries through `--check-only`; mutation | finish-sitting.sh run by hand (its test covers it) |
| Fix 5 72bf29b | records (valid, one bad line, array line, `{` text, split record), indented list timing, slash entry, history range, 5 mutations | a real Claude Code session file (not available, and outside the allowed area) |
| Fix 6 9a5d184 | end-to-end line mapping, message path, mutation | nothing |
| Unit suite | `Ran 60 tests ... OK` in the export | n/a |
| Dog-food run | all 19 reds traced to decisions.md | n/a |
| Privacy | no `git show` on tests or reviews before 79cf188; all probe text made up | n/a |

Nothing was edited or committed. The temp folder was removed and `git status` shows the repo unchanged.
