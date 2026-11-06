"""Tests for scrub.py, on a made-up log and a made-up three-line private list only."""
import getpass
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRUB = os.path.join(REPO, "scrub.py")
sys.path.insert(0, REPO)

import scrub  # noqa: E402

HOME = "/Users/alex"
REPO_PATH = "/Users/alex/Developer/demo-repo"
TEMPS = ["/private/var/folders/zz/abc123/T", "/private/tmp", "/tmp"]
USER = "alex"
PATTERNS = ["Acme Widgets", "secret-project", "alex"]

# Made-up values, joined from pieces at run time so no committed line is shaped like a real key or MAC.
FAKE = {
    "sk": "sk-" + "ant-api03-abcDEF_123",
    "ghp": "ghp" + "_abcdefghijklmnop1234",
    "akia": "AK" + "IA" + "ABCDEFGHIJKLMNOP",
    "xox": "xo" + "xb-123-abc",
    "mac": ":".join(["0a", "1b", "2c", "3d", "4e", "5f"]),
    "begin": "-----BEGIN OPENSSH PRIVATE " + "KEY-----",
    "end": "-----END OPENSSH PRIVATE " + "KEY-----",
}

# One of each start-up block a saved session file was measured to carry (planning/README.md,
# "What nobody could show"), then one of each path, address and token kind, a list word, the username.
LOG = """> /build Read the brief and follow it.
<system-reminder>
Contents of /Users/alex/.claude/CLAUDE.md (user's private global instructions for all projects):
Rules that mention Acme Widgets.
</system-reminder>
## Bash command sandbox
The sandbox denies /Users/alex/Documents.
## Next heading stays
The following skills are available for use with the Skill tool:

- design: Design or restyle
  a wrapped description line
- meeting: Prepare for secret-project meetings

Kept after the skills list.
Base directory for this skill: /Users/alex/.claude/skills/build
The recipe's own text, naming Acme Widgets.
> next prompt stays
SessionStart:startup hook success: # Workspace map
cwd: /Users/alex/Developer/demo-repo
⏺ The reply stays.
Repo file /Users/alex/Developer/demo-repo/check_citations.py and home /Users/alex/notes.txt
Dash form -Users-alex-Developer-demo-repo and -Users-alex-Other, JSON {"p": "\\/Users\\/alex\\/x"}
Temp /private/var/folders/zz/abc123/T/run.1 and /private/tmp/claude-501/x and /tmp/y
Mail alex@example.com, key %(sk)s, %(ghp)s, %(akia)s
Also %(xox)s, Authorization: Bearer abc.def-ghi, router %(mac)s
%(begin)s
b3BlbnNzaC1rZXk=
%(end)s
Signed by alex in the end.
""" % FAKE

PATHS = scrub.machine_paths(REPO_PATH, HOME, TEMPS)


def run(*args):
    return subprocess.run([sys.executable, SCRUB, *args], capture_output=True, text=True, timeout=60)


class ScrubTests(unittest.TestCase):
    def setUp(self):
        self.out, self.changes = scrub.scrub(LOG, PATHS)

    def test_nothing_private_survives(self):
        for gone in ["<system-reminder>", "CLAUDE.md", "Bash command sandbox", "design: Design", "wrapped description",
                     "Base directory", "recipe's own text", "SessionStart", "Workspace map", "/Users", "\\/Users",
                     "-Users-alex", "/private", "/tmp", "/var/folders", "@example.com", "abc.def",
                     "b3BlbnNzaC1rZXk", "Acme", "secret-project"] + list(FAKE.values()):
            self.assertNotIn(gone, self.out)

    def test_what_stays(self):
        for kept in ["> /build Read the brief", "## Next heading stays", "Kept after the skills list.",
                     "> next prompt stays", "⏺ The reply stays.", "./check_citations.py", "~/notes.txt",
                     "<repo-folder>", "~-Other", "<tmp>/run.1", "<tmp>/claude-501/x", "<tmp>/y", "<email>",
                     "<secret>", "<mac>", "Signed by alex"]:
            self.assertIn(kept, self.out)

    def test_line_numbers_stay_put_after_the_first_pass(self):
        self.assertEqual(self.out.count("\n"), scrub.cut_blocks(LOG)[0].count("\n"))

    def test_every_change_is_counted(self):
        kinds = [kind for _, kind, _ in self.changes]
        for kind in ["block", "path", "email", "secret", "mac"]:
            self.assertIn(kind, kinds)

    def test_only_the_username_is_left_for_the_list(self):
        hits, user_hits = scrub.list_hits(self.out, PATTERNS, USER)
        self.assertEqual(hits, [])
        self.assertTrue(user_hits)

    def test_list_word_split_by_a_line_break_is_caught(self):
        hits, _ = scrub.list_hits("the Acme Wid\ngets tender\n", PATTERNS, USER)
        self.assertTrue(hits)

    def test_two_reminders_on_one_line_and_nested_are_both_cut(self):
        text = "<system-reminder>\none\n</system-reminder><system-reminder>\nGit user: Acme Widgets\n</system-reminder>\n"
        text += "<system-reminder> a <system-reminder> b </system-reminder> INNER secret-project </system-reminder>\nkept\n"
        out, _ = scrub.scrub(text, PATHS)
        self.assertEqual(scrub.list_hits(out, PATTERNS, USER)[0], [])
        self.assertNotIn("INNER", out)
        self.assertIn("kept", out)

    def test_wrapped_and_spaced_words_are_caught(self):
        for text in ["the Acme\n  Widgets tender", "Acme Wid\n  gets", "Acme  Widgets", "Acme\tWidgets",
                     "Acme\u00a0Widgets", "Acme\nWidgets"]:
            with self.subTest(text=text):
                self.assertTrue(scrub.list_hits(text, PATTERNS, USER)[0])

    def test_list_match_ignores_case(self):
        hits, _ = scrub.list_hits("SECRET-PROJECT\n", PATTERNS, USER)
        self.assertTrue(hits)


