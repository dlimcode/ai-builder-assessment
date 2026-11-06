# Review of ef0fdaa (task 7, the scrub step)

(Saved as received. The agent tool neutralised the reminder tag in this reply, writing it as `<\system-reminder>`.)

**Outcome:** the commit runs and covers every part of task 7's shape, but it lets private text through with exit 0 in at least seven ways I reproduced. Three of them are High: two start-up blocks written on one line, wrapped words on indented lines, and private words left in branch history.

- **Does it run?** Yes. `python3 -B -m unittest tests.test_scrub` gives `Ran 11 tests ... OK`, and `bash -n planning/finish-sitting.sh` prints `ok`. The three exported files are byte-identical to `git show ef0fdaa:<file>` (checked with `cmp`).
- **Does it match the spec?** Yes, point by point:
  - both argument shapes;
  - passes 1 to 5 in order;
  - pass 5 run with line breaks removed and with line breaks as spaces;
  - username hits in their own section;
  - a list hit exits 1 and writes no output file;
  - the report has counts, line/kind/placeholder for each change, and the last line `private list: 0 hits`;
  - finish-sitting.sh uses mktemp, writes logs/raw → logs/session.txt, checks `git ls-files` and `git log --format=%B main..HEAD`, and leaves the reports in the temp folder.
  - One difference: 02 §3 gives a 3-argument form. The code follows task 7's 4-argument form, which is correct.
- **Mutation test:** two mutations on the riskiest lines both left the tests at `OK`. Details are under "Mutation" below.

All probes used made-up text in a `review7.*` temp folder, which I removed afterwards. Three `scrub.*` report folders left by my finish-sitting probe runs were also removed, after confirming they held only the probe's made-up commits.

### F1. High. Two start-up blocks on one line: the second one's content survives
`scrub.py:44 "if how == "closing tag" and "<\/system-reminder>" in lines[j]:"` ends the block on the line that holds the closing tag. Line 70 (`i = end`) then moves to the next line, so an opening tag on that same closing line is never seen.
- **Input:** `<\system-reminder>\none\n<\/system-reminder><\system-reminder>\nGit user: SECRETUSER\nCurrent branch: x\n<\/system-reminder>`
- **Result:** `<cut: system-reminder, 3 lines>\nGit user: SECRETUSER\nCurrent branch: x\n<\/system-reminder>`. Exit 0 unless a word is on the list.
- **Is this layout real?** In my own context for this review, two reminders follow each other exactly this way (`<\/system-reminder><\system-reminder>`), and the second one carries git status and user context. Whether `/export` prints them that way is unseen.
- **Nested blocks:** the same rule ends an outer block at an inner closing tag. In the probe, `INNER-LEAK` survived.
- **Fix:** scan the text by character position. Track depth, and cut from each opening tag to its matching closing tag, not line by line.

### F2. High. The "line breaks removed" pass misses wrapped words on indented lines, and any other spacing
At `scrub.py:118 "for joiner in ("", " "):"` the text is joined with "" or " ", but the pattern is matched literally. Leading spaces on the next line therefore stay inside the joined text.
- **Probe:** list entry `Acme Widgets` against each input below; every one gave `hits=[]`:
  - `⏺ the Acme\n  Widgets tender`
  - `⏺ Acme Wid\n  gets`
  - `Acme  Widgets` (two spaces)
  - `Acme\tWidgets` (tab)
  - Acme and Widgets joined by a non-breaking space
- Only an unindented `Acme\nWidgets` is caught.
- **Why it matters:** the test log itself assumes indented continuation lines (`tests/test_scrub.py:45 "  a wrapped description line"`). This pass is what the README says closes the gap "Wrapped paths escaping the scrub".
- **Fix:** before matching, turn every run of whitespace into one space in both text and pattern, and also compare with all whitespace removed.

### F3. High. The tracked-file check reads only the working tree, so private words in earlier branch commits get pushed
`planning/finish-sitting.sh:24 "git ls-files -z > "$tmp/files""` checks the current file contents and `:23` checks the messages, but no commit's diff is checked. The script's own advice, `:37 "fix each by a new commit (nothing is pushed)"`, leaves the word in history.
- **Probe** (temp repo, made-up word `Zephyr`):
  1. One commit adds `Zephyr` to `planning/my notes.md`.
  2. A second commit removes it.
  3. finish-sitting then prints `clean` and `private list: 0 hits | private list: 0 hits`.
  4. `git log -p main..HEAD` still shows 2 lines containing the word.
