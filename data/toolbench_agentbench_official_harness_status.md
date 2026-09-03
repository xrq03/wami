# ToolBench / AgentBench Official Harness Status

## Current Status

| Harness | Local Files | Current Reproduction | Status |
|---|---|---|---|
| ToolBench | `external/ToolBench` | Capability-retention proxy and small local examples | Official success-rate harness not completed |
| AgentBench | `external/AgentBench` | Capability-retention proxy via AgentDojo-style benign allow rate | Official success-rate harness not completed |

## Why Strict Table 4 Is Still Open

Strict reproduction requires:

- Official task server/environment setup.
- ToolBench/AgentBench agent execution loop.
- Matching base model.
- Tool execution logs.
- Paper-equivalent scoring scripts.

The current workspace contains repositories/assets, but not a fully configured
running official harness with matching model/runtime conditions.

## Current Proxy Results

The current WAMI benign capability retention proxy is:

| Dataset proxy | Retention |
|---|---:|
| BIPIA as ToolBench-style retention proxy | 99.0% |
| AgentDojo as AgentBench-style retention proxy | 97.7% |

These proxy rows must be reported separately from official Table 4 numbers.
