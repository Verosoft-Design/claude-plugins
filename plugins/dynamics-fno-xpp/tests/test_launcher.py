import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from fixtures import SCRIPTS, TempTest, write

NODE = shutil.which('node')


@unittest.skipUnless(NODE, 'node is not on PATH')
class LauncherTests(TempTest):
    def launch(self, env):
        script = write(self.root / 'echo.py', 'import sys\nsys.stdout.buffer.write(sys.stdin.buffer.read())\nsys.exit(int(sys.argv[1]))\n')
        return subprocess.run([NODE, str(SCRIPTS / 'run-python.mjs'), str(script), '7'], input=b'payload\r\n\x00\xc3\xa9\n', capture_output=True, env=self.env | env, cwd=self.root, timeout=30)

    def test_stdin_bytes_and_exit_code(self):
        r = self.launch({'FNO_PYTHON': sys.executable})
        self.assertEqual(r.stdout, b'payload\r\n\x00\xc3\xa9\n')
        self.assertEqual(r.returncode, 7)
        self.assertEqual(r.stderr, b'')

    def test_nonexistent_override_falls_back(self):
        r = self.launch({'FNO_PYTHON': str(self.root / 'missing-python'), 'PATH': str(Path(sys.executable).parent) + os.pathsep + self.env.get('PATH', '')})
        self.assertEqual(r.returncode, 7)
        self.assertEqual(r.stdout, b'payload\r\n\x00\xc3\xa9\n')

    @unittest.skipIf(os.name == 'nt', 'isolating Python launcher aliases is platform dependent')
    def test_no_python_is_nonblocking(self):
        # Invoke Node by absolute path; an empty search directory hides Python
        # even on systems that install Node and Python in the same directory.
        search_dir = self.root / 'empty-path'
        search_dir.mkdir()
        r = self.launch({'PATH': str(search_dir)})
        self.assertEqual((r.returncode, r.stdout), (0, b''))
        self.assertIn(b'no Python 3 found', r.stderr)