- This comes from the build brief ("a hit is fixed by a new commit"), but this commit is where it is built.
- **Fix:** also write `git log -p main..HEAD` to the temp folder and pass it to `--check-only`. Change the advice to "rewrite the branch before any push".

### F4. Medium. A list entry written as an absolute path can never match the export
Pass 5 runs only after pass 2 has already replaced the home path with `~` (`scrub.py:183 "hits, users = hit_lines("scrubbed", *list_hits(text, ..."`).
- **Probe:** entry `/Users/alex/Documents/Old Shoebox/Zephyr` against an export reading `/Users/alex/Documents/Old Shoebox/Zephyr/plan.md`.
- **Result:** the output is `~/Documents/Old Shoebox/Zephyr/plan.md` with `hits=[]` and exit 0. The folder name is published.
- 02 §3 says the list holds "paths". The `--check-only` side is not affected, because it checks raw text.
- **Fix:** run pass 5 on the raw export as well, or run the list entries through the same path replacements.

### F5. Medium. An empty, comments-only or BOM-prefixed list reports "0 hits" and writes the log
`scrub.py:148` drops blank lines and lines starting with `#`, and `:142` reads the file as plain `utf-8`. `finish-sitting.sh:10` checks only that the file exists (`-f`).
- **Probe:** each case below gave `exit 0 written=yes last=private list: 0 hits`:
  - an empty list;
  - a list whose only entry is `#Acme Widgets` (a real entry starting with `#` is dropped as a comment);
  - a list starting with a UTF-8 BOM, which `strip()` leaves on entry 1.
- **Fix:**
  - read the list as `utf-8-sig`;
  - refuse a list with no entries (exit 2);
  - drop comment support, which nothing in the spec asks for.

### F6. Medium. An old logs/session.txt survives a failing run
`scrub.py:191-195` skips writing on a hit but never removes an earlier output, and `finish-sitting.sh:21` does not remove it either.
- **Probe:**
  1. Run 1 (clean) writes `logs/session.txt`.
  2. Danish adds a word to the list, or re-exports, and run 2 finds a hit.
  3. Run 2 exits 1 and prints "hits found: fix each by a new commit". `logs/session.txt` still holds run 1's text, which may contain the newly listed word.
- `git add logs/session.txt` then commits it. The advice is also wrong here, because a hit in the export cannot be fixed by a commit.
- **Fix:** `rm -f logs/session.txt` before line 21, and a separate message for a hit in the export.

### F7. Medium. Loaded text ends at the first `> ` line, and indented start markers are not cut at all
`scrub.py:17 "MESSAGE_START = re.compile(r"^(> |⏺)")"` together with `:50` treats any blockquote line inside a rules file or skill as the next prompt. The markers at `:25-27` are anchored at the start of the line.
- **Probe 1:** `Contents of …CLAUDE.md:\n# rules\n> quoted rule\nPRIVATE RULE TEXT` gives `<cut: rules file, 2 lines>\n> quoted rule\nPRIVATE RULE TEXT`.
- **Probe 2:** `Base directory for this skill: x\nintro\n> **Note** quoted\nSKILL BODY LEAK` leaks the same way.
- **Probe 3:** `  ⎿  Base directory for this skill: x` (indented) is not cut at all.
- The export format is unseen (decisions entry, choice 1), so this is a concrete failure on a plausible format. Danish's read of the pass-1 counts is the only check.
- **Fix:** allow leading whitespace and tree glyphs before the markers. End loaded text only at a line starting with `⏺`, or at a `> ` line that follows a blank line.

### F8. Low. Some path spellings escape pass 2
The lookbehind at `scrub.py:107 "(?<![A-Za-z0-9_.-])"` rejects a home path that follows a letter.
- **Survived pass 2:**
  - `/System/Volumes/Data/Users/alex/Documents/x` (the Data volume form of the path, which macOS sandbox texts use);
  - `/users/alex/x` (lowercase, which works on this case-insensitive disk);
  - `%2FUsers%2Falex` (URL-encoded);
  - `C:\Users\alex` (Windows; out of scope on this Mac).
- Each lands only in "username hits (yours to decide)" and still exits 0.
- **Sibling folder:** `<repo>-private/notes` becomes `.-private/notes`. The label is misleading but nothing leaks.
- **Already fine:** a trailing slash, quotes, and `~` already written.

