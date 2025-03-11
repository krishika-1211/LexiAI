from typing import List

from fastapi import APIRouter, HTTPException, status

from src.category.models import Topic
from src.conversation.models import ConversationSession, Report
from src.conversation.schemas import HistoryResponse
from src.user.utils.deps import authenticated_user

conversation_router = APIRouter()


@conversation_router.get(
    "/history", response_model=List[HistoryResponse], status_code=status.HTTP_200_OK
)
def get_history(authenticated: authenticated_user):
    user, db = authenticated

    try:
        sessions = (
            db.query(ConversationSession)
            .join(Topic, Topic.id == ConversationSession.topic_id)
            .outerjoin(Report, Report.session_id == ConversationSession.id)
            .filter(ConversationSession.user_id == user.id)
            .all()
        )

        history = []
        for session in sessions:
            history.append(
                HistoryResponse(
                    id=session.id,
                    topic=session.topic.name,
                    mins=session.total_time,
                    score=session.report.score,
                )
            )

        return history

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
