from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

from ..services.gemini_service import analyze_document

router = APIRouter()


class AnalyzeRequest(BaseModel):
    documentText: str
    documentName: Optional[str] = None


class AnalyzeResponse(BaseModel):
    summary: str
    keyTakeaways: List[str]
    suggestedQuestions: List[str]


@router.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    try:
        return analyze_document(document_text=req.documentText, document_name=req.documentName)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

