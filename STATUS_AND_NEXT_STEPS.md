# VeriAlign Status And Next Steps

## What Has Been Done

VeriAlign has been built from the original project idea into a working MVP.

### Core Proxy

- Created a Python/FastAPI project structure.
- Added an OpenAI-compatible endpoint:
  - `POST /v1/chat/completions`
- Added a health endpoint:
  - `GET /health`
- Added upstream provider forwarding for OpenAI-compatible APIs.
- Added local demo mode when provider credentials are not configured.

### Verification Engine

- Added factual claim extraction from assistant responses.
- Added source grounding against request-provided RAG context.
- Added verification statuses:
  - `supported`
  - `unsupported`
  - `unclear`
- Added claim confidence scores based on source overlap.
- Added filtering for noisy meta sentences like request echoes.

### Trace Storage

- Added SQLite trace persistence.
- Stored request payloads, response payloads, and verification results.
- Added a trace inspection endpoint:
  - `GET /traces?limit=10`

### Provider Configuration

- Added `.env.example`.
- Added `.env` loading through `pydantic-settings`.
- Documented provider env vars:
  - `VERIALIGN_UPSTREAM_BASE_URL`
  - `VERIALIGN_UPSTREAM_API_KEY`
  - `VERIALIGN_UPSTREAM_TIMEOUT_SECONDS`
  - `VERIALIGN_DB_PATH`
- Documented demo mode behavior when provider env vars are absent.

### API Safety

- Added explicit handling for unsupported streaming requests.
- Requests with `stream=true` now return HTTP `400` with a clear error message.

### Documentation

- Updated `README.md` with:
  - setup instructions
  - demo request
  - real-provider setup
  - trace inspection
  - API notes
- Added `ROADMAP.md` with future phases.

### Testing

- Added tests for:
  - health endpoint
  - chat completion verification
  - trace logging
  - claim extraction
  - source grounding
  - `stream=true` rejection
  - demo mode without provider env vars

Current test result:

```bash
.venv/bin/python -m pytest -q
# 9 passed
```

## Current Project State

The MVP is usable locally.

You can run it with:

```bash
source .venv/bin/activate
uvicorn verialign.proxy.main:app --reload
```

Then call:

```bash
curl -s http://127.0.0.1:8000/health
```

Demo chat request:

```bash
curl -s http://127.0.0.1:8000/v1/chat/completions \
  -H "content-type: application/json" \
  -d '{
    "model": "demo",
    "messages": [{"role": "user", "content": "What is VeriAlign?"}],
    "metadata": {
      "context": [
        {"id": "doc-1", "text": "VeriAlign is a verification support proxy for LLM outputs."}
      ]
    }
  }'
```

View traces:

```bash
curl -s "http://127.0.0.1:8000/traces?limit=10"
```

## Next Steps

### 1. Improve OpenAI Request Compatibility

Add validation and pass-through support for common OpenAI fields:

- `temperature`
- `max_tokens`
- `top_p`
- `tools`
- `tool_choice`
- `response_format`

Also add tests proving these fields pass through to the upstream provider unchanged.

### 2. Normalize Provider Errors

Right now, upstream errors are returned mostly as raw text.

Improve this by returning a consistent shape:

```json
{
  "error": {
    "message": "...",
    "type": "upstream_error",
    "status_code": 429
  }
}
```

### 3. Add Proxy Authentication

Before real deployment, VeriAlign should require its own API key.

Suggested env var:

```bash
VERIALIGN_PROXY_API_KEY=...
```

Requests without the correct key should return HTTP `401`.

### 4. Add Sensitive Data Redaction

Stored traces may contain user data or secrets.

Add redaction for:

- Authorization headers
- API keys
- common secret-looking fields
- optionally full user messages

### 5. Improve Verification Quality

The current grounding approach is keyword overlap.

Upgrade options:

- Add embeddings-based semantic matching.
- Add stronger claim filtering.
- Add contradiction detection.
- Add explanations for each claim status.

### 6. Build A Dashboard

Add a simple Streamlit dashboard for trace review.

Useful first views:

- recent requests
- unsupported claims
- verification summary by model
- trace detail page

### 7. Add Docker Support

Create:

- `Dockerfile`
- `docker-compose.yml`

The goal should be:

```bash
docker compose up
```

And then:

```text
http://127.0.0.1:8000
```

### 8. Add CI

Add GitHub Actions to run:

```bash
.venv/bin/python -m pytest -q
```

On every pull request or push.

## Recommended Immediate Next Task

Implement OpenAI request compatibility tests and provider pass-through behavior.

This is the most practical next task because VeriAlign needs to behave predictably when used as a drop-in proxy for existing LLM apps.

