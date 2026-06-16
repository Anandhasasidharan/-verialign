# VeriAlign Architecture

## Overview

VeriAlign is a reverse proxy that sits between applications and LLM providers. It intercepts requests, forwards them to the configured LLM provider, then augments the response with verification metadata before returning it to the client.

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
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │  SQLite Storage  │
                    │  (Traces)        │
                    └──────────────────┘
```

## Components

### Proxy Layer (`verialign/proxy/`)

| Component | Responsibility |
|-----------|----------------|
| `main.py` | FastAPI application entry point, routes, middleware wiring |
| `config.py` | Pydantic settings management from environment variables |
| `routing/provider_router.py` | Routes requests to OpenAI, Anthropic, or local providers |
| `routing/fallback.py` | Automatic fallback on provider failures (429, 5xx) |
| `middleware/request_handler.py` | Validates and normalizes incoming OpenAI-compatible requests |
| `middleware/response_handler.py` | Augments responses with verification data |
| `middleware/rate_limiter.py` | Token bucket rate limiting per client IP |

### Verification Engine (`verialign/verification/`)

| Component | Responsibility |
|-----------|----------------|
| `engine.py` | Orchestrates the verification pipeline |
| `claim_extractor.py` | Extracts factual claims from response text using regex patterns |
| `source_grounder.py` | Matches claims to provided RAG context using keyword overlap |
| `contradiction_detector.py` | Detects internal contradictions within a response |
| `confidence_scorer.py` | Scores claim confidence using logprobs (when available) or heuristics |
| `checklist_generator.py` | Generates actionable verification checklists |
| `models.py` | Dataclasses for verification results |

### Storage (`verialign/storage/`)

| Component | Responsibility |
|-----------|----------------|
| `trace_store.py` | SQLite persistence for requests, responses, and verification results |
| `models.py` | SQLAlchemy models for structured storage |
| `metrics_store.py` | Aggregated metrics queries (per model, per task, drift) |

### Dashboard (`verialign/dashboard/`)

Streamlit-based web UI for trace inspection and verification analytics.

Pages:
- **Overview**: System health, request volume, claim status distribution
- **Per Model**: Verification metrics broken down by model
- **Per Task**: Metrics by inferred task category
- **Drift**: Verification score trends over time
- **Contradictions**: Recent contradiction detections
- **Trace Detail**: Full request/response/verification for a single trace

## Data Flow

```
1. Client sends POST /v1/chat/completions
         │
         ▼
2. RequestHandler validates & normalizes request
         │
         ▼
3. RateLimiter checks client limits
         │
         ▼
4. ProviderRouter selects provider (OpenAI/Anthropic/Local)
         │
         ▼
5. ProviderFallback attempts request with retries
         │
         ▼
6. VerificationEngine processes response:
    a) ClaimExtractor extracts factual claims
    b) SourceGrounder matches claims to context
    c) ContradictionDetector checks for conflicts
    d) ConfidenceScorer assigns confidence scores
    e) ChecklistGenerator creates action items
         │
         ▼
7. ResponseHandler augments response with verification object
         │
         ▼
8. TraceStore persists everything to SQLite
         │
         ▼
9. Response returned to client with verification metadata
```

## Verification Pipeline Details

### Claim Extraction
- Splits response into sentences
- Filters meta-sentences (echoes, "as an AI", etc.)
- Identifies factual claims using verb cue patterns

### Source Grounding
- Tokenizes claim and context (removes stopwords)
- Computes keyword overlap score
- Classifies as: `supported` (≥0.55), `unsupported` (≤0.30), `unclear` (between)

### Contradiction Detection
- Negation patterns: "X is Y" vs "X is not Y"
- Antonym pairs: increase/decrease, enable/disable
- Numeric conflicts: same subject, different numbers

### Confidence Scoring
- **With logprobs**: Combines average token logprob with source overlap
- **Heuristic fallback**: Base 0.5 + source overlap + length factor - hedging penalty + specificity bonus

## Configuration

All configuration via environment variables (see `.env.example`):

| Variable | Description |
|----------|-------------|
| `VERIALIGN_UPSTREAM_BASE_URL` | OpenAI-compatible API base URL |
| `VERIALIGN_UPSTREAM_API_KEY` | API key for upstream provider |
| `VERIALIGN_ANTHROPIC_API_KEY` | Anthropic API key (optional) |
| `VERIALIGN_LOCAL_BASE_URL` | Local Ollama endpoint (optional) |
| `VERIALIGN_PROXY_API_KEY` | API key for VeriAlign itself |
| `VERIALIGN_REQUIRE_PROXY_AUTH` | Enable proxy authentication |
| `VERIALIGN_RATE_LIMIT_RPM` | Requests per minute per client |
| `VERIALIGN_RATE_LIMIT_TPM` | Tokens per minute per client |
| `VERIALIGN_REDACT_TRACES` | Redact secrets from stored traces |
| `VERIALIGN_DB_PATH` | SQLite database path |

## Deployment

See `docs/deployment.md` for Docker, Fly.io, Railway, and VPS deployment instructions.