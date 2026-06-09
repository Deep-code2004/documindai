# Deploy backend to Render (FastAPI)

## Prereqs
- A Render account
- `GEMINI_API_KEY` value

## Option A (recommended): Render **Python Web Service** (no Docker)
1. Create a **New Web Service** → choose **Python**.
2. Connect the repo (this folder).
3. Set **Runtime**: Python 3.11 (or closest supported).
4. Build/Install command:
   - Use: `pip install -r backend/requirements.txt`
5. Start command:
   - Use: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
6. Environment variables:
   - `GEMINI_API_KEY=<your key>`
7. Ensure the working directory / root is set correctly:
   - Code lives in `backend/`.
   - If Render asks for “Root Directory”, set it to: `backend/`.


### After deploy
- Test the backend health endpoint:
  - `GET https://<your-render-backend>.onrender.com/health`
- Confirm CORS:
  - The backend currently allows `allow_origins=["*"]`, so it should work.

## Hooking the UI to Render backend
Update UI env var `BACKEND_URL`:
- On the Render/HF side where the UI runs, set:
  - `BACKEND_URL=https://<your-render-backend>.onrender.com`

---

# Deploy UI to Hugging Face Spaces (Streamlit)

## Create Space
1. Create a **New Space** → SDK: **Streamlit**.
2. In Space settings, set secrets/environment variables:
   - `BACKEND_URL=https://<your-render-backend>.onrender.com`
   - (Optional) `GEMINI_API_KEY` only if you decide to call Gemini directly from the UI (current app calls Gemini in the backend only).

## Configure Space build
- Use the `ui/` folder as the app directory.

## Start command
- Streamlit default is usually fine; if you can set it explicitly, use:
  - `streamlit run app/main.py --server.port 7860 --server.address 0.0.0.0`

---

# Upload and chat with a PDF (important note)
Current UI MVP supports **text-based uploads** only: `.txt/.md/.csv/.json`.

To “share a PDF and talk with that chatbot” you need a text-extraction step for PDFs in the UI (or in the backend), then pass the extracted text into `/api/analyze` and `/api/chat`.

## What to do next (code-level)
1. Implement PDF text extraction in `ui/app/main.py`:
   - Add `.pdf` to `st.file_uploader(type=...)`
   - If file endswith `.pdf`, extract text (e.g., using `PyPDF2` already in backend deps; you can add it to UI deps too or move extraction to backend).
2. Alternatively (better architecture):
   - Add a new backend route like `/api/extract` or extend `/api/analyze` to accept uploaded files.

Once extraction works, the rest of the chat flow already mirrors ChatPDF: upload → extract → analyze → chat.


---

# Notes / troubleshooting
- If you see `503 UNAVAILABLE` / `500` from Gemini:
  - It’s not Render connectivity; it’s Gemini model availability/quota.
  - Try a different model name or verify your API key.

