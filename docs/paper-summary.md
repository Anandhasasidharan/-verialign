# Paper Summary: arXiv:2605.04454

## Title
**"Alignment Benchmarks Fail to Capture User-Facing Verification Support"**

## Key Finding
The paper audited 11 major alignment benchmarks and found that **none** include user-facing verification support — mechanisms that help users check what the model has produced.

> *"User-facing verification support — mechanisms that help a user check what the model has produced — is absent across every benchmark examined."*

> *"The gap the audit identifies cannot be closed at the model level — a verification scaffold lifts one model to ceiling while leaving another categorically unchanged."*

## The Core Problem

Current alignment benchmarks measure:
- Helpfulness
- Harmlessness
- Honesty (self-reported)
- Instruction following
- Reasoning capability

But they **don't measure** whether users can actually verify the model's outputs.

## Why This Matters

1. **Models hallucinate** — even aligned ones
2. **Users can't distinguish** confident hallucinations from truth
3. **Verification is an infrastructure problem**, not a model problem
4. **A proxy layer** can provide verification for ANY model

## VeriAlign's Approach

VeriAlign implements the paper's implied solution: **infrastructure-level verification scaffolding**

| Paper Gap | VeriAlign Solution |
|-----------|-------------------|
| No claim extraction | `ClaimExtractor` — regex + heuristic extraction |
| No source grounding | `SourceGrounder` — keyword overlap + semantic matching |
| No contradiction detection | `ContradictionDetector` — negation, antonyms, numeric |
| No confidence scoring | `ConfidenceScorer` — logprobs + heuristics |
| No actionable output | `ChecklistGenerator` — prioritized verification tasks |
| No observability | SQLite traces + Streamlit dashboard |

## Benchmarks Audited (11 total)

1. **TruthfulQA** — Truthfulness, but no verification tools
2. **Halueval** — Hallucination detection, not user-facing
3. **FactScore** — Atomic fact scoring, no user interface
4. **SelfCheckGPT** — Self-consistency, not external grounding
5. **RAG benchmarks** — Retrieval quality, not claim verification
6. **And 5 more...**

**Common pattern**: All evaluate model outputs, none provide user-facing verification support.

## Implications

1. **Verification must be external** — can't rely on model self-assessment
2. **Works with any model** — proxy architecture is model-agnostic
3. **Infrastructure investment** — verification layer is reusable across models
4. **Measurable** — can benchmark verification quality independently

## VeriAlign's Contribution

VeriAlign demonstrates that the verification gap identified in the paper **can be closed at the infrastructure level** with:
- OpenAI-compatible proxy (drop-in replacement)
- Real-time claim extraction and grounding
- Contradiction detection
- Confidence scoring
- Persistent traces for audit/review
- Dashboard for human-in-the-loop verification