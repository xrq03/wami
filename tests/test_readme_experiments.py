"""README 检查器的独立测试，只使用标准库，不加载实验环境。"""

import unittest

from scripts.check_readme_experiments import Command, ROOT, check_commands, read_commands


class ReadmeExperimentTests(unittest.TestCase):
    def test_continued_commands(self):
        """多行 PowerShell 参数必须被当作同一条命令。"""
        text = "# test\n```powershell\npython scripts/demo.py `\n  --help\n```\n"
        self.assertEqual(read_commands(text), [Command(3, "scripts/demo.py", ("--help",))])

    def test_ignores_noncommands(self):
        """正文、安装命令和 text 块里的路径不能误判为待执行实验。"""
        text = "scripts/missing.py\n```text\npython scripts/missing.py\n```\n```powershell\npython -m pip install numpy\n```"
        self.assertEqual(read_commands(text), [])

    def test_missing_script(self):
        errors = check_commands([Command(1, "scripts/not_a_real_script.py", ())], ROOT)
        self.assertTrue(any("脚本不存在" in error for error in errors))

    def test_wrong_ensemble_mode(self):
        """回归：集成脚本没有 --mode，不能因为相似的 --model-a 而放过。"""
        args = ("--model-a", "a.pt", "--model-b", "b.pt", "--test-data", "test.jsonl", "--mode", "or")
        errors = check_commands([Command(1, "scripts/run_paper_mine_ensemble.py", args)], ROOT)
        self.assertTrue(any("未知参数 --mode" in error for error in errors))

    def test_missing_required_option(self):
        errors = check_commands([Command(1, "scripts/run_paper_mine_ensemble.py", ())], ROOT)
        self.assertTrue(any("--model-a" in error for error in errors))

    def test_help_does_not_require_models(self):
        self.assertEqual(check_commands([Command(1, "scripts/run_paper_mine_ensemble.py", ("--help",))], ROOT), [])

    def test_readme_commands(self):
        commands = read_commands((ROOT / "README.md").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(commands), 25)
        self.assertEqual(check_commands(commands, ROOT), [])

    def test_supervisor_guide_commands(self):
        """导师指南必须有可检查的真实实验命令，并使用本地 Ollama 后端。"""
        guide = (ROOT / "docs/supervisor-guide.md").read_text(encoding="utf-8")
        commands = read_commands(guide)
        self.assertGreaterEqual(len(commands), 4)
        self.assertEqual(check_commands(commands, ROOT), [])
        live = [c for c in commands if c.script.endswith('run_qwen_full_live_wami_runtime.py')]
        self.assertEqual(len(live), 1)
        self.assertIn('ollama', live[0].arguments)
        self.assertIn('qwen2.5:7b-instruct', live[0].arguments)


if __name__ == "__main__":
    unittest.main()
