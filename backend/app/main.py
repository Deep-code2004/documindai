from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import analyze, chat, health



app = FastAPI(title="DocuMind AI - FastAPI Backend")

# Streamlit UI talks to this backend over localhost:8000
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(chat.router)

