# Table 1 baseline papers and reproduction status

## GuardReasoner-VL

| Field | Status |
|---|---|
| Paper found | GuardReasoner-VL: Safeguarding VLMs via Reinforced Reasoning |
| Official repo | `external/GuardReasoner-VL` |
| Official method | reasoning-based VLM guard model, SFT + online RL, outputs harmful/unharmful moderation decisions |
| Current reproduction | official repo downloaded; model inference not yet run because it requires downloading a 3B/7B GuardReasoner-VL checkpoint and vLLM/Qwen2.5-VL runtime |
| Strictness | not yet strict Table 1 reproduction |

Why it is not directly Table 1 yet: the official repository evaluates general harmfulness/VL guard benchmarks such as ToxicChat, HarmBench, OpenAIModeration, HarmImageTest, and SPA-VL-Eval. It does not directly provide BIPIA/InjecAgent agent-defense evaluation. To use it for Table 1, we need to convert each BIPIA/InjecAgent sample into GuardReasoner-VL's moderation prompt format and run the official model checkpoint.

## WebAgentGuard

| Field | Status |
|---|---|
| Paper found | WebAgentGuard: Mitigating Agent Vulnerabilities in Web Navigation |
| arXiv | 2604.12284 |
| Official repo | not found |
| Paper method | a parallel guard agent inspects the agent state/action trajectory before execution and blocks unsafe web-agent actions |
| Current reproduction | paper-method sample implemented with a Qwen guard backend |
| Output | `data/webagentguard_paper_method_sample.md` |
| Strictness | method-level attempt, not official reproduction |

The current script `scripts/run_webagentguard_paper_method.py` implements the paper-level idea: a separate guard agent receives the user goal and proposed tool trajectory, then outputs `block` or `allow` with a reason. Since no official code/model was found, this is closer than a hand-written rule proxy but still not official WebAgentGuard.

Small sample result:

| Dataset | IR | FPR | Note |
|---|---:|---:|---|
| BIPIA | 100.0% | 40.0% | High false positives on benign financial-information extraction tasks |
| InjecAgent | 100.0% | 20.0% | Blocks all 5 sampled attacks, one benign false positive |

This matches the paper's qualitative description that WebAgentGuard can be conservative and may hurt autonomy, but sample size is only 10 per dataset.

## BookAgent

| Field | Status |
|---|---|
| PDF provided by user | `6475_BOOKAGENT_Orchestrating_S.pdf` |
| Paper title | BOOKAGENT: Orchestrating Safety-Aware Visual Narratives via Multi-Agent Cognitive Calibration |
| Core method | VAS + ICR + TCC: Value-Aligned Storyboarding, Iterative Cross-modal Refinement, Temporal Cognitive Calibration |
| Official task | safety-aware visual storybook generation |
| Official metrics | Image-Text Consistency, Cross-Frame Character Consistency, Safety |
| Match with WAMI Table 1 metric | weak direct match |
| Current reproduction | no strict IR/FPR reproduction yet |
| Strictness | cannot be directly reproduced as a BIPIA/InjecAgent defense without method adaptation |

After reading the provided PDF, BookAgent is not a prompt-injection defense benchmark method. It is a multi-agent framework for child-safe visual narrative generation. Its safety component is a value/safety auditor inside a storybook generation loop, and its global verifier is Temporal Cognitive Calibration for long-horizon story consistency. Its experiments do not report attack interception rate or false positive rate.

Therefore, strict reproduction of BookAgent's own paper would require generating storybooks and evaluating Image-Text Consistency, Cross-Frame Consistency, and Safety. It would not directly produce the IR/FPR values used in WAMI Table 1.

If BookAgent must be used as a WAMI Table 1 baseline, the only defensible route is a clearly labeled method adaptation:

1. VAS adapted to agent safety: audit the user's goal and proposed trajectory against safety constraints.
2. ICR adapted to trajectory refinement: ask a reviewer-refiner to revise unsafe or inconsistent tool calls.
3. TCC adapted to global trajectory calibration: globally verify the entire action sequence for long-horizon inconsistency or unsafe drift.

This would be a BookAgent-inspired adaptation, not a strict reproduction of the BookAgent paper's original experiments.

## What should go into the formal paper table

| Method | Formal status |
|---|---|
| GuardReasoner-VL | can be attempted after downloading official model checkpoint; not yet strict |
| WebAgentGuard | method-level attempt only unless official code/model appears |
| BookAgent | do not include as reproduced until exact safety paper/code is identified |
| WAMI | local reproduced method |
