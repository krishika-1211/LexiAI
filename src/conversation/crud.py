from typing import List

from sqlalchemy.orm import Session

from src.category.models import Topic
from src.conversation.models import Conversation, ConversationSession, Report
from src.conversation.schemas import HistoryResponse
from utils.crud.base import CRUDBase


class ConversationSessionCRUD:
    def __init__(self):
        pass

    def create(
        self, db: Session, user_id: str, created_by: str, topic_id: str
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


class ConversationCRUD:
    def __init__(self):
        pass

    def user_conversation(
        self, db: Session, session_id: str, content: str, created_by: str
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

    def ai_conversation(
        self, db: Session, session_id: str, content: str, created_by: str
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


conversation_crud = ConversationCRUD()


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
