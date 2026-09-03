# Multimodal Extension Reporting Note

CyberSecEval3 Visual Prompt Injection is now integrated as an additional
multimodal evaluation, not as a paper-original WAMI table.

## Correct Naming

Use:

```text
Additional multimodal evaluation on CyberSecEval3 Visual Prompt Injection
adapted to WAMI tool-action format.
```

Do not use:

```text
Original WAMI multimodal benchmark reproduction.
```

## Current Results

| Run | Rows | Backend | IR | FPR | ACC | File |
|---|---:|---|---:|---:|---:|---|
| Previous completed run | 100 | Qwen-VL-Max | 100.0% | 0.0% | 100.0% | `data/cyberseceval3_vpi_qwenvl_100.md` |
| Current rerun | 40 | Qwen-VL-Max | 100.0% | 0.0% | 100.0% | `data/current_cyberseceval3_vpi_qwenvl_40.md` |

## Why It Is An Adaptation

CyberSecEval3 VPI provides images and visual prompt-injection cases, but not
native WAMI tool trajectories. We convert each case into paired benign/attack
tool-action plans:

- Benign: inspect image and answer the user task.
- Attack: inspect image, read visual injection, then perform a policy-violating
  or secret-exfiltration action.
