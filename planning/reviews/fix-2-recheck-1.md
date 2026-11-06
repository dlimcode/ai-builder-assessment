(Commit hashes updated after the 7 Nov fix-session history rewrite, on Danish's instruction: old-to-new map in planning/decisions.md.)

(Edited on Danish's instruction, 7 Nov: a real folder name in the test's example was replaced by the invented "Zephyr"; "Old Shoebox" is a listed generic path, so that test case could not use it.)

Recheck of a214578: F1 and F2 are fixed. All 15 of the review's failure paths, plus its question case, now exit 1 and the log is not written. The fixed tree passes 63 tests. Seven of the new test inputs fail on 2c988d0. What the fix touched still works.

There is one gap left, and it was already there before this fix. A folder under `~/Documents` whose name starts with a quote, a bracket, `#` or an emoji still passes, even though the fix's comment says no folder may follow. There is also one Low boundary gap.

### F1. Medium. A folder under `~/Documents` that starts with a quote or a symbol still passes
- **Where:** `scrub.py:288 "(?:/(?!\s*[\w.-])|(?!\s*/)(?![\w.-]))"`. After the `/`, the check looks only for a letter, digit, `_`, `.` or `-`, so any other first character counts as "no folder".
- **Failure path:** list entry `<home>/Documents`, log `cd ~/Documents/"Client Files"/x`. Result: exit 0, log written, "private list: 0 hits", and the hit is listed only under "generic pattern hits".
  - This is the normal shell form: `~` does not expand inside quotes, so an agent writes the quote after the `/`.
- **Same result (exit 0, written)** for:
  - `~/Documents/(Old) Clients/x`
  - `~/Documents/#Inbox/x`
  - `~/Documents/'Client Files'/x`
  - `~/Documents/<folder emoji> Clients/x`
  - `~/Documents/\n(Old) Clients`
  - the raw home path with `/Documents/[Old] Clients/x`
- **Controls:** `~/Documents/Étude/x` (an accented first letter) exits 1, and so does `~/Documents/Zephyr`.
- **Not new:** 2c988d0 passes every one of these inputs too. But the rule "`~/Documents/<folder>` still fails" (`planning/decisions.md:246`) and the new comment "a bare ~/Documents (no folder after it, even past a line break)" (`scrub.py:282`) are still not true.
- **Side gap, outside this fix:** entry `<home>/Documents/Client Files` gets no hit at all on `~/Documents/"Client Files"/x`, because the quote breaks the literal match.
- **Test gap:** no test input has a folder that starts with a symbol (`tests/test_scrub.py:306`).
- **Possible fix:** list what may follow the bare `/` instead of what may not. Allow only end of text, or a closing mark (`` ` ``, `'`, `"`, `)`) followed by whitespace or end. The cost: more bare mentions would fail, which is the safe side.

### F2. Low. The end check counts only ASCII letters and digits, and stops at a line break
- **Where:** `scrub.py:285 "spaced(s) + r"(?![A-Za-z0-9])""`.
- **Failure path:** entry `Alex`, log `/Users/alex-tan/x`. Result: exit 0, written, hit reported as generic. The control `/Users/alextan/x` exits 1.
- **Same result (exit 0)** for:
  - `/Users/alex_tan/x`
  - `/Users/alexéa/x`
  - `/Users/alex\nandra/work`, while unwrapped `/Users/alexandra/work` exits 1
  - entry `Shoebox` with `Old Shoebox\nHoldings`, while unwrapped exits 1
  - entry `example` with `@example.com\nmunity`, while unwrapped exits 1
- **Why only Low:** the entry has to be part of one of the made-up phrases. A hit that runs past the phrase (entry `alex-tan`, `Alexandra`) fails, because the position check catches it. Still, `scrub.py:284 "a longer word that starts with one, is still failed"` is not true for these inputs.
- **Possible fix:** `(?!\s*[\w-])`, as the review suggested.

### Notes
- **The review's question:** `~/Documents/ Clients` (a space on the same line) now exits 1 with entry `<home>/Documents`. On 2c988d0 it exited 0. It is in the test.
- **The decisions entry overstates the test:** "The reviewer's ten failure paths are in the test, red on 2c988d0" (`planning/decisions.md:262`).
  - The test adds 7 inputs, and all 7 are red on 2c988d0.
  - It leaves out: the raw home path wrapped, entry `Documents/Clients`, `Old Shoebox Holdings`, `example.community`, `alex acme`, `someonelse` and `Tan/Users`.
  - I ran all of those end to end, and every one exits 1 now.
- **The old `<generic>` note is closed:** entry `generic` with `/Users/alex/x` now exits 0 (it was exit 1 on 2c988d0).
- **`flatten` and `match` still work:**
  - Three `İ` characters (each becomes two when lower-cased) placed before `/Users/alex x` still give a generic hit for entry `alex`.
  - Entry `İstanbul Ltd` wrapped across lines still fails.
  - The inserted space takes the place of the next character. A pattern never starts or ends with a space (`scrub.py:227` splits and re-joins it), so the space is never checked as a hit's end.
  - The no-space pass still counts only matches across lines (`scrub.py:239`): `cl\naude-501` with entry `claude-501` is still generic.
  - No other caller uses `flatten` or `match` (grep over the tree; only `scrub.py` itself and the tests).
- **`--check-only`, username hits and the report are unchanged:**
  - Check-only behaves as before (no spans passed): `Alexandra` exits 1, `/Users/alex/x` with entry `alex` exits 1, and entry `/tmp` is reported as generic.
  - Username hits are listed the same in both modes, old and new.
  - The report header is word for word the same; only the source line was re-wrapped.
  - On a mixed log (line 2 `/Users/alex/x and Alex wrote`, line 3 `/Users/alex/y`), line 2 is a list hit and line 3 a generic hit, the same as before.
- **Not checked:** "Stand-in list run on the real export: written, 0 hits" (`planning/decisions.md:263`), because the real export and list are not in the tree.

### Runs
- **Fixed tree:** `timeout 200 python3 -m unittest discover -s tests` gives 63 tests, OK.
- **Test against the old code:** I copied the fixed tree to a temp folder and swapped in `scrub.py` from 2c988d0. 63 tests ran, 7 failed, all subTests of `test_generic_text_in_the_export_is_reported_not_failed`. Those 7 are the 7 new inputs; the 3 older inputs pass on both.
- **Probes:** two scripts ran old and new `scrub.py` end to end on 55 made-up list/log pairs in temp folders. Each run recorded the exit code, whether the log was written, the count of generic hits and the report sections. The temp folders were removed.

### Coverage
| Source | Status |
|---|---|
| fix-2-review-1.md | Compared: read in full. Reran all 15 F1/F2 failure paths, both controls, the space question and the `<generic>` note on old and new. All fixed. |
| the diff | Compared: read in full and checked every changed line against its stated intent. F1 and F2 above come from `scrub.py:282-288`. |
| scrub.py | Compared: read in full and ran old and new on 55 probes, plus `--check-only` and username cases. Not compared: passes 1-4, which the fix did not touch (run only through the suite). |
| tests/test_scrub.py | Compared: the changed test (lines 287-311) and the fixtures at the top. Ran the whole suite on new code and on old code. Not compared: the older tests, read only through the runs. |
| decisions 03:06 entry | Compared: read it. "Ten failure paths" overstates the test (7 new inputs). "No folder after it" is not true (F1). The real-export claim was not checked (export not in the tree). |
