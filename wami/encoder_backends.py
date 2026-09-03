from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EncoderBackendSpec:
    name: str
    status: str
    notes: str


AVAILABLE_ENCODER_BACKENDS = [
    EncoderBackendSpec("hashing", "implemented", "Default dependency-free encoder."),
    EncoderBackendSpec("sentence-transformers", "stub", "Use bge/e5/gte local embeddings when installed."),
    EncoderBackendSpec("qwen-embedding-api", "stub", "Use external embedding API when credentials are configured."),
]


def list_encoder_backends() -> list[EncoderBackendSpec]:
    return AVAILABLE_ENCODER_BACKENDS
