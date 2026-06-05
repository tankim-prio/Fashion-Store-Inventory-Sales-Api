from typing import Any
from pydantic import BaseModel, Field


class AIQuestion(BaseModel):
    question: str = Field(..., min_length=2, max_length=500)


class AIResponse(BaseModel):
    answer: str
    data: Any = None
    suggestions: list[str] = []
