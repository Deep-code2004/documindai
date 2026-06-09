# TODO - Render + HF Space deployment

- [ ] Create Render backend web service
  - [ ] Root directory: backend/
  - [ ] Install: pip install -r backend/requirements.txt
  - [ ] Start: uvicorn app.main:app --host 0.0.0.0 --port 8000
  - [ ] Env: GEMINI_API_KEY
- [ ] Record Render backend URL
- [ ] Create Hugging Face Space (Streamlit)
  - [ ] Point BACKEND_URL to Render backend URL
  - [ ] Run ui/app/main.py
- [ ] Test:
  - [ ] /health returns ok
  - [ ] UI loads and chat/analyze endpoints work


