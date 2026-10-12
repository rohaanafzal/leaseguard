# LeaseGuard AI

Know what you're signing before you sign it.

LeaseGuard reads a rental lease and pulls out every fee, deadline, and risky clause into structured data, computes your real monthly cost with plain code (not the LLM), and links every finding back to the exact text in the PDF.

> Status: Day 1 — PDF parsing + API skeleton. Not legal advice.

## Setup (Mac)

```bash
# 1. Install uv (fast Python manager) if you don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create the environment on Python 3.12 and install everything
uv sync

# 3. Add your API key
cp .env.example .env      # then open .env and paste your Groq key

# 4. Make the fake test lease and run tests
uv run python scripts/make_sample_lease.py
uv run pytest
```

## Try it

```bash
# Raw LLM call, no framework (Day 1 exercise)
uv run python scripts/raw_llm_call.py

# API — then open http://127.0.0.1:8000/docs and upload the sample lease
uv run uvicorn app.main:app --reload
```

## Layout

```
app/parser.py      PDF -> pages + text blocks with positions (for highlighting)
app/main.py        FastAPI: POST /parse
app/schemas.py     Extraction schemas (Fee, ...) — in progress
scripts/           raw LLM call, fake lease generator
tests/             parser + API tests
data/sample_leases fake lease with planted traps (answer key in make_sample_lease.py)
```

## Roadmap

- [x] Day 1: PDF parsing, API skeleton, raw structured LLM call
- [ ] Day 2: LangChain extraction + citation verifier + fee calculator
- [ ] Day 3: Clause flags + web UI with highlighted evidence
- [ ] Day 4: LangGraph Q&A with citation checking
- [ ] Day 5: Mini eval vs. plain-prompt baseline
- [ ] Day 6: Auth, deploy, privacy controls
- [ ] Day 7: Report download, polish
