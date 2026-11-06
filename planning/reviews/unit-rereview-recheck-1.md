## Recheck of 77e261a (F1 and F2 of unit-rereview-fixes): both fixed, the tests pass and go red without the fix; 4 Low findings

(Saved as received. The agent tool neutralised the reminder tag in this reply, writing it as `<\system-reminder>`.)

| Question | Answer |
|---|---|
| 1. Is it fixed | Yes, for every probe both findings asked for (table below). |
| 2. Did it break what it touched | The suite passes: 62 tests, OK. Two new edges let private text through, both Low. |
| 3. Does its test go red without the fix | Yes. With 9791fcf's scrub.py, 3 test cases fail (names below). |

The export at `.review/77e261a/` matches the commit byte for byte (`scrub.py` and `tests/test_scrub.py`, checked with `cmp`).

**Q1 probes.** These ran end to end through `scrub.py` with a made-up private list.

| Probe | Result | The report's "input" line |
|---|---|---|
| F1: two reminders on one line | both cut (block 2), exit 0 | `line 0: input -> input: text` |
| F1: a reminder after `> ` | cut (4 lines), `> ` left on its own line, exit 0 | `line 0: input -> input: text` |
| F1: a reminder after tool output on its line (the third shape in F1's failure path) | still kept, exit 1 on the listed word | text. This is logged on purpose as a known Low in planning/decisions.md ("F1 (tail) ... cannot be told from a tag quoted in code") |
| F2: all records valid | 2 blocks cut | `input: 3 JSON records, 0 other lines kept as text` |
| F2: plus one truncated line | 2 blocks cut, private text gone, exit 0 | `input: 3 JSON records, 1 other lines kept as text` |
| F2: plus one `[1,2]` line | 2 blocks cut, exit 0 | `input: 3 JSON records, 1 other lines kept as text` |

- The note is printed as a change at "line 0". It does not appear in the `counts:` line. The wording repeats "input" and says "1 other lines"; that is cosmetic only.

**Q3: the tests that fail on 9791fcf's scrub.py**
- `test_a_bad_line_in_a_saved_session_file_keeps_the_records_reading`
- `test_a_reminder_after_text_on_its_line_is_cut`, subtest with two reminders on one line
- `test_a_reminder_after_text_on_its_line_is_cut`, subtest with `> ` before the tag
- Each part of the F1 change is pinned on its own. Taking out only the closed-span removal fails one subtest, and taking out only the `>` fails the other.

### F1. Low. A plain-text export where half or more of the non-blank lines are JSON is now read as records, and each text line's own mark cuts a skill's text after one line
- **Where:**
  - scrub.py:164 "if not records or records * 2 < len(lines):". Before the fix, every line had to be a record.
  - scrub.py:182 "\u23fa line %d, not a JSON record" gives every non-record line a reply mark.
  - scrub.py:55 "lines[j].startswith(\"\u23fa\")" ends a "next message" block at the first such mark.
- **Failure path (probed):**
  - Made-up export: `⏺ Skill`, then `  Base directory for this skill: x`, `  secret-steps one`, `  more steps`, then 5 tool-output lines like `     {"k0": 0}`, then `⏺ reply`.
  - Outcome: `<cut: skill text, 1 lines>`, while `secret-steps one` and `more steps` are kept. Exit 0.
  - The input line does show `input: 5 JSON records, 5 other lines kept as text`.
  - With 4 JSON lines (under half), it stays text and all 4 skill lines are cut correctly.
- **How real:** it needs an export where at least half the lines are bare JSON objects, for example a short session that printed a `.jsonl` file. I have not seen whether `/export` prints tool output in full, so this is unconfirmed.
- **Fix to consider:** give a non-record line a mark that does not start with `⏺`, so a loaded text runs on to the next real reply. Cutting too much is the file's own safe side (scrub.py:23).

### F2. Low. A bad line in a records file is kept almost raw: its own loaded text is not cut, and only `\n` is unescaped
- **Where:** scrub.py:182 "line.replace(\"\\\\n\", \"\\n\")".
- **Failure paths (probed: 2 valid records, then one truncated line):**
  - A truncated skill record, `{"m": "Base directory for this skill: x\nprivate steps are her`, is not cut: the marker sits after `{"m": "`, so it never starts a line. Exit 0, and the unlisted text is kept.
  - `Zephyr\tHoldings` stays as a literal `\t`, so the list entry `Zephyr Holdings` gets no hit. Exit 0.
  - `\u00fc` escapes also miss a listed `Quüxco`. Node's JSON.stringify writes non-ASCII as is, so this half is unlikely. `\t` is real but rare.
  - The asked probe passes: an escaped line break inside a private word (`Zephyr\nHoldings`) is caught by the list check (exit 1).
- **Fix to consider:** cut a bad line whole as `<cut: line N, not a JSON record>`. A truncated line holds nothing the log needs.

### F3. Low. Two parts of the F2 fix have no test
Each of these mutations still passes all 62 tests:
- Removing the unescape at scrub.py:182 (`line` instead of `line.replace(...)`). Without it, the asked `Zephyr\nHoldings` bad line would get past the list check.
- Changing scrub.py:164 to `if not records:`, so a single JSON line would turn any text export into records.

Also:
- The `[1,2]` probe has no test.
- tests/test_scrub.py:202 "self.assertIn(\"input\", [kind for _, kind, _ in changes])" checks only that an "input" note exists, not what it says.

### F4. Low. A `>`-quoted prompt that starts with the tag in prose now cuts the rest of the file
- **Where:** scrub.py:22 "OPENS_LINE = re.compile(r\"[\\s>". A prompt mark now counts as a line start.
- **Failure path (probed):** `> <\system-reminder> blocks should be cut, right?` followed by three more turns becomes `<cut: system-reminder, 5 lines>`, with exit 0. The whole rest of the log is gone, shown only in the block count.
- **Not affected:** `> the <tag> tag ...` (tag mid-line) and ``> `<tag>` `` (in backticks) are left alone, as intended.
- **Why only Low:** this is the 60d5e4b behaviour coming back, and it is the stated trade: cutting too much is safe, and the report shows it. It is worth knowing because this project's own sessions talk about the tag.

**Q2 probes that behave correctly**
- A tag quoted mid-line in code after other text is not treated as a block. This holds both alone and after a closed span on the same line, and the rest of the file is kept.
- A plain-text export with under half its lines as JSON stays text.

**Not in this recheck's scope**
- `planning/STATE.md` is untracked in the main working tree. I did not create it: I wrote only in the temp folder, which is now removed.

## Coverage

| Item | Status |
|---|---|
| unit-rereview-fixes.md F1 section | compared: every probe rerun, including the third shape |
| unit-rereview-fixes.md F2 section | compared: truncated line, `[1,2]`, report path note |
| Rest of unit-rereview-fixes.md | not compared (out of brief) |
| Diff 77e261a, scrub.py and tests/test_scrub.py | compared, export identical to the commit |
| Diff 77e261a, planning/decisions.md | read only its two new entries and the F1-tail Low, to avoid re-filing a known item |
| Test suite in the export | run: 62 tests, OK |
| Q2 probes (code quote, `>` prose, under/at/over half JSON, escaped break, plus tab, unicode and skill text in a bad line) | run |
| Mutation: 9791fcf scrub.py with post-fix tests | run: 3 fail |
| Single-change mutations (6) | run: 2 caught alone, 2 caught, 2 not caught (F3) |
| A real `/export` or a real session file | not compared (made-up text only, per brief) |
| Other `.review/` folders | n/a (not read) |
