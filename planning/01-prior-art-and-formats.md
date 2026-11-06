# 01 Prior art and reference formats (7 Nov 2026)

**Outcome: no tool found checks `path:line "quoted words"` against a local file, so the checker is worth building; below are
the shapes it reads, the match rule, seven verdicts and a 26-row golden set to commit before any code.**

Tags: `[Danish]` his words; `[record path:line "words"]` a repo file read this session; `[source, date read]` an outside
page; `[measured, how]` worked out this session; `[assumed]` a guess or a pick resting on one. Picks are this role's
recommendation, not a decision.

## 1. Prior art (searched 7 Nov 2026)

| Tool | What it does | What it does not do |
|---|---|---|
| citefact 0.3.0 (Python, MIT) | Checks each direct quote in a markdown text is verbatim in its cited source, "normalized + fuzzy"; verdicts include `quote_page_mismatch` (right words, wrong page) [source: pypi.org/project/citefact, released 15 Sep 2026, read 2026-11-07] | Sources are PDFs and page numbers, not local text files and line numbers; needs Python 3.11+ and a 1-2 GB PDF converter on first use [same source] |
| rlm-harness `verify_quote` | A function that treats a quote carrying `cat -n` line numbers as a claim about where it sits; it passes only if the lines are at that spot and occur once [source: github.com/qazbnm456/rlm-harness release v1.9.0, dated "02 Sep" with no year shown, read 2026-11-07] | A function inside an agent harness, not a command that scans a report; the quote must carry its own line numbers; a "closest line" hint was left out on purpose [same source] |
| lychee (link checker) | Checks links and, with `--include-fragments`, heading anchors [source: lychee.cli.rs/recipes/anchors, read 2026-11-07] | Strips GitHub `#L12` line anchors before checking, so a wrong line number is never reported [source: docs.rs lychee-lib 0.24.2 src/quirks/mod.rs, read 2026-11-07] |
| markdown-link-check, markdown crossref skills | Check that a linked file exists; one skill checks `file.py:42` only by counting the file's lines [source: web search snippets for skills.cat markdown-crossref-validator and smithery.ai check-links, read 2026-11-07; the smithery page returned 404 when opened] | Never read the words at the line |
| embedme `--verify` | Fails in CI if code blocks copied into docs (e.g. `// src/x.ts#L44-L82`) differ from the source file [source: npmjs.com/package/embedme 1.22.0, read 2026-11-07] | Works on whole code blocks it owns, not on short quotes in prose |
| SemanticCite and similar research | Model-based checks that a cited paper supports a claim [source: arxiv.org/abs/2511.16198, read 2026-11-07] | Needs a model; the checker must make no model call [record planning/00-options-considered.md:35 "no model call at run time"] |

**Verdict:** nothing found does exactly this; citefact is the closest and the source of two ideas worth taking (a
"right words, wrong place" verdict, and skipping code fences). Not checked: GitHub code search, private tools, and
tools named in languages other than English [assumed]. Close the gap with one GitHub search for `"path:line" quote verify`.

## 2. Reference shapes

| Shape | Example | Pick |
|---|---|---|
| `path:line` | `notes.md:3` | Keep (line-only check) |
| `path:line-line` | `notes.md:6-7` | Keep |
| `[record path:line]`, `[record path:line-line]` | `[record notes.md:3]` | Keep; same parse, the brackets are only a wrapper |
| any of the above + `"words"` | `notes.md:3 "under a minute"` | Keep; the quote is the first `"..."` (straight or curly) right after the line number, same line |
| `path:line:col`, `path#L12`, URLs, paths with spaces | `a.py:3:7` | Cut; a whole URL (from `scheme://` to the next space) is skipped [assumed] |

- **What counts as a path:** a run of letters, digits and `_ . / -` holding at least one `.` or `/`, then `:` and digits.
  This catches `/etc/hosts:1` (so it can be refused, not silently skipped) and skips clock times like `12:30` [assumed].
- **Words inside a quote are not scanned for references**, so `"see a.md:2"` as a quote is one reference, not two [assumed].
- **Skip anything inside backticks or code fences.** They hold examples; the options file shows its sample reference in
  backticks on line 4, which would otherwise go red as "file missing" [record planning/00-options-considered.md:4 "under a minute"].
- **Paths resolve against one root: `--root`, defaulting to the current folder.** Why: the team writes repo-relative
  paths [record planning/00-options-considered.md:38 "the checker's first real input is its own planning notes"], so
  running from the repo root works on any clone, with or without `.git` (e.g. a zip download) [assumed].
  - Case against: run from a subfolder, every reference goes "file missing". Mitigation: the summary line prints the root used.
  - An absolute path in a report is never opened: it is reported "refused: outside root" (row H2).
  - Rejected: the report's own folder (breaks every repo-relative tag in `planning/`); walking up to `.git` (fails on a zip).

## 3. What "the quote is on that line" means

**Pick: exact words after light cleaning, on the cited line (N = 0), case kept.**

| Choice | Pick | What it costs |
|---|---|---|
| Whitespace | Collapse runs to one space, both sides | Hides a changed indent; nobody quotes indents [assumed] |
| Case | Kept | `"Under a minute"` goes red for one capital; in return "exact" stays exact |
| Markdown marks | Strip backticks and `**` from both sides; keep `_` and single `*` | `snake_case` and `a*b` survive; `_italic_` quotes must keep their underscores |
| Near line | N = 0: one line off is red "wrong line", with where the words are | Strict, but a line number that is off by one is exactly the mistake the tool exists to catch [record planning/00-options-considered.md:32 "when the line number or the"] |
| Quote over two lines | Holds if it starts on the cited line and runs into the next (lines joined with one space) | Wrapped markdown paragraphs work; a quote over three lines needs a range |
| Range `a-b` | Holds if the words sit anywhere in lines a..b joined | Wide ranges prove little; no cap in v1 [assumed] |
| `...` inside a quote | Taken literally (cut) | Shortened quotes go red "not in file"; the message should say "`...` is not supported" |

