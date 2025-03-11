from pydantic import BaseModel


class HistoryResponse(BaseModel):
    id: str
    topic: str
    mins: str
    score: float
