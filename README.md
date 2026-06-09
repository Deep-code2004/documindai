# DocuMind AI — FastAPI + Streamlit + Docker

## Run
1. Set `GEMINI_API_KEY` in `streamlit-fastapi-docker/.env`.
2. Run:
- `pip install -r backend/requirements.txt` and `pip install -r ui/requirements.txt`
- In one terminal: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000`
- In another terminal: `cd ui && streamlit run app/main.py --server.address 0.0.0.0 --server.port 8501`

Also supports Docker: `docker compose up --build`


## URLs
- Streamlit UI: http://localhost:8501
- FastAPI backend: http://localhost:8000/health

Chat state: stored in a Docker volume (`docmindai_data`).

