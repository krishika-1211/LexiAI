from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import Float, Integer, String

from src.category.models import Topic
from utils.db.base import ModelBase


class ConversationSession(ModelBase):
    total_time = Column(Float, default=0)

    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    topic_id = Column(String, ForeignKey("topic.id", ondelete="CASCADE"))

    user = relationship("src.user.models.User", back_populates="session")
    topic = relationship(Topic, back_populates="session")
    report = relationship("Report", back_populates="session", cascade="all, delete")
    conversation = relationship(
        "Conversation", back_populates="session", cascade="all, delete"
    )


class Conversation(ModelBase):
    role = Column(String, nullable=False)
    content = Column(String)

    session_id = Column(
        String, ForeignKey("conversation_session.id", ondelete="CASCADE")
    )

    session = relationship("ConversationSession", back_populates="conversation")


class Report(ModelBase):
    score = Column(Float, default=0)
    feedback = Column(String, nullable=True)
    words_spoken = Column(Integer, default=0)

    user_id = Column(String, ForeignKey("user.id", ondelete="CASCADE"))
    topic_id = Column(String, ForeignKey("topic.id"))
    session_id = Column(
        String, ForeignKey("conversation_session.id", ondelete="CASCADE")
    )

    topic = relationship(Topic, back_populates="report")
    session = relationship("ConversationSession", back_populates="report")
