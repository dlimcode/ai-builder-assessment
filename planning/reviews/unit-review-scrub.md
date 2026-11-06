# Unit-end review 3: the log scrub as a whole (354f07e)

(Commit hashes updated after the 7 Nov history rewrite, on Danish's instruction: old-to-new map in planning/decisions.md.)

(Saved as received, with two edits. The agent tool neutralised the reminder tag in this reply, writing it as `<\system-reminder>`. On Danish's instruction, a real folder name in the F5 example is replaced by the invented "Old Shoebox".)

**Outcome:** the tests pass (`Ran 20 tests ... OK`) and `bash -n` prints `ok`. I still found 10 findings, 2 questions and 1 mutation that the tests do not catch:
- **High:** one. The task's fallback is to scrub the saved session file if `/export` fails. That file is the only format anyone measured, and on it pass 1 cuts nothing, while a wrapped name passes pass 5.
- **Medium:** six. Three of them were introduced by the two fix commits.
- **Speed:** fine on ordinary text. A 5 MB made-up export scrubs in 1.4 s, and pass 5 takes another 1.4 s.
- **What the script writes:** in a throwaway repo, `finish-sitting.sh` wrote only `logs/session.txt` and its own temp folder.

### F1. High. On the saved session file, pass 1 cuts nothing and a wrapped name passes pass 5
`planning/README.md` Task 7 says: "if `/export` fails, scrub the saved session file instead". The gap table says the saved session file "carries every start-up block".
- **Why the markers miss:** the markers in `scrub.py:17` `LEAD = r"^[\s...]*"` and `scrub.py:24-28` are anchored to the start of a line. In a one-JSON-object-per-line file, every marker sits inside a JSON string after a literal `\n`, so none of them fires. Only the `<\system-reminder>` cut works, because it goes by character position.
- **Why pass 5 misses:** a line break inside a JSON string is the two characters `\` and `n`. `flatten` (`scrub.py:152-168`) does not treat them as whitespace, so `Zephyr\nHoldings` matches neither of the two passes (`scrub.py:176`).
- **Repro:** I built 5 made-up JSON lines holding a skill's text, hook output, sandbox text, a skills list, and a Write call with `about Zephyr\nHoldings`.
  - Result: `blocks cut: 0`, and pass 5 found `[]` against the list `Zephyr Holdings`.
  - The real run would exit 0 and write all of it, with only paths shortened to `~`.
- **Confidence:** I am taking the file to be JSON lines (Claude Code's session store) without having seen it. That is about 85% sure.

### F2. Medium. Indented skills list or sandbox text: the rest of the log is cut, slowly (introduced by 2aa7047)
- **Cause:** `scrub.py:25` now accepts an indented marker (`LEAD + "The following skills are available"`). The end test at `scrub.py:55` still needs an unindented item: `any(l.startswith("- ") for l in lines[i:j])`.
- **What happens with indented items (`  - design: ...`):** the block runs to the end of the file. The log becomes one line, `<cut: skills list, N lines>`, and the run exits 0.
- **It is also quadratic, because `any(...)` re-scans from the marker at every blank line:**

| Lines in the export | Time |
|---|---|
| 10,004 | 2.0 s |
| 20,004 | 8.1 s |
| 40,004 | 32.7 s |

  A 200,000-line export would take minutes. That is the stuck run that would push Danish to skip the scrub.
- **Same for the sandbox text:** an indented `## Bash command sandbox` ends only at a heading in column 0 (`scrub.py:49` `HEADING.match`), so it also cuts to the end of the file. This is by reading; not run.

### F3. Medium. One unclosed `<\system-reminder>` anywhere cuts the rest of the log, exit 0
- **Cause:** `scrub.py:75` `out.append(reminder_cut(text[start:]) if depth else text[pos:])`. An opening tag with no closing tag cuts to the end of the file. A real reminder after it only pushes the depth to 2 and back to 1.
- **Why it will happen:** this sitting built the scrub, so its export quotes the tag many times (in `tests/test_scrub.py:36`, in greps and in commands).
- **Repro:** a made-up export with the reply line `⏺ Bash(grep -n "<\system-reminder>" tests/test_scrub.py)` followed by 506 lines. Result: `2 lines left of 507`, and the run would exit 0.

### F4. Medium. A blockquote in a loaded recipe ends the cut early, and the rest of the recipe is kept (introduced by 354f07e)
- **Cause:** `scrub.py:52-53` ends "next message" at `lines[j].startswith("> ") and not lines[j - 1].strip()`. In markdown, a blockquote normally follows a blank line.
- **Repro:** skill text `# Build recipe\nStep one.\n\n> Note: quoted guidance\n\nRECIPE-REST private steps follow`.
  - Result: `<cut: skill text, 4 lines>`.
  - `> Note...` and `RECIPE-REST private steps follow` stay in the log. Only pass 5 stands behind it.
- **Not checked:** whether the real `/build` recipe has such a line. It lives outside the repo, which this review may not read.

### F5. Medium. A list entry written as a folder path with a trailing slash misses the folder named without one
- **Cause:** `scrub.py:139` `with_path_forms` keeps the trailing `/`, and `scrub.py:179` matches the entry as written.
- **Repro:** entry `/Users/alex/Documents/Old Shoebox/Zephyr/`:

| Text in the export | Hits |
|---|---|
| `ls /Users/alex/Documents/Old Shoebox/Zephyr` | `[]` |
| `see .../Zephyr.` | `[]` |
| `cd .../Zephyr/x` | 1 |

- 02 §3 says the list is "paths, folder and company names", so path-shaped entries are expected.

### F6. Medium. The main branch's history is never checked, and all of it goes public
- **Cause:** `planning/finish-sitting.sh:24` `git log -p main..HEAD`. The repo has no remote (`git remote -v` is empty), so main's 3 commits are unpushed and will be published along with the branch.
- **Repro:** in a throwaway repo, a main commit adds `plan for Zephyr Holdings` and a second main commit removes it. Result: `private list: 0 hits | private list: 0 hits`, "clean.", `exit=0`. `git log -p main` still shows the word twice.

### F7. Medium. Hits that cannot be found: the report points at a file that is not written, and the no-space pass makes hits across word boundaries
- **The report points at a missing file:** `scrub.py:215` reports `scrubbed line N`, but on a hit `scrub.py:256-259` writes no scrubbed log. Pass 1 also moves line numbers. In the repro, the word was on raw line 13 and the report said `scrubbed line 6`.
- **Hits across word boundaries:** the all-whitespace-removed pass (`scrub.py:176` `for space in (" ", "")`) matches short entries across two words. On the repo's own 94 KB of planning prose, made-up names gave:

| Name | Spaced pass | No-space pass |
|---|---|---|
| `Sato` | 0 | 4 |
| `Ito` | 3 | 21 |
| `Orla` | 0 | 1 |

- **What Danish is left with:** `finish-sitting.sh:36` tells him "Take the word out of the export", but grepping the raw export finds no such word. He is stuck, and the easy way out is to shorten the list.

### F8. Low. A relative list path breaks when run from another folder, with misleading messages
- **Cause:** `finish-sitting.sh:10` checks `"$list"` against the caller's folder, then `:14` runs `cd "$repo"`, then `:21` opens it relative to the repo.
- **Repro:** run from another folder with `mylist.txt`. Result: two `FileNotFoundError` tracebacks, then "hits in the export ..." and "the branch must be rewritten before any push", exit 1.
- It fails safe. Danish's own rule (every path absolute) mostly prevents it.

### F9. Low. The email pattern is quadratic on a long run of characters without a space
`scrub.py:30` `EMAIL`, on a run of characters it accepts with no `@`:

| Input | Time |
|---|---|
| 40k letters | 2.2 s |
| 80k letters | 8.7 s |
| 100k hex characters | 13.6 s |

A 1 MB hex or hash line would take tens of minutes. Base64 is safe, because `/` breaks the run every few hundred characters at most. The other secret patterns took 0.00 s.

### F10. Low. `main` wiring of path-shaped entries is untested (mutation)
I changed `scrub.py:248` from `list_hits(text, with_path_forms(entries, paths), user)` to `list_hits(text, entries, user)` in a temp copy. Result: `Ran 20 tests ... OK`, **not caught**. The test at `tests/test_scrub.py:132-135` calls `with_path_forms` directly, never through the command line.

### Questions (under 80% sure)
- **Box borders and table cells:** if `/export` keeps box borders (the start-up banner, wrapped table cells), a name split as `Zephyr │\n│ Holdings` flattens to `zephyr││holdings` and matches nothing. The username split the same way would not even show as a username hit. Does `/export` keep those characters?
- **Staged content:** `finish-sitting.sh:25-28` checks the working tree, not what is staged. Content staged and then edited would be committed unchecked. Is this worth a line in the script?

### Code no task needed
Nothing new beyond the earlier review's list.

### finish-sitting.sh end to end (throwaway repo, made-up list `Zephyr Holdings`)

| Case | Last lines | Message | Exit | New in the repo |
|---|---|---|---|---|
| Clean | `0 hits \| 0 hits` | "clean." | 0 | `logs/session.txt` |
| Hit in a tracked file | `0 hits \| 2 hits` | must rewrite the branch | 1 | `logs/session.txt` |
| Hit only in history | `0 hits \| 2 hits` | same | 1 | `logs/session.txt` |
| Hit only in the export (wrapped) | `1 hits \| 0 hits` | session.txt not written | 1 | nothing |
| Hit only in main's history | `0 hits \| 0 hits` | "clean." (F6) | 0 | `logs/session.txt` |
| Relative list path from another folder | blank | both hit messages plus tracebacks (F8) | 1 | nothing |

Outside the repo it wrote only `TMPDIR/scrub.XXXXXX/{branch-history.txt,files,scrub-report.txt,check-report.txt}`. That folder is left in place for Danish to read.

### Does it run
- `timeout 180 python3 -B -m unittest tests.test_scrub`: `Ran 20 tests in 1.902s`, `OK`.
- `bash -n planning/finish-sitting.sh`: `ok`.

### Coverage
| Source | Status |
|---|---|
| planning/README.md, Task 7, Task 13, "What nobody could show" | Compared against the code and runs. The fallback to the saved session file gives F1. Task 13's "a hit is fixed by a new commit" holds only for branch history, not main's (F6). The tables-and-wrapping gap is left as a question. |
| planning/02-demo-input-and-logs.md §3 | Compared pass by pass. "Any hit ... exit non-zero" holds. Path-shaped entries can still miss (F5). The report's line numbers cannot be used when there is a hit (F7). |
| planning/03-plan.md §7 | Compared. Danish runs it after the session, and the report stays outside the repo (checked on disk). The made-up-log-only tests hold. |
| planning/build-brief.md, "Logs" and "Secrets and private material" | Compared. "Checks every tracked file and every commit message" misses main's commits (F6). Absolute paths in tracked files are still only username hits (already noted in review 1, not repeated). |
| scrub.py, tests/test_scrub.py, finish-sitting.sh, decisions.md scrub entries | Compared by reading the diff ef0fdaa..354f07e, made-up probes, timing runs, end-to-end runs in a temp git repo, and one mutation. decisions.md 01:46 says "fails safe, not open"; that does not hold for F1 or F4. |
| The real `/export` format, the real `/build` recipe, the real private list | Not compared. Out of scope (outside the repo or not yet made), so F1, F4 and the questions rest on stated assumptions. |

All probes used made-up text in `/tmp/claude-501/unit3.E9KceT`, which has been removed. Nothing in the repo was changed.
