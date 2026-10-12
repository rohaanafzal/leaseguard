"""Generate a FAKE 3-page test lease with deliberate traps.

All names/addresses are invented. Traps planted (this is our answer key):
  - Rent $850/mo, but mandatory monthly fees: trash $25, pest $15, amenity $40,
    tech package $55, pet rent $35 -> true recurring $1,020/mo (not $850)
  - Pet rent $35/mo is stated twice in the addendum (double-count trap)
  - One-time: application $75, admin $200, move-out cleaning $150
  - Deposit $850 (refundable), pet deposit $300 (non-refundable — trap!)
  - Conditional: late fee $50 + $10/day, returned check $40, lock change "actual cost"
  - Auto-renewal month-to-month at +$150/mo unless 60 days' written notice
  - Early termination: 2 months' rent

Run: python scripts/make_sample_lease.py
"""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

OUT = Path(__file__).resolve().parent.parent / "data" / "sample_leases" / "sample_lease.pdf"

PAGES = [
    [
        ("h", "RESIDENTIAL LEASE AGREEMENT"),
        ("p", "This Lease is made between Oakridge Commons Property Management LLC (\"Landlord\") "
              "and Jordan Example (\"Tenant\") for Unit 14B, 100 Sample Lane, Exampletown, AL 36800."),
        ("h", "1. TERM"),
        ("p", "The lease term begins August 1, 2027 and ends July 31, 2028."),
        ("h", "2. RENT"),
        ("p", "Tenant shall pay monthly rent of $850.00, due on the 1st day of each month."),
        ("h", "3. MANDATORY MONTHLY FEES"),
        ("p", "In addition to rent, Tenant shall pay the following each month with rent: valet trash "
              "service fee of $25.00; pest control fee of $15.00; community amenity fee of $40.00; "
              "and a technology package (internet and cable) fee of $55.00. These fees are not optional."),
        ("h", "4. ONE-TIME CHARGES"),
        ("p", "Tenant has paid a non-refundable application fee of $75.00. An administrative fee of "
              "$200.00 is due at lease signing. A move-out cleaning fee of $150.00 will be charged at the "
              "end of the tenancy regardless of unit condition."),
    ],
    [
        ("h", "5. SECURITY DEPOSIT"),
        ("p", "Tenant shall pay a security deposit of $850.00, refundable within 60 days after move-out "
              "less any deductions for damages, unpaid rent, or other charges under this Lease."),
        ("h", "6. LATE PAYMENT AND RETURNED PAYMENTS"),
        ("p", "Rent not received by the 3rd day of the month incurs a late fee of $50.00 plus $10.00 per "
              "additional day until paid in full. Any returned check or failed electronic payment incurs "
              "a $40.00 charge."),
        ("h", "7. RENEWAL"),
        ("p", "Unless either party gives written notice at least sixty (60) days before the end of the "
              "term, this Lease shall automatically renew on a month-to-month basis at the then-current "
              "monthly rent plus a month-to-month premium of $150.00 per month."),
        ("h", "8. EARLY TERMINATION"),
        ("p", "Tenant may terminate this Lease early by giving 30 days' written notice and paying an "
              "early termination fee equal to two (2) months' rent."),
        ("h", "9. MAINTENANCE AND KEYS"),
        ("p", "Tenant is responsible for replacing air filters and light bulbs. Lost keys or lock "
              "changes requested by Tenant will be charged at Landlord's actual cost."),
    ],
    [
        ("h", "PET ADDENDUM"),
        ("p", "This addendum is part of the Lease for Unit 14B. Tenant may keep one (1) cat."),
        ("p", "Tenant shall pay a pet deposit of $300.00, which is non-refundable. Tenant shall pay "
              "monthly pet rent of $35.00."),
        ("h", "FEE SUMMARY (for reference)"),
        ("p", "Monthly pet rent: $35.00 (as stated above). Pet deposit: $300.00."),
        ("h", "SIGNATURES"),
        ("p", "Landlord: ______________________ Date: ________"),
        ("p", "Tenant: ________________________ Date: ________"),
    ],
]


def main() -> None:
    styles = getSampleStyleSheet()
    story = []
    for i, page in enumerate(PAGES):
        for kind, text in page:
            story.append(Paragraph(text, styles["Heading3" if kind == "h" else "BodyText"]))
            story.append(Spacer(1, 6))
        if i < len(PAGES) - 1:
            story.append(PageBreak())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(OUT), pagesize=letter, title="Sample Lease (fake)").build(story)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
