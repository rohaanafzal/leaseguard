"""FastAPI app. Day 1: upload a PDF, get back parsed pages as JSON.

Run:  uvicorn app.main:app --reload
Then open http://127.0.0.1:8000/docs to try it in the browser.
"""

from fastapi import FastAPI, HTTPException, UploadFile

from app.parser import ParsedDocument, parse_pdf_bytes

MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15 MB — leases are small; blocks abuse

app = FastAPI(title="LeaseGuard AI", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/parse", response_model=ParsedDocument)
async def parse(file: UploadFile) -> ParsedDocument:
    data = await file.read()

    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "File too large (max 15 MB).")
    # Check the actual bytes, not just the filename — anyone can rename a file.
    if not data.startswith(b"%PDF"):
        raise HTTPException(400, "That doesn't look like a PDF.")

    try:
        parsed = parse_pdf_bytes(data, filename=file.filename or "upload.pdf")
    except ValueError as e:
        raise HTTPException(400, str(e)) from e

    if parsed.is_scanned:
        raise HTTPException(
            422, "This looks like a scanned lease. Scanned PDFs aren't supported yet."
        )
    return parsed
