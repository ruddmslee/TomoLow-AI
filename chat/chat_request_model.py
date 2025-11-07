from pydantic import BaseModel
from datetime import date
from typing import Optional

class ChatRequest(BaseModel):
    question: str
    data_selected: bool
    tickers: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None

def build_chat_request(question, extract_result):
    return ChatRequest(
        question=question,
        data_selected=True,
        tickers=extract_result["ticker"],
        start_date=extract_result["start"],
        end_date=extract_result["end"]
    )