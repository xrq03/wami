# Reproduced World Model Design

This repository now contains two WAMI world-model implementations. The stronger
paper-style implementation is the PyTorch model in `wami/torch_model.py`.

## Architecture

| Item | Reproduced Setting |
|---|---|
| Backbone | TransformerEncoder cognitive sandbox |
| Layers | 2 by default |
| Hidden size | 512 by default |
| Attention heads | 4 by default |
| Latent dimension | 256 by default |
| Memory module | GRUCell over `[state, observation]` |
| Subgoal module | MLP over `[state, action, memory]` |
| Transition module | MLP over `[context, action, parent_state, memory, subgoal]` |
| Gateway critic | MINE-style MLP over `[intent, state, intent*state, abs(intent-state)]` |

## State Space

Each tool step is represented in a shared latent space:

- `intent`: encoded user/system objective.
- `action`: encoded tool name and parameters.
- `observation`: encoded tool result, image observation, or input/output field.
- `parent_state`: TDG parent state when data-flow dependencies exist.
- `memory`: recurrent working-memory vector.
- `subgoal`: hidden vector predicting the agent's current operational objective.
- `state`: predicted cognitive state after executing the current action.

## Memory And Subgoal

Memory is an implicit vector, not text. It is updated with:

```text
memory_t = GRUCell([state_t, observation_t], memory_{t-1})
```

Subgoal is also an implicit vector:

```text
subgoal_t = MLP([state_t, action_t, memory_t])
```

This is closer to the paper's "working memory and sub-goal evolution" wording
than the earlier lightweight numpy transition.

## Training Loss

The Torch training loop combines:

| Loss | Purpose |
|---|---|
| Logistic MINE loss | Separate clean states from shadow-adversarial states |
| Donsker-Varadhan style MI bound | Encourage higher positive intent-state MI than negative MI |
| InfoNCE world loss | Make clean world states align with their matching intent against batch negatives |
| Margin world loss | Force clean state-intent similarity to exceed shadow state-intent similarity |
| Variance penalty | Stabilize critic scores |

## Sampling

Training samples are benign trajectories. For each benign TDG, `perturb_tdg`
creates a shadow adversarial trajectory through one of several modes:

- Sensitive tool replacement.
- Inserted untrusted instruction.
- Secret leakage action.
- Policy/logic violation answer.
- Attacker exfiltration path.

The clean and shadow trajectories are paired for both MINE training and world
model contrastive training.
