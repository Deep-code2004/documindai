from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Any, List, Optional, Literal

from ..services.gemini_service import chat_with_document

router = APIRouter()


class ChatMessage(BaseModel):
    role: Literal["user", "model"]
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    documentText: str
    documentName: Optional[str] = None


class ChatResponse(BaseModel):
    text: str


@router.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        return {"text": chat_with_document(messages=req.messages, document_text=req.documentText, document_name=req.documentName)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