When the words are not on the cited line, search the whole file and list every place they are (first three).

## 4. Verdicts (closed list)

| Verdict | Colour | Exit | When |
|---|---|---|---|
| holds | green | 0 | words on the cited line or range |
| line only | neutral | 0 | no quote given; the line exists |
| wrong line | red | 1 | words elsewhere in the file; prints `found at path:line` |
| not in file | red | 1 | words nowhere in the file |
| no such line | red | 1 | line 0, past the end, or a reversed range; still prints `found at` if the words exist |
| file missing | red | 1 | path not found or not a readable UTF-8 text file |
| refused: outside root | red | 1 | after resolving `..` and symlinks, the path is outside the root |

Exit 2 for usage errors (no such report, bad flag) [assumed]. "Unreadable" folds into "file missing" to keep the list at seven.

## 5. Golden set (commit before the checker exists)

Fixtures live in `tests/fixtures/`, run with `--root tests/fixtures`. Line numbers on the left are not part of the file.

`notes.md` (9 lines):
```
1  # Office notes
2
3  The kettle boils in under a minute.
4  Lunch is served at noon on Fridays.
5  The **blue door** is the side entrance.
6  Deliveries arrive before eight and are
7  signed for at the front desk.
8  Use the `print_report` button twice.
9  Visitors   sign the   paper book.
```
`data/plan.txt` (3 lines):
```
1  Step one: water the plants.
2  Step two: lock the back gate.
3  Step three: water the plants.
```
`empty.md`: 0 bytes. `report.md`: one reference per line, in table order (rows 1-26 plus H1-H4).

| # | Reference | Expected verdict | Found at | Tests |
|---|---|---|---|---|
| 1 | `notes.md:3 "under a minute"` | holds | notes.md:3 | plain |
| 2 | `[record notes.md:4 "noon on Fridays"]` | holds | notes.md:4 | record form |
| 3 | `notes.md:4 "under a minute"` | wrong line | notes.md:3 | off by one |
| 4 | `notes.md:3 "Under a minute"` | not in file | - | case kept |
| 5 | `notes.md:5 "blue door is"` | holds | notes.md:5 | `**` in file |
| 6 | `notes.md:5 "**blue door**"` | holds | notes.md:5 | `**` in quote |
| 7 | `notes.md:8 "print_report button"` | holds | notes.md:8 | backticks stripped, `_` kept |
| 8 | `notes.md:9 "Visitors sign the paper book"` | holds | notes.md:9 | whitespace |
| 9 | `notes.md:6 "before eight and are signed for"` | holds | notes.md:6 | two-line quote |
| 10 | `notes.md:7 "before eight and are signed for"` | wrong line | notes.md:6 | span starts earlier |
| 11 | `notes.md:6-7 "signed for at the front desk"` | holds | notes.md:7 | range |
| 12 | `[record notes.md:3-4 "side entrance"]` | wrong line | notes.md:5 | range, record form |
| 13 | `notes.md:3` | line only | - | no quote |
| 14 | `notes.md:40` | no such line | - | past end |
| 15 | `notes.md:40 "under a minute"` | no such line | notes.md:3 | past end, words exist |
| 16 | `notes.md:0 "Office notes"` | no such line | notes.md:1 | line 0 |
| 17 | `notes.md:7-6 "signed for"` | no such line | notes.md:7 | reversed range |
| 18 | `missing.md:1 "anything"` | file missing | - | |
| 19 | `notes.md:3 "boils in under an hour"` | not in file | - | |
| 20 | `data/plan.txt:2 "water the plants"` | wrong line | data/plan.txt:1, data/plan.txt:3 | many places, subfolder |
| 21 | `data/plan.txt:3 "water the plants"` | holds | data/plan.txt:3 | duplicate, right one |
| 22 | `empty.md:1 "anything"` | no such line | - | empty file |
| 23 | `notes.md:3 “under a minute”` | holds | notes.md:3 | curly quotes |
| 24 | `notes.md:3 "kettle ... minute"` | not in file | - | `...` cut |
| 25 | `` `notes.md:99 "x"` `` (in backticks) | not checked | - | example skipped |
| 26 | `see 12:30 and https://example.com:443/a.md:2` | not checked | - | times and URLs |
| H1 | `../outside.md:1 "x"` | refused: outside root | - | `..` |
| H2 | `/etc/hosts:1 "localhost"` | refused: outside root | - | absolute path |
| H3 | `link-out.md:1 "x"` (symlink to a file outside the root, made by the test in a temp folder) | refused: outside root | - | symlink |
| H4 | `notes.md:99999999999999999999 "x"` | no such line | - | huge number, no crash |

Expected summary for `report.md`: 10 holds, 1 line only, 17 red, 2 not checked; exit 1 [measured, a Python count of the verdict column above].
For H3, the file must never be opened: refuse on the resolved path before reading [assumed].

## Dog-food check

Real tags this file carries, for the checker's first run (all six `[record ...]` tags in this file hold
[measured, a Python check of each against `planning/00-options-considered.md` using the section 3 cleaning, 7 Nov 2026]):
[record planning/00-options-considered.md:3 "Picked: a citation checker"] (needs `**` stripping),
[record planning/00-options-considered.md:39-40 "the demo shows what it finds rather than a planted error"] (range).
