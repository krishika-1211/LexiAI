from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from src.conversation.models import ConversationSession, Report
from src.conversation.schemas import UserStatsResponse


class UserStatsCRUD:
    def get_user_stats(self, db: Session, user_id: str) -> UserStatsResponse:
        total_session = db.query(ConversationSession).filter_by(user_id=user_id).count()

        avg_score = (
            db.query(func.avg(Report.score))
            .join(ConversationSession)
            .filter(ConversationSession.user_id == user_id)
            .scalar()
            or 0
        )

        high_score = (
            db.query(func.max(Report.score))
            .join(ConversationSession)
            .filter(ConversationSession.user_id == user_id)
            .scalar()
            or 0
        )

        return UserStatsResponse(
            total_session=total_session,
            avg_score=round(avg_score, 2),
            high_score=round(high_score, 2),
        )


user_stats_crud = UserStatsCRUD()
