"""The commands the step files tell people and agents to run must work as written,
from the repo root, once <skill folder> is replaced by the skill's folder."""

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "feature-lifecycle"


def command_lines(step_file: str, needle: str) -> list[str]:
    text = (SKILL / "steps" / step_file).read_text(encoding="utf-8")
    blocks = re.findall(r"```bash\n(.*?)```", text, flags=re.S)
    return [line for block in blocks for line in block.splitlines() if needle in line]


def git(cwd, *args):
    subprocess.run(
        ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        cwd=cwd, check=True, capture_output=True,
    )


class DocumentedCommandsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        git(self.repo, "init", "-q")
        (self.repo / "README.md").write_text("start\n")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-qm", "start")
        git(self.repo, "update-ref", "refs/remotes/origin/main", "HEAD")
        entry = self.repo / "docs" / "release-notes" / "unreleased" / "TAG-1.md"
        entry.parent.mkdir(parents=True)
        entry.write_text("---\nproduct: mobi\ntype: fix\nissue: TAG-1\naudience: users\n---\nFixed the export.\n")
        git(self.repo, "add", "docs")
        git(self.repo, "commit", "-qm", "entry")
        self.pr_body = self.tmp / "pr-body.md"
        self.pr_body.write_text("## What\nA fix.\n")

    def run_documented(self, line: str):
        line = (
            line.replace("<skill folder>", str(SKILL))
            .replace("<PR description file>", str(self.pr_body))
            .replace("<ISSUE-ID>", "TAG-1")
        )
        self.assertNotIn("<", line, f"unfilled placeholder in: {line}")
        env = {"PATH": os.environ["PATH"], "HOME": str(self.tmp), "VSD_CUSTOMER_NAMES": "Zeta Industries"}
        return subprocess.run(["bash", "-c", line], cwd=self.repo, env=env, capture_output=True, text=True)

    def test_prove_name_check_runs_from_repo_root(self):
        lines = command_lines("prove.md", "check_customer_names.py")
        self.assertEqual(len(lines), 1)
        result = self.run_documented(lines[0])
        self.assertNotIn("can't open file", result.stderr)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_docs_release_note_validate_runs_from_repo_root(self):
        lines = command_lines("docs.md", "release_notes.py")
        self.assertEqual(len(lines), 1)
        result = self.run_documented(lines[0])
        self.assertNotIn("can't open file", result.stderr)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