### F9. Low. Token shapes that slip past pass 4
`scrub.py:35-37` misses:
- a private key whose END line is missing (truncated output): the header and body survive;
- `bearer` in lowercase;
- a MAC written with dashes (`0a-1b-…`).

These are within 02's list of shapes, but the unclosed key is the realistic one. Fix: cut from `-----BEGIN … KEY-----` to the end line, or to the end of the file.

### F10. Low. A non-UTF-8 export or list is read with `errors="replace"`, so matches silently fail
At `scrub.py:142 "errors="replace""`, each case below exits 0 with "0 hits":
- a Latin-1 list against a UTF-8 log;
- a UTF-8 list against a Latin-1 log;
- a UTF-16 log containing a listed word.

Probably out of scope (`/export` on macOS writes UTF-8). Fix: read strictly and exit 2 on a decode error.

### Notes (no concrete failure, or by the spec)
- **Report path:** scrub.py does not refuse a report path inside the repo. The report holds list line numbers and username snippets of about 40 characters, never the list words. finish-sitting always uses the temp folder.
- **List folder check:** the "outside the repo" check (`finish-sitting.sh:12-13`) uses the logical path. A symlink into the repo, or a lowercased path, gets past it.
- **Spaces in file names:** handled. `planning/my notes.md` was reported by name. `read -d ''` together with `[ -f ] && set --` does not trip `set -e` (I tested a missing last file: the loop continues).
- **Partial failure:** if scrub.py dies part-way, `status=1`, the output is not written and the `tail` of a missing report just prints an error. The run still exits 1.
- **Run on main:** after a merge, `main..HEAD` is empty and no commit messages are checked.
- **What `--check-only` covers:** pass 5 only, per spec. An email, token or absolute home path in a tracked file exits 0; the path shows up only as a username hit.

### Code the task did not need
Most of the 200 lines are things the spec asks for: six markers, JSON-escaped and dash-encoded path forms, line-tracked changes, a check-only mode and two joins. 02's "about 40" was an underestimate. About 15 lines could go:
- the comment handling in `read_list` (`:146-148`), which also causes part of F5;
- the username de-duplication dict (`:135-137`);
- `hit_lines` as a separate function (`:151-154`);
- the second temp-folder lookups (`:179-180`): `tempfile.gettempdir()` and `TMPDIR` usually give the same folder on this Mac.

### Mutation
Run in temp copies of scrub.py plus its tests.
- **Mutation 1, the riskiest line:** `scrub.py:118` `("", " ")` → `("",)`. Result `OK`, **not caught**. No test has a wrapped multi-word entry like `Acme\nWidgets`. The only wrapped test, `Acme Wid\ngets`, passes with "" alone.
- **Mutation 2:** delete the "rules file" marker at `:27`. Result `OK`, **not caught**. The test's `Contents of …CLAUDE.md` line sits inside a `<\system-reminder>` (`tests/test_scrub.py:36`), so that marker is never tested on its own.

### Coverage
| Source | Status |
|---|---|
| planning/README.md, Task 7 and "What nobody could show" | Compared, item by item against the code and a temp-repo run. All shapes are met. The six blocks are present in BLOCKS (`scrub.py:21-28`), but the rules-file block is untested on its own (mutation 2). |
| planning/02-demo-input-and-logs.md §3 | Compared: pass order, placeholders, report contents, username section. Its 3-argument form differs from task 7's 4-argument form, and the code follows task 7. The "about 40 lines" is addressed above. |
| planning/03-plan.md §7 | Compared: Danish runs the scrub after the session, the report stays outside the repo, and the test uses a made-up log only. All met. |
| planning/build-brief.md, "Logs" and "Secrets and private material" | Compared: "a hit is fixed by a new commit" leads to F3, and "no absolute paths in committed files" is not enforced by `--check-only` (notes). |
| planning/decisions.md, "The scrub: built to 02's five passes" | Compared. Choices 1-3 match the code. Choice 1's "fails safe, not open" holds for an unclosed block but not for F1 or F7. |
| Exported commit (scrub.py, tests/test_scrub.py, finish-sitting.sh) | Compared: `cmp` against the commit, read in full, tests and `bash -n` run, about 30 probes, 2 mutations, 3 finish-sitting runs in a temp repo. |
| A real `/export` file | Not compared: none exists yet and none was in scope. F1's one-line layout comes from my own session context, not from an export. |
| planning/04-devils-advocate.md:23 (cited by Task 7) | Not compared: outside the read list. |
