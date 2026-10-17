import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "lifecycle-release"
    / "release_notes.py"
)


def load_module():
    spec = importlib.util.spec_from_file_location("release_notes", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["release_notes"] = module
    spec.loader.exec_module(module)
    return module


def write_entry(directory, issue, product="tag", type_="fix", audience="users",
                body="Fixed the status caption.", filename=None):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (filename or f"{issue}.md")
    path.write_text(
        f"---\nproduct: {product}\ntype: {type_}\nissue: {issue}\n"
        f"audience: {audience}\n---\n{body}\n",
        encoding="utf-8",
    )
    return path


def run_script(*args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True
    )


class ValidateTest(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        self.dir = Path(tempfile.mkdtemp())

    def problems(self, **kwargs):
        return self.mod.validate_entry(write_entry(self.dir, **kwargs))

    def test_valid_entry_passes(self):
        self.assertEqual(self.problems(issue="TAG-12"), [])

    def test_filename_must_match_issue(self):
        problems = self.problems(issue="TAG-13", filename="TAG-12.md")
        self.assertEqual(len(problems), 1)
        self.assertIn("file name", problems[0])

    def test_rejects_lowercase_issue(self):
        problems = self.problems(issue="tag-12")
        self.assertTrue(any("issue" in p for p in problems), problems)

    def test_rejects_unknown_product(self):
        problems = self.problems(issue="TAG-12", product="trax")
        self.assertTrue(any("product" in p for p in problems), problems)

    def test_rejects_more_than_three_sentences(self):
        problems = self.problems(issue="TAG-12", body="One. Two. Three. Four.")
        self.assertTrue(any("sentences" in p for p in problems), problems)

    def test_rejects_empty_body(self):
        problems = self.problems(issue="TAG-12", body="")
        self.assertTrue(any("empty" in p for p in problems), problems)

    def test_validate_cli_exit_codes(self):
        good = write_entry(self.dir, "TAG-1")
        bad = write_entry(self.dir, "TAG-2", product="trax")
        self.assertEqual(run_script("validate", str(good)).returncode, 0)
        result = run_script("validate", str(good), str(bad))
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"{bad}: ", result.stdout)


class RenderTest(unittest.TestCase):
    def setUp(self):
        self.mod = load_module()
        self.dir = Path(tempfile.mkdtemp())

    def entry(self, issue, **kwargs):
        return self.mod.parse_entry(write_entry(self.dir, issue, **kwargs))

    def test_render_groups_and_orders(self):
        entries = [
            self.entry("TAG-10", type_="fix", body="Ten fixed."),
            self.entry("TAG-2", type_="fix", body="Two fixed."),
            self.entry("TAG-5", type_="feature", body="Five added."),
            self.entry("TAG-7", type_="change", audience="consultants", body="Seven changed."),
        ]
        self.assertEqual(
            self.mod.render(entries, "13.6"),
            "## 13.6\n\n"
            "### New\n\n- Five added.\n\n"
            "### Fixed\n\n- Two fixed.\n- Ten fixed.\n\n"
            "### For consultants\n\n- Seven changed.\n",
        )

    def test_render_prefixes_admins(self):
        entries = [self.entry("TAG-3", audience="admins", body="Admins can reset it.")]
        self.assertIn("- **For admins:** Admins can reset it.", self.mod.render(entries, "1.0"))


class GatherTest(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.unreleased = self.root / "unreleased"

    def test_gather_filters_product(self):
        write_entry(self.unreleased, "TAG-1", product="tag", body="Tag body.")
        write_entry(self.unreleased, "TAG-2", product="mobi", body="Mobi body.")
        result = run_script("gather", "--dir", str(self.root), "--product", "tag", "--version", "13.6")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Tag body.", result.stdout)
        self.assertNotIn("Mobi body.", result.stdout)

    def test_gather_apply_moves_files(self):
        write_entry(self.unreleased, "TAG-2")
        result = run_script("gather", "--dir", str(self.root), "--product", "tag",
                            "--version", "13.6", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.root / "13.6" / "TAG-2.md").exists())
        self.assertFalse((self.unreleased / "TAG-2.md").exists())

    def test_gather_invalid_entry_moves_nothing(self):
        write_entry(self.unreleased, "TAG-1")
        write_entry(self.unreleased, "TAG-2", body="")
        result = run_script("gather", "--dir", str(self.root), "--product", "tag",
                            "--version", "13.6", "--apply")
        self.assertEqual(result.returncode, 1)
        self.assertTrue((self.unreleased / "TAG-1.md").exists())
        self.assertTrue((self.unreleased / "TAG-2.md").exists())
        self.assertFalse((self.root / "13.6").exists())

    def test_gather_blocks_on_an_entry_with_an_unknown_product(self):
        write_entry(self.unreleased, "TAG-1", product="mobi")
        write_entry(self.unreleased, "TAG-2", product="Mobi")
        result = run_script("gather", "--dir", str(self.root), "--product", "mobi",
                            "--version", "1.0", "--apply")
        self.assertEqual(result.returncode, 1)
        self.assertIn("TAG-2.md", result.stderr)
        self.assertIn("product", result.stderr)
        self.assertTrue((self.unreleased / "TAG-1.md").exists())

    def test_gather_for_another_product_still_blocks_on_an_unknown_product(self):
        write_entry(self.unreleased, "TAG-2", product="Mobi")
        result = run_script("gather", "--dir", str(self.root), "--product", "tag", "--version", "1.0")
        self.assertEqual(result.returncode, 1)
        self.assertIn("TAG-2.md", result.stderr)

    def test_gather_ignores_the_folder_readme(self):
        self.unreleased.mkdir(parents=True)
        (self.unreleased / "README.md").write_text("# How to write an entry\n")
        write_entry(self.unreleased, "TAG-3", product="tag", body="Tag fix.")
        result = run_script("gather", "--dir", str(self.root), "--product", "tag",
                            "--version", "1.0", "--apply")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.unreleased / "README.md").exists())
        self.assertTrue((self.root / "1.0" / "TAG-3.md").exists())

    def test_gather_problems_go_to_stderr(self):
        write_entry(self.unreleased, "TAG-4", body="")
        result = run_script("gather", "--dir", str(self.root), "--product", "tag", "--version", "1.0")
        self.assertEqual(result.returncode, 1)
        self.assertIn("TAG-4.md", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_gather_no_entries(self):
        result = run_script("gather", "--dir", str(self.root), "--product", "mobi", "--version", "1.0")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), "No unreleased entries for mobi.")


if __name__ == "__main__":
    unittest.main()
