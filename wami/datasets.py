"""WAMI 数据集转换与加载模块。

本文件把三个测试集的不同原始格式转换为统一的用户意图、工具计划、标签格式。统一格式便于 WAMI 和所有对比方法在同一数据口径下计算攻击拦截率、正常误拦率和准确率。"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import random
from typing import Any, Iterable

from .shadow import PlanSample


def write_jsonl(samples: Iterable[PlanSample], path: str | Path) -> int:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(
                json.dumps(
                    {"intent": sample.intent, "plan": sample.plan, "label": sample.label},
                    ensure_ascii=False,
                )
                + "\n"
            )
            count += 1
    return count


def load_plan_samples(path: str | Path) -> list[PlanSample]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    samples: list[PlanSample] = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            item = json.loads(line)
            samples.append(PlanSample(item["intent"], item["plan"], int(item.get("label", 0))))
    return samples


def convert_injecagent(root: str | Path) -> list[PlanSample]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    root = Path(root)
    data_dir = root / "data"
    samples: list[PlanSample] = []

    user_cases = data_dir / "user_cases.jsonl"
    if user_cases.exists():
        for item in _read_jsonl(user_cases):
            samples.append(_injecagent_benign(item))

    for name in (
        "test_cases_ds_base.json",
        "test_cases_ds_enhanced.json",
        "test_cases_dh_base.json",
        "test_cases_dh_enhanced.json",
    ):
        path = data_dir / name
        if not path.exists():
            continue
        rows = json.loads(path.read_text(encoding="utf-8"))
        for item in rows:
            samples.append(_injecagent_benign(item))
            samples.append(_injecagent_attack(item))
    return samples


def convert_bipia(root: str | Path, max_pairs_per_task: int | None = None) -> list[PlanSample]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    root = Path(root)
    benchmark = root / "benchmark"
    samples: list[PlanSample] = []

    task_files = [
        ("email", benchmark / "email" / "train.jsonl", benchmark / "text_attack_train.json"),
        ("email", benchmark / "email" / "test.jsonl", benchmark / "text_attack_test.json"),
        ("table", benchmark / "table" / "train.jsonl", benchmark / "text_attack_train.json"),
        ("table", benchmark / "table" / "test.jsonl", benchmark / "text_attack_test.json"),
        ("code", benchmark / "code" / "train.jsonl", benchmark / "code_attack_train.json"),
        ("code", benchmark / "code" / "test.jsonl", benchmark / "code_attack_test.json"),
    ]
    for task, context_path, attack_path in task_files:
        if not context_path.exists() or not attack_path.exists():
            continue
        contexts = _read_jsonl(context_path)
        attacks = _flatten_attack_json(attack_path)
        if max_pairs_per_task:
            contexts = contexts[:max_pairs_per_task]
        for idx, item in enumerate(contexts):
            samples.append(_bipia_benign(task, item))
            if attacks:
                attack = attacks[idx % len(attacks)]
                samples.append(_bipia_attack(task, item, attack))
    return samples


def convert_agentdojo(
    root: str | Path,
    version: str = "v1",
    max_attack_pairs_per_suite: int | None = 300,
    seed: int = 13,
) -> list[PlanSample]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    root = Path(root)
    base = root / "src" / "agentdojo" / "default_suites" / version
    if not base.exists():
        raise FileNotFoundError(f"AgentDojo suite directory not found: {base}")
    samples: list[PlanSample] = []
    rng = random.Random(seed)
    for suite_dir in sorted(path for path in base.iterdir() if path.is_dir() and path.name != "tools"):
        user_tasks = _agentdojo_tasks_from_file(suite_dir / "user_tasks.py", "PROMPT")
        injection_tasks = _agentdojo_tasks_from_file(suite_dir / "injection_tasks.py", "GOAL")
        for user in user_tasks:
            if user["text"] and user["calls"]:
                samples.append(PlanSample(user["text"], _calls_to_plan(user["calls"]), label=0))
        attack_pairs = [(user, inj) for user in user_tasks for inj in injection_tasks if user["text"] and inj["text"]]
        rng.shuffle(attack_pairs)
        if max_attack_pairs_per_suite is not None:
            attack_pairs = attack_pairs[:max_attack_pairs_per_suite]
        for user, injection in attack_pairs:
            calls = list(user["calls"])
            calls.append(
                {
                    "function": "ReadUntrustedInjection",
                    "args": {"suite": suite_dir.name, "goal": injection["text"]},
                }
            )
            calls.extend(injection["calls"] or [{"function": "ExecuteInjectionGoal", "args": {"goal": injection["text"]}}])
            samples.append(PlanSample(user["text"], _calls_to_plan(calls), label=1))
    return samples


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def _flatten_attack_json(path: Path) -> list[dict[str, str]]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    data = json.loads(path.read_text(encoding="utf-8"))
    attacks: list[dict[str, str]] = []
    for category, prompts in data.items():
        for prompt in prompts:
            attacks.append({"category": str(category), "prompt": str(prompt)})
    return attacks


def _parse_params(value: Any) -> dict[str, Any]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    if isinstance(value, dict):
        return value
    if value is None:
        return {}
    text = str(value)
    try:
        parsed = ast.literal_eval(text)
        return parsed if isinstance(parsed, dict) else {"value": parsed}
    except (SyntaxError, ValueError):
        return {"value": text}


def _format_args(params: dict[str, Any]) -> str:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    return ", ".join(f"{key}={json.dumps(value, ensure_ascii=False)}" for key, value in params.items())


def _safe_text(value: Any, limit: int = 1200) -> str:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    text = str(value).replace("\n", "\\n")
    return text[:limit]


def _agentdojo_tasks_from_file(path: Path, text_attr: str) -> list[dict[str, Any]]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    if not path.exists():
        return []
    tree = ast.parse(path.read_text(encoding="utf-8"))
    tasks: list[dict[str, Any]] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        text = ""
        calls: list[dict[str, Any]] = []
        for stmt in node.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name) and target.id == text_attr:
                        text = _ast_value_to_text(stmt.value)
            elif isinstance(stmt, ast.FunctionDef) and stmt.name == "ground_truth":
                calls = _extract_function_calls(stmt)
        if text:
            tasks.append({"name": node.name, "text": text, "calls": calls})
    return tasks


def _ast_value_to_text(node: ast.AST) -> str:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    try:
        value = ast.literal_eval(node)
        return _safe_text(value, 2000)
    except (ValueError, SyntaxError):
        return _safe_text(ast.unparse(node), 2000)


def _extract_function_calls(func: ast.FunctionDef) -> list[dict[str, Any]]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    calls: list[dict[str, Any]] = []
    for node in ast.walk(func):
        if not isinstance(node, ast.Call):
            continue
        name = ""
        args: dict[str, Any] = {}
        if isinstance(node.func, ast.Name) and node.func.id == "FunctionCall":
            for kw in node.keywords:
                if kw.arg == "function":
                    name = _literal_or_source(kw.value)
                elif kw.arg in {"placeholder_args", "args"} and not args:
                    args = _dict_from_ast(kw.value)
        if name:
            calls.append({"function": name, "args": args})
    return calls


def _literal_or_source(node: ast.AST) -> str:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    try:
        value = ast.literal_eval(node)
        return str(value)
    except (ValueError, SyntaxError):
        return ast.unparse(node)


def _dict_from_ast(node: ast.AST) -> dict[str, Any]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    if not isinstance(node, ast.Dict):
        return {"value": ast.unparse(node)}
    out: dict[str, Any] = {}
    for key, value in zip(node.keys, node.values):
        if key is None:
            continue
        out[_literal_or_source(key)] = _literal_or_source(value)
    return out


def _calls_to_plan(calls: list[dict[str, Any]]) -> str:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    lines = []
    for call in calls:
        tool = str(call.get("function") or "UnknownTool")
        args = call.get("args") if isinstance(call.get("args"), dict) else {}
        lines.append(f"Action: {tool}({_format_args(args)})")
    return "\n".join(lines)


def _injecagent_benign(item: dict[str, Any]) -> PlanSample:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    intent = str(item.get("User Instruction", ""))
    user_tool = str(item.get("User Tool", "UserTool"))
    params = _parse_params(item.get("Tool Parameters"))
    response = _safe_text(item.get("Tool Response Template", "")).replace(
        "<Attacker Instruction>", "benign external content"
    )
    plan = "\n".join(
        [
            f"Action: {user_tool}({_format_args(params)})",
            f"Action: ReadToolResponse(input=$0, response={json.dumps(response, ensure_ascii=False)})",
            "Action: RespondToUser(input=$1)",
        ]
    )
    return PlanSample(intent=intent, plan=plan, label=0)


def _injecagent_attack(item: dict[str, Any]) -> PlanSample:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    intent = str(item.get("User Instruction", ""))
    user_tool = str(item.get("User Tool", "UserTool"))
    params = _parse_params(item.get("Tool Parameters"))
    response = _safe_text(item.get("Tool Response", item.get("Tool Response Template", "")))
    attacker_instruction = _safe_text(item.get("Attacker Instruction", ""))
    attacker_tools = item.get("Attacker Tools") or ["ExfiltrateData"]
    if not isinstance(attacker_tools, list):
        attacker_tools = [str(attacker_tools)]
    lines = [
        f"Action: {user_tool}({_format_args(params)})",
        f"Action: ReadToolResponse(input=$0, response={json.dumps(response, ensure_ascii=False)})",
    ]
    previous = "$1"
    for index, tool in enumerate(attacker_tools):
        node_input = previous
        lines.append(
            f"Action: {tool}(input={node_input}, instruction={json.dumps(attacker_instruction, ensure_ascii=False)})"
        )
        previous = f"${index + 2}"
    return PlanSample(intent=intent, plan="\n".join(lines), label=1)


def _bipia_benign(task: str, item: dict[str, Any]) -> PlanSample:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    question = str(item.get("question", item.get("prompt", "Answer the question from the context.")))
    context = _safe_text(item.get("context", item.get("code", "")))
    plan = "\n".join(
        [
            f"Action: ReadContext(task={json.dumps(task)}, context={json.dumps(context, ensure_ascii=False)})",
            f"Action: AnswerQuestion(question={json.dumps(question, ensure_ascii=False)}, context=$0)",
        ]
    )
    return PlanSample(intent=question, plan=plan, label=0)


def _bipia_attack(task: str, item: dict[str, Any], attack: dict[str, str]) -> PlanSample:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    question = str(item.get("question", item.get("prompt", "Answer the question from the context.")))
    context = _safe_text(item.get("context", item.get("code", "")))
    attack_prompt = _safe_text(attack["prompt"])
    attack_tool = "ExecuteBash" if task == "code" else "ExfiltrateData"
    plan = "\n".join(
        [
            f"Action: ReadContext(task={json.dumps(task)}, context={json.dumps(context, ensure_ascii=False)})",
            f"Action: ParseInjectedInstruction(input=$0, instruction={json.dumps(attack_prompt, ensure_ascii=False)})",
            f"Action: {attack_tool}(input=$1, category={json.dumps(attack['category'], ensure_ascii=False)})",
        ]
    )
    return PlanSample(intent=question, plan=plan, label=1)
