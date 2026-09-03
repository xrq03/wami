"""离线检查 README 的实验命令，不导入实验模块，也不执行任何模型调用。"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path
import re
import shlex


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Command:
    """保存文档中的脚本及参数；行号用于直接定位错误命令。"""

    line: int
    script: str
    arguments: tuple[str, ...]


def read_commands(markdown: str) -> list[Command]:
    """只读 PowerShell 代码块中的 Python 脚本命令，合并反引号续行。"""
    commands = []
    for block in re.finditer(r"^```powershell\s*\n(.*?)^```", markdown, re.M | re.S):
        body = block.group(1)
        lines = body.splitlines()
        index = 0
        first_line = markdown.count("\n", 0, block.start(1)) + 1
        while index < len(lines):
            start = index
            line = lines[index].strip()
            while line.endswith("`") and index + 1 < len(lines):
                index += 1
                line = line[:-1] + " " + lines[index].strip()
            index += 1
            if not re.match(r"^python\s+scripts[/\\]", line):
                continue
            # 文档中的脚本路径使用正斜杠；不按 shell 执行任何字符串。
            parts = shlex.split(line)
            commands.append(Command(first_line + start, parts[1], tuple(parts[2:])))
    return commands


def argument_specs(script: Path) -> tuple[set[str], list[set[str]]]:
    """从 AST 读取 add_argument 声明，避免 import 时触发下载或推理。"""
    tree = ast.parse(script.read_text(encoding="utf-8-sig"), filename=str(script))
    known = {"--help", "-h"}
    required = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "add_argument":
            continue
        aliases = {
            arg.value
            for arg in node.args
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str) and arg.value.startswith("-")
        }
        known.update(aliases)
        if aliases and any(
            kw.arg == "required" and isinstance(kw.value, ast.Constant) and kw.value.value is True
            for kw in node.keywords
        ):
            required.append(aliases)
    return known, required


def check_commands(commands: list[Command], root: Path) -> list[str]:
    """检查路径、选项拼写和必需参数；不验证数据、依赖或模型性能。"""
    errors = []
    for command in commands:
        path = root / command.script
        prefix = f"第 {command.line} 行 {command.script}"
        if not path.is_file():
            errors.append(f"{prefix}：脚本不存在")
            continue
        try:
            known, required = argument_specs(path)
        except (SyntaxError, UnicodeError) as exc:
            errors.append(f"{prefix}：无法解析源码：{exc}")
            continue
        supplied = {arg.split("=", 1)[0] for arg in command.arguments if arg.startswith("--")}
        for unknown in sorted(supplied - known):
            errors.append(f"{prefix}：未知参数 {unknown}")
        if not supplied.intersection({"--help"}) and "-h" not in command.arguments:
            for aliases in required:
                if not aliases.intersection(command.arguments) and not aliases.intersection(supplied):
                    errors.append(f"{prefix}：缺少必需参数 {' / '.join(sorted(aliases))}")
    return errors


def main() -> int:
    """打印检查结果；出现缺失脚本或参数错误时返回非零退出码。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--readme", type=Path, default=ROOT / "README.md")
    args = parser.parse_args()
    commands = read_commands(args.readme.read_text(encoding="utf-8-sig"))
    if not commands:
        print("未找到实验命令，不能认定检查通过。")
        return 1
    errors = check_commands(commands, ROOT)
    print(f"读取 {len(commands)} 条命令，涉及 {len({c.script for c in commands})} 个脚本。")
    for error in errors:
        print(error)
    if errors:
        return 1
    print("脚本路径、参数名和必需参数检查通过。未运行实验、未联网、未核验结果数值。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
