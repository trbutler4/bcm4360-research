from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
from pathlib import Path
import subprocess
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "check_repository.py"
SPEC = importlib.util.spec_from_file_location("check_repository", MODULE_PATH)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class RepositoryChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def write(self, name, content):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def errors(self):
        return CHECKER.check_repository(self.root)

    def test_clean_notebook_and_links(self):
        self.write("README.md", "[Note](docs/note.md#heading)\n[Source][s]\n[s]: https://example.org\n")
        self.write("docs/note.md", "# Heading\n[Home](../README.md)\n")
        self.assertEqual(self.errors(), [])

    def test_missing_inline_link(self):
        self.write("README.md", "[Missing](missing.md)\n")
        self.assertIn("local link is not included", "\n".join(self.errors()))

    def test_missing_reference_link(self):
        self.write("README.md", "[Missing][m]\n[m]: missing.md\n")
        self.assertIn("local link is not included", "\n".join(self.errors()))

    def test_escaping_link(self):
        self.write("README.md", "[Outside](../outside.md)\n")
        self.assertIn("escapes repository", "\n".join(self.errors()))

    def test_percent_encoded_local_link(self):
        self.write("README.md", "[Space](note%20one.md)\n")
        self.write("note one.md", "# Note\n")
        self.assertEqual(self.errors(), [])

    def test_directory_link(self):
        self.write("README.md", "[Docs](docs/)\n")
        self.write("docs/note.md", "# Note\n")
        self.assertEqual(self.errors(), [])

    def test_ignored_artifact_not_scanned(self):
        self.write(".gitignore", "/vendor-input/\n")
        self.write("vendor-input/object.bin", b"\0\xff")
        self.assertEqual(self.errors(), [])

    def test_force_added_artifact_rejected(self):
        self.write(".gitignore", "*.bin\n")
        self.write("object.bin", b"\0")
        subprocess.run(["git", "-C", str(self.root), "add", "-f", "object.bin"], check=True)
        self.assertIn("prohibited artifact", "\n".join(self.errors()))

    def test_local_link_to_ignored_file_rejected(self):
        self.write(".gitignore", "/private/\n")
        self.write("README.md", "[Private](private/note.md)\n")
        self.write("private/note.md", "Not distributed\n")
        self.assertIn("local link is not included", "\n".join(self.errors()))

    def test_unignored_private_directory(self):
        self.write("private/note.md", "Private artifact\n")
        self.assertIn("prohibited artifact", "\n".join(self.errors()))

    def test_private_key_marker_without_echoing_content(self):
        marker = "-----BEGIN OPENSSH" + " PRIVATE KEY-----"
        self.write("note.txt", marker)
        errors = "\n".join(self.errors())
        self.assertIn("private-key marker", errors)
        self.assertNotIn(marker, errors)

    def test_github_token_marker_without_echoing_content(self):
        token = "ghp_" + "a" * 36
        self.write("note.txt", token)
        errors = "\n".join(self.errors())
        self.assertIn("GitHub-token marker", errors)
        self.assertNotIn(token, errors)

    def test_original_workstation_path_rejected(self):
        self.write("note.txt", "/home/" + "researcher/.jcode/scratch/input")
        self.assertIn("workstation research path", "\n".join(self.errors()))

    def test_non_utf8_rejected(self):
        self.write("note.txt", b"\xff")
        self.assertIn("non-UTF-8", "\n".join(self.errors()))

    def test_binary_nul_rejected(self):
        self.write("note.txt", b"data\0data")
        self.assertIn("binary NUL", "\n".join(self.errors()))

    def test_oversized_file_rejected(self):
        self.write("note.txt", b"a" * (CHECKER.MAX_FILE_BYTES + 1))
        self.assertIn("1 MiB", "\n".join(self.errors()))

    def test_symlink_rejected(self):
        self.write("note.txt", "Safe text\n")
        (self.root / "link.txt").symlink_to("note.txt")
        self.assertIn("symlinks are not allowed", "\n".join(self.errors()))

    def test_environment_file_rejected(self):
        self.write(".env.local", "SETTING=value\n")
        self.assertIn("prohibited artifact", "\n".join(self.errors()))

    def test_cli_success_and_failure_exit_statuses(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(CHECKER.main(["--root", str(self.root)]), 0)
            self.write("object.ko", b"data")
            self.assertEqual(CHECKER.main(["--root", str(self.root)]), 1)

    def test_cli_non_repository_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                self.assertEqual(CHECKER.main(["--root", directory]), 2)


if __name__ == "__main__":
    unittest.main()
