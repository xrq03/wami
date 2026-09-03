"""WAMI 主防御网关模块。

本文件实现最终放行或拦截决策。它接收用户意图和工具计划或运行轨迹，构建工具依赖图，滚动世界模型状态，计算 MINE 轨迹对齐分数，并根据动态阈值判断是否拦截。"""

from __future__ import annotations

from dataclasses import dataclass
import math

from .gateway import GateDecision, WAMIGateway
from .tdg import build_tdg


@dataclass
class PaperMINEConfig:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    base_threshold: float = 0.15
    decay: float = 0.02
    plan_threshold: float | None = None
    use_plan_mine: bool = True
    risk_margin: float = 0.15
    passive_margin: float = 0.10
    use_transition_mine: bool = False
    transition_fusion: float = 0.35
    use_auxiliary_heads: bool = False
    auxiliary_fusion: float = 0.20
    use_来源memory_memory: bool = False
    来源memory_fusion: float = 0.10


class PaperMINEGateway:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""

    def __init__(self, model, config: PaperMINEConfig | None = None):
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        self.model = model
        self.config = config or PaperMINEConfig()
        if self.config.plan_threshold is None:
            self.config.plan_threshold = self.config.base_threshold

    def threshold(self, step: int) -> float:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        return self.config.base_threshold * math.exp(-self.config.decay * step)

    def inspect(self, intent: str, plan: str, toolset: set[str] | None = None) -> GateDecision:
        """执行 WAMI 主拦截判断。
        
        函数接收用户原始意图和 agent 工具计划，先构建 TDG，再按工具执行顺序滚动 world model 状态，计算 MINE 对齐分数、转移分数和来源记忆分数。若某一步分数低于动态阈值，则返回 block 决策和具体原因。"""
        tdg = build_tdg(plan, toolset=toolset)
        if not tdg.nodes:
            return GateDecision(True, None, None, 0.0, self.threshold(0), "no tool calls found")

        if self.config.use_plan_mine and hasattr(self.model, "plan_score"):
            plan_score = self.model.plan_score(intent, plan)
            plan_threshold = float(self.config.plan_threshold)
            if plan_score < plan_threshold:
                return GateDecision(
                    False,
                    None,
                    None,
                    plan_score,
                    plan_threshold,
                    "paper MINE plan alignment below threshold",
                )

        intent_vec = self.model.encode_intent(intent)
        last_score = 0.0
        last_threshold = self.threshold(0)
        seen_untrusted = False
        helper = WAMIGateway(self.model, use_action_prior=False)
        trajectory = (
            self.model.cognitive_rollout(intent, tdg)
            if self.config.use_transition_mine and hasattr(self.model, "transition_score")
            else None
        )
        if trajectory is not None:
            iterator = ((item["step"], item["node"], item) for item in trajectory)
        else:
            iterator = ((step, node, {"state": state}) for step, (node, state) in enumerate(self.model.rollout(intent, tdg)))

        for step, node, item in iterator:
            intent_score = self.model.mine_score(intent_vec, item["state"])
            score = intent_score
            reason = "paper MINE trajectory alignment below dynamic threshold"
            if self.config.use_transition_mine and hasattr(self.model, "transition_score") and "previous_state" in item:
                transition_score = self.model.transition_score(
                    intent_vec,
                    item["previous_state"],
                    item["action"],
                    item["observation"],
                    item["state"],
                )
                fusion = min(1.0, max(0.0, self.config.transition_fusion))
                score = (1.0 - fusion) * intent_score + fusion * transition_score
                if transition_score < intent_score:
                    reason = "paper MINE transition alignment below dynamic threshold"
            if self.config.use_auxiliary_heads and hasattr(self.model, "aux_scores") and "previous_state" in item:
                source_logit, drift_logit, sink_auth_logit = self.model.aux_scores(
                    intent_vec,
                    item["previous_state"],
                    item["action"],
                    item["observation"],
                    item["state"],
                )
                aux_score = sink_auth_logit - 0.5 * source_logit - drift_logit
                fusion = min(1.0, max(0.0, self.config.auxiliary_fusion))
                score = (1.0 - fusion) * score + fusion * aux_score
                if aux_score < score:
                    reason = "paper MINE source-aware auxiliary alignment below dynamic threshold"
            if self.config.use_来源memory_memory and hasattr(self.model, "来源memory_scores") and "memory" in item:
                trusted, untrusted, instruction, sensitive = self.model.来源memory_scores(
                    intent_vec,
                    item["action"],
                    item["observation"],
                    item["memory"],
                    item["state"],
                )
                来源memory_score = trusted - 0.5 * untrusted - instruction - 0.5 * sensitive
                fusion = min(1.0, max(0.0, self.config.来源memory_fusion))
                score = (1.0 - fusion) * score + fusion * 来源memory_score
                if 来源memory_score < score:
                    reason = "paper MINE 来源memory memory alignment below dynamic threshold"
            threshold = self.threshold(step)
            threshold += self._risk_margin(helper, node.tool, str(node.params), seen_untrusted)
            last_score, last_threshold = score, threshold

            compact_tool = node.tool.lower().replace("_", "").replace("-", "")
            if "readuntrustedinjection" in compact_tool or "parseinjectedinstruction" in compact_tool:
                seen_untrusted = True

            if score < threshold:
                return GateDecision(
                    False,
                    step,
                    node.tool,
                    score,
                    threshold,
                    reason,
                )
        return GateDecision(True, None, None, last_score, last_threshold, "paper MINE trajectory remained aligned")

    def _risk_margin(self, helper: WAMIGateway, tool: str, params: str, seen_untrusted: bool) -> float:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        tool_key = tool.lower()
        margin = 0.0
        if helper._is_passive_observation(tool_key):
            margin -= self.config.passive_margin
        if helper._requires_explicit_authorization(tool_key):
            margin += self.config.risk_margin
        if seen_untrusted and helper._requires_explicit_authorization(tool_key):
            margin += self.config.risk_margin
        if helper._has_attack_target(params):
            margin += self.config.risk_margin
        return margin


class PaperMultimodalMINEGateway(PaperMINEGateway):
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""

    def inspect_multimodal(self, intent: str, plan: str, image_paths=None, toolset: set[str] | None = None) -> GateDecision:
        """函数说明。
        
        这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
        if not hasattr(self.model, "use_images"):
            return self.inspect(intent, plan, toolset=toolset)
        with self.model.use_images(image_paths):
            return self.inspect(intent, plan, toolset=toolset)
