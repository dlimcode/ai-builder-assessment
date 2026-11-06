# Options considered, and why a citation checker (6 Nov 2026)

**Picked: a citation checker for agent-written reports.** It reads a markdown report, finds each reference like
`notes.md:32 "under a minute"`, opens that file, checks the quoted words are on that line, and marks it green or red,
with where the words really are when red.

## How the pick was made

Before any code, a small team of agents (Claude Code subagents, one file each, each wave reading the last) mapped the
problem space: what the assessment asks for, what take-home submissions usually look like, and what fits one 3-4 hour
sitting. Ten candidates came out of it; a scope check cut each to one sitting, and a devil's advocate attacked each.
None of the survivors settled it for me; the pick came from my own list of repeat mistakes, last row below.

| Option | The moment that shows it working | Why it was not picked |
|---|---|---|
| Ask-these-documents tool that cites its source or says "not in the documents" | A cited answer, or a refusal | The most common submission shape; kept as the fallback |
| Price-summary checker: an AI summarises public HDB resale prices, code re-checks every number | One sentence turns red | Measured (below): the model got every number right, so the red sentence may never appear |
| Log auditor: reads the coding agent's own session logs, flags loops and repeated failures | "Same test failed 4 times" | Hard to explain in 30 seconds; useful mostly to the person who built it |
| Chat orders to an order sheet for a home food seller | "Pickup time: not found", with a question back | Close to the common text-to-fields shape |
| **Citation checker for agent reports** | A confident report, one command, one reference turns red | **Picked** |

## The measurement that changed the pick

The price-summary checker needs the model to get a number wrong. Before choosing it, I tested that: 236 real HDB resale
rows (data.gov.sg, "Resale Flat Prices", three towns, June 2024), six medians computed in Python, then the same six
asked of `claude -p` with its tools turned off (`--tools ""`), twice. 12 of 12 answers were exactly right, about 24
seconds a call. Only medians, six groups and 236 rows were tried, but it was enough to stop betting the demo on a
model mistake.

## Why the citation checker

- **A real, repeated problem.** Agent-written reports quote a source and a line number; when the line number or the
  quote is wrong, the reader checks the wrong line and a decision can rest on it. It is a repeat
  mistake in my own notes: one of eight that each came back more than once this month.
- **It needs no luck to work.** The checker is plain code: no model call at run time, no API key, Python standard
  library, one command.
- **It runs on real agent output.** The `planning/` folder of this repo is written by agents with references like
  these, so the checker's first real input is its own planning notes.
- **Its limits, stated up front:** whether a fresh agent report miscites anything is not guaranteed, so the demo shows
  what it finds rather than a planted error; there is no AI inside the product, only in how it was built.

## Facts checked while choosing (6 Nov 2026)

- `claude --help`: `-p` (print mode), `--output-format stream-json`, `--json-schema`, `--tools`, `--bare`; no
  temperature or seed flag.
- Anthropic's legal page (code.claude.com/docs/en/legal-and-compliance, read 6 Nov 2026): products should use API key
  authentication and may not route requests through Free, Pro, Max or Ultra plan credentials on users' behalf. This
  tool makes no model call at run time, so the question does not arise for a reviewer.
- data.gov.sg "Resale Flat Prices": 244,315 rows from January 2017, Open Data Licence.
