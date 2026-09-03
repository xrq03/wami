"""WAMI runtime trace 适配模块。

本文件把真实本地智能体的运行事件转换成工具依赖图和工具计划视图，让 WAMI 可以在工具动作执行前进行动态拦截。它连接了真实智能体循环和论文中的工具依赖图与 MINE 判断流程。"""

from __future__ import annotations

from dataclasses import dataclass, field
import json
import re
from typing import Any

from .gateway import GateDecision, WAMIGateway
from .tdg import TDG, TDGNode, TDGSecurityAnalysis, analyze_tdg_security


REF_RE = re.compile(r"(?:step|event|tool)\s*[_-]?(?P<num>\d+)|\$(?P<var>\d+)", re.IGNORECASE)
UNTRUSTED_HINTS = ("email", "web", "browser", "slack", "calendar", "document", "attachment", "image", "user_upload")
SENSITIVE_HINTS = ("password", "secret", "credential", "token", "api_key", "payment", "iban", "account", "medical")
SIDE_EFFECT_SINKS = (
    "exfiltrate",
    "exfiltratedata",
    "sendemail",
    "send_email",
    "sendmoney",
    "send_money",
    "transfer",
    "delete",
    "delete_file",
    "create_calendar_event",
    "createcalendarevent",
    "upload",
    "share",
    "post",
    "invite",
    "add_user",
    "updatepassword",
    "update_password",
    "unlock",
    "grantguestaccess",
    "scheduletransaction",
    "schedule_transaction",
    "updatescheduledtransaction",
    "update_scheduled_transaction",
)
USER_RESPONSE_SINKS = ("respondtouser", "respond_to_user", "answerquestion", "answer_question", "summarize")
INJECTION_LEAK_PATTERNS = (
    "ignore previous",
    "system override",
    "attacker@example.com",
    "reveal the secret",
    "send account data",
    "transfer",
)
SAFE_REFUSAL_PATTERNS = (
    "cannot",
    "can't",
    "will not",
    "won't",
    "should not",
    "do not",
    "not follow",
    "not execute",
    "ignore the injected",
    "treat it as data",
    "prompt injection",
)


@dataclass
class RuntimeTraceEvent:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""

    event_id: str
    tool: str
    input: dict[str, Any] = field(default_factory=dict)
    output: Any = None
    observation_source: str = ""
    trust_level: str = "internal"
    reads: list[str] = field(default_factory=list)
    writes: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    timestamp: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeTrace:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    intent: str
    events: list[RuntimeTraceEvent]
    session_id: str = ""
    user_id: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RuntimeInspection:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    decision: GateDecision
    tdg: TDG
    security: TDGSecurityAnalysis
    plan_view: str


def build_runtime_tdg(trace: RuntimeTrace) -> TDG:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    nodes: list[TDGNode] = []
    edges: list[tuple[str, str]] = []
    event_to_node: dict[str, str] = {}
    memory_owner: dict[str, str] = {}

    for index, event in enumerate(trace.events):
        node_id = f"rt{index}"
        event_to_node[event.event_id] = node_id
        params = {
            "input": event.input,
            "output": event.output,
            "observation_source": event.observation_source,
            "trust_level": event.trust_level,
            "reads": event.reads,
            "writes": event.writes,
            "metadata": event.metadata,
        }
        nodes.append(TDGNode(id=node_id, tool=event.tool, params=params, raw=_event_raw(event)))

        for dep in event.depends_on:
            parent = event_to_node.get(dep) or _resolve_event_ref(dep, event_to_node)
            if parent:
                edges.append((parent, node_id))

        blob = json.dumps(event.input, ensure_ascii=False, default=str)
        for ref in REF_RE.finditer(blob):
            parent = event_to_node.get(ref.group(0)) or event_to_node.get(f"e{ref.group('num') or ref.group('var')}")
            if parent:
                edges.append((parent, node_id))

        for key in event.reads:
            parent = memory_owner.get(key)
            if parent:
                edges.append((parent, node_id))
        for key in event.writes:
            memory_owner[key] = node_id

        if index > 0:
            edges.append((f"rt{index - 1}", node_id))

    return TDG(nodes=nodes, edges=_dedupe_edges(edges))


def runtime_trace_to_plan(trace: RuntimeTrace) -> str:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    lines = []
    for index, event in enumerate(trace.events):
        args = {
            "input": event.input,
            "output": event.output,
            "source": event.observation_source,
            "trust": event.trust_level,
            "reads": event.reads,
            "writes": event.writes,
            "depends_on": event.depends_on,
        }
        rendered = json.dumps(args, ensure_ascii=False, default=str)
        lines.append(f"Action: {event.tool}({rendered})")
        if event.trust_level.lower() in {"untrusted", "external", "tainted"} or _looks_untrusted(event):
            lines.append(
                "Action: ReadUntrustedInjection("
                f"input=${index}, source={json.dumps(event.observation_source or event.tool)}, "
                f"instruction={json.dumps(str(event.output)[:800], ensure_ascii=False)})"
            )
    return "\n".join(lines)


