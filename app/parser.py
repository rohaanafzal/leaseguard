"""PDF parsing: turn a lease PDF into text we can cite back to.

Why keep page numbers and positions?
Every finding LeaseGuard shows must point to the exact spot in the PDF.
If we only kept one big text blob, we couldn't highlight evidence later.
So we keep text per page, and per text block (a paragraph-ish chunk) with
its bounding box (x0, y0, x1, y1) on the page.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf
from pydantic import BaseModel

# If a page has fewer characters than this, it's probably a scanned image.
MIN_CHARS_FOR_TEXT_PAGE = 30


class TextBlock(BaseModel):
    page: int  # 1-indexed, matches what users see in a PDF viewer
    text: str
    bbox: tuple[float, float, float, float]  # position on the page, for highlighting


class Page(BaseModel):
    number: int
    text: str
    blocks: list[TextBlock]
    likely_scanned: bool


class ParsedDocument(BaseModel):
    filename: str
    page_count: int
    pages: list[Page]

    @property
    def full_text(self) -> str:
        return "\n\n".join(f"[Page {p.number}]\n{p.text}" for p in self.pages)

    @property
    def is_scanned(self) -> bool:
        """True if most pages have no real text layer (needs OCR, not supported yet)."""
        if not self.pages:
            return False
        scanned = sum(p.likely_scanned for p in self.pages)
        return scanned > len(self.pages) / 2


def _clean(text: str) -> str:
    # A block is roughly one paragraph. PDFs break lines wherever the page edge
    # is, so "pet rent of\n$35.00" must become "pet rent of $35.00" — otherwise
    # exact-quote matching (our citation verifier) fails on perfectly good quotes.
    return " ".join(text.split())


def parse_pdf_bytes(data: bytes, filename: str = "upload.pdf") -> ParsedDocument:
    try:
        doc = pymupdf.open(stream=data, filetype="pdf")
    except Exception as e:  # corrupted or not actually a PDF
        raise ValueError(f"Could not open PDF: {e}") from e

    if doc.needs_pass:
        raise ValueError("PDF is password-protected.")

    pages: list[Page] = []
    with doc:
        for i, pg in enumerate(doc, start=1):
            blocks: list[TextBlock] = []
            # get_text("blocks") -> (x0, y0, x1, y1, text, block_no, block_type)
            for x0, y0, x1, y1, text, _no, btype in pg.get_text("blocks", sort=True):
                if btype != 0:  # 1 = image block, skip
                    continue
                cleaned = _clean(text)
                if cleaned:
                    blocks.append(TextBlock(page=i, text=cleaned, bbox=(x0, y0, x1, y1)))
            page_text = "\n".join(b.text for b in blocks)
            pages.append(
                Page(
                    number=i,
                    text=page_text,
                    blocks=blocks,
                    likely_scanned=len(page_text) < MIN_CHARS_FOR_TEXT_PAGE,
                )
            )

    return ParsedDocument(filename=filename, page_count=len(pages), pages=pages)


def parse_pdf(path: str | Path) -> ParsedDocument:
    path = Path(path)
    return parse_pdf_bytes(path.read_bytes(), filename=path.name)
