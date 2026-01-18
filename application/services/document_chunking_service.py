from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np

from application.ports.embedding_model import EmbeddingModel


def _split_sentences(text: str) -> list[str]:
    # Simple rule-based splitter (good enough to start; can be swapped later).
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if s and s.strip()]


def _token_count(text: str) -> int:
    return len(text.split())


@dataclass
class DocumentChunkingService:
    embedding_model: EmbeddingModel

    def semantic_sliding_window(
        self,
        *,
        text: str,
        similarity_threshold: float = 0.75,
        max_tokens: int = 200,
        overlap: int = 50,
    ) -> list[str]:
        """
        Semantic segmentation based on consecutive sentence similarity, then sliding-window chunking
        per segment (adapted from the notebook implementation).
        """
        sentences = _split_sentences(text)
        if not sentences:
            return []
        if len(sentences) == 1:
            return [sentences[0]]

        # For multilingual-e5 style prompting, prefix with "chunk: "
        sent_emb = self.embedding_model.encode([f"chunk: {s}" for s in sentences])
        # embeddings are normalized in the adapter; cosine(sim) == dot
        sims = np.sum(sent_emb[1:] * sent_emb[:-1], axis=1)

        segments: list[list[str]] = []
        current: list[str] = [sentences[0]]

        for i in range(1, len(sentences)):
            sim = float(sims[i - 1])
            if sim < similarity_threshold:
                segments.append(current)
                current = [sentences[i]]
            else:
                current.append(sentences[i])
        segments.append(current)

        # Sliding-window chunking inside each segment
        chunks: list[str] = []
        for seg in segments:
            window: list[str] = []
            token_count = 0

            for sent in seg:
                sent_tokens = _token_count(sent)

                if window and token_count + sent_tokens > max_tokens:
                    chunks.append(" ".join(window).strip())

                    # overlap: keep last sentences until overlap token budget
                    overlap_tokens = 0
                    new_window: list[str] = []
                    for s in reversed(window):
                        overlap_tokens += _token_count(s)
                        new_window.insert(0, s)
                        if overlap_tokens >= overlap:
                            break

                    window = new_window
                    token_count = sum(_token_count(s) for s in window)

                window.append(sent)
                token_count += sent_tokens

            if window:
                chunks.append(" ".join(window).strip())

        return [c for c in chunks if c]


