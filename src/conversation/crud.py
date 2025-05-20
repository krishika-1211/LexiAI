from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.billing.models import Plan, Subscription
from src.category.models import Topic
from src.conversation.models import Conversation, ConversationSession, Report
from src.conversation.schemas import HistoryResponse
from src.user.models import User
from utils.crud.base import CRUDBase


class ConversationSessionCRUD:
    @staticmethod
    def create(
        db: Session, user_id: str, created_by: str, topic_id: str
    ) -> ConversationSession:
        session = ConversationSession(
            user_id=user_id,
            created_by=created_by,
            updated_by=created_by,
            topic_id=topic_id,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session


conversation_session_crud = ConversationSessionCRUD()


class ConversationCrud:
    @staticmethod
    def user_conversation(
        db: Session, session_id: str, content: str, created_by: str
    ) -> Conversation:
        conversation = Conversation(
            role="user",
            content=content,
            session_id=session_id,
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def ai_conversation(
        db: Session, session_id: str, content: str, created_by: str
    ) -> Conversation:
        conversation = Conversation(
            role="ai",
            content=content,
            session_id=session_id,
            created_by=created_by,
            updated_by=created_by,
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        return conversation

    @staticmethod
    def check_conversation_permission(db: Session, user_id: str):
        subscription = (
            db.query(Subscription).filter(Subscription.user_id == user_id).first()
        )
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have subscription",
            )

        plan = db.query(Plan).filter(Plan.id == subscription.plan_id).first()
        if not plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plan with the subscription not found",
            )

        allowed_conversations = plan.allowed_conversations

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        if user.used_conversations >= allowed_conversations:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You exceeded allowed conversations for the subscription plan",
            )

        user.used_conversations += 1
        db.commit()
        db.refresh(user)

        return allowed_conversations - user.used_conversations


conversation_crud = ConversationCrud()


class HistoryCRUD(CRUDBase[ConversationSession, None, HistoryResponse]):
    def get_user_history(self, db: Session, user_id: str) -> List[HistoryResponse]:
        sessions = (
            db.query(ConversationSession)
            .join(Topic, Topic.id == ConversationSession.topic_id)
            .outerjoin(Report, Report.session_id == ConversationSession.id)
            .filter(ConversationSession.user_id == user_id)
            .all()
        )
        return [
            HistoryResponse(
                id=session.id,
                topic=session.topic.name,
                mins=session.total_time,
                score=session.report[0].score if session.report else None,
            )
            for session in sessions
        ]


history_crud = HistoryCRUD(ConversationSession)
