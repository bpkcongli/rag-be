from __future__ import annotations

from abc import ABC, abstractmethod


class LLM(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def generate(self, *, prompt: str, max_new_tokens: int, temperature: float, top_p: float) -> tuple[str, int, int]:
        """
        Returns (answer_text, prompt_tokens, completion_tokens)
        Token counts can be approximate depending on implementation.
        """
        raise NotImplementedError


