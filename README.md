# VeriAlign — Verification Support Proxy for LLM Outputs

> **Domain:** Alignment  
> **Source Paper:** arXiv:2605.04454 (May 2026)  
> **Stack:** Python, FastAPI, SQLite, Streamlit, Docker

A **reverse proxy** that sits between any application and any LLM API. It intercepts every request, forwards it to the model, then augments the response with verification information before returning it to the user.

The paper **arXiv:2605.04454** audited 11 alignment benchmarks and found verification support absent from every one. VeriAlign fills that gap at the **infrastructure level**.

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Client    │────▶│    VeriAlign     │────▶│  LLM Provider   │
│  (App/API)  │     │   (FastAPI)      │     │  (OpenAI, etc.) │
└─────────────┘     └────────┬─────────┘     └─────────────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ Verification     │
                    │ Engine           │
                    ├──────────────────┤
                    │ • Claim Extract  │
                    │ • Source Ground  │
                    │ • Contradictions │
                    │ • Confidence     │
                    │ • Checklist      │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  SQLite Storage  │
                    │  (Traces)        │
                    └──────────────────┘
```

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn verialign.proxy.main:app --reload
```

Demo request without an upstream provider:

```bash
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H "content-type: application/json" \
  -d '{
    "model": "demo",
    "messages": [{"role": "user", "content": "Summarize the project."}],
    "metadata": {
      "context": [
        {"id": "doc-1", "text": "VeriAlign is a verification support proxy for LLM outputs."}
      ]
    }
  }'
```

Dashboard (in another terminal):

```bash
streamlit run verialign/dashboard/app.py
```

## Verification Response Shape

Every response includes a `verification` object:

```json
{
  "verification": {
    "claims": [
      {
        "claim_id": "claim-0",
        "text": "VeriAlign is a verification support proxy for LLM outputs.",
        "status": "supported",
        "confidence": 0.85,
        "sources": [{"source_id": "doc-1", "score": 0.8, "excerpt": "..."}]
      }
    ],
    "contradictions": [
      {"claim_a": "...", "claim_b": "...", "type": "negation", "confidence": 0.8}
    ],
    "checklist": [
      {"description": "...", "category": "security", "priority": "high"}
    ],
    "summary": {
      "total_claims": 1,
      "supported": 1,
      "unsupported": 0,
      "unclear": 0,
      "contradictions_found": 0,
      "checklist_items": 1
    }
  }
}
```

## Features

| Feature | Description |
|---------|-------------|
| **Provider routing** | OpenAI, Anthropic, local Ollama, any OpenAI-compatible endpoint |
| **Request validation** | Full OpenAI field support: temperature, max_tokens, tools, tool_choice, response_format |
| **Claim extraction** | Regex-based factual claim extraction with meta-sentence filtering |
| **Source grounding** | Keyword overlap matching against provided RAG context |
| **Contradiction detection** | Negation, antonym, and numeric conflict detection |
| **Confidence scoring** | Logprob-based (when available) + heuristic fallback |
| **Checklist generation** | Action-oriented verification checklist by category |
| **Rate limiting** | Token bucket algorithm per client IP |
| **Provider fallback** | Automatic retry on 429/5xx with alternate providers |
| **Proxy auth** | Optional API-key authentication |
| **Trace persistence** | SQLite storage with sensitive data redaction |
| **Metrics** | Per-model, per-task, drift over time |
| **Dashboard** | Streamlit UI with 6 pages for trace inspection |
| **Seed data** | Generate sample traces for demo |
| **Benchmark** | Latency benchmarking with percentile stats |

## Configuration

