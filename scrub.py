"""Scrub a Claude Code session export before it is committed (planning/02-demo-input-and-logs.md section 3).

    python3 scrub.py <export> <scrubbed-out> <private-list> <report-out>
    python3 scrub.py --check-only <private-list> <report-out> FILE...

Passes: 1 cut start-up blocks whole, 2 this machine's absolute paths, 3 emails, 4 tokens, keys and MACs,
5 the private list (case-insensitive, also on the text with line breaks removed). The private list and the
report stay outside the repo. Exit 0 clean; 1 a private-list hit, and the scrubbed log is not written; 2 usage.
"""
import bisect
import getpass
import os
import re
import sys
import tempfile

LEAD = r"^[\s\u23bf\u2502\u2514\u251c\u2500]*"  # an indent or the export's tree glyphs before a marker
HEADING = re.compile(r"^#{1,2} ")
REMINDER_TAG = re.compile(r"<(/)?system-reminder>")
OPENS_LINE = re.compile(r"[\s\u23bf\u2502\u2514\u251c\u2500]*")
# Pass 1: (kind, start marker, where the block ends). A block whose end is never found runs to the end of
# the file: cutting too much is safe, the report shows it.
BLOCKS = [
    ("system-reminder", re.compile(r"^<cut: system-reminder, \d+ lines>$"), "this line"),
    ("sandbox text", re.compile(LEAD + r"## Bash command sandbox"), "next heading"),
    ("skills list", re.compile(LEAD + r"The following skills are available"), "end of list"),
    ("skill text", re.compile(LEAD + r"Base directory for this skill"), "next message"),
    ("hook output", re.compile(LEAD + r"SessionStart"), "next message"),
    ("rules file", re.compile(LEAD + r"Contents of .*CLAUDE\.md"), "next message"),
]
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
SECRETS = [
    ("secret", re.compile(r"sk-ant-[A-Za-z0-9_-]+")),
    ("secret", re.compile(r"ghp_[A-Za-z0-9]+|github_pat_[A-Za-z0-9_]+")),
    ("secret", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("secret", re.compile(r"xox[bp]-[A-Za-z0-9-]+")),
    ("secret", re.compile(r"Bearer\s+[A-Za-z0-9._~+/=-]+")),
    ("secret", re.compile(r"-----BEGIN [A-Z ]*KEY-----[\s\S]*?-----END [A-Z ]*KEY-----")),
    ("mac", re.compile(r"(?<![0-9A-Fa-f:])[0-9A-Fa-f]{2}(?::[0-9A-Fa-f]{2}){5}(?![0-9A-Fa-f:])")),
]


def block_end(lines, i, how):
    """Index of the first line after the block that starts at lines[i]."""
    if how == "this line":
        return i + 1
    for j in range(i, len(lines)):
        if j == i:
            continue
        if how == "next heading" and HEADING.match(lines[j]):
            return j
        # Only a reply ends it: a quoted line inside a rules file or skill looks like a prompt. The prompt after
        # the loaded text is cut with it, which is safe.
        if how == "next message" and lines[j].startswith("\u23fa"):
            return j
        if how == "end of list" and not lines[j].strip() and any(l.startswith("- ") for l in lines[i:j]):
            return j + 1
    return len(lines)


def cut_reminders(text):
    """Cut each outermost reminder block, from its opening tag to the matching closing tag (or the end of the
    file), wherever on a line the tags sit; the cut stands on its own line."""
    out, depth, start, pos = [], 0, 0, 0
    for m in REMINDER_TAG.finditer(text):
        if m.group(1) is None:
            before = text[text.rfind("\n", 0, m.start()) + 1:m.start()].replace("</system-reminder>", "")
            if depth == 0 and not OPENS_LINE.fullmatch(before):
                continue  # a tag quoted mid-line, e.g. in code, is not a block
            if depth == 0:
                out.append(text[pos:m.start()])
                start = m.start()
            depth += 1
        elif depth:
            depth -= 1
            if depth == 0:
                out.append(reminder_cut(text[start:m.end()]))
                pos = m.end()
    out.append(reminder_cut(text[start:]) if depth else text[pos:])
    return "".join(out)


def reminder_cut(block):
    return "\n<cut: system-reminder, %d lines>\n" % (block.count("\n") + 1)


def cut_blocks(text):
    """Pass 1: each start-up block becomes one line, so later line numbers match the scrubbed file."""
    lines, out, changes, i = cut_reminders(text).split("\n"), [], [], 0
    while i < len(lines):
        block = next(((kind, how) for kind, start, how in BLOCKS if start.search(lines[i])), None)
        if not block:
            out.append(lines[i])
            i += 1
            continue
        end = block_end(lines, i, block[1])
        placeholder = lines[i] if block[1] == "this line" else "<cut: %s, %d lines>" % (block[0], end - i)
        out.append(placeholder)
        changes.append((len(out), "block", placeholder))
        i = end
    return "\n".join(out), changes


def machine_paths(repo, home, temps):
    """Pass 2's (literal, placeholder) pairs, longest first: plain, JSON-escaped and dash-encoded forms."""
    pairs = {}
    for path, placeholder in [(home, "~")] + [(t, "<tmp>") for t in temps] + [(repo, ".")]:
        path = path.rstrip("/")
        if path:
            pairs[path] = placeholder
            pairs[path.replace("/", "\\/")] = placeholder
    pairs[re.sub(r"[^A-Za-z0-9]", "-", home.rstrip("/"))] = "~"
    pairs[re.sub(r"[^A-Za-z0-9]", "-", repo.rstrip("/"))] = "<repo-folder>"
    return sorted(pairs.items(), key=lambda kv: -len(kv[0]))


def line_of(text):
    starts = [0] + [m.end() for m in re.finditer("\n", text)]
    return lambda pos: bisect.bisect_right(starts, pos)


def replace(pattern, text, kind, placeholder, changes):
    """Replace each match, keeping its line breaks so line numbers do not move; log line and kind."""
    line = line_of(text)

    def swap(m):
        changes.append((line(m.start()), kind, placeholder))
        return placeholder + "\n" * m.group(0).count("\n")

    return pattern.sub(swap, text)


def replace_paths(text, paths, changes):
    for literal, placeholder in paths:
        pattern = re.compile(r"(?<![A-Za-z0-9_.-])" + re.escape(literal) + r"(?![A-Za-z0-9_])")
        text = replace(pattern, text, "path", placeholder, changes)
    return text


def with_path_forms(entries, paths):
    """Each list entry, plus its form after pass 2 (an entry written as a home path reads `~/...` in the
    scrubbed log), as alternatives under the entry's own number."""
    return [(e, replace_paths(e, paths, [])) for e in entries]


def scrub(text, paths):
    """Passes 1-4. Returns (scrubbed text, [(line, kind, placeholder)])."""
    text, changes = cut_blocks(text)
    text = replace_paths(text, paths, changes)
    text = replace(EMAIL, text, "email", "<email>", changes)
    for kind, pattern in SECRETS:
        text = replace(pattern, text, kind, "<%s>" % kind, changes)
    return text, sorted(changes)


def flatten(text, space):
    """Lower-cased text with each whitespace run (line breaks, indents, tabs, no-break spaces) turned into
    `space`, and the line each kept character came from."""
    chars, lines, line, gap = [], [], 1, False
    for c in text:
        if c.isspace():
            line += c == "\n"
            gap = True
            continue
        if gap and chars and space:
            chars.append(space)
            lines.append(line)
        gap = False
        for low in c.lower():
            chars.append(low)
            lines.append(line)
    return "".join(chars), lines


def list_hits(text, patterns, username):
    """Pass 5. Returns (hits as (line, list entry number), username hits as (line, 40 characters around)).
    Matched twice: whitespace runs as one space, and all whitespace removed, so a word split by terminal
    wrapping, an indent or a tab still matches."""
    hits, user_lines = set(), {}
    for space in (" ", ""):
        flat, lines = flatten(text, space)
        for n, forms in enumerate(patterns, 1):
            for p in {space.join(f.lower().split()) for f in ((forms,) if isinstance(forms, str) else forms)}:
                hits.update(match(p, flat, lines, n, space.join(username.lower().split()), user_lines, space == ""))
    return sorted(hits), sorted(user_lines.items())


def match(p, flat, lines, n, user, user_lines, crossing):
    """(line, entry number) for each place p is in flat; the username's places go to user_lines instead."""
    found = set()
    if not p or p in ("~", ".", "<tmp>", "<repo-folder>"):
        return found  # a blank entry, or one that was only a machine path
    for m in re.finditer(re.escape(p), flat):
        if crossing and lines[m.start()] == lines[m.end() - 1]:
            continue  # with spaces removed, only a word split across lines counts, or "Tan" hits "that answer"
        line = lines[m.start()]
        if p == user:
            user_lines.setdefault(line, flat[max(0, m.start() - 20):m.end() + 20])
        else:
            found.add((line, n))
    return found


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def read_list(path):
    """List entries, numbered by their line in the list file (blank lines keep their number, match nothing).
    Every other line is an entry, even one starting with #. An empty list is refused: it would pass anything."""
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        entries = [l.strip() for l in f.read().split("\n")]
    if not any(entries):
        print("stop: the private list %s has no entries" % path, file=sys.stderr)
        sys.exit(2)
    return entries


# List entries that are generic path roots or folder names: scrub.py and its tests must name them, so their hits
# are reported for Danish to read, never failed. An entry counts as generic only if it is exactly one of these
# (any case, a trailing / ignored); "/Users/someone" or "Documents/Clients" is not.
GENERIC = {"/users", "/private", "/private/tmp", "/private/var/folders", "/var/folders", "/tmp", "/home", "/volumes",
           "documents", "developer", "~/documents", "~/developer", ".claude", "~/.claude"}


def split_generic(entries):
    """(private entries, generic entries), each keeping every entry's number; the other side holds a blank."""
    generic = [e if e.lower().rstrip("/") in GENERIC else "" for e in entries]
    return [e if not g else "" for e, g in zip(entries, generic)], generic


def hit_lines(name, hits, user_hits):
    out = ["%s line %d: list line %d" % (name, line, n) for line, n in hits]
    users = ["%s line %d: ...%s..." % (name, line, context.replace("\n", " ")) for line, context in user_hits]
    return out, users


def write_report(path, body, hits, users, generic):
    tail = "private list: 0 hits" if not hits else "private list: %d hits (listed above)" % len(hits)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(body + ["", "username hits (yours to decide):"] + (users or ["none"])
                          + ["", "generic pattern hits (allowed, not failed; the set is GENERIC in scrub.py):"]
                          + (generic or ["none"]) + ["", "list hits:"] + (hits or ["none"]) + ["", tail]) + "\n")
    if generic:
        print("generic pattern hits: %d (allowed; read them in %s)" % (len(generic), path))


