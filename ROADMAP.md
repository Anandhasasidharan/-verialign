# VeriAlign Roadmap

## Current MVP

VeriAlign is now a working OpenAI-compatible verification proxy.

Implemented:

- FastAPI proxy endpoint at `POST /v1/chat/completions`
- Local demo mode when no upstream LLM provider is configured
- Upstream OpenAI-compatible provider forwarding
- Claim extraction from assistant responses
- Source grounding against `metadata.context`
- SQLite trace persistence
- Trace inspection endpoint at `GET /traces`
- Basic test suite

The MVP proves the core idea: an application can route LLM calls through VeriAlign and receive the original model response plus a `verification` object.

## Phase 1: Provider Readiness

Goal: make VeriAlign reliable with real OpenAI-compatible providers.

Tasks:

- Validate common OpenAI request fields: `temperature`, `max_tokens`, `top_p`, `tools`, `tool_choice`
- Reject unsupported `stream=true` requests with a clear error
- Preserve provider error shape where possible
- Add request timeout tests
- Add upstream provider integration examples
- Add `.env.example`

Success criteria:

- Existing OpenAI-compatible clients can switch to VeriAlign by changing only `base_url`
- Failed upstream calls return useful errors
- Demo mode and real-provider mode are both documented

## Phase 2: Better Verification Quality

Goal: reduce noisy verification results and improve source matching.

Tasks:

- Improve claim filtering for conversational, instructional, and subjective sentences
- Add claim IDs and sentence offsets
- Add contradiction detection for direct conflicts inside one response
- Add semantic source matching with embeddings
- Separate statuses into `supported`, `unsupported`, `partially_supported`, and `unclear`
- Add confidence reasons, not only numeric scores

Success criteria:

- Verification output is useful enough for a human reviewer to act on
- Unsupported claims are meaningfully different from weak-but-related matches
- Tests cover common hallucination and RAG-grounding cases

## Phase 3: Trace Review UI

Goal: make logged verification results easy to inspect.

Tasks:

- Build a small Streamlit dashboard
- Show recent traces with model, timestamp, and verification summary
- Add filters for model, status, and date range
- Add a detail view for request, response, claims, and sources
- Highlight unsupported and unclear claims
- Add export to JSON or CSV

Success criteria:

- A reviewer can find risky responses without reading raw SQLite
- Demo data can show the product value in under one minute

## Phase 4: Production Hardening

Goal: make the proxy safe to run as internal infrastructure.

Tasks:

- Add API-key authentication for the proxy itself
- Add request size limits
- Add sensitive-data redaction for stored traces
- Add structured logging
- Add rate limiting
- Add Dockerfile and docker-compose setup
- Add GitHub Actions test workflow
- Add deployment docs for Railway, Fly.io, or a VPS

Success criteria:

- VeriAlign can run behind an internal service boundary
- Logs and traces avoid storing secrets by default
- The full stack can be launched with one documented command

## Phase 5: Evaluation And Benchmarking

Goal: prove whether VeriAlign improves review workflows.

Tasks:

- Create benchmark datasets with supported, unsupported, and contradictory claims
- Measure verification precision and recall
- Measure added latency per request
- Track SQLite growth and query performance
- Compare keyword grounding vs embedding grounding
- Write a short evaluation report

Success criteria:

- The project has measurable quality and latency numbers
- Tradeoffs are documented honestly
- The README can cite concrete benchmark results

## Suggested Next Task

Implement Phase 1 streaming handling:

- Detect `stream=true`
- Return HTTP `400` with a clear message that streaming is not supported yet
- Add a test for that behavior

This avoids silent incompatibility with real OpenAI clients and makes the proxy safer to test in existing apps.

