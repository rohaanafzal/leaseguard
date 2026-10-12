from pathlib import Path

import pymupdf
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.parser import parse_pdf, parse_pdf_bytes

SAMPLE = Path(__file__).resolve().parent.parent / "data" / "sample_leases" / "sample_lease.pdf"
client = TestClient(app)


@pytest.fixture(scope="module")
def doc():
    if not SAMPLE.exists():
        pytest.skip("Run scripts/make_sample_lease.py first")
    return parse_pdf(SAMPLE)


def test_page_count(doc):
    assert doc.page_count == 3


def test_key_text_on_right_pages(doc):
    assert "$850.00" in doc.pages[0].text
    assert "automatically renew" in doc.pages[1].text
    assert "pet rent of $35.00" in doc.pages[2].text


def test_blocks_have_positions(doc):
    block = doc.pages[0].blocks[0]
    x0, y0, x1, y1 = block.bbox
    assert x1 > x0 and y1 > y0
    assert block.page == 1


def test_blank_pdf_flagged_as_scanned():
    blank = pymupdf.open()
    blank.new_page()
    parsed = parse_pdf_bytes(blank.tobytes())
    assert parsed.is_scanned


def test_garbage_rejected():
    with pytest.raises(ValueError):
        parse_pdf_bytes(b"not a pdf at all")


def test_api_parse(doc):
    r = client.post("/parse", files={"file": ("lease.pdf", SAMPLE.read_bytes(), "application/pdf")})
    assert r.status_code == 200
    assert r.json()["page_count"] == 3


def test_api_rejects_non_pdf():
    r = client.post("/parse", files={"file": ("evil.pdf", b"MZ fake exe", "application/pdf")})
    assert r.status_code == 400
