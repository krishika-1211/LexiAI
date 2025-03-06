from pydantic import BaseModel


class UserStatsResponse(BaseModel):
    total_session: int
    avg_score: float
    high_score: float
