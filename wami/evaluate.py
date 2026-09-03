"""WAMI 实验指标计算模块。

本文件负责计算攻击拦截率、正常误拦率、准确率、延迟等指标。对于本地智能体流程，还需要区分样本级拦截率和动作级 WAMI 拦截率，因为智能体未生成危险动作时不应算作 WAMI 漏拦。"""

from __future__ import annotations

from dataclasses import dataclass

from .gateway import WAMIGateway
from .shadow import PlanSample


@dataclass
class Metrics:
    """类说明。
    
    这个类属于最终认可实验代码的一部分，用于保存配置、样本记录、模型结构、检查结果或数据集级统计。保留为类结构是为了让实验输入、输出和中间证据更清晰，方便导出表格和逐条审计。"""
    interception_rate: float
    false_positive_rate: float
    accuracy: float
    total: int


def evaluate_gateway(gateway: WAMIGateway, samples: list[PlanSample]) -> Metrics:
    """函数说明。
    
    这个函数属于最终认可实验流程的一部分。它负责读取数据、构造输入、执行检测、调用模型或汇总指标中的一个环节。函数输出会继续传给后续评估、表格生成或 Excel 审计流程。"""
    tp = fp = tn = fn = 0
    for sample in samples:
        decision = gateway.inspect(sample.intent, sample.plan)
        predicted_attack = not decision.allowed
        actual_attack = sample.label == 1
        if predicted_attack and actual_attack:
            tp += 1
        elif predicted_attack and not actual_attack:
            fp += 1
        elif not predicted_attack and actual_attack:
            fn += 1
        else:
            tn += 1
    total = max(1, len(samples))
    return Metrics(
        interception_rate=tp / max(1, tp + fn),
        false_positive_rate=fp / max(1, fp + tn),
        accuracy=(tp + tn) / total,
        total=total,
    )

