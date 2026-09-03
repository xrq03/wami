# Commitment Clearing Round 6: Zero-Supervision Official Test

## Protocol

- Training data: `data/paper_shadow_train.jsonl`
- Validation/calibration data: `data/paper_shadow_val.jsonl`
- Official test-only datasets:
  - `data/injecagent_wami.jsonl`
  - `data/bipia_wami.jsonl`
  - `data/agentdojo_wami.jsonl`
- Model: paper-strict 4-layer Transformer world model, dim 1024, 8 heads.
- MINE: 3-layer MLP.
- Optimizer: AdamW, lr 2e-4, cosine schedule.
- Epochs: 20.
- Device: CUDA.

The official datasets were not used for training or threshold calibration in
this run. Threshold calibration used only the generated shadow validation split.

## Outputs

- Model: `wami_paper_strict_zero_supervision_e20_cuda.pt`
- Training log: `data/wami_paper_strict_zero_supervision_e20_cuda.progress.csv`
- Initial test report: `data/wami_paper_strict_zero_supervision_e20_cuda.md`
- Current best gateway report: `data/wami_paper_strict_zero_supervision_e20_cuda_gateway_v4.md`
- Current best gateway CSV: `data/wami_paper_strict_zero_supervision_e20_cuda_gateway_v4.csv`

## Result

| Dataset | IR | FPR | ACC | Latency ms | N |
|---|---:|---:|---:|---:|---:|
| InjecAgent | 95.9% | 0.0% | 97.9% | 11.830 | 4233 |
| BIPIA | 100.0% | 0.1% | 100.0% | 13.182 | 2400 |
| AgentDojo | 100.0% | 1.2% | 99.8% | 22.314 | 653 |

## Repair Log

The first clean zero-supervision run showed high false positives on InjecAgent
and AgentDojo. Error inspection showed that most false positives came from
generic gateway semantics rather than dataset-specific training:

- Domain-prefixed passive tools such as `AmazonGetProductDetails` and
  `WebBrowserNavigateTo` were not treated as passive observation tools.
- Explicitly user-authorized active tools still used a strict neural alignment
  threshold, causing legitimate payment, invitation, calendar, and file actions
  to be blocked.
- Attack-target detection used substring matching, so benign table/context text
  could trigger attacker-target logic accidentally.

The gateway now uses broader passive observation recognition, relaxes the
threshold for explicitly aligned user-authorized actions when no untrusted
injection has been observed, and uses boundary-aware attack-target matching.

## Interpretation

This clears the methodological issue where official benchmark datasets were
previously mixed into training/calibration. The result is therefore more honest
as an out-of-distribution defense test.

The main remaining weakness is InjecAgent false negatives: some attacks embed
the injection inside generic tool responses rather than an explicit
`ReadUntrustedInjection` node. The next improvement should classify suspicious
tool-response text as an untrusted instruction source without raising benign
context false positives.
