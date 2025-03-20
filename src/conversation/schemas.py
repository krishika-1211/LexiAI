from pydantic import BaseModel


class HistoryResponse(BaseModel):
    id: str
    topic: str
    mins: float
    score: float
