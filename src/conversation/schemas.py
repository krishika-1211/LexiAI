from typing import Optional

from pydantic import BaseModel

from utils.schemas.base import BaseSchema


class HistoryResponse(BaseModel):
    id: str
    topic: str
    mins: float
    score: float


class ConversationSessionRequest(BaseSchema):
    user_id: str
    topic_id: Optional[str] = None


class ConversationSessionResponse(ConversationSessionRequest):
    total_time: float
