"""资源清单检查的离线测试，不联网或加载模型。"""

import tempfile
import unittest
from pathlib import Path

from scripts.check_runtime_resources import file_state, safe_target, sha256


class RuntimeResourceTests(unittest.TestCase):
    def test_relative_path(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(safe_target(root, "data/image.png"), root.resolve() / "data/image.png")

    def test_rejects_escaping_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            for value in ("../key", "/absolute", "C:/key", "data\\..\\key"):
                with self.subTest(value=value), self.assertRaises(ValueError):
                    safe_target(Path(directory), value)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            self.assertEqual(file_state(Path(directory) / "missing", {"bytes": 3}, False), "missing")

    def test_size_and_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "asset"
            path.write_bytes(b"abc")
            expected = {"bytes": 3, "sha256": sha256(path)}
            self.assertEqual(file_state(path, expected, True), "ready")
            self.assertEqual(file_state(path, {**expected, "bytes": 4}, True), "size-mismatch")
            path.write_bytes(b"xyz")
            self.assertEqual(file_state(path, expected, True), "hash-mismatch")


if __name__ == "__main__":
    unittest.main()
