# DistilGPT2 — Downloaded Model

**Model:** `distilgpt2` (Distilled GPT-2)
**Source:** Hugging Face Hub (`distilgpt2`)
**Size:** ~340 MB
**Cached at:** `~/.cache/huggingface/hub/models--distilgpt2/`
**Downloaded:** June 6, 2026

## What is DistilGPT2?

DistilGPT2 is a distilled version of GPT-2, reduced from 12 layers (124M params) to 6 layers (82M params) while retaining ~95% of the original performance. It's a causal language model for text generation.

## Purpose

Used for testing the verification pipeline and LLM-as-judge features in a local, offline-capable setup — avoids making real API calls during development and CI.

## Usage

The model can be loaded with Hugging Face `transformers`:

```python
from transformers import pipeline

generator = pipeline("text-generation", model="distilgpt2")
output = generator("VeriAlign is a", max_length=50)
```

## Notes

- This is the only model cached locally.
- `sentence-transformers` / `all-MiniLM-L6-v2` is NOT installed — semantic source grounding degrades gracefully to TF-IDF fallback.
- The model was pulled from the Hugging Face Hub automatically on first use.
