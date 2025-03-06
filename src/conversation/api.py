from fastapi import APIRouter, status

from src.conversation.crud import user_stats_crud
from src.conversation.schemas import UserStatsResponse
from src.user.utils.deps import authenticated_user

session_router = APIRouter()


@session_router.get(
    "/stats", response_model=UserStatsResponse, status_code=status.HTTP_200_OK
)
def get_user_stats(authenticated: authenticated_user):
    user, db = authenticated

    stats = user_stats_crud.get_user_stats(db, user.id)

    if stats.total_session == 0:
        return UserStatsResponse(total_session=0, avg_score=0.0, high_score=0.0)

    return stats
