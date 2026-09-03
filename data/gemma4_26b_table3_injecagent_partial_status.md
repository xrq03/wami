# Gemma4 26B Table 3 Partial Status

Command attempted:

```powershell
$env:OLLAMA_MODELS='D:\OllamaModels'; .\.venv\Scripts\python.exe scripts\run_qwen_full_live_wami_runtime.py --provider ollama --model gemma4:26b --dataset InjecAgent --attack-limit 10 --benign-limit 10 --max-steps 4 --planner-mode max-directive-parser --use-runtime-flow-check --planner-retries 2 --bootstrap-first-observation --output-md data\gemma4_26b_table3_injecagent_10x10.md --output-csv data\gemma4_26b_table3_injecagent_10x10.csv
```

The run timed out after 30 minutes before the script could write its final CSV/Markdown outputs.

Observed partial progress from terminal output:

| Dataset | Backbone | Completed | Attack completed | Benign completed | Blocked | Planner risky actions | Latency pattern |
|---|---|---:|---:|---:|---:|---:|---|
| InjecAgent | gemma4:26b | 18 / 20 | 10 / 10 | 8 / 10 | 0 | 0 | roughly 42-140 seconds/sample |

Interpretation:

- `gemma4:26b` is installed and callable, but it is too slow on the current 8GB GPU setup because Ollama runs it as a CPU/GPU split model.
- In the observed 18 samples, the planner usually returned `finished=True` after 0-1 steps and did not emit dangerous side-effect actions.
- Because no dangerous actions were emitted, WAMI had no meaningful action to block. This makes the model unsuitable as a strong Table 3 backbone under the current prompt/runtime setting.
- This should not replace the Mistral-v0.3 row. Mistral is much more practical and produced usable agent actions.
