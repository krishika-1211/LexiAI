from typing import Optional

from pydantic import BaseModel


class HistoryResponse(BaseModel):
    id: str
    topic: str
    mins: float
    score: Optional[float] = None
