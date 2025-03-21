from typing import Optional


class HistoryResponse(BaseModel):
    id: str
    topic: str
    mins: float
    score: float
