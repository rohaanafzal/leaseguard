"""Extraction schemas — YOUR file to write (Day 1 task).

What is a schema here?
It's the exact shape we force the LLM's answer into. Instead of "tell me about
the fees" (free text we can't compute with), we say "return a list of Fee
objects with these fields." Pydantic then *validates* the answer: wrong types
or missing fields raise an error instead of silently slipping through.

Example from a real lease:
    "Tenant shall pay a monthly pest control fee of $15.00, billed with rent."
should become something like:
    Fee(name="Pest control", amount=15.0, frequency="monthly",
        category="recurring", is_conditional=False,
        source_quote="monthly pest control fee of $15.00", page=3)

Design questions to think about while writing Fee (we'll discuss your answers):
  1. Some fees have no fixed amount ("actual cost of repairs"). How do you
     represent "unknown amount" without inventing a number?
  2. A late fee only happens IF you pay late. How do you mark that so the
     calculator doesn't add it to monthly cost?
  3. A deposit is money you (maybe) get back. Is it a "fee"? Same category?
  4. Why must source_quote be an EXACT copy of the lease text, not a summary?
     (Hint: think about the verifier we build on Day 2.)

Fill in the TODOs. Delete the `raise` line when Fee is ready.
"""

from typing import Literal

from pydantic import BaseModel, Field

# --- Allowed values. Literal means the LLM can ONLY return one of these. ---
FeeFrequency = Literal[
    # TODO: e.g. "monthly", "one_time", ... add what you see in real leases
]

FeeCategory = Literal[
    # TODO: recurring, one-time, deposit, conditional, optional, penalty?
]


class Fee(BaseModel):
    # TODO: name — short label, e.g. "Pest control"
    # TODO: amount — dollars. What type if it can be unknown? (see question 1)
    # TODO: frequency: FeeFrequency
    # TODO: category: FeeCategory
    # TODO: is_conditional — and maybe a field saying WHAT the condition is
    # TODO: source_quote — exact text copied from the lease
    # TODO: page — page number where the quote appears
    #
    # Tip: Field(description="...") text gets sent to the LLM as instructions,
    # so write descriptions as if you're explaining the field to a person.
    pass


class FeeExtraction(BaseModel):
    """Top-level wrapper: the LLM returns one of these per lease."""

    fees: list[Fee] = Field(description="Every financial obligation found in the lease.")


raise NotImplementedError("Fee schema not written yet — see TODOs in app/schemas.py")
