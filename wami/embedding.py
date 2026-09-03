from __future__ import annotations

import hashlib
import re
import numpy as np

TOKEN_RE = re.compile(r"[A-Za-z0-9_$.-]+")


class HashingTextEncoder:
    """Small deterministic encoder used when no external LMM encoder is available."""

    def __init__(self, dim: int = 128, seed: int = 17):
        self.dim = dim
        self.seed = seed

    def encode(self, text: str) -> np.ndarray:
        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = TOKEN_RE.findall(text.lower())
        for token in tokens:
            for feature in (token, *self._ngrams(token)):
                digest = hashlib.blake2b(
                    f"{self.seed}:{feature}".encode("utf-8"), digest_size=8
                ).digest()
                value = int.from_bytes(digest, "little")
                index = value % self.dim
                sign = 1.0 if (value >> 63) == 0 else -1.0
                vec[index] += sign
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    @staticmethod
    def _ngrams(token: str):
        padded = f"<{token}>"
        for n in (3, 4):
            for i in range(max(0, len(padded) - n + 1)):
                yield padded[i : i + n]