class CommandTests(unittest.TestCase):
    """The command line, with this machine's own home and username built at run time."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.list = self.path("list.txt", "# made-up list\nAcme Widgets\n%s\n" % getpass.getuser())
        self.report = os.path.join(self.dir, "report.txt")
        self.out = os.path.join(self.dir, "out.txt")

    def tearDown(self):
        self.tmp.cleanup()

    def path(self, name, text):
        p = os.path.join(self.dir, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p

    def last_line(self):
        with open(self.report, encoding="utf-8") as f:
            return f.read().strip().splitlines()[-1]

    def test_clean_export_is_written_and_reported(self):
        log = self.path("log.txt", "home %s and user %s\n" % (os.path.expanduser("~"), getpass.getuser()))
        res = run(log, self.out, self.list, self.report)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(self.last_line(), "private list: 0 hits")
        with open(self.out, encoding="utf-8") as f:
            self.assertNotIn(os.path.expanduser("~"), f.read())
        with open(self.report, encoding="utf-8") as f:
            self.assertIn("username hits", f.read())

    def test_list_hit_fails_and_writes_nothing(self):
        log = self.path("log.txt", "a note on Acme Widgets\n")
        res = run(log, self.out, self.list, self.report)
        self.assertNotEqual(res.returncode, 0)
        self.assertFalse(os.path.exists(self.out))
        self.assertNotEqual(self.last_line(), "private list: 0 hits")

    def test_a_failing_run_removes_an_earlier_scrubbed_log(self):
        log = self.path("log.txt", "clean text\n")
        self.assertEqual(run(log, self.out, self.list, self.report).returncode, 0)
        self.assertTrue(os.path.exists(self.out))
        self.path("log.txt", "now with Acme Widgets\n")
        self.assertNotEqual(run(log, self.out, self.list, self.report).returncode, 0)
        self.assertFalse(os.path.exists(self.out))

    def test_check_only_over_many_files(self):
        a = self.path("a.txt", "clean\n")
        b = self.path("b.txt", "acme widgets here\n")
        res = run("--check-only", self.list, self.report, a, b)
        self.assertNotEqual(res.returncode, 0)
        with open(self.report, encoding="utf-8") as f:
            self.assertIn("b.txt", f.read())
        res = run("--check-only", self.list, self.report, a)
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertEqual(self.last_line(), "private list: 0 hits")

    def test_wrong_arguments_exit_2(self):
        self.assertEqual(run("only-one").returncode, 2)


class FinishSittingTests(unittest.TestCase):
    """finish-sitting.sh in a throwaway repo, in its own temp folder outside every repo."""

    def git(self, *args):
        return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-c",
                               "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false", *args],
                              cwd=self.repo, capture_output=True, text=True, timeout=60)

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = os.path.join(self.tmp.name, "r")
        os.makedirs(os.path.join(self.repo, "planning"))
        if self.git("init", "-q", "-b", "main").returncode != 0:
            self.fail("git init failed; stopping before any git command can reach a real repo")
        self.assertTrue(os.path.isdir(os.path.join(self.repo, ".git")))
        shutil.copy(SCRUB, self.repo)
        shutil.copy(os.path.join(REPO, "planning", "finish-sitting.sh"), os.path.join(self.repo, "planning"))
        self.git("add", ".")
        self.git("commit", "-q", "-m", "start")
        self.git("switch", "-q", "-c", "build")
        self.list = os.path.join(self.tmp.name, "list.txt")
        with open(self.list, "w", encoding="utf-8") as f:
            f.write("Zephyr Holdings\n")
        os.makedirs(os.path.join(self.repo, "logs", "raw"))
        with open(os.path.join(self.repo, "logs", "raw", "session.txt"), "w", encoding="utf-8") as f:
            f.write("a clean log\n")

    def tearDown(self):
        self.tmp.cleanup()

    def finish(self):
        env = dict(os.environ, TMPDIR=self.tmp.name)
        return subprocess.run(["bash", "planning/finish-sitting.sh", self.list], cwd=self.repo,
                              capture_output=True, text=True, timeout=120, env=env)

    def test_a_word_removed_by_a_later_commit_is_still_caught(self):
        notes = os.path.join(self.repo, "planning", "my notes.md")
        with open(notes, "w", encoding="utf-8") as f:
            f.write("about Zephyr Holdings\n")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "add notes")
        with open(notes, "w", encoding="utf-8") as f:
            f.write("about nothing\n")
        self.git("commit", "-q", "-am", "remove the word")
        res = self.finish()
        self.assertNotEqual(res.returncode, 0, res.stdout + res.stderr)

    def test_clean_branch_passes(self):
        res = self.finish()
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertTrue(os.path.exists(os.path.join(self.repo, "logs", "session.txt")))


if __name__ == "__main__":
    unittest.main()
