# Demo script: about five minutes, six points (planning/03-plan.md section 4; red moment by card 3, answer a)

Run everything from the repo root. Each command is real and its output below was measured on 7 Nov 2026; re-run
before recording and update any number that moved.

## 1. What it does (45 s)
- One line: "Checks that the words an AI report quotes are really on the file line it cites."
- Run it on the planning team's own notes: `python3 check_citations.py planning/*.md --root .`
- Measured: 89 references hold, 19 red, all real. 18 are the "Found at" column of the golden table in
  `planning/01-prior-art-and-formats.md`, written bare and naming test fixtures, so not found from the repo root.
  One is a true miscite: `planning/README.md` line 113 cites `build-brief.md:15`, but the file is
  `planning/build-brief.md`. Show that red line: this is the real red moment, so no planted edit is needed.

## 2. Tools (20 s)
- Claude Code in the terminal. A planning team of subagents wrote `planning/00-04*.md`.
- The `/build` recipe: tests first, one commit per task, a fresh reviewer agent on the commits for tasks 2, 4 and 7
  and three more at the end, every reply saved in `planning/reviews/`.

## 3. How the agent helped (60 s)
- `git log --reverse --oneline`: the golden set (`test(checker): add golden set before any code`) comes before any
  checker code.
- Read one "helped" entry from `planning/decisions.md`: the dog-food run that found the real miscite.
- Read one "failed, corrected" entry: task 4's review found an unclosed quote coming out green ("line only", exit 0);
  the fix commit checks it instead. Read them from the file; never paraphrase into something it does not say.

## 4. Features and bugs (60 s)
- The seven verdicts (README's table): `wrong line` lists where the words really are.
- `python3 check_citations.py tests/fixtures/report.md --root tests/fixtures`: point at row 3 (`wrong line, found at
  notes.md:3`) and the `/etc/hosts:1` line, `refused: outside root`: an absolute path is never opened.
- The reviewers' notes against the final code: `python3 check_citations.py planning/reviews/*.md --root .`
  Measured: 40 references, 0 red, 37 not checked: the reviewers wrapped their citations in backticks, which the
  checker treats as examples. Say so: an honest limit, and the next rule to give reviewers.

## 5. Cut (40 s)
Three said aloud: `...` inside a quote (taken literally, and the line says it is not supported); fuzzy or
case-blind matching; any model call at run time. The full list is in README, "What was cut".

## 6. Weakest part (45 s)
It cannot tell a file that changed after the report from a citation that was wrong when written; both say
"wrong line". Next: `--at <commit>`, reading each file as it was at that commit with `git show`.
