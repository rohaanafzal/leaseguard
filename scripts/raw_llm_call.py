"""Day 1 exercise: call an LLM with NO framework and get structured output.

Why do this before LangChain?
LangChain hides three steps behind one line. Doing them by hand once means
you'll know what's happening (and what to debug) when you use it tomorrow:
  1. Describe the output shape to the model (we send a JSON schema).
  2. Ask for JSON back (response_format = json_object).
  3. Validate the reply against the schema (Pydantic). If it fails, we KNOW.

This uses a tiny practice schema (LeaseBasics), not your Fee schema, so you
can see the pattern working before writing your own.

Run:  python scripts/raw_llm_call.py data/sample_leases/sample_lease.pdf
"""

import json
import os
import sys

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from app.parser import parse_pdf  # noqa: E402
from app.schemas import FeeExtraction  # noqa: E402

load_dotenv()

# Groq speaks the same API format as OpenAI, so this is a plain HTTP POST.
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")  # check console.groq.com for current models


class LeaseBasics(BaseModel):
    monthly_rent: float | None = Field(description="Base monthly rent in dollars, or null if not stated.")
    lease_start: str | None = Field(description="Lease start date as written in the lease.")
    lease_end: str | None = Field(description="Lease end date as written in the lease.")
    landlord_name: str | None = Field(description="Landlord or property manager name.")
    parking_fee: float | None = Field(description="Monthly parking fee")

def main(pdf_path: str) -> None:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        sys.exit("Missing GROQ_API_KEY. Copy .env.example to .env and paste your key.")

    doc = parse_pdf(pdf_path)

    # Step 1: tell the model the exact shape we want, using Pydantic's JSON schema.
    schema = json.dumps(FeeExtraction.model_json_schema(), indent=2)
    system = (
        "You extract facts from rental leases. Reply with ONLY a JSON object "
        f"matching this JSON schema:\n{schema}\n"
        "Use null for anything the lease does not state. Never guess."
    )

    # Step 2: send the request, asking for JSON mode.
    resp = httpx.post(
        GROQ_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "model": MODEL,
            "temperature": 0,  # 0 = most deterministic; we want facts, not creativity
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": doc.full_text},
            ],
        },
        timeout=60,
    )
    resp.raise_for_status()
    body = resp.json()
    raw = body["choices"][0]["message"]["content"]
    print("Raw model reply:\n", raw, "\n")

    # Step 3: validate. This is the line that catches bad/hallucinated shapes.
    try:
        basics = FeeExtraction.model_validate_json(raw)
    except ValidationError as e:
        sys.exit(f"Model reply didn't match the schema:\n{e}")

    print("Validated:", basics)
    print("Tokens used:", body.get("usage"))  # this is what costs money on paid APIs


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/sample_leases/sample_lease.pdf")
