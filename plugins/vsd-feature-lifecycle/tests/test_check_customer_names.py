import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "feature-lifecycle"
    / "scripts"
    / "check_customer_names.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("check_customer_names", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_script(args, home, env_names=None, cwd=None):
    env = {"PATH": os.environ["PATH"], "HOME": str(home)}
    if env_names is not None:
        env["VSD_CUSTOMER_NAMES"] = env_names
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        env=env,
        cwd=cwd,
    )


def git(cwd, *args):
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
    )


class FindHitsTest(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()

    def test_finds_name_case_insensitive(self):
        self.assertEqual(
            self.mod.find_hits("We met acme corp today", ["Acme Corp"]),
            [(1, "Acme Corp")],
        )

    def test_no_match_inside_longer_word(self):
        self.assertEqual(self.mod.find_hits("Zetaville plant", ["Zeta"]), [])

    def test_matches_name_with_ampersand(self):
        self.assertEqual(
            self.mod.find_hits("line one\nfrom A&Z's site", ["A&Z"]),
            [(2, "A&Z")],
        )


class LoadNamesTest(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        self.tmp = Path(tempfile.mkdtemp())

    def test_env_names_split_on_commas_and_newlines(self):
        names = self.mod.load_names(
            None, {"VSD_CUSTOMER_NAMES": "Acme Corp, Zeta\nBeta Inc"}, self.tmp
        )
        self.assertEqual(names, ["Acme Corp", "Zeta", "Beta Inc"])

    def test_file_skips_comments_and_blanks(self):
        names_file = self.tmp / "names.txt"
        names_file.write_text("# list\nAcme Corp\n\nZeta\n")
        self.assertEqual(
            self.mod.load_names(str(names_file), {}, self.tmp), ["Acme Corp", "Zeta"]
        )


class CliTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_missing_list_exits_2(self):
        result = run_script([], home=self.tmp)
        self.assertEqual(result.returncode, 2)
        self.assertIn("no customer-name list", result.stderr)

    def test_file_hit_exits_1(self):
        target = self.tmp / "notes.md"
        target.write_text("ok\nsent to Acme Corp\n")
        result = run_script([str(target)], home=self.tmp, env_names="Acme Corp")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.strip(), f"{target}:2: Acme Corp")

    def test_diff_checks_added_lines_only(self):
        repo = self.tmp / "repo"
        repo.mkdir()
        git(repo, "init", "-q")
        (repo / "a.txt").write_text("Acme Corp\n")
        git(repo, "add", "a.txt")
        git(repo, "commit", "-qm", "A")
        (repo / "a.txt").write_text("Zeta\n")
        git(repo, "commit", "-qam", "B")
        result = run_script(
            ["--base", "HEAD~1"], home=self.tmp, env_names="Acme Corp,Zeta", cwd=repo
        )
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.strip().splitlines(), ["diff:a.txt:1: Zeta"])


if __name__ == "__main__":
    unittest.main()