def main(argv):
    user = getpass.getuser()
    if argv[:1] == ["--check-only"] and len(argv) >= 4:
        private, generic = split_generic(read_list(argv[1]))
        all_hits, all_users, all_generic = [], [], []
        for name in argv[3:]:
            text = read(name)
            hits, users = hit_lines(name, *list_hits(text, private, user))
            all_hits += hits
            all_users += users
            all_generic += hit_lines(name, list_hits(text, generic, user)[0], [])[0]
        write_report(argv[2], ["check-only: %d files" % len(argv[3:])], all_hits, all_users, all_generic)
        return 1 if all_hits else 0
    if len(argv) != 4 or argv[0].startswith("-"):
        print(__doc__.strip(), file=sys.stderr)
        return 2
    export, out, private_list, report = argv
    temps = [os.environ.get("TMPDIR", ""), tempfile.gettempdir(), os.path.realpath(tempfile.gettempdir()),
             "/private/var/folders", "/var/folders", "/private/tmp", "/tmp"]
    repo = os.path.dirname(os.path.abspath(__file__))
    paths = machine_paths(repo, os.path.expanduser("~"), temps)
    private, generic = split_generic(read_list(private_list))
    text, changes = scrub(read(export), paths)
    hits, users = hit_lines("scrubbed", *list_hits(text, with_path_forms(private, paths), user))
    generic_hits = hit_lines("scrubbed", list_hits(text, generic, user)[0], [])[0]
    counts = {}
    for _, kind, _ in changes:
        counts[kind] = counts.get(kind, 0) + 1
    body = ["counts: " + ", ".join("%s %d" % (k, counts.get(k, 0)) for k in ("block", "path", "email", "secret", "mac")),
            "", "changes (line in the scrubbed log, kind, placeholder):"]
    body += ["  line %d: %s -> %s" % c for c in changes] or ["  none"]
    write_report(report, body, hits, users, generic_hits)
    if hits:
        if os.path.exists(out):
            os.remove(out)  # an earlier clean run's log may hold a word listed since
        print("private-list hits in the export: %s not written; see %s" % (out, report), file=sys.stderr)
        return 1
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
