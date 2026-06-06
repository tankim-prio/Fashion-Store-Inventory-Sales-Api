from typing import Any
from pydantic import BaseModel


class MLResponse(BaseModel):
    title: str
    summary: str
    data: Any = None
