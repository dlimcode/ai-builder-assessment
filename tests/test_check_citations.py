"""Golden-set tests for check_citations.py (planning/01-prior-art-and-formats.md section 5, plus H5-H7).

Written before the checker exists: run them and see them fail first.
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURES = os.path.join(REPO, "tests", "fixtures")
EVIL = os.path.join(REPO, "tests", "fixtures-evil")
CHECKER = os.path.join(REPO, "check_citations.py")
sys.path.insert(0, REPO)

import check_citations as cc  # noqa: E402  (fails until the checker exists)

# (row, reference as it sits on its report.md line, expected verdict, expected "found at" places)
GOLDEN = [
    ("1", 'notes.md:3 "under a minute"', "holds", []),
    ("2", '[record notes.md:4 "noon on Fridays"]', "holds", []),
    ("3", 'notes.md:4 "under a minute"', "wrong line", ["notes.md:3"]),
    ("4", 'notes.md:3 "Under a minute"', "not in file", []),
    ("5", 'notes.md:5 "blue door is"', "holds", []),
    ("6", 'notes.md:5 "**blue door**"', "holds", []),
    ("7", 'notes.md:8 "print_report button"', "holds", []),
    ("8", 'notes.md:9 "Visitors sign the paper book"', "holds", []),
    ("9", 'notes.md:6 "before eight and are signed for"', "holds", []),
    ("10", 'notes.md:7 "before eight and are signed for"', "wrong line", ["notes.md:6"]),
    ("11", 'notes.md:6-7 "signed for at the front desk"', "holds", []),
    ("12", '[record notes.md:3-4 "side entrance"]', "wrong line", ["notes.md:5"]),
    ("13", "notes.md:3", "line only", []),
    ("14", "notes.md:40", "no such line", []),
    ("15", 'notes.md:40 "under a minute"', "no such line", ["notes.md:3"]),
    ("16", 'notes.md:0 "Office notes"', "no such line", ["notes.md:1"]),
    ("17", 'notes.md:7-6 "signed for"', "no such line", ["notes.md:7"]),
    ("18", 'missing.md:1 "anything"', "file missing", []),
    ("19", 'notes.md:3 "boils in under an hour"', "not in file", []),
    ("20", 'data/plan.txt:2 "water the plants"', "wrong line", ["data/plan.txt:1", "data/plan.txt:3"]),
    ("21", 'data/plan.txt:3 "water the plants"', "holds", []),
    ("22", 'empty.md:1 "anything"', "no such line", []),
    ("23", "notes.md:3 “under a minute”", "holds", []),
    ("24", 'notes.md:3 "kettle ... minute"', "not in file", []),
    ("25", '`notes.md:99 "x"`', "not checked", []),
    ("26", "see 12:30 and https://example.com:443/a.md:2", "not checked", []),
    ("H1", '../outside.md:1 "x"', "refused: outside root", []),
    ("H2", '/etc/hosts:1 "localhost"', "refused: outside root", []),
    ("H3", 'link-out.md:1 "x"', "file missing", []),  # on the repo copy; refused in SymlinkTests
    ("H4", 'notes.md:99999999999999999999 "x"', "no such line", []),
    ("H5", '../fixtures-evil/x.md:1 "x"', "refused: outside root", []),
    ("H6", 'data/:1 "x"', "file missing", []),
    ("H7", 'bin.dat:1 "x"', "file missing", []),
]

SUMMARY = ("33 references", "10 holds", "1 line only", "20 red", "2 not checked")


def run_cli(*args, cwd=REPO):
    return subprocess.run(
        [sys.executable, CHECKER, *args], cwd=cwd, capture_output=True, text=True, timeout=60
    )


class FindTests(unittest.TestCase):
    """Finding references in report text (task 3)."""

    def one(self, text):
        refs, skipped = cc.find_refs(text)
        self.assertEqual(skipped, 0, text)
        self.assertEqual(len(refs), 1, text)
        return refs[0]

    def test_plain(self):
        r = self.one('notes.md:3 "under a minute"')
        self.assertEqual((r.line, r.path, r.start, r.end, r.quote), (1, "notes.md", 3, 3, "under a minute"))

    def test_record_wrapper(self):
        r = self.one('[record notes.md:4 "noon on Fridays"]')
        self.assertEqual((r.path, r.start, r.quote), ("notes.md", 4, "noon on Fridays"))

    def test_range(self):
        r = self.one('notes.md:6-7 "signed for at the front desk"')
        self.assertEqual((r.start, r.end), (6, 7))

    def test_no_quote(self):
        self.assertIsNone(self.one("notes.md:3").quote)

    def test_curly_quote(self):
        self.assertEqual(self.one("notes.md:3 “under a minute”").quote, "under a minute")

    def test_huge_line_number_is_not_an_int(self):
        r = self.one('notes.md:99999999999999999999 "x"')
        self.assertIsNone(r.start)

    def test_absolute_and_dotdot_paths_are_found(self):
        self.assertEqual(self.one('/etc/hosts:1 "localhost"').path, "/etc/hosts")
        self.assertEqual(self.one('../outside.md:1 "x"').path, "../outside.md")

    def test_words_inside_a_quote_are_not_scanned(self):
        r = self.one('a.md:1 "see b.md:2"')
        self.assertEqual(r.quote, "see b.md:2")

    def test_line_numbers_count_from_one(self):
        refs, _ = cc.find_refs('intro\n\nnotes.md:3 "under a minute"\n')
        self.assertEqual([r.line for r in refs], [3])

    def test_backticks_are_skipped(self):
        self.assertEqual(cc.find_refs('`notes.md:99 "x"`'), ([], 1))

    def test_urls_and_times_are_skipped(self):
        self.assertEqual(cc.find_refs("see 12:30 and https://example.com:443/a.md:2"), ([], 1))

    def test_code_fences_are_skipped(self):
        refs, skipped = cc.find_refs('```\nnotes.md:99 "x"\n```\nnotes.md:3\n')
        self.assertEqual([(r.line, r.path) for r in refs], [(4, "notes.md")])
        self.assertEqual(skipped, 1)

    def test_line_and_column_is_not_a_reference(self):
        self.assertEqual(cc.find_refs("a.py:3:7"), ([], 0))

    def test_two_references_on_one_line(self):
        refs, _ = cc.find_refs('[record a.md:1 "x"]; [record b.md:2-3 "y"]')
        self.assertEqual([(r.path, r.start, r.end, r.quote) for r in refs], [("a.md", 1, 1, "x"), ("b.md", 2, 3, "y")])


class GoldenTests(unittest.TestCase):
    """Each golden row, checked against tests/fixtures (task 4)."""

    def test_report_fixture_matches_the_table(self):
        with open(os.path.join(FIXTURES, "report.md"), encoding="utf-8") as f:
            self.assertEqual(f.read().splitlines(), [row[1] for row in GOLDEN])

    def test_rows(self):
        for row, text, verdict, found in GOLDEN:
            with self.subTest(row=row):
                refs, skipped = cc.find_refs(text)
                if verdict == "not checked":
                    self.assertEqual((refs, skipped), ([], 1))
                    continue
                self.assertEqual(len(refs), 1)
                result = cc.check(refs[0], FIXTURES)
                self.assertEqual(result.verdict, verdict)
                if verdict != "holds":
                    self.assertEqual(result.found, found)


class SymlinkTests(unittest.TestCase):
    """H3 (and H5) on a copy of the fixtures, with a symlink pointing outside the copy's root."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="cc-golden-")
        self.root = os.path.join(self.tmp, "fixtures")
        shutil.copytree(FIXTURES, self.root)
        shutil.copytree(EVIL, os.path.join(self.tmp, "fixtures-evil"))
        os.symlink(os.path.join(self.tmp, "fixtures-evil", "x.md"), os.path.join(self.root, "link-out.md"))

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_symlink_out_of_root_is_refused(self):
        refs, _ = cc.find_refs('link-out.md:1 "x"')
        self.assertEqual(cc.check(refs[0], self.root).verdict, "refused: outside root")

    def test_report_run_in_the_copy(self):
        out = run_cli(os.path.join(self.root, "report.md"), "--root", self.root)
        self.assertEqual(out.returncode, 1, out.stderr)
        line = [l for l in out.stdout.splitlines() if "link-out.md:1" in l]
        self.assertEqual(len(line), 1, out.stdout)
        self.assertIn("refused: outside root", line[0])


