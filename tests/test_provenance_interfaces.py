"""验证注释汉化没有改变运行接口和来源记忆层的权重名称。"""

import inspect
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest

import numpy as np

from scripts.run_full_live_wami_runtime import config
from scripts.run_paper_mine_ensemble import make_gateway
from wami.paper_mine_gateway import PaperMINEConfig, PaperMINEGateway
from wami.shadow import PlanSample
from wami.torch_model import TorchWAMIConfig, TorchWAMIModel
from wami.torch_training import train_shadow_torch


class ProvenanceInterfaceTests(unittest.TestCase):
    def test_runtime_and_static_configuration(self):
        """复现曾经的构造报错，两个实际入口都必须能传入来源记忆配置。"""
        runtime = config(-5.85, SimpleNamespace(risk_margin=0.0, passive_margin=0.15))
        self.assertTrue(runtime.use_provenance_memory)
        self.assertEqual(runtime.provenance_fusion, 0.10)
        static = make_gateway(object(), -4.5, 0.35, 0.10, False, 0.0)
        self.assertFalse(static.config.use_provenance_memory)

    def test_checkpoint_keys_and_roundtrip(self):
        """用真实小网络检查权重键和保存加载，防止 strict=False 静默漏加载。"""
        model = TorchWAMIModel(TorchWAMIConfig(dim=16, hidden_dim=32, layers=1, heads=4))
        keys = {key for key in model.net.state_dict() if key.startswith('provenance_head.')}
        self.assertEqual(keys, {f'provenance_head.{layer}.{suffix}' for layer in (0, 1, 4) for suffix in ('weight', 'bias')})
        with model.torch.no_grad():
            for parameter in model.net.provenance_head.parameters():
                parameter.fill_(0.125)
        vector = np.zeros(16, dtype=np.float32)
        expected = model.provenance_scores(vector, vector, vector, vector, vector)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'checkpoint.pt'
            model.save(path)
            loaded = TorchWAMIModel.load(path)
        for key in keys:
            self.assertTrue(model.torch.equal(model.net.state_dict()[key], loaded.net.state_dict()[key]))
        np.testing.assert_allclose(loaded.provenance_scores(vector, vector, vector, vector, vector), expected)

    def test_gateway_calls_provenance_head(self):
        """确认开启来源记忆时确实计算分数，不能因方法改名而静默跳过。"""
        from unittest.mock import patch

        model = TorchWAMIModel(TorchWAMIConfig(dim=16, hidden_dim=32, layers=1, heads=4))
        gateway = PaperMINEGateway(model, PaperMINEConfig(
            base_threshold=-1000000, use_plan_mine=False,
            use_transition_mine=True, use_provenance_memory=True,
        ))
        with patch.object(model, 'provenance_scores', wraps=model.provenance_scores) as scores:
            gateway.inspect('Read the report', 'Action: ReadFile(path="report.txt")')
            scores.assert_called()

    def test_training_uses_same_interface(self):
        """做一次真实小批次训练，验证模型方法改名没有破坏训练调用方。"""
        self.assertIn('provenance_weight', inspect.signature(train_shadow_torch).parameters)
        model = TorchWAMIModel(TorchWAMIConfig(dim=16, hidden_dim=32, layers=1, heads=4))
        samples = [
            PlanSample(intent='Read the report', plan='Action: ReadFile(path="report.txt")', label=0),
            PlanSample(intent='Read the report', plan='Action: SendEmail(to="test@example.invalid", body="report")', label=1),
        ]
        stats = train_shadow_torch(model, samples=samples, epochs=1, batch_size=2, provenance_weight=0.15)
        self.assertEqual(len(stats), 1)
        self.assertTrue(np.isfinite(stats[0].loss))


if __name__ == '__main__':
    unittest.main()
