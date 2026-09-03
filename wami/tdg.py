"""WAMI 工具依赖图 TDG 构建与安全流分析模块。

本文件把智能体工具调用计划解析成图结构。节点表示工具调用，边表示数据依赖、执行顺序、记忆读写和不可信内容传播路径。WAMI 依靠工具依赖图理解多步间接提示注入，而不是只看关键词。"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
import ast
from collections import defaultdict, deque
from typing import Any, Iterable


ACTION_RE = re.compile( 
    r"(?P<prefix>(?:Action|Tool|Call)\s*:)?\s*"
    r"(?P<assign>\$?[A-Za-z_][\w-]*\s*=)?\s*"
    r"(?P<tool>[A-Za-z_][\w.-]*)\s*"
    r"(?:\((?P<args>.*)\)|\{(?P<json>.*)\})?\s*$",
    re.IGNORECASE,
)
VAR_RE = re.compile(r"\$[A-Za-z_][\w-]*|\$\d+")
NOISE_PREFIXES = ("thought:", "observation:", "reasoning:", "final answer:")
UNTRUSTED_TOOL_PATTERNS = ("readuntrustedinjection", "parseinjectedinstruction", "readtoolresponse", "readcontext")
EXTERNAL_OBSERVATION_TOOLS = ("read", "search", "fetch", "get", "inspect", "extract", "parse")
SENSITIVE_PATTERNS = (
    "secret",
    "password",
    "credential",
    "private",
    "token",
    "api_key",
    "card",
    "payment",
    "iban",
    "email",
    "phone",
    "address",
)
SINK_PATTERNS = (
    "send",
    "email",
    "upload",
    "exfiltrate",
    "transfer",
    "post",
    "share",
    "revealsecret",
    "answerquestion",
    "respondtouser",
)


@dataclass
class TDGNode:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    id: str
    tool: str
    params: dict[str, Any] = field(default_factory=dict)
    raw: str = ""


@dataclass
class TDG:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    nodes: list[TDGNode]
    edges: list[tuple[str, str]]

    def parents(self) -> dict[str, list[str]]:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        out: dict[str, list[str]] = defaultdict(list)
        for src, dst in self.edges:
            out[dst].append(src)
        return out

    def children(self) -> dict[str, list[str]]:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        out: dict[str, list[str]] = defaultdict(list)
        for src, dst in self.edges:
            out[src].append(dst)
        return out

    def topological_order(self) -> list[TDGNode]:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        ids = {n.id for n in self.nodes}
        indeg = {node_id: 0 for node_id in ids}
        children = defaultdict(list)
        for src, dst in self.edges:
            if src in ids and dst in ids:
                children[src].append(dst)
                indeg[dst] += 1
        queue = deque([n.id for n in self.nodes if indeg[n.id] == 0])
        order: list[str] = []
        while queue:
            node_id = queue.popleft()
            order.append(node_id)
            for child in children[node_id]:
                indeg[child] -= 1
                if indeg[child] == 0:
                    queue.append(child)
        if len(order) != len(self.nodes):
            return self.nodes
        by_id = {n.id: n for n in self.nodes}
        return [by_id[node_id] for node_id in order]


@dataclass
class TDGSecurityNode:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    node_id: str
    tool: str
    order: int
    external_observation: bool = False
    untrusted_source: bool = False
    sensitive_source: bool = False
    tainted: bool = False
    sensitive: bool = False
    sink: bool = False
    memory_reads: list[str] = field(default_factory=list)
    memory_writes: list[str] = field(default_factory=list)


@dataclass
class TDGSecurityEdge:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    src: str
    dst: str
    kind: str
    evidence: str = ""


@dataclass
class TDGSecurityAnalysis:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    nodes: dict[str, TDGSecurityNode]
    edges: list[TDGSecurityEdge]
    tool_order: list[str]
    untrusted_paths: list[list[str]]
    sensitive_flows: list[list[str]]

    def edges_by_kind(self, kind: str) -> list[TDGSecurityEdge]:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        return [edge for edge in self.edges if edge.kind == kind]


def _parse_args(arg_text: str | None) -> dict[str, Any]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    if not arg_text:
        return {}
    text = arg_text.strip()
    if not text:
        return {}
    if text.startswith("{") and text.endswith("}"):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    params: dict[str, Any] = {}
    parts = _split_top_level_args(text)
    for idx, part in enumerate(parts):
        part = part.strip()
        if not part:
            continue
        if "=" in part:
            key, value = part.split("=", 1)
            params[key.strip()] = _decode_arg_value(value)
        else:
            params[f"arg{idx}"] = _decode_arg_value(part)
    return params


def _split_top_level_args(text: str) -> list[str]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    parts: list[str] = []
    start = 0
    quote = ""
    escaped = False
    for idx, char in enumerate(text):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = ""
            continue
        if char in {"'", '"'}:
            quote = char
            continue
        if char == ",":
            parts.append(text[start:idx])
            start = idx + 1
    parts.append(text[start:])
    return parts


def _decode_arg_value(value: str) -> Any:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    text = value.strip()
    if not text:
        return ""
    try:
        return ast.literal_eval(text)
    except (SyntaxError, ValueError):
        return text.strip("\"'")


def _line_candidates(plan: str) -> Iterable[str]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    for raw in plan.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.lower().startswith(NOISE_PREFIXES):
            continue
        if line.lower().startswith(("action:", "tool:", "call:")) or ACTION_RE.match(line):
            yield line


def build_tdg(plan: str, toolset: set[str] | None = None) -> TDG:
    """构建工具依赖图。
    
    输入是一段 agent 工具调用计划，函数会逐行解析 Action、Tool 或 Call，把每一步工具调用变成 TDG 节点，并根据变量引用、步骤引用、memory 读写关系建立有向边。输出的 TDG 是 WAMI 后续安全流分析和 world model rollout 的基础。"""
    nodes: list[TDGNode] = []
    edges: list[tuple[str, str]] = []
    variable_owner: dict[str, str] = {}

    for index, line in enumerate(_line_candidates(plan)):
        match = ACTION_RE.match(line)
        if not match:
            continue
        tool = match.group("tool")
        if toolset and tool not in toolset:
            continue
        node_id = f"n{len(nodes)}"
        arg_text = match.group("args") or match.group("json")
        params = _parse_args(arg_text)
        node = TDGNode(id=node_id, tool=tool, params=params, raw=line)
        nodes.append(node)

        assign = match.group("assign")
        if assign:
            variable_owner[assign.rstrip("=").strip()] = node_id
        variable_owner[f"${index}"] = node_id
        variable_owner[f"${len(nodes) - 1}"] = node_id

        param_blob = json.dumps(params, ensure_ascii=False) + " " + line
        for var in VAR_RE.findall(param_blob):
            parent = variable_owner.get(var)
            if parent and parent != node_id:
                edges.append((parent, node_id))

    seen = set()
    deduped = []
    for edge in edges:
        if edge not in seen:
            seen.add(edge)
            deduped.append(edge)
    return TDG(nodes=nodes, edges=deduped)


def analyze_tdg_security(tdg: TDG) -> TDGSecurityAnalysis:
    """分析 TDG 中的安全语义。
    
    函数会给每个工具节点标注是否来自外部 observation、是否是不可信来源、是否涉及敏感数据、是否是外发或副作用 sink，并追踪不可信内容和敏感数据流向。它不直接替代 MINE 决策，而是为 WAMI 提供结构化证据。"""
    order = tdg.topological_order()
    order_index = {node.id: idx for idx, node in enumerate(order)}
    nodes = {
        node.id: TDGSecurityNode(
            node_id=node.id,
            tool=node.tool,
            order=order_index[node.id],
            external_observation=_is_external_observation(node),
            untrusted_source=_is_untrusted_source(node),
            sensitive_source=_has_sensitive_content(node),
            sink=_is_sink(node),
            memory_reads=_memory_refs(node),
            memory_writes=[node.id],
        )
        for node in order
    }
    edges: list[TDGSecurityEdge] = []
    for src, dst in tdg.edges:
        edges.append(TDGSecurityEdge(src, dst, "data", "$ reference"))

    for prev, cur in zip(order, order[1:]):
        edges.append(TDGSecurityEdge(prev.id, cur.id, "order", "tool order"))
        edges.append(TDGSecurityEdge(prev.id, cur.id, "memory", "working memory carries prior state"))

    for node in order:
        for ref in _memory_refs(node):
            ref_id = _normalize_ref(ref, order)
            if ref_id and ref_id != node.id:
                edges.append(TDGSecurityEdge(ref_id, node.id, "memory", ref))

    children: dict[str, list[str]] = defaultdict(list)
    for edge in edges:
        if edge.kind in {"data", "memory", "order"}:
            children[edge.src].append(edge.dst)

    for node in order:
        info = nodes[node.id]
        info.tainted = info.untrusted_source
        info.sensitive = info.sensitive_source
    for node in order:
        info = nodes[node.id]
        for child in children.get(node.id, []):
            if info.tainted:
                nodes[child].tainted = True
                edges.append(TDGSecurityEdge(node.id, child, "taint", "untrusted content propagation"))
            if info.sensitive:
                nodes[child].sensitive = True
                edges.append(TDGSecurityEdge(node.id, child, "sensitive", "sensitive data propagation"))
    edges = _dedupe_security_edges(edges)

    untrusted_paths = _paths_to_sinks(nodes, children, source_attr="untrusted_source", flow_attr="tainted")
    sensitive_flows = _paths_to_sinks(nodes, children, source_attr="sensitive_source", flow_attr="sensitive")
    return TDGSecurityAnalysis(
        nodes=nodes,
        edges=edges,
        tool_order=[node.id for node in order],
        untrusted_paths=untrusted_paths,
        sensitive_flows=sensitive_flows,
    )


def _dedupe_security_edges(edges: list[TDGSecurityEdge]) -> list[TDGSecurityEdge]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    seen = set()
    out = []
    for edge in edges:
        key = (edge.src, edge.dst, edge.kind, edge.evidence)
        if key not in seen:
            seen.add(key)
            out.append(edge)
    return out


def _compact_tool(node: TDGNode) -> str:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    return node.tool.lower().replace("_", "").replace("-", "")


def _blob(node: TDGNode) -> str:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    return f"{node.tool} {json.dumps(node.params, ensure_ascii=False)} {node.raw}".lower()


def _is_untrusted_source(node: TDGNode) -> bool:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    compact = _compact_tool(node)
    blob = _blob(node)
    return any(pattern in compact for pattern in UNTRUSTED_TOOL_PATTERNS) or "untrusted" in blob or "injection" in blob


def _is_external_observation(node: TDGNode) -> bool:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    compact = _compact_tool(node)
    blob = _blob(node)
    return any(compact.startswith(prefix) for prefix in EXTERNAL_OBSERVATION_TOOLS) or any(
        key in blob for key in ("url", "image", "context", "response", "observation")
    )


def _has_sensitive_content(node: TDGNode) -> bool:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    blob = _blob(node)
    return any(pattern in blob for pattern in SENSITIVE_PATTERNS)


def _is_sink(node: TDGNode) -> bool:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    compact = _compact_tool(node)
    return any(pattern in compact for pattern in SINK_PATTERNS)


def _memory_refs(node: TDGNode) -> list[str]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    blob = json.dumps(node.params, ensure_ascii=False) + " " + node.raw
    return VAR_RE.findall(blob)


def _normalize_ref(ref: str, order: list[TDGNode]) -> str | None:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    if ref.startswith("$") and ref[1:].isdigit():
        index = int(ref[1:])
        if 0 <= index < len(order):
            return order[index].id
    return None


def _paths_to_sinks(
    nodes: dict[str, TDGSecurityNode],
    children: dict[str, list[str]],
    source_attr: str,
    flow_attr: str,
) -> list[list[str]]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    paths: list[list[str]] = []
    sources = [node_id for node_id, node in nodes.items() if getattr(node, source_attr)]
    for source in sources:
        stack = [(source, [source])]
        while stack:
            cur, path = stack.pop()
            cur_node = nodes[cur]
            if cur != source and cur_node.sink and getattr(cur_node, flow_attr):
                paths.append(path)
            for child in children.get(cur, []):
                if child not in path and getattr(nodes[child], flow_attr):
                    stack.append((child, path + [child]))
    seen = set()
    unique = []
    for path in paths:
        key = tuple(path)
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique
