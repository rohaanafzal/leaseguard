"""Extraction schemas: the exact shape the LLM's answer must fit.

Design decisions (the 4 questions):
  1. Unknown amounts ("actual cost of repairs") -> amount is None, and
     amount_text keeps the original wording. We never invent a number.
  2. Conditional fees (late fee) -> category="conditional" plus a `condition`
     saying WHEN it applies. The calculator never adds these to monthly cost.
  3. Deposits are their own category, with is_refundable. A NON-refundable
     "deposit" is really a one-time fee, and the calculator treats it that way.
  4. source_quote must be copied exactly so the verifier can find it in the
     PDF text. A paraphrase can't be checked, so it can't be trusted.

Note: amount is a float here because this is what the LLM fills in (JSON has
no Decimal type). The calculator converts to Decimal before doing any math.
"""

from typing import Literal

from pydantic import BaseModel, Field, model_validator

FeeFrequency = Literal[
    "monthly",
    "one_time",
    "daily",  # e.g. "$10 per additional day" late fees
    "annual",
    "per_occurrence",  # each time something happens (returned check, lock change)
]

FeeCategory = Literal[
    "recurring",  # mandatory, paid every period no matter what (rent, trash, pet rent)
    "one_time",  # paid once for sure (admin fee, mandatory move-out cleaning)
    "deposit",  # money held by landlord; may or may not come back
    "conditional",  # only if something happens (late fee, early termination, lost keys)
    "optional",  # tenant chooses it (reserved parking, storage unit)
]


class Fee(BaseModel):
    name: str = Field(
        description="Short label for the fee as the lease calls it, e.g. 'Pest control fee'."
    )
    amount: float | None = Field(
        description=(
            "Dollar amount as a number, e.g. 15.0 for $15.00. Use null if the lease gives no "
            "fixed dollar figure (e.g. 'actual cost', 'two months' rent'). Never estimate."
        )
    )
    amount_text: str | None = Field(
        default=None,
        description=(
            "How the lease words the amount when it isn't a plain fixed number, e.g. "
            "'two (2) months' rent', 'Landlord's actual cost', '$50.00 plus $10.00 per day'."
        ),
    )
    frequency: FeeFrequency = Field(description="How often this fee is charged.")
    category: FeeCategory = Field(
        description=(
            "recurring = mandatory every period; one_time = paid once for certain; "
            "deposit = held by landlord; conditional = only if an event happens "
            "(late payment, breaking the lease, lost keys); optional = tenant chooses it."
        )
    )
    condition: str | None = Field(
        default=None,
        description="For conditional fees: the event that triggers it, e.g. 'rent paid after the 3rd'.",
    )
    is_refundable: bool | None = Field(
        default=None,
        description="For deposits only: true if the lease says it can be returned, false if non-refundable.",
    )
    source_quote: str = Field(
        description=(
            "The exact sentence or phrase from the lease that states this fee, copied word for "
            "word. Do not paraphrase, fix typos, or combine text from different places."
        )
    )
    page: int = Field(description="Page number where source_quote appears (from the [Page N] markers).")

    @model_validator(mode="after")
    def conditional_needs_condition(self) -> "Fee":
        # Pydantic runs this after the fields are filled. Catches lazy LLM output.
        if self.category == "conditional" and not self.condition:
            raise ValueError("conditional fees must say what triggers them in `condition`")
        return self


class FeeExtraction(BaseModel):
    """Top-level wrapper: the LLM returns one of these per lease."""

    fees: list[Fee] = Field(description="Every financial obligation found in the lease.")