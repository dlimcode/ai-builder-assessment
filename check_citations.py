"""Check that the words a report quotes are really on the file line it cites.

Usage: python3 check_citations.py REPORT.md [REPORT.md ...] [--root DIR]
Python 3.9 standard library only; no model call, no network.
"""
import re
from collections import namedtuple

# line: line number in the report; start/end: cited lines (None when the number is too long to be real)
Ref = namedtuple("Ref", "line path start end quote raw")

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
