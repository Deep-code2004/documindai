# PDF upload + chat support (UI code changes)

## Problem
Current Streamlit UI only accepts text-based files (.txt/.md/.csv/.json). Uploading a .pdf fails.

## Goal
Allow users to upload a PDF and immediately chat with it, like “share a PDF and talk with that chatbot”.

## Approach
Implement PDF text extraction inside the UI (simplest), then reuse existing `/api/analyze` and `/api/chat` endpoints.

## Code changes (ui/app/main.py)
1. Update uploader types to include pdf:
   - `type=["txt","md","csv","json","pdf"]`
2. Update `extract_file_text()`:
   - If filename endswith `.pdf`:
     - Extract all page text using `PyPDF2`.
     - Return concatenated text.
   - Keep existing behavior for text-based formats.
3. Add dependency to UI:
   - `PyPDF2` is already in backend requirements, but not in UI requirements.
   - Add `PyPDF2==3.0.1` to `ui/requirements.txt`.

## Notes
- If the PDF is scanned images, text extraction may return empty; add fallback later (OCR) if needed.
- After extraction, UI passes `documentText` to backend exactly as before.

## Files to edit
- `ui/app/main.py`
- `ui/requirements.txt`

## Verification
- Run locally with docker compose.
- Upload a small PDF.
- Check that:
  - “Analyzing document...” succeeds
  - Chat answers are returned.