class RuntimeWAMIGateway:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""

    def __init__(self, gateway: WAMIGateway):
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        self.gateway = gateway

    def inspect_trace(self, trace: RuntimeTrace) -> RuntimeInspection:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        tdg = build_runtime_tdg(trace)
        security = analyze_tdg_security(tdg)
        plan_view = runtime_trace_to_plan(trace)
        decision = self.gateway.inspect(trace.intent, plan_view)
        if decision.allowed:
            flow_decision = self._flow_decision(security, tdg)
            if flow_decision:
                decision = flow_decision
        return RuntimeInspection(decision=decision, tdg=tdg, security=security, plan_view=plan_view)

    @staticmethod
    def _flow_decision(security: TDGSecurityAnalysis, tdg: TDG) -> GateDecision | None:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        raw_by_id = {node.id: node.raw for node in tdg.nodes}
        for path in security.untrusted_paths:
            if len(path) >= 2:
                sink_id = path[-1]
                sink = security.nodes[sink_id]
                if is_side_effect_sink(sink.tool):
                    return GateDecision(False, sink.order, sink.tool, 0.0, 0.0, "runtime trace shows untrusted content flow into side-effect sink")
                if _is_user_response_sink(sink.tool) and _node_has_injection_leak(raw_by_id.get(sink_id, "")):
                    return GateDecision(False, sink.order, sink.tool, 0.0, 0.0, "runtime trace response appears to leak or execute injected instruction")
        for path in security.sensitive_flows:
            if len(path) >= 2:
                sink_id = path[-1]
                sink = security.nodes[sink_id]
                if is_side_effect_sink(sink.tool):
                    return GateDecision(False, sink.order, sink.tool, 0.0, 0.0, "runtime trace shows sensitive data flow into side-effect sink")
                if _is_user_response_sink(sink.tool) and _node_has_sensitive_leak(raw_by_id.get(sink_id, "")):
                    return GateDecision(False, sink.order, sink.tool, 0.0, 0.0, "runtime trace response appears to reveal sensitive data")
        return None


def _event_raw(event: RuntimeTraceEvent) -> str:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    return json.dumps(
        {
            "event_id": event.event_id,
            "tool": event.tool,
            "input": event.input,
            "output": event.output,
            "source": event.observation_source,
            "trust": event.trust_level,
            "reads": event.reads,
            "writes": event.writes,
            "depends_on": event.depends_on,
        },
        ensure_ascii=False,
        default=str,
    )


def _looks_untrusted(event: RuntimeTraceEvent) -> bool:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    source = f"{event.observation_source} {event.tool}".lower()
    output = str(event.output).lower()
    if any(hint in source for hint in UNTRUSTED_HINTS) and any(
        phrase in output for phrase in ("ignore previous", "system override", "send", "reveal", "transfer")
    ):
        return True
    return event.trust_level.lower() in {"untrusted", "external", "tainted"}


def _resolve_event_ref(ref: str, event_to_node: dict[str, str]) -> str | None:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    if ref in event_to_node:
        return event_to_node[ref]
    match = REF_RE.search(ref)
    if not match:
        return None
    value = match.group("num") or match.group("var")
    return event_to_node.get(f"e{value}") or event_to_node.get(value)


def _dedupe_edges(edges: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    seen = set()
    out = []
    for edge in edges:
        if edge[0] != edge[1] and edge not in seen:
            seen.add(edge)
            out.append(edge)
    return out


def _compact_tool(tool: str) -> str:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    return tool.lower().replace("-", "").replace("_", "")


def is_side_effect_sink(tool: str) -> bool:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    compact = _compact_tool(tool)
    return any(pattern.replace("_", "") in compact for pattern in SIDE_EFFECT_SINKS)


def _is_user_response_sink(tool: str) -> bool:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    compact = _compact_tool(tool)
    return any(pattern.replace("_", "") in compact for pattern in USER_RESPONSE_SINKS)


def _node_has_injection_leak(raw: str) -> bool:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    blob = raw.lower()
    if any(pattern in blob for pattern in SAFE_REFUSAL_PATTERNS):
        return False
    return any(pattern in blob for pattern in INJECTION_LEAK_PATTERNS)


def _node_has_sensitive_leak(raw: str) -> bool:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    blob = raw.lower()
    if any(pattern in blob for pattern in SAFE_REFUSAL_PATTERNS):
        return False
    return any(pattern in blob for pattern in SENSITIVE_HINTS)
