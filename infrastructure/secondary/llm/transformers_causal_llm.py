from __future__ import annotations

import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from application.ports.llm import LLM


class TransformersCausalLLM(LLM):
    def __init__(self, model_name: str, device: str = "cpu"):
        self._model_name = model_name
        self._device = device
        self._tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self._model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True)
        self._model.to(device)
        self._model.eval()

    def name(self) -> str:
        return self._model_name

    def generate(
        self,
        *,
        prompt: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float,
    ) -> tuple[str, int, int]:
        inputs = self._tokenizer(prompt, return_tensors="pt")
        input_ids = inputs["input_ids"].to(self._device)
        prompt_tokens = int(input_ids.shape[1])

        with torch.no_grad():
            output = self._model.generate(
                input_ids=input_ids,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                eos_token_id=self._tokenizer.eos_token_id,
                pad_token_id=self._tokenizer.eos_token_id,
            )

        generated = output[0][prompt_tokens:]
        completion_tokens = int(generated.shape[0])
        text = self._tokenizer.decode(generated, skip_special_tokens=True)
        return text.strip(), prompt_tokens, completion_tokens