class CliTests(unittest.TestCase):
    """Command line: exits 0 / 1 / 2 and the summary (task 5)."""

    def test_golden_report_summary_and_exit(self):
        out = run_cli("tests/fixtures/report.md", "--root", "tests/fixtures")
        self.assertEqual(out.returncode, 1, out.stderr)
        last = out.stdout.strip().splitlines()[-1]
        for part in SUMMARY:
            self.assertIn(part, last)
        self.assertIn("root", last)

    def test_all_green_exits_0(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = os.path.join(tmp, "r.md")
            with open(report, "w", encoding="utf-8") as f:
                f.write('notes.md:3 "under a minute"\nnotes.md:3\n')
            out = run_cli(report, "--root", FIXTURES)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_folder_argument_is_a_usage_error(self):
        self.assertEqual(run_cli("tests/fixtures", "--root", "tests/fixtures").returncode, 2)

    def test_missing_report_is_a_usage_error(self):
        self.assertEqual(run_cli("no-such-report.md").returncode, 2)

    def test_bad_flag_is_a_usage_error(self):
        self.assertEqual(run_cli("tests/fixtures/report.md", "--no-such-flag").returncode, 2)

    def test_no_arguments_is_a_usage_error(self):
        self.assertEqual(run_cli().returncode, 2)

    def test_red_line_says_where_the_words_are(self):
        out = run_cli("tests/fixtures/report.md", "--root", "tests/fixtures")
        line = [l for l in out.stdout.splitlines() if 'notes.md:4 "under a minute"' in l]
        self.assertEqual(len(line), 1, out.stdout)
        self.assertIn("wrong line", line[0])
        self.assertIn("found at notes.md:3", line[0])

    def test_ellipsis_is_named(self):
        out = run_cli("tests/fixtures/report.md", "--root", "tests/fixtures")
        line = [l for l in out.stdout.splitlines() if "kettle ... minute" in l]
        self.assertIn("not supported", line[0])

    def test_no_colour_and_no_control_characters_off_a_terminal(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = os.path.join(tmp, "r.md")
            with open(report, "w", encoding="utf-8") as f:
                f.write('notes.md:3 "under \x1b[31ma minute"\n')
            out = run_cli(report, "--root", FIXTURES)
        self.assertNotIn("\x1b", out.stdout)


if __name__ == "__main__":
    unittest.main()