All via environment variables (see `.env.example`):

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VERIALIGN_UPSTREAM_BASE_URL` | No | — | OpenAI-compatible API endpoint |
| `VERIALIGN_UPSTREAM_API_KEY` | No | — | API key for upstream provider |
| `VERIALIGN_ANTHROPIC_API_KEY` | No | — | Anthropic API key |
| `VERIALIGN_LOCAL_BASE_URL` | No | — | Local Ollama endpoint |
| `VERIALIGN_UPSTREAM_TIMEOUT_SECONDS` | No | 60 | Request timeout |
| `VERIALIGN_DB_PATH` | No | ./verialign.sqlite3 | SQLite database path |
| `VERIALIGN_PROXY_API_KEY` | No | — | VeriAlign's own API key |
| `VERIALIGN_REQUIRE_PROXY_AUTH` | No | false | Enable proxy authentication |
| `VERIALIGN_RATE_LIMIT_RPM` | No | 60 | Requests per minute per client |
| `VERIALIGN_RATE_LIMIT_TPM` | No | 100000 | Tokens per minute per client |
| `VERIALIGN_REDACT_TRACES` | No | true | Redact secrets from stored traces |

## Project Structure

```
verialign/
├── README.md
├── pyproject.toml
├── requirements.txt
├── .env.example
├── verialign/
│   ├── proxy/
│   │   ├── main.py                       # FastAPI entry point
│   │   ├── config.py                     # Settings from env vars
│   │   ├── middleware/
│   │   │   ├── rate_limiter.py           # Token bucket rate limiter
│   │   │   ├── request_handler.py        # Validate incoming requests
│   │   │   └── response_handler.py       # Augment responses with verification
│   │   └── routing/
│   │       ├── provider_router.py        # Route to OpenAI/Anthropic/local
│   │       └── fallback.py               # Provider fallback on failure
│   ├── verification/
│   │   ├── engine.py                     # Orchestrates verification pipeline
│   │   ├── claim_extractor.py            # Extract factual claims
│   │   ├── source_grounder.py            # Match claims to RAG context
│   │   ├── contradiction_detector.py     # Cross-check internal contradictions
│   │   ├── confidence_scorer.py          # Logprob + heuristic scoring
│   │   ├── checklist_generator.py        # Actionable verification checklists
│   │   └── models.py                     # Dataclasses for verification data
│   ├── storage/
│   │   ├── models.py                     # SQLAlchemy ORM models
│   │   ├── trace_store.py                # SQLite persistence
│   │   └── metrics_store.py              # Aggregated metrics queries
│   └── dashboard/
│       ├── app.py                        # Streamlit entry point
│       ├── pages/                        # Overview, Per Model, Per Task, Drift, Contradictions
│       └── components/                   # Charts, Filters
├── tests/
│   ├── test_api.py
│   ├── test_claim_extractor.py
│   ├── test_source_grounder.py
│   ├── test_contradiction_detector.py
│   ├── test_confidence_scorer.py
│   ├── test_checklist_generator.py
│   ├── test_provider_router.py
│   ├── test_fallback.py
│   ├── test_rate_limiter.py
│   ├── test_request_handler.py
│   ├── test_response_handler.py
│   ├── test_trace_store.py
│   └── test_integration.py
├── scripts/
│   ├── seed_data.py                      # Generate sample traces
│   └── benchmark.py                      # Latency benchmarking
├── deploy/
│   ├── Dockerfile
│   ├── Dockerfile.dashboard
│   ├── docker-compose.yml
│   └── .env.example
├── docs/
│   ├── architecture.md
│   ├── deployment.md
│   ├── paper-summary.md
│   └── interview-pitch.md
└── .github/workflows/
    ├── test.yml
    └── deploy.yml
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/v1/chat/completions` | Chat completion with verification |
| GET | `/traces?limit=25` | List recent traces |

## Deployment

```bash
# Docker Compose (full stack)
docker compose -f deploy/docker-compose.yml up -d

# Fly.io
flyctl launch
flyctl deploy

# Railway
railway up
```

See `docs/deployment.md` for detailed instructions.

## API Notes

- `metadata.context` may be a list of strings or objects with `id` and `text`
- If no upstream provider is configured, VeriAlign uses demo mode
- Streaming (`stream=true`) is rejected with HTTP 400

## Tests

```bash
# Run all tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=verialign
```

## Acknowledgements

- **arXiv:2605.04454** — The paper that identified the verification gap
- **Anthropic Engineering Blog** — Proxy/containment architecture patterns
- **Bifrost AI Gateway** — Reference for production AI gateway architecture