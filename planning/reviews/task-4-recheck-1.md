## Recheck of a95a1be (task 4 review, F1)

**F1 is fixed for all four cases in the review, and the 29 tests pass.** The fix brings in one new false green: a curly quote with a straight mark inside it is now cut short. One smaller case named in F1 (an empty quote) is still "line only".

| Question | Answer |
|---|---|
| 1. Is F1 fixed? | Yes for all four. `notes.md:3 "Under a minute` gives **not in file** (red); before the fix it gave line only. `notes.md:3 “under a minute"` gives quote `under a minute`, **holds**; before, line only. A wrapped `notes.md:6 "Deliveries arrive before eight and are` is checked on its first line's words: **holds**, and with wrong words it is **not in file**. `a.md:1 "see notes.md:2` gives **one** reference with quote `see notes.md:2`; before, it gave two. |
| 2. Did it break what it touched? | Unittest: `Ran 29 tests ... OK`. These parse the same before and after: a closed straight quote, a closed curly quote, two references on one line, a quote followed by more words, and no quote. One break, a curly quote with a straight mark inside: see F1 below. The new end-of-line rule also swallows a later reference on the same line: see the note under F3. |
| 3. Does the test go red without the fix? | Yes. I put a7bbd9b's checker with the post-fix tests in a temp copy. FindTests: `Ran 16, FAILED (failures=2)`. The failing tests are `test_curly_open_may_close_straight` (`None != 'under a minute'`) and `test_unclosed_quote_runs_to_the_end_of_the_line` (`2 != 1`). In the second test, the verdict check at line 130 is never reached. a7bbd9b's `scan_line` is the same as the commit just before the fix; the only difference is the command line added later. |

### F1. Medium. A curly quote with a straight mark inside now closes at that mark: the check runs on part of the quote and can go green
- **Where:** `check_citations.py:23 "\"“\": re.compile('[”\"]')"` and `check_citations.py:64 "close = QUOTE_CLOSE[q.group(1)].search(text, q.end())"`. After a curly open, the first `"` now closes the quote, even when a `”` comes later.
- **Failure path (probed):**
  - `notes.md:3 “The kettle" boils fast”`: the quote becomes `The kettle` and **holds**. Before the fix the whole quote was checked and was **not in file** (red). That is a new false green.
  - `notes.md:5 “The "blue door" is”`: the quote becomes `The ` and **holds**. Before, **not in file**.
  - `notes.md:3 “see "a.md:2" here”`: the rest of the quote is then scanned, so you get a second reference, `a.md:2` with quote ` here”` (file missing). That breaks `planning/01-prior-art-and-formats.md:37 "Words inside a quote are not scanned for references"`.
- **Why it matters:** curly quotes are often used exactly when the quoted words hold straight marks, for example quoting code. No test covers this.
- **Smallest fix to consider:** after a curly open, look for `”` first, and fall back to `"` only when no `”` follows on the line. Add one test with the case above.

### F2. Low. An opened quote with nothing after it is still "line only", exit 0
- **Where:** `check_citations.py:130 "if not words:"`. It returns line only when the cleaned quote is empty.
- **Failure path (probed):** each of these gives **line only**:
  - `notes.md:3 "` (open mark at the end of the line)
  - `notes.md:3 "   `
  - `notes.md:3 ""`
  - `notes.md:3 "**"`
- **Against the spec:** `planning/01-prior-art-and-formats.md:68 "no quote given"`. Here a quote mark was given.
- **Scope:** F1 named the empty quote as "a smaller case of the same kind", and this commit does not address it. It is rare in practice: a line wrapper keeps `"` attached to the next word, so a wrapped line almost never ends in a lone mark.

### F3. Low. A wrapped quote is checked only on its first line, and still gets a full green
- **Where:** `check_citations.py:65 "end = close.start() if close else len(text)"`.
- **Failure path (probed):** `See notes.md:6 "Deliveries arrive before eight and are` followed by the report line `signed for at the back door."` gives **holds**. The real line 7 says "front desk"; the words on the second report line are never compared.
- **Scope:** this is better than the old line only, and it matches what the brief asked for ("checked on its first line's words"). But "holds" claims more than was checked. If that is accepted, it is worth one line in the decisions log.

**Note on the end-of-line rule (not a finding):** an unclosed quote swallows a later reference on the same line. `notes.md:3 "kettle, see also notes.md:4` gives one reference, **not in file**. Before the fix it gave two references, both line only (green). This hardly matters:
- The line is red either way, so the run fails.
- Once the author closes the quote, the second reference is checked.
- The only cost is that the summary count is one short until then.

A straight open with a curly close, `notes.md:3 "under a minute”`, gives **not in file**, with `”` inside the quote. Before the fix it was line only. Red is the safe side, though the message does not say why.

### Coverage
| Item | Status |
|---|---|
| Task 4 review F1 section (`planning/reviews/task-4-review-1.md:25-34`) | Compared: each of its four failure paths and the empty-quote case probed against the code before and after the fix |
| 01 section 2 (quote rule, lines 25-45) | Compared: line 32 "first `"..."` ... same line" and line 37 "not scanned for references" |
| 01 section 4 (seven verdicts, lines 63-75) | Compared: no new verdict; unclosed quotes map onto the existing red ones |
| The diff (`git show a95a1be -- check_citations.py tests/test_check_citations.py`) | Compared against the export's `check_citations.py` and test file |
| Run 1: probes on the export with tests/fixtures | Compared: 20 inputs |
| Run 2: export unittest discover | Compared: 29 tests OK; also the five old shapes run on a7bbd9b and on the fix, same results |
| Run 3: a7bbd9b checker + post-fix tests, FindTests | Compared: 2 failures, named above |
| The command line's output and exit code for these cases | Not compared: I ran `check()` directly, not `main()`; exit code worked out from the RED set at `check_citations.py:141` |
| Rest of the review file, 01 sections 1, 3 and 5, other tests | Not compared: outside the three questions |

I changed nothing in the repo. The temp folder was made and removed as the rule says.
