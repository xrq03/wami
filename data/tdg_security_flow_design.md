# Enhanced TDG Security/Data-Flow Reproduction

The enhanced TDG implementation is in `wami/tdg.py`.

## What Is Tracked

| Requirement | Implementation |
|---|---|
| Tool call order | `order_edges` connect adjacent topological steps |
| Tool input-output dependency | `data_edges` come from `$0`, `$1`, named variable references |
| External observation source | Node tag `external_observation=True` for read/search/fetch/get/inspect/extract/parse tools or params like `url/image/context/response/observation` |
| Untrusted content propagation | Node tag `untrusted_source=True`; propagated through data/order/memory edges into `tainted=True` |
| Sensitive data flow | Node tag `sensitive_source=True`; propagated through data/order/memory edges into `sensitive=True` |
| Cross-step memory dependency | `memory_edges` connect prior steps to later steps and explicit `$n` memory references |

## Security Node Tags

Each TDG node receives:

- `external_observation`
- `untrusted_source`
- `sensitive_source`
- `tainted`
- `sensitive`
- `sink`
- `memory_reads`
- `memory_writes`

## Edge Kinds

| Edge kind | Meaning |
|---|---|
| `data` | Explicit tool input/output dependency |
| `order` | Tool execution order dependency |
| `memory` | Cross-step working-memory dependency |
| `taint` | Untrusted content propagation |
| `sensitive` | Sensitive information propagation |

## Path Outputs

The analysis returns:

- `untrusted_paths`: paths from untrusted source nodes to sink nodes.
- `sensitive_flows`: paths from sensitive source nodes to sink nodes.

These outputs make the TDG closer to a security data-flow graph rather than a
simple action sequence.
