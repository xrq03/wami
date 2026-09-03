# Full Live WAMI Runtime Summary

This is the complete runtime form of WAMI:

1. The agent emits one action at a time.
2. The runtime creates a pending tool event.
3. WAMI builds an incremental TDG from the runtime trace.
4. Passive observation actions are allowed to execute and become TDG evidence.
5. Before side-effect tools execute, WAMI decides whether to block.

The implementation is in `scripts/run_full_live_wami_runtime.py`.

## Sink-Only Runtime Results

| Dataset | Setting | IR | FPR | ACC | Latency ms | N | Attack | Benign | Avg Steps | Avg TDG Nodes | Avg TDG Edges | Source |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| InjecAgent | v2/v3 low-FPR dual ensemble | 100.0% | 0.0% | 100.0% | 420.011 | 40 | 20 | 20 | 3.00 | 3.00 | 2.00 | `data/full_live_wami_runtime_injecagent_20x20.md` |
| BIPIA | v2/v3 high-recall dual ensemble | 100.0% | 0.0% | 100.0% | 122.655 | 40 | 20 | 20 | 2.00 | 2.00 | 1.00 | `data/full_live_wami_runtime_bipia_20x20_highrecall.md` |
| AgentDojo | v2/v3 low-FPR dual ensemble | 95.0% | 0.0% | 97.5% | 368.472 | 40 | 20 | 20 | 2.67 | 2.67 | 1.68 | `data/full_live_wami_runtime_agentdojo_20x20.md` |

## Why This Is Different From Replay

Replay evaluation passes the whole dataset `plan` to WAMI at once. This runtime version does not. It grows the TDG step by step:

```text
agent proposes action_0
  -> pending runtime event
  -> WAMI TDG check
  -> execute tool if allowed
  -> append observation to trace
agent proposes action_1
  -> TDG now includes action_0 and observation_0
  -> WAMI checks the next pending action
```

For example, on InjecAgent, WAMI allows:

```text
AmazonGetProductDetails
ReadToolResponse
```

Then blocks before:

```text
GmailSendEmail
```

This shows the intended architecture: WAMI does not merely classify the user prompt; it gates the agent's next action using the accumulated action/observation TDG.

## Caveat

This is a full runtime loop, but the planner is still dataset-stepwise/scripted rather than a live Qwen/GPT planner. It is therefore stronger than plain replay and cheaper than API live-agent testing, but not yet the final "LLM planner generates every action" experiment.
