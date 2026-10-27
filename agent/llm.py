"""Loads a local Hugging Face chat model and generates replies (with tool definitions)."""

import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Qwen2.5-3B fits a Colab T4. On a small laptop GPU (4 GB) use Qwen/Qwen2.5-1.5B-Instruct.
DEFAULT_MODEL = "Qwen/Qwen2.5-3B-Instruct"


class LocalLLM:
    def __init__(self, model_id: str | None = None):
        self.model_id = model_id or os.getenv("MODEL_ID", DEFAULT_MODEL)
        print(f"Loading {self.model_id} ... (first run downloads the weights)")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id, torch_dtype="auto", device_map="auto"
        )

    def generate(self, messages: list[dict], tools: list, max_new_tokens: int = 512) -> str:
        """Run the model on the chat history; `tools` are Python functions with docstrings."""
        inputs = self.tokenizer.apply_chat_template(
            messages, tools=tools, add_generation_prompt=True,
            return_dict=True, return_tensors="pt",
        ).to(self.model.device)
        with torch.no_grad():
            out = self.model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
        new_tokens = out[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(new_tokens, skip_special_tokens=True)
