"""风险分数复算的边界测试，测试 CSV 仅写入临时目录。"""

import csv
from pathlib import Path
import tempfile
import unittest

from scripts.summarize_webagentguard_operating_points import summarize


class WebAgentGuardSummaryTests(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = Path(self.folder.name) / "scores.csv"

    def write_rows(self, scores):
        """构造标签、分数和原decision相冲突的样本，确保仅使用规定的分数规则。"""
        with self.path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["dataset", "label", "risk_score", "latency_ms", "error", "blocked"])
            for label, score, error in scores:
                writer.writerow(["BIPIA", label, score, 10, error, False])

    def test_counts_and_input_unchanged(self):
        self.write_rows([(1, 80, ""), (1, 79, ""), (0, 85, ""), (0, 20, "")])
        before = self.path.read_bytes()
        row = summarize(self.path, "BIPIA", 80)
        self.assertEqual([row[k] for k in ["tp", "fn", "fp", "tn"]], [1, 1, 1, 1])
        self.assertEqual(row["ir"], 0.5)
        self.assertEqual(row["fpr"], 0.5)
        self.assertEqual(self.path.read_bytes(), before)

    def test_rejects_failed_inference(self):
        self.write_rows([(1, 80, "timeout"), (0, 20, "")])
        with self.assertRaisesRegex(ValueError, "推理错误"):
            summarize(self.path, "BIPIA", 80)

    def test_rejects_nonfinite_score(self):
        self.write_rows([(1, "nan", ""), (0, 20, "")])
        with self.assertRaisesRegex(ValueError, "分数无效"):
            summarize(self.path, "BIPIA", 80)

    def test_rejects_missing_dataset(self):
        self.write_rows([(1, 80, ""), (0, 20, "")])
        with self.assertRaisesRegex(ValueError, "没有"):
            summarize(self.path, "AgentDojo", 80)

    def test_rejects_missing_class(self):
        self.write_rows([(1, 80, "")])
        with self.assertRaisesRegex(ValueError, "缺少"):
            summarize(self.path, "BIPIA", 80)


if __name__ == "__main__":
    unittest.main()
