# AgentBench Strict Reproduction Blocker

AgentBench strict Table 4 reproduction is currently blocked locally.

| Check | Result |
|---|---|
| Official repo present | `external/AgentBench` exists |
| Docker runtime | unavailable locally; `docker` command is not recognized |
| Documented entrypoint | docs/configs reference `python -m src.start_task` |
| Local entrypoint file | `external/AgentBench/src/start_task.py` is absent |
| Current usable result | proxy only: `data/table4_capability_proxy.md` |

This means AgentBench official SR should stay blank in final paper-reproduction tables until Docker and a compatible AgentBench harness are available.
