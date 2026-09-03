# Threshold Strategy Paper Check

The WAMI paper does specify the dynamic threshold form.

## Paper Formula

The paper defines the online MINE alignment score:

```text
I_hat_t = T_phi(z_user, s_t)
```

and the time-adaptive threshold:

```text
tau(t) = tau_0 * exp(-lambda * t)
```

The intervention rule is:

```text
trigger intervention if I_hat_t < tau(t)
```

## Current Code

The current implementation matches this form in `wami/gateway.py`:

```python
def threshold(self, step: int) -> float:
    return self.base_threshold * math.exp(-self.decay * step)
```

Mapping:

| Paper | Code |
|---|---|
| `tau_0` | `base_threshold` |
| `lambda` | `decay` |
| `t` | `step` |
| `I_hat_t < tau(t)` | `score < effective_limit` |

## Remaining Difference

The paper gives the functional form, but the extracted PDF text does not expose
the exact numeric values of `tau_0` and `lambda` used in the experiments.
Therefore:

- Threshold strategy formula: reproduced.
- Exact paper hyperparameters: still require calibration or author code.

## Correction To Earlier Summary

Earlier summaries saying "original threshold strategy is unknown" were too
broad. The correct statement is:

```text
The dynamic threshold formula is specified and reproduced; the exact tau_0,
lambda, and calibration protocol used by the paper are not fully recoverable
from the available PDF text.
```
