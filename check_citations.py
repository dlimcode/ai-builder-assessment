"""Check that the words a report quotes are really on the file line it cites.

Usage: python3 check_citations.py REPORT.md [REPORT.md ...] [--root DIR]
Python 3.9 standard library only; no model call, no network.
"""
import os
import re
from collections import namedtuple

# line: line number in the report; start/end: cited lines (None when the number is too long to be real)
Ref = namedtuple("Ref", "line path start end quote raw")
# found: up to three "path:line" places where the words are, for red verdicts
Result = namedtuple("Result", "verdict found")

PATH_CHARS = r"[A-Za-z0-9_./-]"
REF_RE = r"(?<!%s)(?P<path>%s+):(?P<a>\d+)(?:-(?P<b>\d+))?" % (PATH_CHARS, PATH_CHARS)
# One scan finds whichever comes first: a code span, a URL, or a reference.
TOKEN = re.compile(r"(?P<code>(?P<ticks>`+).+?(?<!`)(?P=ticks)(?!`))|(?P<url>[A-Za-z][A-Za-z0-9+.-]*://\S*)|" + REF_RE)
SHAPE = re.compile(REF_RE)
QUOTE_OPEN = re.compile("[ \t]*([\"“])")
QUOTE_CLOSE = {'"': '"', "“": "”"}
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})")


def line_number(digits):
    """A digit run longer than 9 is no real line; never call int() on it."""
    return int(digits) if digits and len(digits) <= 9 else None


def is_path(text):
    return "." in text or "/" in text


def is_ref(m, text):
    """A path shape, not a clock time like 12:30 and not path:line:col (cut)."""
    return is_path(m.group("path")) and not re.match(r":\d", text[m.end():])


def has_shape(text):
    return any(is_ref(m, text) for m in SHAPE.finditer(text))


def scan_line(text, number):
    """Return (references, skipped spans holding a reference shape) for one report line."""
    refs, skipped, pos = [], 0, 0
    while True:
        m = TOKEN.search(text, pos)
        if not m:
            return refs, skipped
        pos = m.end()
        if m.group("code") or m.group("url"):
            skipped += has_shape(m.group(0))
            continue
        if not is_ref(m, text):
            continue
        a = m.group("a")
        b = m.group("b") or a
        quote = None
        q = QUOTE_OPEN.match(text, pos)
        if q:
            close = text.find(QUOTE_CLOSE[q.group(1)], q.end())
            if close != -1:
                quote = text[q.end():close]
                pos = close + 1  # words inside a quote are not scanned for references
        refs.append(Ref(number, m.group("path"), line_number(a), line_number(b), quote, text[m.start():pos]))


def find_refs(text):
    """Return (references, count of skipped spans holding a reference shape) for a whole report."""
    refs, skipped, fence = [], 0, None
    for number, line in enumerate(text.split("\n"), 1):
        f = FENCE.match(line)
        if fence:
            if f and f.group(1)[0] == fence[0] and len(f.group(1)) >= len(fence):
                fence = None
            else:
                skipped += has_shape(line)
            continue
        if f:
            fence = f.group(1)
            continue
        found, n = scan_line(line, number)
        refs += found
        skipped += n
    return refs, skipped


def clean(text):
    """Strip backticks and ** marks, collapse whitespace runs to one space; case is kept."""
    return " ".join(text.replace("`", "").replace("**", "").split())


def read_lines(root, path):
    """Return the file's lines, or a verdict string when it must not or cannot be read."""
    root = os.path.realpath(root)
    target = os.path.realpath(os.path.join(root, path))
    if os.path.commonpath([root, target]) != root:
        return "refused: outside root"  # decided on the resolved path, before any open
    if not os.path.isfile(target):
        return "file missing"
    try:
        with open(target, encoding="utf-8") as f:
            lines = f.read().split("\n")
    except (OSError, UnicodeDecodeError):
        return "file missing"
    if lines[-1] == "":
        lines.pop()
    return lines


def starts_at(lines, i, words):
    """The words are on line i (1-based), or start there and run into the next line."""
    here = clean(lines[i - 1])
    joined = here + " " + clean(lines[i]) if i < len(lines) else here
    return 0 <= joined.find(words) < len(here)


def check(ref, root):
    lines = read_lines(root, ref.path)
    if isinstance(lines, str):
        return Result(lines, [])
    words = clean(ref.quote or "")
    places = ["%s:%d" % (ref.path, i) for i in range(1, len(lines) + 1) if words and starts_at(lines, i, words)][:3]
    a, b = ref.start, ref.end
    if a is None or b is None or a < 1 or a > b or b > len(lines):
        return Result("no such line", places)
    if not words:
        return Result("line only", [])
    if a == b:
        held = starts_at(lines, a, words)
    else:
        held = words in " ".join(clean(l) for l in lines[a - 1:b])
    if held:
        return Result("holds", [])
    return Result("wrong line" if places else "not in file", places)
